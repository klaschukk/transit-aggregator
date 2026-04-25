#!/usr/bin/env python3
"""Populate {site_title}, {their_topic}, {our_hook} in backlinks-targets.csv.

For each row with status='todo' and enriched_at='':
  1. GET the target URL (15s timeout, browser-style UA)
  2. Extract <title> → site_title
  3. Extract the first 2 h1/h2/h3 headings → their_topic (joined)
  4. Keyword-match transit/travel vocabulary → suggest our_hook
  5. Write enriched_at=<ISO timestamp> and flip status→'enriched'

Also opportunistically sniffs a contact email from the page
(mailto: links, "info@domain", "contact@domain") — never overwrites an
existing `contact_email`, only fills empties.

Rate-limited to 1 req/s so we look like a normal visitor. Idempotent:
re-running only touches rows that haven't been enriched yet unless
--force is passed.

    scripts/backlinks_enrich.py --n 20
    scripts/backlinks_enrich.py --force --only-domain example.com
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.outreach import load_targets, save_targets  # noqa: E402

try:
    import requests
except ImportError:
    print('requests required: pip install requests', file=sys.stderr)
    sys.exit(2)


HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (compatible; PrevozniEnrich/1.0; '
        '+https://prevozni.com/bot)'
    ),
    'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1',
    'Accept-Language': 'en,sr;q=0.8,ru;q=0.6',
}


# Category → hook URL mapping. The enricher suggests this as a default
# deep link — a human can override by editing `our_hook` in the CSV.
_HOOK_FOR_CATEGORY: dict[str, str] = {
    'serbian_tourism':        'https://prevozni.com/rute/',
    'serbian_gov':            'https://prevozni.com/rute/',
    'serbian_operator':       'https://prevozni.com/prevoznici/',
    'travel_blog_global':     'https://prevozni.com/destinacije/',
    'balkan_blog':            'https://prevozni.com/destinacije/',
    'expat_serbia':           'https://prevozni.com/gradski/beograd/',
    'travel_forum':           'https://prevozni.com/rute/',
    'russian_diaspora':       'https://prevozni.com/ru/rute/',
    'broken_link_candidates': 'https://prevozni.com/rute/',
    'youtube_travel':         'https://prevozni.com/destinacije/',
    'facebook_groups':        'https://prevozni.com/gradski/beograd/',
    'wikipedia_edit':         'https://prevozni.com/rute/',
}


_KEYWORD_HOOKS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(r'belgrade|beograd', re.I), 'https://prevozni.com/gradski/beograd/'),
    (re.compile(r'novi sad|novisad', re.I), 'https://prevozni.com/gradski/novi-sad/'),
    (re.compile(r'ni[sš]|nis', re.I),       'https://prevozni.com/gradski/nis/'),
    (re.compile(r'kragujevac', re.I),       'https://prevozni.com/gradski/kragujevac/'),
    (re.compile(r'bus|autobus|автобус'),    'https://prevozni.com/rute/'),
    (re.compile(r'train|voz|поезд'),        'https://prevozni.com/prevoznici/'),
    (re.compile(r'montenegro|crna gora'),   'https://prevozni.com/destinacije/crna-gora/'),
)

_EMAIL_RE = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
)


class _MetaExtractor(HTMLParser):
    """Pulls <title> and the first few h1/h2/h3 texts out of an HTML
    document without depending on bs4 — keeps the enricher runnable
    on a stripped-down cron host."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.headings: list[str] = []
        self._in_title = False
        self._heading_buf: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title = True
        elif tag in ('h1', 'h2', 'h3') and len(self.headings) < 3:
            self._heading_buf = []

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        elif tag in ('h1', 'h2', 'h3') and self._heading_buf is not None:
            text = ' '.join(''.join(self._heading_buf).split()).strip()
            if text:
                self.headings.append(text)
            self._heading_buf = None

    def handle_data(self, data):
        if self._in_title:
            self.title_parts.append(data)
        elif self._heading_buf is not None:
            self._heading_buf.append(data)

    @property
    def title(self) -> str:
        return ' '.join(''.join(self.title_parts).split()).strip()


def _pick_hook(category: str, text: str) -> str:
    """Best hook URL for this target. First matching keyword wins;
    falls back to the category default; final fallback is /rute/."""
    for pat, hook in _KEYWORD_HOOKS:
        if pat.search(text):
            return hook
    return _HOOK_FOR_CATEGORY.get((category or '').strip(),
                                  'https://prevozni.com/rute/')


def _extract_email(html: str, domain: str) -> str:
    """Prefer `info@domain`/`contact@domain`/`hello@domain` over any
    random match. Avoids picking up CDN / third-party addresses."""
    candidates = set(m.group(0).lower() for m in _EMAIL_RE.finditer(html or ''))
    d = (domain or '').strip().lower().lstrip('.')
    preferred_prefixes = ('info@', 'contact@', 'hello@', 'team@', 'press@')

    # Score: same-domain preferred, preferred-prefix preferred.
    def score(addr: str) -> int:
        s = 0
        if d and addr.endswith('@' + d):
            s += 10
        if any(addr.startswith(p) for p in preferred_prefixes):
            s += 5
        return s

    if not candidates:
        return ''
    ranked = sorted(candidates, key=score, reverse=True)
    best = ranked[0]
    return best if score(best) > 0 else ''


def enrich_one(row: dict, session: requests.Session, timeout: int) -> bool:
    """Mutate `row` in place. Return True when any field was updated."""
    url = (row.get('url') or '').strip()
    if not url:
        return False
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
    except Exception as exc:  # noqa: BLE001
        row['notes'] = (row.get('notes') or '') + f' [enrich_err: {exc!r}]'
        return True

    if resp.status_code != 200 or not resp.text:
        row['notes'] = (row.get('notes') or '') + \
            f' [enrich_err: HTTP {resp.status_code}]'
        return True

    parser = _MetaExtractor()
    try:
        parser.feed(resp.text[:300_000])  # cap to keep runtime bounded
    except Exception:
        pass

    title = parser.title[:200]
    topic = ' · '.join(parser.headings[:2])[:200]

    row['site_title'] = title or row.get('site_title') or ''
    row['their_topic'] = topic or row.get('their_topic') or ''
    row['our_hook'] = row.get('our_hook') or _pick_hook(
        row.get('category', ''), (title + ' ' + topic + ' ' + resp.text[:5000]),
    )
    if not (row.get('contact_email') or '').strip():
        sniffed = _extract_email(resp.text, urlparse(url).hostname or '')
        if sniffed:
            row['contact_email'] = sniffed

    row['enriched_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    # Only move status forward when we're still at 'todo' — never
    # overwrite 'contacted'/'replied'/'backlinked'.
    if (row.get('status') or '').strip() in ('', 'todo'):
        row['status'] = 'enriched'
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', type=Path, default=None)
    ap.add_argument('--n', type=int, default=20,
                    help='max rows to enrich this run (default 20)')
    ap.add_argument('--sleep', type=float, default=1.0,
                    help='seconds between requests (default 1.0)')
    ap.add_argument('--timeout', type=int, default=15)
    ap.add_argument('--force', action='store_true',
                    help='re-enrich rows that already have enriched_at')
    ap.add_argument('--only-domain', default='',
                    help='restrict to a single domain substring')
    args = ap.parse_args()

    fieldnames, rows = load_targets(args.csv)
    session = requests.Session()
    session.headers.update(HEADERS)

    touched = errored = 0
    for row in rows:
        if touched >= args.n:
            break
        if args.only_domain and args.only_domain not in (row.get('domain') or ''):
            continue
        if not args.force and (row.get('enriched_at') or '').strip():
            continue
        status = (row.get('status') or '').strip()
        if status in ('contacted', 'replied', 'backlinked', 'opted_out',
                      'no_response'):
            continue

        updated = enrich_one(row, session, args.timeout)
        if updated:
            touched += 1
            print(f'  {row["domain"]:<35}  title="{(row.get("site_title") or "")[:60]}"')
            if 'enrich_err' in (row.get('notes') or ''):
                errored += 1
        time.sleep(args.sleep)

    if touched:
        save_targets(fieldnames, rows, args.csv)
        print(f'\nEnriched {touched} row(s), {errored} errored. CSV updated.')
    else:
        print('nothing to enrich (use --force to re-enrich).')
    return 0 if errored == 0 else 3


if __name__ == '__main__':
    sys.exit(main())

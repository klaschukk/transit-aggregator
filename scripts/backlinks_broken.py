"""
Broken-link building helper — crawl authority pages, HEAD every external
href, report 4xx/5xx links that could be pitched as replacement opportunities.

Usage:
    python scripts/backlinks_broken.py \\
        --urls https://example.com/serbia-guide \\
               https://another.com/balkan-bus-tips \\
        --out /tmp/broken.tsv

The script does not contact anybody automatically — it just produces a
TSV report you eyeball + paste into the broken-link pitch template
(docs/00_strategy/pitch-templates/broken-link.md).

TSV columns:
    source_url  broken_href  status_code  anchor_text  wayback_hint

Standalone: requests + stdlib regex only.

IMPORTANT: respect robots.txt of each source. This is a research tool
that issues one GET per source URL and one HEAD per external href; no
re-entrant crawling, no depth >1.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    print('requests module required: pip install requests', file=sys.stderr)
    sys.exit(2)

# Outbound-only: skip links back to the source domain and to obvious
# junk (javascript:, mailto:, tel:, fragment-only anchors)
_SKIP_SCHEMES = ('javascript:', 'mailto:', 'tel:', '#')


class _HrefExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[tuple[str, str]] = []  # (href, anchor_text)
        self._current_href: str | None = None
        self._text_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() != 'a':
            return
        for (k, v) in attrs:
            if k.lower() == 'href' and v:
                self._current_href = v
                self._text_buf = []
                return

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._text_buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == 'a' and self._current_href is not None:
            anchor = ' '.join(self._text_buf).strip()
            self.hrefs.append((self._current_href, anchor[:120]))
            self._current_href = None
            self._text_buf = []


def extract_external_hrefs(html: str, base_url: str) -> list[tuple[str, str]]:
    """Return (absolute_url, anchor_text) for external <a href> only."""
    p = _HrefExtractor()
    try:
        p.feed(html)
    except Exception:
        return []
    base_host = (urlparse(base_url).hostname or '').removeprefix('www.').lower()
    out: list[tuple[str, str]] = []
    for href, anchor in p.hrefs:
        href_stripped = href.strip()
        low = href_stripped.lower()
        if any(low.startswith(s) for s in _SKIP_SCHEMES):
            continue
        abs_url = urljoin(base_url, href_stripped)
        parsed = urlparse(abs_url)
        if parsed.scheme not in ('http', 'https'):
            continue
        host = (parsed.hostname or '').removeprefix('www.').lower()
        if host == base_host or not host:
            continue
        out.append((abs_url, anchor))
    return out


def head_status(url: str, timeout: int, session: requests.Session) -> int:
    """HEAD the URL, fall back to small GET if HEAD unsupported."""
    try:
        r = session.head(url, timeout=timeout, allow_redirects=True)
        if r.status_code == 405 or r.status_code == 403:
            # Some sites (cloudflare, some bloggers) block HEAD
            r = session.get(url, timeout=timeout, stream=True,
                            allow_redirects=True)
            r.close()
        return r.status_code
    except requests.RequestException:
        return 0


def wayback_hint(url: str) -> str:
    """Return the Wayback Machine URL so pitcher can check archived content."""
    return f'https://web.archive.org/web/*/{url}'


def scan(source_url: str, session: requests.Session, timeout: int,
         sleep_head: float) -> Iterable[dict]:
    try:
        r = session.get(source_url, timeout=timeout)
    except requests.RequestException as e:
        print(f'  ! could not fetch source {source_url}: {e}', file=sys.stderr)
        return
    if r.status_code != 200:
        print(f'  ! source {source_url} returned {r.status_code}',
              file=sys.stderr)
        return
    links = extract_external_hrefs(r.text, source_url)
    print(f'  [{source_url}] {len(links)} external links — probing…',
          file=sys.stderr)
    for href, anchor in links:
        status = head_status(href, timeout, session)
        # 4xx + 5xx + 0 (fetch error) all count as broken-for-outreach
        # purposes; 2xx/3xx are fine.
        if 200 <= status < 400:
            continue
        yield {
            'source_url': source_url,
            'broken_href': href,
            'status_code': str(status) if status else 'NET_ERR',
            'anchor_text': anchor,
            'wayback_hint': wayback_hint(href),
        }
        time.sleep(sleep_head)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--urls', nargs='+', required=True,
                    help='source URLs to scan (article pages, roundup posts)')
    ap.add_argument('--out', type=Path, default=None,
                    help='TSV output path (default: stdout)')
    ap.add_argument('--timeout', type=int, default=10)
    ap.add_argument('--sleep-head', type=float, default=0.5,
                    help='seconds between outbound HEAD requests')
    ap.add_argument('--sleep-source', type=float, default=2.0,
                    help='seconds between source GETs (robots.txt politeness)')
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (compatible; PrevozniBacklinkBot/1.0; '
            '+https://prevozni.com/bot)'
        ),
    })

    results: list[dict] = []
    for u in args.urls:
        for row in scan(u, session, args.timeout, args.sleep_head):
            results.append(row)
        time.sleep(args.sleep_source)

    header = 'source_url\tbroken_href\tstatus_code\tanchor_text\twayback_hint\n'

    def _tsv_row(r: dict) -> str:
        # Tabs in anchor text would wreck the format; strip them.
        return '\t'.join(
            (r.get(k, '') or '').replace('\t', ' ').replace('\n', ' ')
            for k in ('source_url', 'broken_href', 'status_code',
                      'anchor_text', 'wayback_hint')
        ) + '\n'

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(header + ''.join(_tsv_row(r) for r in results),
                            encoding='utf-8')
        print(f'Wrote {len(results)} broken-link rows to {args.out}',
              file=sys.stderr)
    else:
        sys.stdout.write(header)
        for r in results:
            sys.stdout.write(_tsv_row(r))

    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
Backlinks research — query Google via SerpAPI, filter out competitors,
emit candidate domains we don't already have in targets.csv.

Usage:
  export SERPAPI_KEY=...   # get one at https://serpapi.com (free tier: 100/mo)
  python scripts/backlinks_research.py \
      --keywords "bus Serbia" "putovanje autobusom Srbija" \
      --locale rs --limit 50

Output is printed to stdout as pipe-delimited rows matching the
targets.csv schema, so you can `>> docs/00_strategy/backlinks-targets.csv`
after eyeballing the list.

No Flask, no DuckDB — this is a pure HTTP + CSV tool that runs
standalone on a laptop or via cron.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover — script environment expected to have it
    print('requests module required: pip install requests', file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
TARGETS_CSV = ROOT / 'docs' / '00_strategy' / 'backlinks-targets.csv'

# Domains that should never be pitched — either it's us, or a known
# competitor (linking them back would be self-sabotage), or the link
# won't help SEO (aggregators we're scraping from).
EXCLUDE_DOMAINS = frozenset({
    'prevozni.com',
    'busticket4.me',
    'getbybus.com',
    'traveling.com',
    'bookaway.com',
    'flixbus.com',
    'flixbus.rs',
    'omio.com',
    'busbud.com',
    '12go.asia',
    # Our data sources — we already interact with them, don't pitch cold
    'data.gov.rs',
    'polazak.rs',
    'bgprevoz.rs',
    'gspns.co.rs',
    'srbijavoz.rs',
    'jgpnis.rs',
    'lasta.rs',
    'nis-ekspres.rs',
    # Generic throwaway aggregators
    'google.com',
    'youtube.com',
    'facebook.com',
    'instagram.com',
})


def domain_of(url: str) -> str:
    try:
        host = urlparse(url).hostname or ''
    except Exception:
        return ''
    return host.removeprefix('www.').lower()


def already_in_targets() -> set[str]:
    """Return the set of domains already listed in targets.csv."""
    if not TARGETS_CSV.exists():
        return set()
    seen: set[str] = set()
    with TARGETS_CSV.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = (row.get('domain') or '').strip().lower()
            if d:
                seen.add(d)
    return seen


def search_serpapi(key: str, query: str, locale: str, limit: int) -> list[dict]:
    """Single SerpAPI call; returns list of {url, title, snippet}."""
    params = {
        'engine': 'google',
        'q': query,
        'api_key': key,
        'num': min(limit, 100),
        'gl': locale,          # country, e.g. 'rs'
        'hl': 'en' if locale != 'rs' else 'sr',
    }
    resp = requests.get('https://serpapi.com/search', params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    results = []
    for item in payload.get('organic_results', [])[:limit]:
        link = item.get('link')
        if not link:
            continue
        results.append({
            'url': link,
            'title': item.get('title', ''),
            'snippet': item.get('snippet', ''),
        })
    return results


def categorise(url: str, title: str, snippet: str) -> str:
    """Cheap heuristic category based on URL/title — user will correct."""
    d = domain_of(url)
    text = f'{title} {snippet}'.lower()
    if d.endswith(('.gov.rs', '.sr.gov')):
        return 'serbian_gov'
    if d in {'serbia.travel', 'tob.rs', 'novisad.travel', 'nis.travel'}:
        return 'serbian_tourism'
    if any(t in d for t in ('reddit.com', 'r/serbia', 'r/belgrade')):
        return 'expat_serbia'
    if 'wikipedia.org' in d:
        return 'wikipedia_edit'
    if any(t in text for t in ('expat', 'forum', 'digital nomad')):
        return 'expat_serbia'
    if any(t in text for t in ('travel blog', 'itinerary', 'backpacking')):
        return 'travel_blog_global'
    if any(t in d for t in ('.rs', 'balkaninsight')):
        return 'balkan_blog'
    return 'uncategorised'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--keywords', nargs='+', required=True,
                    help='one or more Google queries (quote multi-word)')
    ap.add_argument('--locale', default='rs',
                    help='Google country code (default: rs for Serbia)')
    ap.add_argument('--limit', type=int, default=50,
                    help='top-N results per keyword (default: 50)')
    ap.add_argument('--sleep', type=float, default=1.0,
                    help='seconds between SerpAPI calls (default: 1.0)')
    ap.add_argument('--no-filter-existing', action='store_true',
                    help='include domains already in targets.csv (default: drop them)')
    args = ap.parse_args()

    api_key = os.environ.get('SERPAPI_KEY')
    if not api_key:
        print('ERR: set SERPAPI_KEY env var '
              '(free account: https://serpapi.com)', file=sys.stderr)
        return 2

    existing = set() if args.no_filter_existing else already_in_targets()
    seen_this_run: set[str] = set()

    for kw in args.keywords:
        print(f'# querying: {kw!r} ({args.locale})', file=sys.stderr)
        try:
            results = search_serpapi(api_key, kw, args.locale, args.limit)
        except Exception as e:
            print(f'  ! SerpAPI error for {kw!r}: {e}', file=sys.stderr)
            continue

        for r in results:
            d = domain_of(r['url'])
            if not d or d in EXCLUDE_DOMAINS or d in existing or d in seen_this_run:
                continue
            seen_this_run.add(d)
            cat = categorise(r['url'], r['title'], r['snippet'])
            # Default DA estimate: govs get 80, blogs 30, others 40
            da = 80 if cat == 'serbian_gov' else 30 if 'blog' in cat else 40
            # Pipe-delimited to match targets.csv; user eyeballs + adjusts
            lang = 'sr' if d.endswith('.rs') else 'en'
            notes = (r['title'][:80] + '…') if len(r['title']) > 80 else r['title']
            print(
                f'{d}|{r["url"]}|{cat}|{da}|{lang}|form|found via '
                f'serpapi kw={kw!r}: {notes}'
            )

        time.sleep(args.sleep)

    print(f'# {len(seen_this_run)} new candidates across '
          f'{len(args.keywords)} keywords', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())

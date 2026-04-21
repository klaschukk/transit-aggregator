"""
Crawl every URL in backlinks-targets.csv and flip status→"backlinked" for
any page that already links back to prevozni.com.

Weekly cron:
    0 4 * * 1 /path/to/venv/bin/python /path/to/scripts/backlinks_check.py

The script is deliberately forgiving — it HEADs first (cheap), only GETs
on 2xx/3xx, and treats any 4xx/5xx as "still todo". Rate-limit is 1 req/s
so we look like a normal visitor even on tiny blogs.

Idempotent: re-running is safe. The only state mutation is the `status`
column; everything else stays untouched so manual edits (new rows,
contact_method tweaks) survive.
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print('requests module required: pip install requests', file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
TARGETS_CSV = ROOT / 'docs' / '00_strategy' / 'backlinks-targets.csv'

# What counts as "us" in the target page's HTML. Any one of these on the
# page flips status→backlinked. List strict forms first so we don't match
# plain "prevozni" in Serbian prose about public transport.
LINK_PATTERNS = (
    'href="https://prevozni.com',
    "href='https://prevozni.com",
    'href="https://www.prevozni.com',
    'href="http://prevozni.com',
    'prevozni.com/rute',
    'prevozni.com/voznja',
    'prevozni.com/gradski',
    'prevozni.com/pretraga',
)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (compatible; PrevozniBacklinkBot/1.0; '
        '+https://prevozni.com/bot)'
    ),
    'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1',
    'Accept-Language': 'en,sr;q=0.8,ru;q=0.6',
}


def rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        return fieldnames, list(reader)


def write_rows(path: Path, fieldnames: list[str], data: list[dict]) -> None:
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def check_one(url: str, session: requests.Session, timeout: int) -> bool | None:
    """Return True if page links to us, False if not, None on fetch error."""
    try:
        # HEAD first — cheap probe; follow redirects up to 3 hops
        head = session.head(url, timeout=timeout, allow_redirects=True)
        if head.status_code >= 400:
            return None
        # Some blogs block HEAD; treat 405 as "try GET"
        if head.status_code != 200 and head.status_code != 405:
            return None
    except Exception:
        return None

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    text = resp.text.lower()
    return any(pattern.lower() in text for pattern in LINK_PATTERNS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv', type=Path, default=TARGETS_CSV,
                    help=f'CSV path (default: {TARGETS_CSV})')
    ap.add_argument('--sleep', type=float, default=1.0,
                    help='seconds between requests (default: 1.0)')
    ap.add_argument('--timeout', type=int, default=15,
                    help='request timeout seconds (default: 15)')
    ap.add_argument('--dry-run', action='store_true',
                    help='print diffs without writing CSV')
    ap.add_argument('--only-status', nargs='+',
                    default=['todo', 'contacted', 'responded'],
                    help='only check rows with these statuses')
    args = ap.parse_args()

    if not args.csv.exists():
        print(f'ERR: {args.csv} not found — run research step first',
              file=sys.stderr)
        return 2

    fields, data = rows(args.csv)
    if 'status' not in fields or 'url' not in fields:
        print('ERR: CSV must have "url" and "status" columns',
              file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers.update(HEADERS)

    checked = linked_new = errors = skipped = 0

    for row in data:
        if row.get('status') not in args.only_status:
            skipped += 1
            continue
        url = (row.get('url') or '').strip()
        if not url:
            skipped += 1
            continue
        checked += 1
        result = check_one(url, session, args.timeout)
        if result is True:
            if row['status'] != 'backlinked':
                linked_new += 1
                print(f'  NEW BACKLINK: {row["domain"]} ({url})')
                row['status'] = 'backlinked'
        elif result is None:
            errors += 1
        time.sleep(args.sleep)

    print('')
    print(f'Checked: {checked}, new backlinks: {linked_new}, '
          f'errors: {errors}, skipped: {skipped}')

    if args.dry_run:
        print('(dry-run — not writing CSV)')
        return 0

    if linked_new:
        write_rows(args.csv, fields, data)
        print(f'Wrote {args.csv}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

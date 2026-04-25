"""Crawl every URL in backlinks-targets.csv and flip status → 'backlinked'
on any page that already links back to prevozni.com.

Weekly cron:

    0 4 * * 1 /path/to/venv/bin/python /path/to/scripts/backlinks_check.py

HEADs first (cheap probe), GETs only on 2xx/3xx, treats 4xx/5xx as
"still todo". Rate-limit 1 req/s so we look like a normal visitor on
tiny blogs. Idempotent: the only mutations are the state columns
(`status`, `backlink_url`, `backlink_detected_at`, `last_event`,
`last_event_at`). Manual edits stay intact.

Extensions over the original passive crawler:

  * Detects and stores the exact URL where our link was found in
    `backlink_url` (first match on the page).
  * Telegram 🎉 notification on each newly-discovered backlink via
    TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env vars. Script stays
    app-context-free — POSTs directly to api.telegram.org.
  * Appends a line to docs/00_strategy/backlinks-tracker.md so the
    human-readable log stays in sync with CSV state.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import requests
except ImportError:
    print('requests required: pip install requests', file=sys.stderr)
    sys.exit(2)

from app.outreach import load_targets, save_targets  # noqa: E402

TRACKER_MD = _REPO_ROOT / 'docs' / '00_strategy' / 'backlinks-tracker.md'

# What counts as "us" in the target page's HTML. List strict URL-anchored
# forms first so we don't match plain "prevozni" in Serbian prose about
# transit. The regex pulls the matching href out so we can store it.
LINK_PATTERNS = (
    r'https?://(?:www\.)?prevozni\.com(?:/[^\s"\'<>]*)?',
)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (compatible; PrevozniBacklinkBot/1.0; '
        '+https://prevozni.com/bot)'
    ),
    'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1',
    'Accept-Language': 'en,sr;q=0.8,ru;q=0.6',
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def check_one(
    url: str,
    session: requests.Session,
    timeout: int,
) -> tuple[bool | None, str]:
    """Return (linked, backlink_url).
      linked is True/False/None (None on fetch error).
      backlink_url is the first prevozni.com URL found on the page, or ''.
    """
    try:
        head = session.head(url, timeout=timeout, allow_redirects=True)
        if head.status_code >= 400 and head.status_code != 405:
            return None, ''
    except Exception:
        return None, ''

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
    except Exception:
        return None, ''

    if resp.status_code != 200 or not resp.text:
        return None, ''

    for pat in LINK_PATTERNS:
        m = re.search(pat, resp.text, re.IGNORECASE)
        if m:
            return True, m.group(0)
    return False, ''


def notify_telegram(message: str) -> bool:
    """Direct POST to api.telegram.org — doesn't need Flask context.
    Returns True on 2xx, False on any failure. Deliberately silent on
    errors; the cron log captures them."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return False
    try:
        resp = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message[:3900],
                  'disable_web_page_preview': True},
            timeout=5,
        )
        return resp.ok
    except Exception:
        return False


def _append_tracker(domain: str, url: str, backlink_url: str) -> None:
    """One-line log entry in tracker.md. File is created if missing."""
    line = (
        f'- {_now_iso()}  🎉 **{domain}** — '
        f'[source]({url}) → [backlink]({backlink_url})\n'
    )
    try:
        TRACKER_MD.parent.mkdir(parents=True, exist_ok=True)
        if not TRACKER_MD.exists():
            TRACKER_MD.write_text(
                '# Backlinks Tracker\n\n'
                '> Auto-appended by scripts/backlinks_check.py on each new '
                'backlink.\n\n',
                encoding='utf-8',
            )
        with TRACKER_MD.open('a', encoding='utf-8') as f:
            f.write(line)
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', type=Path, default=None,
                    help='CSV path (default: docs/00_strategy/backlinks-targets.csv)')
    ap.add_argument('--sleep', type=float, default=1.0,
                    help='seconds between requests (default: 1.0)')
    ap.add_argument('--timeout', type=int, default=15)
    ap.add_argument('--dry-run', action='store_true',
                    help='print diffs without writing CSV or sending notifications')
    ap.add_argument('--only-status', nargs='+',
                    default=['todo', 'enriched', 'contacted', 'replied', 'no_response'],
                    help='only check rows with these statuses')
    args = ap.parse_args()

    fieldnames, rows = load_targets(args.csv)
    if not rows:
        print('no rows in CSV', file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers.update(HEADERS)

    checked = linked_new = errors = skipped = 0

    for row in rows:
        if row.get('status') not in args.only_status:
            skipped += 1
            continue
        url = (row.get('url') or '').strip()
        if not url:
            skipped += 1
            continue
        checked += 1
        result, found_url = check_one(url, session, args.timeout)
        if result is True:
            if row['status'] != 'backlinked':
                linked_new += 1
                row['status'] = 'backlinked'
                row['backlink_url'] = found_url
                row['backlink_detected_at'] = _now_iso()
                row['last_event'] = 'backlinked'
                row['last_event_at'] = row['backlink_detected_at']
                row['last_status_change'] = row['backlink_detected_at']
                print(f'  🎉 NEW BACKLINK: {row["domain"]} → {found_url}')
                if not args.dry_run:
                    notify_telegram(
                        f'🎉 New backlink\n\n'
                        f'{row["domain"]} ({row.get("category")})\n'
                        f'Source: {url}\n'
                        f'Link:   {found_url}\n'
                        f'DA:     {row.get("DA_estimate")}'
                    )
                    _append_tracker(row['domain'], url, found_url)
        elif result is None:
            errors += 1
        time.sleep(args.sleep)

    print(f'\nChecked: {checked}, new backlinks: {linked_new}, '
          f'errors: {errors}, skipped: {skipped}')

    if args.dry_run:
        print('(dry-run — not writing CSV)')
        return 0

    if linked_new:
        save_targets(fieldnames, rows, args.csv)
        print('CSV updated.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

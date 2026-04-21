"""
Weekly digest — summarise backlinks-targets.csv into a markdown report
(or Telegram message) so solo-dev knows what to do this week.

Usage:
    python scripts/backlinks_digest.py                    # prints markdown
    python scripts/backlinks_digest.py --out FILE.md      # writes to file
    python scripts/backlinks_digest.py --telegram         # posts via env vars

Digest lines:
    * Total backlinks landed (status=backlinked)
    * New this week (status flipped in last 7 days — uses CSV mtime + the
      `last_status_change` col if present; falls back to CSV mtime)
    * Responses pending follow-up >7 days (status=contacted)
    * Targets not yet contacted this month (status=todo, contacted_at
      older than 30 days or empty)

Standalone — no Flask or DuckDB. Reads docs/00_strategy/backlinks-targets.csv
only.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TARGETS_CSV = ROOT / 'docs' / '00_strategy' / 'backlinks-targets.csv'
DOCS_DIR = ROOT / 'docs' / '00_strategy'

STATUS_ORDER = ('todo', 'contacted', 'responded', 'backlinked', 'rejected')


def parse_date(s: str | None) -> datetime | None:
    if not s:
        return None
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def read_targets(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding='utf-8') as f:
        return list(csv.DictReader(f))


def build_digest(rows: list[dict], now: datetime) -> str:
    counts = Counter(r.get('status', '').strip() or 'todo' for r in rows)
    total = len(rows)
    landed = counts.get('backlinked', 0)

    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    new_this_week: list[dict] = []
    stale_contacted: list[dict] = []
    not_contacted: list[dict] = []

    for r in rows:
        status = (r.get('status') or '').strip()
        contacted_at = parse_date(r.get('contacted_at') or '')
        changed_at = parse_date(r.get('last_status_change') or '')
        if status == 'backlinked' and changed_at and changed_at >= week_ago:
            new_this_week.append(r)
        if status == 'contacted' and contacted_at and contacted_at < week_ago:
            stale_contacted.append(r)
        if status == 'todo' and (not contacted_at or contacted_at < month_ago):
            not_contacted.append(r)

    # DA-weighted score (sum of DA for all backlinked rows)
    da_sum = sum(
        int(r.get('DA_estimate', 0) or 0)
        for r in rows if (r.get('status') or '').strip() == 'backlinked'
    )

    lines: list[str] = []
    lines.append(f'# Backlinks digest — {now.strftime("%Y-%m-%d")}')
    lines.append('')
    lines.append('## Scoreboard')
    lines.append('')
    lines.append(f'- Total targets: **{total}**')
    lines.append(f'- Backlinks landed: **{landed}**  '
                 f'(DA-weighted score: {da_sum})')
    for s in STATUS_ORDER:
        if s == 'backlinked':
            continue
        n = counts.get(s, 0)
        if n:
            lines.append(f'- {s.title()}: {n}')
    lines.append('')

    lines.append('## New this week')
    lines.append('')
    if new_this_week:
        for r in sorted(new_this_week,
                        key=lambda r: -int(r.get('DA_estimate', 0) or 0)):
            lines.append(
                f'- **{r.get("domain", "?")}** '
                f'(DA≈{r.get("DA_estimate", "?")}, '
                f'{r.get("category", "?")}) — '
                f'`{r.get("url", "")}`'
            )
    else:
        lines.append('*No new backlinks detected in the last 7 days.*')
    lines.append('')

    lines.append('## Needs follow-up (contacted >7 days, no reply)')
    lines.append('')
    if stale_contacted:
        for r in sorted(stale_contacted,
                        key=lambda r: r.get('contacted_at', '')):
            lines.append(
                f'- [ ] **{r.get("domain", "?")}** — contacted '
                f'{r.get("contacted_at", "?")} via '
                f'{r.get("contact_method", "?")}'
            )
    else:
        lines.append('*Inbox zero — no stale contacted threads.*')
    lines.append('')

    lines.append('## Queue (todo, not contacted in the last 30 days)')
    lines.append('')
    # Top 10 by DA — solo dev has limited hours; prioritise high-authority
    top_queue = sorted(
        not_contacted, key=lambda r: -int(r.get('DA_estimate', 0) or 0),
    )[:10]
    if top_queue:
        for r in top_queue:
            lines.append(
                f'- **{r.get("domain", "?")}** '
                f'(DA≈{r.get("DA_estimate", "?")}, '
                f'{r.get("category", "?")}) — '
                f'{r.get("notes", "")[:80]}'
            )
        remainder = len(not_contacted) - len(top_queue)
        if remainder > 0:
            lines.append(f'- *…and {remainder} more lower-DA targets*')
    else:
        lines.append('*Nothing pending — time to research more targets.*')
    lines.append('')

    lines.append('## This week\'s goal')
    lines.append('')
    # Sanity anchor — if landing rate < 1/week, pitch more. If > 5/week,
    # slow down and personalise more.
    lines.append(
        '- Target: **5 personalised pitches** (expat-forum + travel-blog + '
        'broken-link)'
    )
    lines.append(
        '- If landed ≥ 3 this week → stop pitching, write 1 content piece '
        'instead'
    )

    return '\n'.join(lines) + '\n'


def send_telegram(text: str) -> None:
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print('WARN: --telegram requested but TELEGRAM_BOT_TOKEN / '
              'TELEGRAM_CHAT_ID not set — skipping', file=sys.stderr)
        return
    try:
        import requests
    except ImportError:
        print('requests required for --telegram', file=sys.stderr)
        return
    # Telegram limit is 4096 chars — truncate safely
    if len(text) > 3900:
        text = text[:3900] + '\n\n…truncated'
    r = requests.post(
        f'https://api.telegram.org/bot{token}/sendMessage',
        json={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'},
        timeout=15,
    )
    if r.status_code >= 400:
        print(f'telegram error: {r.status_code} {r.text[:200]}', file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--csv', type=Path, default=TARGETS_CSV)
    ap.add_argument('--out', type=Path, default=None,
                    help='write digest to file; default: print to stdout')
    ap.add_argument('--telegram', action='store_true',
                    help='also post via TELEGRAM_BOT_TOKEN / _CHAT_ID')
    args = ap.parse_args()

    rows = read_targets(args.csv)
    now = datetime.now(timezone.utc)
    digest = build_digest(rows, now)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(digest, encoding='utf-8')
        print(f'Wrote {args.out}', file=sys.stderr)
    else:
        sys.stdout.write(digest)

    if args.telegram:
        send_telegram(digest)

    return 0


if __name__ == '__main__':
    sys.exit(main())

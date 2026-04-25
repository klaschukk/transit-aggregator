#!/usr/bin/env python3
"""Follow-up cadence driver.

Rules (baked in, not configurable — the whole point is discipline):

    contacted (≥7d ago, 0 follow-ups, no reply)
        → send follow_up_<lang>.tpl, follow_up_count=1
    contacted + follow_up_count=1 (≥14d since contacted_at, no reply)
        → mark status='no_response', don't send again
    any row where last_event='replied' OR status='replied'
        → never follow up
    any row where opted_out='1'
        → never contact again

Run daily via cron; idempotent. Respects the same 20/day cap as
backlinks_send.py (they share the send log).

    0 9 * * * /path/to/venv/bin/python /path/to/scripts/backlinks_follow_up.py
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.outreach import (  # noqa: E402
    MAX_SENDS_PER_DAY,
    daily_send_cap_ok,
    load_targets,
    render_template,
    save_targets,
    send_outreach,
)


def _parse_iso(s: str) -> datetime | None:
    s = (s or '').strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        return None


def _eligible_for_follow_up(row: dict, now: datetime) -> bool:
    if (row.get('opted_out') or '').strip() in ('1', 'true', 'True'):
        return False
    if (row.get('status') or '').strip() != 'contacted':
        return False
    if (row.get('last_event') or '').strip() in ('replied', 'bounced', 'complained'):
        return False
    try:
        followups = int((row.get('follow_up_count') or '0').strip() or '0')
    except ValueError:
        followups = 0
    if followups >= 1:
        return False
    contacted = _parse_iso(row.get('contacted_at') or '')
    if not contacted:
        return False
    return (now - contacted) >= timedelta(days=7)


def _eligible_for_giveup(row: dict, now: datetime) -> bool:
    """After 14d with 1 follow-up sent and still no reply → no_response."""
    if (row.get('status') or '').strip() != 'contacted':
        return False
    try:
        followups = int((row.get('follow_up_count') or '0').strip() or '0')
    except ValueError:
        followups = 0
    if followups < 1:
        return False
    contacted = _parse_iso(row.get('contacted_at') or '')
    if not contacted:
        return False
    return (now - contacted) >= timedelta(days=14)


def _placeholders(row: dict) -> dict[str, str]:
    raw_email = (row.get('contact_email') or '').strip()
    name_hint = raw_email.split('@', 1)[0].split('.')[0].capitalize() \
        if raw_email else 'there'
    contacted = _parse_iso(row.get('contacted_at') or '')
    return {
        'name':             name_hint,
        'site_title':       (row.get('site_title') or row.get('domain') or '').strip(),
        'their_topic':      (row.get('their_topic') or '').strip(),
        'our_hook':         (row.get('our_hook') or 'https://prevozni.com/rute/').strip(),
        'previous_subject': '',
        'previous_date':    contacted.strftime('%Y-%m-%d') if contacted else '',
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', type=Path, default=None)
    ap.add_argument('--dry-run', action='store_true',
                    help='render + log but never actually send')
    ap.add_argument('--from', dest='from_addr',
                    default=os.environ.get('MAIL_FROM', 'kirill@prevozni.com'))
    ap.add_argument('--base-url', default='https://prevozni.com')
    ap.add_argument('--secret',
                    default=os.environ.get('SECRET_KEY', 'dev-secret'))
    ap.add_argument('--mailgun-domain',
                    default=os.environ.get('MAILGUN_DOMAIN', ''))
    args = ap.parse_args()

    mailgun_api_key = os.environ.get('MAILGUN_API_KEY', '')
    fieldnames, rows = load_targets(args.csv)
    now = datetime.now(timezone.utc)

    fu_candidates = [r for r in rows if _eligible_for_follow_up(r, now)]
    giveup_candidates = [r for r in rows if _eligible_for_giveup(r, now)]

    print(f'Follow-up candidates: {len(fu_candidates)}  Give-up: {len(giveup_candidates)}')

    # Give-ups first (purely CSV mutation, no sends).
    for row in giveup_candidates:
        row['status'] = 'no_response'
        row['last_status_change'] = now.isoformat(timespec='seconds')
        print(f'  ⏲  GIVE UP   {row["domain"]} (14d elapsed, no reply)')

    sent = errors = 0
    for row in fu_candidates:
        ok_cap, sent_24h = daily_send_cap_ok()
        if not ok_cap and not args.dry_run:
            print(f'daily cap reached — stopping ({sent_24h}/{MAX_SENDS_PER_DAY})')
            break
        lang = (row.get('language') or 'en').strip().lower()
        if lang not in ('en', 'sr', 'ru'):
            lang = 'en'
        tpl = f'follow_up_{lang}'
        try:
            subject, body = render_template(tpl, _placeholders(row))
        except FileNotFoundError:
            subject, body = render_template('follow_up_en', _placeholders(row))

        ok, detail = send_outreach(
            to=row['contact_email'], subject=subject, text=body,
            from_addr=args.from_addr,
            domain_target=row.get('domain', ''),
            url_target=row.get('url', ''),
            base_url=args.base_url, secret=args.secret,
            mailgun_api_key=mailgun_api_key,
            mailgun_domain=args.mailgun_domain,
            notes=row.get('notes', ''),
            dry_run=args.dry_run,
        )
        if ok:
            try:
                fu = int((row.get('follow_up_count') or '0').strip() or '0')
            except ValueError:
                fu = 0
            row['follow_up_count'] = str(fu + 1)
            row['last_status_change'] = now.isoformat(timespec='seconds')
            row['last_event'] = 'follow_up_sent' if not args.dry_run else 'dry_run'
            row['last_event_at'] = row['last_status_change']
            sent += 1
            print(f'  ✓ FOLLOW   {row["domain"]}  ({detail})')
        else:
            errors += 1
            print(f'  ✗ ERROR    {row["domain"]}  ({detail})')

    if fu_candidates or giveup_candidates:
        save_targets(fieldnames, rows, args.csv)
    print(f'\nDone: follow-ups sent={sent} errors={errors} '
          f'gave up={len(giveup_candidates)}')
    return 0 if errors == 0 else 3


if __name__ == '__main__':
    sys.exit(main())

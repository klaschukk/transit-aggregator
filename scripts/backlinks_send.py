#!/usr/bin/env python3
"""Cold-outreach sender for docs/00_strategy/backlinks-targets.csv.

Three modes, all via the same pipeline (CSV → template → guards → send):

    # Preview only — no emails, writes dry_run events to send log.
    scripts/backlinks_send.py --dry-run --n 5

    # Interactive — per-email [S]end [K]skip [E]dit [Q]uit.
    scripts/backlinks_send.py --n 5

    # Batch — skips interactive prompt. Use only after the manual flow
    # has produced 20+ quality sends with no regressions.
    scripts/backlinks_send.py --auto --n 20

Hard rules:

 - Never sends when FLASK_ENV=testing or PYTEST_CURRENT_TEST is set
   (see app/outreach/sender.py `_testing_env`).
 - Daily cap of 20 actual sends per rolling 24h (MAX_SENDS_PER_DAY).
 - 30–300s randomised sleep between sends to avoid burst fingerprints.
 - Rows missing `contact_email` are skipped with an explanatory line.
 - Rows in GDPR-strict TLDs (.de/.fr/.at/.ch/.nl) require `gdpr_ok`
   in `notes` before they'll go out.
 - Rows with `opted_out=1` are skipped forever.
 - Every send attempt (including skips, dry-runs, rate-limit blocks)
   appends a JSON line to logs/backlinks_sent.log.

CSV mutations on success:

    status               → 'contacted' (if first send) or unchanged
    contacted_at         → ISO-8601 UTC timestamp (first send only)
    last_status_change   → ISO-8601 UTC timestamp (always)
    last_event           → 'sent' (webhook may later overwrite)
    last_event_at        → ISO-8601 UTC timestamp
"""
from __future__ import annotations

import argparse
import os
import random
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow running either as a module (`python -m scripts.backlinks_send`)
# or as a plain script from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.outreach import (  # noqa: E402
    MAX_SENDS_PER_DAY,
    SEND_LOG,
    daily_send_cap_ok,
    load_targets,
    render_template,
    save_targets,
    send_outreach,
    template_for_category,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _pick(rows: list[dict], n: int, min_da: int) -> list[dict]:
    """Filter `status in {'', 'todo', 'enriched'}` AND `opted_out != 1`,
    sort by DA descending, take top `n`."""
    eligible: list[dict] = []
    for r in rows:
        if (r.get('opted_out') or '').strip() in ('1', 'true', 'True'):
            continue
        status = (r.get('status') or '').strip()
        if status not in ('', 'todo', 'enriched'):
            continue
        if not (r.get('contact_email') or '').strip():
            continue
        try:
            da = int((r.get('DA_estimate') or '0').strip() or '0')
        except ValueError:
            da = 0
        if da < min_da:
            continue
        r['_da_numeric'] = da
        eligible.append(r)
    eligible.sort(key=lambda r: r['_da_numeric'], reverse=True)
    return eligible[:n]


def _placeholders(row: dict, default_name: str = 'there') -> dict[str, str]:
    """Resolve {name}, {site_title}, {their_topic}, {our_hook} with
    fallbacks. Enricher populates the real values; this keeps the
    template sensible even if enrichment hasn't run."""
    # Best-effort first name from contact_email local part (before @)
    raw_email = (row.get('contact_email') or '').strip()
    name_hint = raw_email.split('@', 1)[0].split('.')[0] if raw_email else ''
    name_hint = name_hint.capitalize() if name_hint else default_name
    hook = (row.get('our_hook') or '').strip()
    if not hook:
        hook = 'https://prevozni.com/rute/'
    return {
        'name':             (row.get('site_title') and name_hint) or name_hint,
        'site_title':       (row.get('site_title') or row.get('domain') or '').strip(),
        'their_topic':      (row.get('their_topic') or row.get('category') or '').strip(),
        'our_hook':         hook,
        'category_hint':    (row.get('category') or '').strip(),
        'domain':           (row.get('domain') or '').strip(),
        'previous_subject': (row.get('notes') and '' or '').strip() or '',
        'previous_date':    (row.get('contacted_at') or '').strip(),
    }


def _preview(row: dict, subject: str, body: str) -> str:
    header = textwrap.dedent(f"""
        ──────────────────────────────────────────────────────────────
          Target:   {row.get('domain')} ({row.get('url')})
          Category: {row.get('category')}  DA: {row.get('DA_estimate')}  Lang: {row.get('language')}
          To:       {row.get('contact_email')}
          Template: {row.get('template') or template_for_category(row.get('category', ''), row.get('language', 'en'))}
        ──────────────────────────────────────────────────────────────
        Subject: {subject}

    """).strip('\n')
    return header + '\n' + body


def _prompt(msg: str) -> str:
    try:
        return input(msg).strip().lower()
    except EOFError:
        return 'q'


def _sleep_jitter(low: int, high: int) -> None:
    if low <= 0 and high <= 0:
        return
    time.sleep(random.uniform(low, high))


def _render_or_fail(row: dict) -> tuple[str, str, str] | None:
    template_name = (row.get('template') or '').strip()
    if not template_name:
        template_name = template_for_category(
            row.get('category', ''), row.get('language', 'en'),
        )
    try:
        subject, body = render_template(template_name, _placeholders(row))
    except (FileNotFoundError, ValueError) as exc:
        print(f'  SKIP {row["domain"]}: template error — {exc}')
        return None
    return subject, body, template_name


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--csv', type=Path, default=None,
                    help='targets CSV path (default: docs/00_strategy/backlinks-targets.csv)')
    ap.add_argument('--n', type=int, default=5,
                    help='max emails to process this run (default 5)')
    ap.add_argument('--min-da', type=int, default=0,
                    help='filter out rows with DA_estimate below this (default 0)')
    ap.add_argument('--dry-run', action='store_true',
                    help='render + log but never actually send')
    ap.add_argument('--auto', action='store_true',
                    help='skip per-email approval prompt')
    ap.add_argument('--sleep-low', type=int, default=30,
                    help='min seconds between sends (default 30)')
    ap.add_argument('--sleep-high', type=int, default=300,
                    help='max seconds between sends (default 300)')
    ap.add_argument('--from', dest='from_addr',
                    default=os.environ.get('MAIL_FROM', 'kirill@prevozni.com'),
                    help='From: header; default env MAIL_FROM')
    ap.add_argument('--base-url', default='https://prevozni.com',
                    help='base URL for unsubscribe links')
    ap.add_argument('--secret',
                    default=os.environ.get('SECRET_KEY', 'dev-secret'),
                    help='HMAC secret for unsubscribe tokens')
    ap.add_argument('--mailgun-domain',
                    default=os.environ.get('MAILGUN_DOMAIN', ''),
                    help='Mailgun domain; env MAILGUN_DOMAIN')
    args = ap.parse_args()

    mailgun_api_key = os.environ.get('MAILGUN_API_KEY', '')

    fieldnames, rows = load_targets(args.csv)
    if not rows:
        print('no rows in CSV — nothing to send', file=sys.stderr)
        return 1

    ok_cap, sent_24h = daily_send_cap_ok()
    print(f'Daily cap: {sent_24h}/{MAX_SENDS_PER_DAY} in last 24h.')
    if not ok_cap and not args.dry_run:
        print(f'Daily cap hit — refusing to send. Try again in 24h or use --dry-run.',
              file=sys.stderr)
        return 1

    picks = _pick(rows, args.n, args.min_da)
    if not picks:
        print('no eligible rows (no contact_email, wrong status, or DA<min)',
              file=sys.stderr)
        return 0

    print(f'Selected {len(picks)} target(s) (by DA desc):')
    for r in picks:
        print(f'  DA {r["DA_estimate"]:>3}  {r["domain"]:<35}  {r["category"]}')
    print()

    sent = skipped = errors = 0
    last_subject = ''
    for i, row in enumerate(picks, 1):
        # Refresh cap on every iteration — another process may have sent
        # meanwhile, or this run may have pushed us over.
        ok_cap, sent_24h = daily_send_cap_ok()
        if not ok_cap and not args.dry_run:
            print(f'[{i}/{len(picks)}] daily cap reached — stopping '
                  f'({sent_24h}/{MAX_SENDS_PER_DAY})')
            break

        rendered = _render_or_fail(row)
        if not rendered:
            skipped += 1
            continue
        subject, body, template_name = rendered

        # Subject-line variance check — refuse to send 2 in a row with an
        # identical subject (spam-filter fingerprint). Variance comes
        # automatically when `{site_title}` is populated by the enricher.
        if subject == last_subject:
            print(f'[{i}/{len(picks)}] SKIP {row["domain"]}: '
                  f'subject identical to previous send — run '
                  f'backlinks_enrich.py to populate site_title first.')
            skipped += 1
            continue

        print(_preview(row, subject, body))
        decision = 's' if args.auto else _prompt(
            '\n  [S]end  [K]skip  [E]dit (opens $EDITOR)  [Q]uit all: '
        )
        if decision == 'q':
            print('aborted by user; no further sends.')
            break
        if decision == 'k':
            skipped += 1
            continue
        if decision == 'e':
            body = _edit_in_editor(body)

        ok, detail = send_outreach(
            to=row['contact_email'],
            subject=subject,
            text=body,
            from_addr=args.from_addr,
            domain_target=row.get('domain', ''),
            url_target=row.get('url', ''),
            base_url=args.base_url,
            secret=args.secret,
            mailgun_api_key=mailgun_api_key,
            mailgun_domain=args.mailgun_domain,
            notes=row.get('notes', ''),
            dry_run=args.dry_run,
        )
        if ok:
            now = _now_iso()
            if not (row.get('contacted_at') or '').strip():
                row['contacted_at'] = now
                row['status'] = 'contacted'
            row['last_status_change'] = now
            row['last_event'] = 'sent' if not args.dry_run else 'dry_run'
            row['last_event_at'] = now
            row['template'] = template_name
            sent += 1
            last_subject = subject
            print(f'  ✓ {detail}')
        else:
            errors += 1
            print(f'  ✗ {detail}')

        # Jittered pause before the next one — last iteration skips sleep.
        if i < len(picks) and not args.dry_run:
            _sleep_jitter(args.sleep_low, args.sleep_high)

    # Persist CSV state. Dry-runs still update `last_event='dry_run'` so
    # the reviewer can see what WOULD have been sent; use --dry-run
    # deliberately, knowing it writes bookkeeping columns.
    if sent or errors:
        save_targets(fieldnames, rows, args.csv)
    print(f'\nDone: sent={sent} skipped={skipped} errors={errors}')
    print(f'Log:  {SEND_LOG}')
    return 0 if errors == 0 else 3


def _edit_in_editor(initial: str) -> str:
    """Open $EDITOR on a tempfile; return the edited text. Falls back to
    the original on any failure — better to send the reviewed-but-
    unedited version than to crash mid-campaign."""
    import subprocess
    import tempfile
    editor = os.environ.get('EDITOR') or 'nano'
    with tempfile.NamedTemporaryFile(
        mode='w+', suffix='.txt', delete=False, encoding='utf-8',
    ) as f:
        f.write(initial)
        tmp = f.name
    try:
        subprocess.call([editor, tmp])
        with open(tmp, encoding='utf-8') as f:
            return f.read()
    except Exception:
        return initial
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


if __name__ == '__main__':
    sys.exit(main())

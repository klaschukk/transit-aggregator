#!/usr/bin/env python3
"""scripts/newsletter_send.py — fire one campaign end-to-end.

Wraps app.newsletter.dispatch.send_campaign with an app context, the
real send_mail function, and the production-safe rate-limit defaults.

Usage:
    python scripts/newsletter_send.py --slug welcome-confirmed --dry-run
    python scripts/newsletter_send.py --slug welcome-confirmed --apply
    python scripts/newsletter_send.py --campaign-id 1 --apply --delay 1.0

Conventions:
    - dry-run is the *default*; --apply is required to send. Avoids the
      classic mistake of running the script in a console and watching
      a thousand emails fly out by accident.
    - --resume re-runs without changing campaign status; the unique
      constraint on (campaign_id, subscriber_id) skips already-sent rows.
    - Exits non-zero on dispatch error so cron jobs fail loud.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Make `app` importable when run from project root or from cron.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app, mailer  # noqa: E402
from app.newsletter import campaigns as cmp_mod  # noqa: E402
from app.newsletter import dispatch as disp_mod  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s — %(message)s',
)
log = logging.getLogger('newsletter_send')


def _resolve_id(args) -> int:
    if args.campaign_id:
        return int(args.campaign_id)
    if args.slug:
        c = cmp_mod.get_campaign_by_slug(args.slug)
        if not c:
            raise SystemExit(f'no campaign with slug {args.slug!r}')
        return int(c['id'])
    raise SystemExit('--slug or --campaign-id required')


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--slug', help='campaign slug (preferred)')
    p.add_argument('--campaign-id', type=int, help='campaign id (numeric)')
    p.add_argument('--apply', action='store_true',
                   help='actually send (else dry-run)')
    p.add_argument('--delay', type=float, default=0.6,
                   help='seconds between sends (default 0.6 = ~100/min)')
    p.add_argument('--max', type=int, default=10_000,
                   help='hard cap on this run (default 10k)')
    p.add_argument('--test-to', help='send single test to this email instead')
    args = p.parse_args()

    app = create_app()
    with app.app_context():
        cid = _resolve_id(args)
        base = app.config.get('BASE_URL') or 'https://prevozni.com'

        log.info('dispatching campaign id=%s apply=%s delay=%.2fs max=%d',
                 cid, args.apply, args.delay, args.max)

        summary = disp_mod.send_campaign(
            cid,
            send_fn=mailer.send_mail,
            unsub_base_url=base,
            test_email=args.test_to,
            min_delay_s=args.delay if args.apply else 0.0,
            max_per_run=args.max,
            dry_run=not args.apply,
        )

        # Pretty-print the summary so cron logs are scannable.
        if summary.get('rows_dry_run'):
            preview = summary['rows_dry_run'][:10]
            summary['rows_dry_run'] = preview + (
                [{'note': f'+{len(summary["rows_dry_run"]) - len(preview)} more'}]
                if len(summary['rows_dry_run']) > len(preview) else []
            )
        log.info('summary:\n%s', json.dumps(summary, indent=2, default=str))

        # Cron-friendly exit code: non-zero on any error.
        if summary.get('errors'):
            return 2
        return 0


if __name__ == '__main__':
    raise SystemExit(main())

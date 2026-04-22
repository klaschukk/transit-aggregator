"""
Send one fake price-alert email to a test address — useful for previewing
template changes without waiting for a real drop.

The email goes through the real send_mail() path, so SMTP_HOST respects
the same DEV-log fallback as production. With --dry-run, the rendered
subject + text are printed to stdout and nothing is sent.

Usage:
    python scripts/price_alert_test.py \\
        --route beograd-novi-sad \\
        --email me@example.com \\
        --lang sr \\
        --old 900 --new 720    # simulate 20% drop
    python scripts/price_alert_test.py ... --dry-run
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import create_app  # noqa: E402
from app.mailer import send_mail  # noqa: E402
from app.price_alerts import build_price_alert_email  # noqa: E402


def _lookup_route(transit_db: str, slug: str) -> tuple[str, str] | None:
    con = duckdb.connect(transit_db, read_only=True)
    try:
        row = con.execute(
            "SELECT from_city, to_city FROM routes WHERE slug = ? LIMIT 1",
            [slug],
        ).fetchone()
    finally:
        con.close()
    return (row[0], row[1]) if row else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--route', required=True, help='route slug, e.g. beograd-nis')
    ap.add_argument('--email', required=True, help='recipient address')
    ap.add_argument('--lang', default='sr', choices=('sr', 'en', 'ru'))
    ap.add_argument('--old', type=int, default=1000, help='baseline price RSD')
    ap.add_argument('--new', type=int, default=750, help='dropped price RSD')
    ap.add_argument('--dry-run', action='store_true',
                    help='render and print, do not send')
    args = ap.parse_args()

    app = create_app()
    with app.app_context():
        pair = _lookup_route(app.config.get('DUCKDB_PATH', ''), args.route)
        if not pair:
            print(f'route not found: {args.route}', file=sys.stderr)
            return 2
        from_city, to_city = pair

        if args.old <= 0 or args.new <= 0 or args.new >= args.old:
            print('old must be > new > 0 for a drop', file=sys.stderr)
            return 2
        drop_pct = int(round((args.old - args.new) * 100 / args.old))

        subject, text, html = build_price_alert_email(
            route_slug=args.route,
            from_city=from_city, to_city=to_city,
            old_price=args.old, new_price=args.new, drop_pct=drop_pct,
            lang=args.lang,
            unsubscribe_token='TEST-TOKEN-DO-NOT-CLICK',
        )

        if args.dry_run:
            print('=' * 60)
            print(f'TO:      {args.email}')
            print(f'SUBJECT: {subject}')
            print('=' * 60)
            print(text)
            print('=' * 60)
            print('(dry-run — nothing sent; HTML length: %d bytes)' % len(html))
            return 0

        ok = send_mail(to=args.email, subject=subject, text=text, html=html)
        print('sent' if ok else 'FAILED')
        return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

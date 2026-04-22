"""
Scan price snapshots, fire price-drop emails to matching subscribers.

Runs from nightly_refresh.sh after scripts/price_snapshot.py. Emits
logs/price_alerts.log line per evaluation so we can debug "why didn't
this alert fire".

Selection pipeline:
  1. Distinct route_slug values among confirmed subscribers
  2. Last 7 days of price_snapshots per route
  3. evaluate_snapshots() → today_min < 7d_min × 0.9 qualifies
  4. For each confirmed subscriber on that route:
     - skip if unsubscribed or unconfirmed
     - skip if we already emailed them about this route in the past 7 days
     - render + send email; record in price_alerts_sent
  5. Stop if we've already sent MAX_EMAILS_PER_RUN (SMTP-ban safety)

Usage:
    python scripts/price_alert_scan.py                  # real run
    python scripts/price_alert_scan.py --dry-run        # no emails, log only
    python scripts/price_alert_scan.py --max 5          # override per-run cap
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date as _date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import analytics_db, create_app  # noqa: E402
from app.mailer import send_mail  # noqa: E402
from app.price_alerts import (  # noqa: E402
    COOLDOWN_DAYS,
    MAX_EMAILS_PER_RUN,
    build_price_alert_email,
    evaluate_snapshots,
)


def _setup_log(log_path: Path) -> logging.Logger:
    logger = logging.getLogger('price_alert_scan')
    logger.setLevel(logging.INFO)
    # Console + file so cron mailer + grep both work
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except OSError as exc:
        logger.warning('file log unavailable: %s', exc)
    return logger


def _route_labels(transit_db_path: str, slugs: list[str]) -> dict[str, tuple[str, str]]:
    """Resolve route_slug → (from_city, to_city) for email subject lines."""
    if not slugs:
        return {}
    import duckdb
    con = duckdb.connect(transit_db_path, read_only=True)
    try:
        placeholders = ','.join('?' for _ in slugs)
        rows = con.execute(
            f"SELECT slug, from_city, to_city FROM routes WHERE slug IN ({placeholders})",
            slugs,
        ).fetchall()
    finally:
        con.close()
    return {slug: (fc, tc) for slug, fc, tc in rows}


def scan(
    *,
    today: _date | None = None,
    dry_run: bool = False,
    max_emails: int = MAX_EMAILS_PER_RUN,
) -> dict:
    """Main entry. Returns stats dict: routes_seen, qualified, emails_sent,
    skipped_cooldown, skipped_unconfirmed, skipped_unsubscribed."""
    app = create_app()
    today = today or _date.today()
    log_path = Path(app.root_path).parent / 'logs' / 'price_alerts.log'

    stats = {
        'routes_seen': 0, 'routes_qualified': 0, 'subscribers_checked': 0,
        'emails_sent': 0, 'emails_failed': 0,
        'skipped_cooldown': 0, 'skipped_capped': 0,
    }

    with app.app_context():
        logger = _setup_log(log_path)
        analytics_db.init_schema()

        # Routes that have at least one confirmed subscriber tracking them
        routes = analytics_db.query("""
            SELECT DISTINCT route_slug FROM subscribers
            WHERE route_slug IS NOT NULL
              AND confirmed_at IS NOT NULL
              AND unsubscribed_at IS NULL
        """)
        route_slugs = [r['route_slug'] for r in routes if r.get('route_slug')]
        labels = _route_labels(app.config.get('DUCKDB_PATH', ''), route_slugs)
        stats['routes_seen'] = len(route_slugs)
        logger.info('scan start: %d routes with subscribers (today=%s, dry_run=%s, max=%d)',
                    len(route_slugs), today, dry_run, max_emails)

        for slug in route_slugs:
            if stats['emails_sent'] >= max_emails:
                stats['skipped_capped'] += 1
                continue
            snapshots = analytics_db.price_snapshots_for_route(slug, days=10)
            # decorate with route_slug for evaluate_snapshots' diagnostic text
            for s in snapshots:
                s['route_slug'] = slug
            ev = evaluate_snapshots(snapshots, today)
            if not ev.qualifies:
                logger.info('[%s] skip — %s', slug, ev.reason)
                continue
            stats['routes_qualified'] += 1
            from_city, to_city = labels.get(slug, (slug, slug))
            logger.info('[%s] QUALIFIES — today %s RSD vs baseline %s (drop %d%%)',
                        slug, ev.today_min, ev.baseline_min, ev.drop_pct)

            subs = analytics_db.subscribers_for_route_alerts(slug)
            for sub in subs:
                stats['subscribers_checked'] += 1
                if stats['emails_sent'] >= max_emails:
                    stats['skipped_capped'] += 1
                    break
                if analytics_db.price_alert_recently_sent(
                    sub['id'], slug, COOLDOWN_DAYS,
                ):
                    stats['skipped_cooldown'] += 1
                    logger.info('  sub=%d skip: cooldown', sub['id'])
                    continue
                subject, text, html = build_price_alert_email(
                    route_slug=slug,
                    from_city=from_city, to_city=to_city,
                    old_price=ev.baseline_min, new_price=ev.today_min,
                    drop_pct=ev.drop_pct,
                    lang=sub.get('lang') or 'sr',
                    unsubscribe_token=sub['unsubscribe_token'] or '',
                )
                if dry_run:
                    logger.info('  sub=%d DRY-RUN subject=%r', sub['id'], subject)
                    continue
                ok = send_mail(
                    to=sub['email'], subject=subject, text=text, html=html,
                )
                if ok:
                    stats['emails_sent'] += 1
                else:
                    stats['emails_failed'] += 1
                analytics_db.record_price_alert_sent(
                    subscriber_id=sub['id'], route_slug=slug,
                    old_price=ev.baseline_min, new_price=ev.today_min,
                    drop_pct=ev.drop_pct, delivered_ok=ok,
                )
                logger.info('  sub=%d sent=%s', sub['id'], ok)

        logger.info('scan done: %s', stats)
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dry-run', action='store_true',
                    help='evaluate but do not send emails')
    ap.add_argument('--max', type=int, default=MAX_EMAILS_PER_RUN,
                    help=f'hard cap on emails per run (default: {MAX_EMAILS_PER_RUN})')
    ap.add_argument('--date', type=_date.fromisoformat, default=None,
                    help='evaluate as if today were this date (YYYY-MM-DD)')
    args = ap.parse_args()
    scan(today=args.date, dry_run=args.dry_run, max_emails=args.max)
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""
Nightly price snapshot — one row per (route_slug, date) in
analytics.duckdb.price_snapshots.

Runs from nightly_refresh.sh *after* build_db.py so it reads the freshly
rebuilt transit DB. Idempotent — rerunning on the same day UPSERTs the
same row instead of duplicating.

Usage:
    python scripts/price_snapshot.py              # prod run (today)
    python scripts/price_snapshot.py --date 2026-04-15  # backfill

Only routes with at least one paid trip (price_rsd > 0) contribute.
Tripless / price-less routes are skipped — their drop detector would
never fire anyway, and an empty snapshot row would poison the baseline.
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date as _date
from pathlib import Path

import duckdb

# Flask app context → analytics_db writes
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import analytics_db, create_app  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger('price_snapshot')


def _transit_db_path(app) -> str:
    return app.config.get('DUCKDB_PATH') or 'data/dbs/transit.duckdb'


def _aggregate_routes(transit_db_path: str) -> list[dict]:
    """Pull per-route price aggregates from transit.duckdb (read-only).

    Only intercity routes with paid trips are included — city_lines has
    no meaningful per-ride price, and price_rsd=0 rows are placeholders
    from scrapers that couldn't read a price.
    """
    con = duckdb.connect(transit_db_path, read_only=True)
    try:
        rows = con.execute("""
            SELECT r.slug                     AS route_slug,
                   MIN(t.price_rsd)           AS min_price,
                   MAX(t.price_rsd)           AS max_price,
                   AVG(t.price_rsd)::DOUBLE   AS avg_price,
                   COUNT(*)                   AS trip_count
            FROM routes r
            JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity' AND t.price_rsd > 0
            GROUP BY r.slug
            ORDER BY r.slug
        """).fetchall()
    finally:
        con.close()

    cols = ('route_slug', 'min_price', 'max_price', 'avg_price', 'trip_count')
    return [dict(zip(cols, r)) for r in rows]


def snapshot(
    snapshot_date: _date | None = None,
    transit_db_path: str | None = None,
) -> int:
    """Emit snapshots for `snapshot_date` (default: today). Returns the
    number of routes written."""
    app = create_app()
    snap_date = snapshot_date or _date.today()

    with app.app_context():
        analytics_db.init_schema()
        routes = _aggregate_routes(transit_db_path or _transit_db_path(app))
        written = 0
        for r in routes:
            ok = analytics_db.insert_or_refresh_price_snapshot(
                r['route_slug'],
                snapshot_date=snap_date,
                min_price=int(r['min_price']) if r['min_price'] is not None else None,
                max_price=int(r['max_price']) if r['max_price'] is not None else None,
                avg_price=float(r['avg_price']) if r['avg_price'] is not None else None,
                trip_count=int(r['trip_count']),
            )
            if ok:
                written += 1
        log.info(
            'snapshot %s complete: %d routes eligible, %d written',
            snap_date.isoformat(), len(routes), written,
        )
        return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--date', type=_date.fromisoformat, default=None,
                    help='snapshot date (YYYY-MM-DD); default: today')
    ap.add_argument('--transit-db', type=str, default=None,
                    help='path to transit.duckdb (default: config DUCKDB_PATH)')
    args = ap.parse_args()
    snapshot(args.date, args.transit_db)
    return 0


if __name__ == '__main__':
    sys.exit(main())

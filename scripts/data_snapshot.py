"""Snapshot row counts from transit.duckdb into analytics_db.data_snapshots.

Runs once per night, after build_db.py succeeds. Captures the size of each
load-bearing entity bucket so the diff against yesterday surfaces upstream
scrape drift that the file-mtime freshness signal misses (e.g. operator
added 3 trips but the JSON file mtime stayed the same because the scraper
unconditionally overwrites the file every run).

Kinds captured:
  - operator_routes: route_count per operator slug
  - route_trips:     trip_count per route slug (priced trips only)
  - city_lines:      line_count per city
  - city_stops:      stop_count per city

Usage:
    PYTHONPATH=. ./venv/bin/python scripts/data_snapshot.py

The script reads transit.duckdb in read-only mode (no lock contention) and
writes to analytics_db (which is single-writer; Flask is stopped during
nightly_refresh.sh's window so no contention). Idempotent — re-running on
the same day overwrites the existing rows for that snapshot_date.
"""
import os
import sys
from datetime import date as date_cls
from pathlib import Path

import duckdb

# Bootstrap Flask app context so analytics_db helpers can resolve config.
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("SECRET_KEY", "snapshot-tool")
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app  # noqa: E402
from app import analytics_db  # noqa: E402


def _read_counts(transit_db_path: str) -> dict[str, list[tuple[str, int]]]:
    """Return per-kind list of (key, value) tuples from the read-only transit DB."""
    conn = duckdb.connect(transit_db_path, read_only=True)
    try:
        operator_routes = conn.execute("""
            SELECT o.slug, COUNT(DISTINCT r.id)
            FROM operators o
            JOIN trips t ON t.operator_id = o.id
            JOIN routes r ON r.id = t.route_id
            WHERE t.price_rsd > 0
            GROUP BY o.slug
        """).fetchall()
        route_trips = conn.execute("""
            SELECT r.slug, COUNT(t.id)
            FROM routes r
            JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity' AND t.price_rsd > 0
            GROUP BY r.slug
        """).fetchall()
        city_lines = conn.execute(
            "SELECT city, COUNT(*) FROM city_lines GROUP BY city"
        ).fetchall()
        city_stops = conn.execute(
            "SELECT city, COUNT(*) FROM city_stops GROUP BY city"
        ).fetchall()
    finally:
        conn.close()
    return {
        'operator_routes': operator_routes,
        'route_trips': route_trips,
        'city_lines': city_lines,
        'city_stops': city_stops,
    }


def main() -> int:
    app = create_app()
    today = date_cls.today().isoformat()

    with app.app_context():
        transit_path = app.config['DUCKDB_PATH']
        if not Path(transit_path).exists():
            print(f'transit.duckdb missing at {transit_path}', file=sys.stderr)
            return 1

        counts = _read_counts(transit_path)
        analytics_db.init_schema()
        total = 0
        for kind, rows in counts.items():
            for key, value in rows:
                analytics_db.record_snapshot(today, kind, str(key), int(value))
                total += 1
            print(f'{kind}: {len(rows)} rows')
        print(f'snapshot_date={today} rows={total}')

        # Print today-vs-yesterday diff for the operator_routes kind so the
        # nightly log shows the headline delta. The other kinds are still
        # captured in the table — humans pull them ad hoc.
        for kind in ('operator_routes',):
            diff = analytics_db.diff_snapshots(kind)
            if not diff:
                print(f'{kind}: no diff (first snapshot or no changes)')
                continue
            print(f'\n{kind} delta (top 10 by abs delta):')
            for row in diff[:10]:
                print(f'  {row["key"]:<30} {row["value_a"]:>4} → {row["value_b"]:>4}  Δ{row["delta"]:+d}')

        analytics_db.close_thread_conn()
    return 0


if __name__ == '__main__':
    sys.exit(main())

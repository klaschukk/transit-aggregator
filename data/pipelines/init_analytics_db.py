"""Initialise the analytics DuckDB (ba_clicks table).

Idempotent — safe to run repeatedly. The Flask app also initialises on boot,
but this script lets ops create the DB file ahead of first traffic and hand
it off to gunicorn with the correct owner/permissions.

Usage:
  python data/pipelines/init_analytics_db.py [/path/to/analytics.duckdb]

Default path: data/dbs/analytics.duckdb (matches Config.ANALYTICS_DB_PATH).
"""
import sys
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PATH = REPO_ROOT / 'data' / 'dbs' / 'analytics.duckdb'

SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS ba_clicks_id_seq;
CREATE TABLE IF NOT EXISTS ba_clicks (
    id          BIGINT PRIMARY KEY DEFAULT nextval('ba_clicks_id_seq'),
    route_slug  VARCHAR,
    surface     VARCHAR,
    operator    VARCHAR,
    trip_time   VARCHAR,
    ip_hash     VARCHAR,
    user_agent  VARCHAR,
    referrer    VARCHAR,
    ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ba_clicks_ts_idx ON ba_clicks(ts);
CREATE INDEX IF NOT EXISTS ba_clicks_slug_idx ON ba_clicks(route_slug);
"""


def main() -> int:
    db_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(db_path), read_only=False)
    try:
        conn.execute(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM ba_clicks").fetchone()[0]
        print(f"ok: analytics.duckdb ready at {db_path} (ba_clicks rows: {count})")
    finally:
        conn.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

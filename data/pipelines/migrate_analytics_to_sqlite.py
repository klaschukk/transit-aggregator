"""Migrate analytics.duckdb → analytics.sqlite.

Run once before switching ANALYTICS_DB_PATH in config.
Copies all rows from every table; idempotent (uses INSERT OR IGNORE so
re-running won't duplicate data, but won't overwrite either).

Usage:
    python data/pipelines/migrate_analytics_to_sqlite.py
"""
import sqlite3
import sys
from pathlib import Path

import duckdb

BASE = Path(__file__).parent.parent.parent
SRC = BASE / 'data' / 'dbs' / 'analytics.duckdb'
DST = BASE / 'data' / 'dbs' / 'analytics.sqlite'

TABLES = [
    'ba_clicks',
    'reviews',
    'subscribers',
    'price_snapshots',
    'price_alerts_sent',
    'campaigns',
    'campaign_sends',
    'email_suppressions',
    'ab_events',
    'data_snapshots',
]


def main() -> None:
    if not SRC.exists():
        print(f"Source not found: {SRC}")
        sys.exit(1)

    print(f"Source : {SRC}")
    print(f"Target : {DST}")

    src = duckdb.connect(str(SRC), read_only=True)

    # Init schema in target via the app's own init_schema
    sys.path.insert(0, str(BASE))
    from app import create_app
    app = create_app('development')
    app.config['ANALYTICS_DB_PATH'] = str(DST)
    with app.app_context():
        from app import analytics_db
        analytics_db.init_schema()

    dst = sqlite3.connect(str(DST))
    dst.execute('PRAGMA journal_mode=WAL')
    dst.execute('PRAGMA synchronous=NORMAL')

    total = 0
    for table in TABLES:
        try:
            rows = src.execute(f"SELECT * FROM {table}").fetchall()
            cols = [d[0] for d in src.execute(f"SELECT * FROM {table} LIMIT 0").description]
        except duckdb.CatalogException:
            print(f"  {table}: not found in source, skipping")
            continue

        if not rows:
            print(f"  {table}: 0 rows")
            continue

        placeholders = ', '.join(['?'] * len(cols))
        col_list = ', '.join(cols)
        # Coerce DuckDB types to SQLite-friendly ones
        clean_rows = []
        for row in rows:
            clean = []
            for val in row:
                if hasattr(val, 'isoformat'):
                    val = val.isoformat()
                elif isinstance(val, bool):
                    val = int(val)
                clean.append(val)
            clean_rows.append(clean)

        dst.executemany(
            f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})",
            clean_rows,
        )
        dst.commit()
        print(f"  {table}: {len(rows)} rows migrated")
        total += len(rows)

    src.close()
    dst.close()
    print(f"\nDone. {total} total rows migrated to {DST}")


if __name__ == '__main__':
    main()

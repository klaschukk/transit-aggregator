"""Analytics DuckDB connection — read/write, separate file from the main
read-only transit DB so concurrent writes don't conflict with the scraper
refresh of data/dbs/transit.duckdb.

Schema is created idempotently on app boot via init_schema().
"""
import hashlib
import logging
import os
import threading
from pathlib import Path

import duckdb
from flask import current_app

logger = logging.getLogger(__name__)

_local = threading.local()


def _path() -> str:
    return current_app.config['ANALYTICS_DB_PATH']


def _get_conn() -> duckdb.DuckDBPyConnection:
    """Return a per-thread R/W connection. Reconnects automatically when the
    configured path changes (matters for tests that swap DBs between apps)."""
    target = _path()
    conn = getattr(_local, 'conn', None)
    bound_path = getattr(_local, 'path', None)
    if conn is None or bound_path != target:
        if conn is not None:
            try: conn.close()
            except duckdb.Error: pass
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(target, read_only=False)
        _local.conn = conn
        _local.path = target
    return conn


_SCHEMA_SQL = """
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


def init_schema() -> None:
    """Idempotent schema creation. Runs every app boot (CREATE ... IF NOT
    EXISTS is cheap) so tests that swap ANALYTICS_DB_PATH still get a valid
    schema on the new file."""
    try:
        _get_conn().execute(_SCHEMA_SQL)
        logger.info("analytics_db schema ready at %s", _path())
    except duckdb.Error as exc:
        logger.error("analytics_db init failed: %s", exc)


def hash_ip(ip: str) -> str:
    """sha256(salt + ip) — not pseudonymising; just reducing re-identifiability.
    Salt comes from config so rotating it invalidates history for fresh audits."""
    salt = current_app.config.get('IP_HASH_SALT', '')
    if not salt:
        # Missing salt in production is a config error, but we still return
        # something stable so /api/ba-click doesn't 500 — rotation is a ops task.
        salt = 'dev-only-rotate-me'
    return hashlib.sha256((salt + '|' + (ip or '')).encode('utf-8')).hexdigest()[:32]


def insert_ba_click(
    route_slug: str,
    surface: str,
    operator: str,
    trip_time: str,
    ip: str,
    user_agent: str,
    referrer: str,
) -> None:
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO ba_clicks (route_slug, surface, operator, trip_time, ip_hash, user_agent, referrer) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (route_slug or '')[:200],
                (surface or '')[:40],
                (operator or '')[:100],
                (trip_time or '')[:10],
                hash_ip(ip),
                (user_agent or '')[:300],
                (referrer or '')[:500],
            ],
        )
    except duckdb.Error as exc:
        logger.error("insert_ba_click failed: %s", exc)
        _local.conn = None  # reset stale connection


def query(sql: str, params: list | None = None) -> list[dict]:
    """Read query helper for the admin dashboard."""
    try:
        conn = _get_conn()
        res = conn.execute(sql, params or [])
        cols = [d[0] for d in res.description]
        return [dict(zip(cols, row)) for row in res.fetchall()]
    except duckdb.Error as exc:
        logger.error("analytics_db query failed: %s | %s", exc, sql)
        _local.conn = None
        return []

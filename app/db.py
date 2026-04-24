import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import Any

import duckdb
from flask import current_app

from . import observability

logger = logging.getLogger(__name__)

# Thread-local persistent connections (one per gunicorn worker thread)
_local = threading.local()

# Simple in-memory TTL cache shared across requests within a worker
_cache: dict[str, tuple[float, Any]] = {}
_cache_lock = threading.Lock()


def _db_path() -> str:
    return current_app.config['DUCKDB_PATH']


def _get_conn() -> duckdb.DuckDBPyConnection:
    """Return a persistent read-only connection for the current thread."""
    conn = getattr(_local, 'conn', None)
    if conn is None:
        conn = duckdb.connect(_db_path(), read_only=True)
        _local.conn = conn
    return conn


def db_ready() -> bool:
    """Check if database file exists."""
    return Path(_db_path()).exists()


def query(sql: str, params: list[Any] | None = None) -> list[dict]:
    """Execute a read query and return list of dicts."""
    p = params or []
    try:
        conn = _get_conn()
        result = conn.execute(sql, p)
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]
    except duckdb.IOException as exc:
        # Connection went stale (e.g. DB rebuilt) — reconnect once.
        logger.warning("DuckDB IO error, reconnecting: %s | sql=%s params=%s", exc, sql, p)
        _local.conn = None
        try:
            conn = _get_conn()
            result = conn.execute(sql, p)
            columns = [desc[0] for desc in result.description]
            return [dict(zip(columns, row)) for row in result.fetchall()]
        except duckdb.Error as exc2:
            logger.error("DuckDB query failed after reconnect: %s | sql=%s params=%s",
                         exc2, sql, p)
            observability.capture_exception(exc2, subsystem='duckdb',
                                            phase='post_reconnect')
            return []
    except duckdb.Error as exc:
        logger.error("DuckDB query error: %s | sql=%s params=%s", exc, sql, p)
        _local.conn = None
        observability.capture_exception(exc, subsystem='duckdb', phase='query')
        return []


def query_one(sql: str, params: list[Any] | None = None) -> dict | None:
    """Execute a query and return single row as dict, or None."""
    rows = query(sql, params)
    return rows[0] if rows else None


def cached_query(sql: str, params: list[Any] | None = None, ttl: int = 300) -> list[dict]:
    """Query with in-memory TTL cache. Default 5 min."""
    key = hashlib.md5((sql + str(params or [])).encode()).hexdigest()

    with _cache_lock:
        if key in _cache:
            expires, data = _cache[key]
            if time.time() < expires:
                return data

    data = query(sql, params)

    with _cache_lock:
        _cache[key] = (time.time() + ttl, data)

    return data


def cached_query_one(sql: str, params: list[Any] | None = None, ttl: int = 300) -> dict | None:
    rows = cached_query(sql, params, ttl)
    return rows[0] if rows else None

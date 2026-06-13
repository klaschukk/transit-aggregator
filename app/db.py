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

# Simple in-memory TTL cache shared across requests within a worker.
# Bounded so a crawler hitting thousands of distinct keys (every /api/cities
# prefix, every line_id/stop_id) can't grow it without limit until the worker
# recycles at --max-requests.
_cache: dict[str, tuple[float, Any]] = {}
_cache_lock = threading.Lock()
_CACHE_MAX = 2000


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
    """Execute a read query and return list of dicts.

    On a DB error the result is an empty list AND the thread-local ``errored``
    flag is set, so cached_query() knows not to cache this (a transient blip
    must not poison the cache with an empty page/sitemap for the full TTL).
    Params are not logged — for /pretraga/ they are user search input and the
    Sentry logging integration would forward them as telemetry.
    """
    p = params or []
    _local.errored = False

    def _run() -> list[dict]:
        result = _get_conn().execute(sql, p)
        columns = [desc[0] for desc in result.description]
        return [dict(zip(columns, row)) for row in result.fetchall()]

    try:
        return _run()
    except duckdb.Error as exc:
        # Any DuckDB error after a rebuild (IOException on a swapped file,
        # CatalogException/SerializationException on a changed catalog) means
        # the thread-local connection is stale — drop it and retry ONCE so the
        # first post-rebuild request recovers instead of returning empty.
        logger.warning("DuckDB error, reconnecting: %s | sql=%s", exc, sql)
        _local.conn = None
        try:
            return _run()
        except duckdb.Error as exc2:
            logger.error("DuckDB query failed after reconnect: %s | sql=%s", exc2, sql)
            observability.capture_exception(exc2, subsystem='duckdb',
                                            phase='post_reconnect')
            _local.conn = None
            _local.errored = True
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

    # Never cache an error result: a transient DB blip would otherwise serve an
    # empty page/sitemap for the whole TTL (up to an hour) after the DB recovers.
    if getattr(_local, 'errored', False):
        return data

    now = time.time()
    with _cache_lock:
        if key not in _cache and len(_cache) >= _CACHE_MAX:
            # Evict expired entries first; if still full, drop the soonest-to-
            # expire one. Keeps the dict bounded under a wide crawl.
            for k in [k for k, (exp, _) in _cache.items() if exp <= now]:
                _cache.pop(k, None)
            if len(_cache) >= _CACHE_MAX:
                _cache.pop(min(_cache, key=lambda k: _cache[k][0]), None)
        _cache[key] = (now + ttl, data)

    return data


def cached_query_one(sql: str, params: list[Any] | None = None, ttl: int = 300) -> dict | None:
    rows = cached_query(sql, params, ttl)
    return rows[0] if rows else None

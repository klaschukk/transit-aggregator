import logging
import threading
import time
from pathlib import Path
from typing import Any

import duckdb
from flask import current_app

logger = logging.getLogger(__name__)

_lock = threading.Lock()


def _db_path() -> str:
    return current_app.config['DUCKDB_PATH']


def db_ready() -> bool:
    """Check if database file exists."""
    return Path(_db_path()).exists()


def query(sql: str, params: list[Any] | None = None) -> list[dict]:
    """Execute a query and return list of dicts. Retries on DuckDB lock errors."""
    for attempt in range(10):
        try:
            with _lock:
                conn = duckdb.connect(_db_path(), read_only=True)
                result = conn.execute(sql, params or [])
                columns = [desc[0] for desc in result.description]
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                conn.close()
                return rows
        except duckdb.IOException:
            logger.warning("DuckDB locked, attempt %d/10, retrying...", attempt + 1)
            time.sleep(0.5)
    return []


def query_one(sql: str, params: list[Any] | None = None) -> dict | None:
    """Execute a query and return single row as dict, or None."""
    rows = query(sql, params)
    return rows[0] if rows else None

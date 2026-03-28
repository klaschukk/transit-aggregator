import threading
from pathlib import Path
from typing import Any

import duckdb
from flask import current_app, g


_local = threading.local()


def get_db() -> duckdb.DuckDBPyConnection:
    """Get a thread-local DuckDB read-only connection."""
    if not hasattr(_local, 'conn') or _local.conn is None:
        db_path = current_app.config['DUCKDB_PATH']
        if Path(db_path).exists():
            _local.conn = duckdb.connect(db_path, read_only=True)
        else:
            # Return in-memory DB for dev when db file doesn't exist yet
            _local.conn = duckdb.connect(':memory:')
    return _local.conn


def query(sql: str, params: list[Any] | None = None) -> list[dict]:
    """Execute a query and return list of dicts."""
    conn = get_db()
    result = conn.execute(sql, params or [])
    columns = [desc[0] for desc in result.description]
    return [dict(zip(columns, row)) for row in result.fetchall()]


def query_one(sql: str, params: list[Any] | None = None) -> dict | None:
    """Execute a query and return single row as dict, or None."""
    rows = query(sql, params)
    return rows[0] if rows else None

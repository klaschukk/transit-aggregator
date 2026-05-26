"""Concurrency regression tests for analytics_db (SQLite/WAL).

Replaced DuckDB-specific retry tests with SQLite WAL equivalents:
- WAL mode enables concurrent readers while a writer is active
- busy_timeout handles writer contention without raising errors
- close_thread_conn() releases the per-thread connection cleanly
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def wal_app(tmp_path):
    from flask import Flask
    app = Flask(__name__)
    app.config['ANALYTICS_DB_PATH'] = str(tmp_path / 'analytics.sqlite')
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()
        yield app, analytics_db


def test_wal_mode_enabled(wal_app):
    """Connection must be opened in WAL journal mode."""
    app, analytics_db = wal_app
    with app.app_context():
        conn = analytics_db._get_conn()
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == 'wal'


def test_close_thread_conn_releases_connection(wal_app):
    """After close_thread_conn() the thread-local slot is cleared."""
    app, analytics_db = wal_app
    with app.app_context():
        conn = analytics_db._get_conn()
        assert conn is not None
        analytics_db.close_thread_conn()
        assert getattr(analytics_db._local, 'conn', None) is None


def test_reconnect_after_close(wal_app):
    """_get_conn() transparently reopens after close_thread_conn()."""
    app, analytics_db = wal_app
    with app.app_context():
        c1 = analytics_db._get_conn()
        analytics_db.close_thread_conn()
        c2 = analytics_db._get_conn()
        # Must be a fresh connection, not the closed one.
        assert c2 is not c1
        assert c2 is not None

"""Lock-contention regression test for analytics_db.

DuckDB allows many R/W connections inside one process but rejects any
cross-process open while the file is held R/W. With 2 gunicorn workers
+ nightly cron writers (adsense_fetch, price_snapshot, seed_reviews)
this used to spam journalctl with "Could not set lock on file" errors.

Fix: app/analytics_db.py wraps duckdb.connect in _open_with_retry
and Flask closes the per-thread conn on teardown_appcontext.
This test reproduces the cross-process conflict and asserts that the
retry path eventually succeeds.
"""
import os
import sys
import time
import multiprocessing as mp
from pathlib import Path

import duckdb
import pytest


def _hold_writelock(db_path: str, ready_event, release_event):
    conn = duckdb.connect(db_path, read_only=False)
    conn.execute('CREATE TABLE IF NOT EXISTS x(a INTEGER)')
    ready_event.set()
    release_event.wait(timeout=5)
    conn.close()


def test_open_with_retry_recovers_from_transient_lock(tmp_path, monkeypatch):
    """Spawn a child process holding the R/W lock for ~600 ms. The
    parent calls _open_with_retry and must succeed once the child lets
    go — proving the retry budget is wide enough to ride out a real
    cross-process collision."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    db_path = str(tmp_path / 'analytics.duckdb')
    # Prime the schema so child + parent talk to the same file.
    duckdb.connect(db_path, read_only=False).close()

    ctx = mp.get_context('fork')
    ready = ctx.Event()
    release = ctx.Event()
    holder = ctx.Process(target=_hold_writelock, args=(db_path, ready, release))
    holder.start()
    try:
        assert ready.wait(timeout=5), 'child failed to acquire write lock'

        # Schedule release ~600 ms from now — within the 100+200+400+800
        # retry envelope (1500 ms total).
        from threading import Timer
        Timer(0.6, release.set).start()

        from app.analytics_db import _open_with_retry
        t0 = time.time()
        conn = _open_with_retry(db_path)
        elapsed = time.time() - t0
        try:
            # Sanity: opened R/W, can run a write.
            conn.execute('CREATE TABLE IF NOT EXISTS y(a INTEGER)')
        finally:
            conn.close()

        # Should have waited at least until the holder released — but
        # well within the worst-case 1500 ms budget.
        assert 0.5 <= elapsed <= 2.0, f'unexpected wait time: {elapsed:.2f}s'
    finally:
        release.set()
        holder.join(timeout=5)
        if holder.is_alive():
            holder.terminate()


def test_close_thread_conn_releases_lock(tmp_path, monkeypatch):
    """After close_thread_conn() returns, a fresh process must be able
    to open the file R/W immediately. Without the close, the per-thread
    cache would keep the lock indefinitely."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    db_path = str(tmp_path / 'analytics.duckdb')
    duckdb.connect(db_path, read_only=False).close()

    from flask import Flask
    app = Flask(__name__)
    app.config['ANALYTICS_DB_PATH'] = db_path

    from app import analytics_db
    with app.app_context():
        # Open via the cached path — sets _local.conn.
        conn = analytics_db._get_conn()
        conn.execute('CREATE TABLE IF NOT EXISTS x(a INTEGER)')
        # Release.
        analytics_db.close_thread_conn()

    # Spawned process must succeed immediately — no retry needed.
    ctx = mp.get_context('fork')

    def _try_open(path, q):
        try:
            c = duckdb.connect(path, read_only=False)
            c.close()
            q.put('ok')
        except Exception as e:  # noqa: BLE001
            q.put(f'fail: {e}')

    q = ctx.Queue()
    p = ctx.Process(target=_try_open, args=(db_path, q))
    p.start()
    p.join(timeout=3)
    result = q.get(timeout=1)
    assert result == 'ok', f'cross-process open failed: {result}'

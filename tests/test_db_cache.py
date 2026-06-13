"""Reliability tests for app.db cache + error handling."""
import duckdb
import pytest

from app import db


@pytest.fixture(autouse=True)
def _clear_cache():
    with db._cache_lock:
        db._cache.clear()
    yield
    with db._cache_lock:
        db._cache.clear()


def test_error_result_is_not_cached(app, monkeypatch):
    """A transient DB error returns [] but must NOT poison the cache."""
    calls = {"n": 0}

    def boom(sql, params=None):
        calls["n"] += 1
        db._local.errored = True
        return []

    with app.app_context():
        monkeypatch.setattr(db, "query", boom)
        assert db.cached_query("SELECT 1", ttl=3600) == []
        assert db.cached_query("SELECT 1", ttl=3600) == []
    # Not cached → queried both times (no empty result frozen for an hour).
    assert calls["n"] == 2


def test_good_result_is_cached(app, monkeypatch):
    calls = {"n": 0}

    def ok(sql, params=None):
        calls["n"] += 1
        db._local.errored = False
        return [{"c": 1}]

    with app.app_context():
        monkeypatch.setattr(db, "query", ok)
        assert db.cached_query("SELECT 1", ttl=3600) == [{"c": 1}]
        assert db.cached_query("SELECT 1", ttl=3600) == [{"c": 1}]
    assert calls["n"] == 1  # second served from cache


def test_cache_is_bounded(app, monkeypatch):
    def ok(sql, params=None):
        db._local.errored = False
        return [{"c": 1}]

    with app.app_context():
        monkeypatch.setattr(db, "query", ok)
        for i in range(db._CACHE_MAX + 200):
            db.cached_query("SELECT 1", [i], ttl=3600)
    assert len(db._cache) <= db._CACHE_MAX


def test_db_ready_false_when_file_present_but_query_fails(app, monkeypatch):
    """After an atomic swap the file exists but a query can fail mid-window —
    db_ready() must report not-ready so the 503 guard fires (no empty 200s)."""
    import duckdb

    class BrokenConn:
        def execute(self, sql, p=None):
            raise duckdb.IOException("mid-swap")

    with app.app_context():
        db._ready_cache.clear()
        monkeypatch.setattr("app.db.Path.exists", lambda self: True)
        monkeypatch.setattr(db, "_get_conn", lambda: BrokenConn())
        assert db.db_ready() is False
    db._ready_cache.clear()


def test_db_ready_true_when_query_binds(app, monkeypatch):
    class OkConn:
        def execute(self, sql, p=None):
            return None

    with app.app_context():
        db._ready_cache.clear()
        monkeypatch.setattr("app.db.Path.exists", lambda self: True)
        monkeypatch.setattr(db, "_get_conn", lambda: OkConn())
        assert db.db_ready() is True
    db._ready_cache.clear()


def test_query_reconnects_once_on_catalog_error(app, monkeypatch):
    """A non-IO DuckDB error (stale catalog after rebuild) reconnects + retries."""
    state = {"first": True}

    class FakeConn:
        def execute(self, sql, p):
            if state["first"]:
                state["first"] = False
                raise duckdb.CatalogException("stale catalog")
            class R:
                description = [("c",)]
                def fetchall(self):
                    return [(1,)]
            return R()

    with app.app_context():
        monkeypatch.setattr(db, "_get_conn", lambda: FakeConn())
        rows = db.query("SELECT 1")
    assert rows == [{"c": 1}]  # recovered on retry, not []

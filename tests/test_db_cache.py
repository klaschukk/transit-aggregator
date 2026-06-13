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

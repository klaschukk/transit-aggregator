"""Recently-seen intercity routes survive a scrape that misses them.

busticket4 answers international searches one date at a time and its coverage
flickers: on 2026-08-04 the API returned a departure for Beograd->Sofija and
none for Sofija->Beograd, while the DB held exactly the opposite from an
earlier run. _cleanup drops any intercity route with no trips, so the page
404s into abort(410) and Google is told a live route is permanently gone —
/rute/beograd-sofija/ was crawled and served 410 while the API had a departure.
"""
import importlib.util
import json
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pytest

MODULE_PATH = Path(__file__).parent.parent / 'data' / 'pipelines' / 'build_db.py'


@pytest.fixture(scope='module')
def build_db():
    spec = importlib.util.spec_from_file_location('build_db_mod', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _make_routes_db(path: Path, rows: list[tuple]) -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(path))
    conn.execute("""
        CREATE TABLE routes (
            id INTEGER, slug VARCHAR, from_city VARCHAR, to_city VARCHAR,
            from_city_slug VARCHAR, to_city_slug VARCHAR,
            distance_km DOUBLE, type VARCHAR
        )
    """)
    for row in rows:
        conn.execute("INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", row)
    return conn


def _history_entry(days_ago: int) -> dict:
    return {
        'from_city': 'Beograd', 'to_city': 'Sofija',
        'from_city_slug': 'beograd', 'to_city_slug': 'sofija',
        'distance_km': 395.0, 'type': 'intercity',
        'last_seen': (date.today() - timedelta(days=days_ago)).isoformat(),
    }


def test_missing_route_is_restored_from_memory(build_db, tmp_path, monkeypatch):
    """A route absent from this scrape but seen recently comes back."""
    monkeypatch.setattr(build_db, 'ROUTE_HISTORY_FILE',
                        tmp_path / 'route_slug_history.json')
    (tmp_path / 'route_slug_history.json').write_text(
        json.dumps({'beograd-sofija': _history_entry(3)}), encoding='utf-8')

    conn = _make_routes_db(tmp_path / 'a.duckdb', [
        (1, 'sofija-beograd', 'Sofija', 'Beograd', 'sofija', 'beograd', 395.0, 'intercity'),
    ])
    build_db._remember_routes(conn)

    slugs = {r[0] for r in conn.execute("SELECT slug FROM routes").fetchall()}
    assert 'beograd-sofija' in slugs, "recently-seen route must be restored"
    assert 'sofija-beograd' in slugs, "live route must be untouched"
    conn.close()


def test_long_gone_route_is_not_restored(build_db, tmp_path, monkeypatch):
    """Memory expires — a route gone for months stays gone and still 410s."""
    monkeypatch.setattr(build_db, 'ROUTE_HISTORY_FILE',
                        tmp_path / 'route_slug_history.json')
    (tmp_path / 'route_slug_history.json').write_text(
        json.dumps({'beograd-sofija': _history_entry(
            build_db.ROUTE_MEMORY_DAYS + 10)}), encoding='utf-8')

    conn = _make_routes_db(tmp_path / 'b.duckdb', [])
    build_db._remember_routes(conn)

    slugs = {r[0] for r in conn.execute("SELECT slug FROM routes").fetchall()}
    assert 'beograd-sofija' not in slugs, "expired route must not come back"
    conn.close()


def test_history_records_current_routes(build_db, tmp_path, monkeypatch):
    """Today's routes are written to the history file for future runs."""
    hist = tmp_path / 'route_slug_history.json'
    monkeypatch.setattr(build_db, 'ROUTE_HISTORY_FILE', hist)

    conn = _make_routes_db(tmp_path / 'c.duckdb', [
        (1, 'nis-sofija', 'Niš', 'Sofija', 'nis', 'sofija', 170.0, 'intercity'),
    ])
    build_db._remember_routes(conn)
    conn.close()

    saved = json.loads(hist.read_text(encoding='utf-8'))
    assert 'nis-sofija' in saved
    assert saved['nis-sofija']['last_seen'] == date.today().isoformat()


def test_restored_route_does_not_duplicate_ids(build_db, tmp_path, monkeypatch):
    """Restored rows must get fresh ids, not collide with live ones."""
    monkeypatch.setattr(build_db, 'ROUTE_HISTORY_FILE',
                        tmp_path / 'route_slug_history.json')
    (tmp_path / 'route_slug_history.json').write_text(
        json.dumps({'beograd-sofija': _history_entry(1)}), encoding='utf-8')

    conn = _make_routes_db(tmp_path / 'd.duckdb', [
        (7, 'nis-sofija', 'Niš', 'Sofija', 'nis', 'sofija', 170.0, 'intercity'),
    ])
    build_db._remember_routes(conn)

    ids = [r[0] for r in conn.execute("SELECT id FROM routes").fetchall()]
    assert len(ids) == len(set(ids)), f"duplicate route ids: {ids}"
    conn.close()

"""Guards for scripts/make_seed.py and the committed tests/seed.duckdb.

The headline test asserts the committed seed's schema still matches what
make_seed.py would build from build_db's canonical DDL. That turns the old
silent failure mode — build_db gains a column, the frozen seed goes stale,
the CI gate breaks invisibly — into a loud, actionable test failure that
says "regenerate the seed".
"""
from pathlib import Path

import duckdb
import pytest

from scripts import make_seed

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMITTED_SEED = REPO_ROOT / 'tests' / 'seed.duckdb'


def _schema(path) -> dict:
    """Map table_name -> [(column_name, column_type), ...] for a DuckDB file."""
    conn = duckdb.connect(str(path), read_only=True)
    try:
        tables = [r[0] for r in conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_name").fetchall()]
        return {
            t: [(r[1], r[2]) for r in conn.execute(
                f"PRAGMA table_info('{t}')").fetchall()]
            for t in tables
        }
    finally:
        conn.close()


def test_committed_seed_schema_matches_build_db(tmp_path):
    """The committed seed must match a freshly built one column-for-column.

    If this fails, build_db's schema drifted from the committed fixture —
    regenerate it:  python scripts/make_seed.py
    """
    fresh = make_seed.build_seed(tmp_path / 'fresh.duckdb')
    fresh_schema = _schema(fresh)
    committed_schema = _schema(COMMITTED_SEED)

    assert set(committed_schema) == set(fresh_schema), (
        "table set drifted — run: python scripts/make_seed.py\n"
        f"committed-only: {set(committed_schema) - set(fresh_schema)}\n"
        f"fresh-only:     {set(fresh_schema) - set(committed_schema)}"
    )
    for table in sorted(fresh_schema):
        assert committed_schema[table] == fresh_schema[table], (
            f"schema of '{table}' drifted from build_db — "
            f"run: python scripts/make_seed.py\n"
            f"committed: {committed_schema[table]}\n"
            f"fresh:     {fresh_schema[table]}"
        )


def test_build_seed_is_atomic_no_tmp_left(tmp_path):
    """A successful build leaves the target and no .tmp sibling behind."""
    out = tmp_path / 'seed.duckdb'
    make_seed.build_seed(out)
    assert out.exists()
    assert not out.with_name(out.name + '.tmp').exists()


def test_seed_carries_fixtures_tests_depend_on(tmp_path):
    """Rows that non-skipping seed tests assume must be present.

    Keeps make_seed honest if someone trims a fixture: the Cyrillic-redirect
    tests need sava-centar / linija-15 to exist, and route/trip tests need the
    beograd-novi-sad route to carry trips.
    """
    out = make_seed.build_seed(tmp_path / 'seed.duckdb')
    conn = duckdb.connect(str(out), read_only=True)
    try:
        def scalar(sql):
            return conn.execute(sql).fetchone()[0]

        assert scalar("SELECT COUNT(*) FROM city_stops "
                      "WHERE city='beograd' AND slug='sava-centar'") == 1
        assert scalar("SELECT COUNT(*) FROM city_lines "
                      "WHERE city='beograd' AND slug='linija-15'") == 1
        route_id = scalar("SELECT id FROM routes WHERE slug='beograd-novi-sad'")
        assert route_id is not None
        assert scalar(f"SELECT COUNT(*) FROM trips WHERE route_id={route_id}") >= 1
        # bt4_line_id column populated on at least one trip (drives BT4 checkout).
        assert scalar("SELECT COUNT(*) FROM trips WHERE bt4_line_id IS NOT NULL") >= 1
    finally:
        conn.close()


def test_every_city_line_and_stop_has_non_null_id(tmp_path):
    """The rebuilt seed must not reintroduce the NULL-id rows the old hand-built
    fixture carried — build_db's id-as-PRIMARY-KEY schema would otherwise be a
    lie, and joins on those ids would silently drop rows."""
    out = make_seed.build_seed(tmp_path / 'seed.duckdb')
    conn = duckdb.connect(str(out), read_only=True)
    try:
        assert conn.execute(
            "SELECT COUNT(*) FROM city_lines WHERE id IS NULL").fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM city_stops WHERE id IS NULL").fetchone()[0] == 0
    finally:
        conn.close()

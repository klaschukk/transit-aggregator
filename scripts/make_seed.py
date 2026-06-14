#!/usr/bin/env python3
"""Rebuild tests/seed.duckdb from build_db's canonical schema + inline fixtures.

Why this exists
---------------
The CI test gate runs pytest against the tiny ``tests/seed.duckdb``, NOT the
full DuckDB. The seed used to be a frozen binary with no build script, so when
``build_db`` grew a column (e.g. ``trips.bt4_line_id``) the seed silently went
stale: ``query()`` hit a Binder Error, pages came back empty and the gate broke
— invisibly, because every loop-chat works on a symlinked full DB and never
runs against the seed.

This script makes the seed *reproducible*. It builds the schema by calling the
exact same ``build_db._create_schema`` / ``_restore_line_geometries`` the real
pipeline uses — the ONE source of truth — then inserts a curated handful of
fixture rows (the Beograd/Novi-Sad routes, lines and stops the tests reach for).
When the schema drifts, regenerating is one command:

    python scripts/make_seed.py            # rewrites tests/seed.duckdb
    python scripts/make_seed.py --out /tmp/seed.duckdb   # elsewhere

``tests/test_make_seed.py`` additionally asserts the committed seed's schema
still matches what this script would produce, so a schema change that forgets
to regenerate the seed fails CI loudly instead of silently.

The fixtures are intentionally minimal but must satisfy what the non-skipping
seed tests assume — notably that ``sava-centar`` / ``linija-15`` exist (the
Cyrillic-redirect tests) and that ``beograd-novi-sad`` has trips. Data-quality
and GTFS-dependent tests grace-skip on the seed, so no GTFS rows are needed.
"""
import argparse
import os
import sys
from pathlib import Path

import duckdb

# Make `data.pipelines.build_db` importable (repo root on path) regardless of
# CWD, so the seed schema is always the build_db schema, never a stale copy.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from data.pipelines.build_db import (  # noqa: E402
    _create_schema,
    _restore_line_geometries,
    _verify_slug_invariant,
)

DEFAULT_OUT = REPO_ROOT / 'tests' / 'seed.duckdb'

# ── Fixtures ────────────────────────────────────────────────────────────────
# One small, deterministic slice. Insert order respects FK dependencies
# (operators+routes before trips; lines+stops before line_stops). Every row is
# a plain tuple matching the build_db column order so a schema change surfaces
# here as an arity mismatch rather than silently mis-binding.

OPERATORS = [
    # id, name, slug, website, type
    (1, 'Lasta', 'lasta', 'https://lasta.rs', 'bus'),
    (2, 'Niš-Ekspres', 'nis-ekspres', None, 'bus'),
]

ROUTES = [
    # id, slug, from_city, to_city, from_city_slug, to_city_slug, distance_km, type
    (1, 'beograd-novi-sad', 'Beograd', 'Novi Sad', 'beograd', 'novi-sad', 90, 'intercity'),
    (2, 'beograd-nis', 'Beograd', 'Niš', 'beograd', 'nis', 250, 'intercity'),
    (3, 'beograd-kragujevac', 'Beograd', 'Kragujevac', 'beograd', 'kragujevac', 140, 'intercity'),
]

TRIPS = [
    # id, route_id, operator_id, departure, arrival, duration_min, price_rsd,
    # days_of_week, is_active, bt4_line_id
    (1, 1, 1, '06:00', '07:30', 90, 600, '1234567', True, 909),
    (2, 1, 1, '08:00', '09:30', 90, 600, '1234567', True, None),
    (3, 2, 2, '07:00', '10:30', 210, 1200, '1234567', True, None),
]

CITY_LINES = [
    # id, city, number, name, slug, type, color, code
    (1, 'beograd', '2a', 'Linija 2a', 'linija-2a', 'tram', '#e53935', None),
    (2, 'beograd', '29', 'Linija 29', 'linija-29', 'bus', '#1565c0', None),
    (3, 'novi-sad', '3', 'Linija 3', 'linija-3', 'bus', '#2e7d32', None),
    # line 15 backs the Cyrillic /linija/ redirect test — needs a real id so
    # build_db's id-as-PRIMARY-KEY schema accepts it (the old hand-built seed
    # left it NULL, which a strict rebuild would reject).
    (4, 'beograd', '15', 'Linija 15', 'linija-15', 'bus', '#e63946', None),
]

CITY_STOPS = [
    # id, city, name, slug, lat, lon, code
    (1, 'beograd', 'Sajam', 'sajam', 44.806, 20.435, None),
    (2, 'beograd', 'Slavija', 'slavija', 44.804, 20.466, None),
    (3, 'novi-sad', 'Trg Slobode', 'trg-slobode', 45.254, 19.842, None),
    # sava-centar backs the Cyrillic /stajaliste/ redirect test (id was NULL).
    (4, 'beograd', 'Sava Centar', 'sava-centar', 44.8032, 20.4629, None),
]

CITY_LINE_STOPS = [
    # line_id, stop_id, stop_order
    (1, 1, 1),
    (1, 2, 2),
    (2, 1, 1),
]

STATIONS = [
    # id, city, city_slug, name, code, type, lat, lon
    (1, 'Beograd', 'beograd', 'Beograd Centar', 'BG', 'train', 44.806, 20.467),
]

LINE_GEOMETRIES = [
    # line_id, city, coords_json, way_count, node_count, fetched_at
    (1, 'beograd', '[[44.8,20.4]]', 1, 2, '2026-01-01'),
]


def build_seed(out_path: Path) -> Path:
    """Build a fresh seed DuckDB at ``out_path`` and return it.

    Writes to a temp sibling and atomically replaces the target, so a crash
    mid-build never leaves a half-written seed (mirrors build_db's own swap).
    """
    out_path = Path(out_path)
    tmp_path = out_path.with_name(out_path.name + '.tmp')
    if tmp_path.exists():
        tmp_path.unlink()

    # 16 KiB blocks (the DuckDB minimum) keep this 21-row fixture ~45 KB instead
    # of multi-MB default-block bloat — it's committed to git and regenerated on
    # every schema drift, so each MB compounds in history. The block size lives
    # in the file header; the app opens it read-only without caring.
    conn = duckdb.connect(str(tmp_path), config={'default_block_size': '16384'})
    try:
        _create_schema(conn)
        conn.executemany(
            "INSERT INTO operators VALUES (?, ?, ?, ?, ?)", OPERATORS)
        conn.executemany(
            "INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", ROUTES)
        conn.executemany(
            "INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", TRIPS)
        conn.executemany(
            "INSERT INTO city_lines VALUES (?, ?, ?, ?, ?, ?, ?, ?)", CITY_LINES)
        conn.executemany(
            "INSERT INTO city_stops VALUES (?, ?, ?, ?, ?, ?, ?)", CITY_STOPS)
        conn.executemany(
            "INSERT INTO city_line_stops VALUES (?, ?, ?)", CITY_LINE_STOPS)
        conn.executemany(
            "INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, ?)", STATIONS)
        # Reuses build_db's canonical line_geometries DDL + dangling-row guard.
        _restore_line_geometries(conn, LINE_GEOMETRIES)
        # Same slug guard build_db enforces — fixtures must be ASCII-clean too.
        _verify_slug_invariant(conn)
        conn.execute("CHECKPOINT")
    finally:
        conn.close()

    os.replace(tmp_path, out_path)
    return out_path


def _summarise(path: Path) -> None:
    conn = duckdb.connect(str(path), read_only=True)
    try:
        tables = [r[0] for r in conn.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_name").fetchall()]
        print(f"\nSeed written to {path}")
        for t in tables:
            n = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            print(f"  {t:18s} {n:4d} rows")
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT,
                    help=f'destination DuckDB (default: {DEFAULT_OUT})')
    args = ap.parse_args()
    path = build_seed(args.out)
    _summarise(path)


if __name__ == '__main__':
    main()

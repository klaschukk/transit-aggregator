"""Tests for build_db intercity merge: row validation + type-aware dedup.

Covers the pure validator and an integration run of _load_intercity against an
in-memory DuckDB with temp feed files — proving (a) broken rows are dropped,
not inserted, and (b) a train and a bus leaving the same pair at the same
minute both survive (the dedup key now includes type, so the train is no
longer silently lost to the busticket4 bus).
"""
import json

import duckdb
import pytest

from data.pipelines import build_db
from data.pipelines.build_db import _validate_intercity_trip


# ── pure validator ──────────────────────────────────────────────────────────

def _trip(**over):
    base = {'from_city': 'Beograd', 'to_city': 'Novi Sad',
            'departure_time': '08:00', 'arrival_time': '09:30',
            'price_rsd': 600, 'operator': 'Lasta'}
    base.update(over)
    return base


@pytest.mark.parametrize("over, reason", [
    ({}, ''),                                  # valid
    ({'price_rsd': 0}, ''),                    # 0 = "unknown", allowed
    ({'price_rsd': None}, ''),                 # None → 0, allowed
    ({'departure_time': ''}, 'bad_departure_time'),
    ({'departure_time': '25:99'}, 'bad_departure_time'),
    ({'departure_time': '8:00'}, 'bad_departure_time'),   # needs 2-digit hour
    ({'arrival_time': 'soon'}, 'bad_arrival_time'),
    ({'from_city': ''}, 'missing_city'),
    ({'to_city': None}, 'missing_city'),
    ({'price_rsd': -5}, 'negative_price'),
    ({'price_rsd': 'abc'}, 'bad_price'),
])
def test_validate_intercity_trip(over, reason):
    assert _validate_intercity_trip(_trip(**over)) == reason


def test_validate_missing_time_key_does_not_raise():
    # A row missing the key entirely must be reported, never KeyError.
    assert _validate_intercity_trip({'from_city': 'A', 'to_city': 'B'}) \
        == 'bad_departure_time'


# ── _load_intercity integration ─────────────────────────────────────────────

def _prepare(tmp_path, monkeypatch):
    """Isolate RAW_DIR so lasta/intl feeds don't leak in, and give a schema'd
    in-memory DB with operators loaded (the trips FK needs them)."""
    monkeypatch.setattr(build_db, 'RAW_DIR', tmp_path)
    conn = duckdb.connect(':memory:')
    build_db._create_schema(conn)
    build_db._load_operators(conn)
    return conn


def test_train_and_bus_same_minute_both_survive(tmp_path, monkeypatch, capsys):
    conn = _prepare(tmp_path, monkeypatch)

    intercity = [
        # bus 08:00 Beograd→Novi Sad
        _trip(departure_time='08:00', arrival_time='09:30', price_rsd=600),
        # exact duplicate bus (same pair+minute+type) → deduped away
        _trip(departure_time='08:00', arrival_time='10:00', price_rsd=550),
        # broken rows → dropped by validation, never inserted
        _trip(to_city='Niš', departure_time='25:99'),
        _trip(to_city='Niš', departure_time='07:00', price_rsd=-5),
    ]
    srbvoz = [
        # TRAIN 08:00 on the same pair — same (from,to,dep) as the bus but a
        # different type, so it must NOT be deduped away.
        {'from_city': 'Beograd', 'to_city': 'Novi Sad',
         'departure_time': '08:00', 'arrival_time': '09:45',
         'price_rsd': 400, 'operator': 'Srbija Voz', 'type': 'train'},
    ]
    ic_path = tmp_path / 'intercity_routes.json'
    sv_path = tmp_path / 'srbvoz.json'
    ic_path.write_text(json.dumps(intercity), encoding='utf-8')
    sv_path.write_text(json.dumps(srbvoz), encoding='utf-8')

    build_db._load_intercity(conn, ic_path, sv_path)

    # Exactly 2 trips survive on beograd-novi-sad: the bus and the train.
    rows = conn.execute(
        "SELECT t.departure_time, o.name FROM trips t "
        "JOIN operators o ON o.id = t.operator_id "
        "JOIN routes r ON r.id = t.route_id "
        "WHERE r.slug = 'beograd-novi-sad' ORDER BY o.name").fetchall()
    assert len(rows) == 2, rows
    operators = {r[1] for r in rows}
    assert 'Srbija Voz' in operators        # train kept
    assert all(r[0] == '08:00' for r in rows)

    # The two broken Niš rows created no trips AND no route.
    assert conn.execute(
        "SELECT COUNT(*) FROM routes WHERE slug='beograd-nis'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM trips").fetchone()[0] == 2

    out = capsys.readouterr().out
    assert 'Dropped 2 invalid trips' in out
    assert 'bad_departure_time=1' in out
    assert 'negative_price=1' in out
    assert 'Deduplicated: 1 duplicate trips removed' in out


def test_same_mode_exact_duplicate_is_deduped(tmp_path, monkeypatch):
    """Two identical bus rows (e.g. the same Lasta bus surfaced by bt4 and a
    second feed) collapse to one — the core duplicate-removal still works."""
    conn = _prepare(tmp_path, monkeypatch)
    intercity = [
        _trip(departure_time='06:00', arrival_time='07:30'),
        _trip(departure_time='06:00', arrival_time='07:30'),
    ]
    ic_path = tmp_path / 'intercity_routes.json'
    ic_path.write_text(json.dumps(intercity), encoding='utf-8')
    sv_path = tmp_path / 'srbvoz.json'   # absent → skipped
    build_db._load_intercity(conn, ic_path, sv_path)
    assert conn.execute("SELECT COUNT(*) FROM trips").fetchone()[0] == 1

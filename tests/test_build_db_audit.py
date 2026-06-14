"""Tests for build_db's end-of-build data-quality audit.

Covers the pure slug-collision finder and an integration run of
_audit_data_quality against an in-memory DB seeded with the exact anomaly
classes found in the 2026-06 audit (duplicate line slug, half-coordinate,
stop outside Serbia).
"""
import duckdb

from data.pipelines import build_db
from data.pipelines.build_db import _find_slug_collisions, _audit_data_quality


# ── pure collision finder ───────────────────────────────────────────────────

def test_find_slug_collisions_detects_shared_slug():
    rows = [
        ('beograd', '9Л', 'linija-9l'),
        ('beograd', '9л', 'linija-9l'),   # collides with the above
        ('beograd', '7', 'linija-7'),     # unique
        ('novi-sad', '9л', 'linija-9l'),  # same slug, different city → no collision
    ]
    collisions = _find_slug_collisions(rows)
    assert collisions == {('beograd', 'linija-9l'): ['9Л', '9л']}


def test_find_slug_collisions_empty_when_unique():
    rows = [('beograd', '7', 'linija-7'), ('beograd', '8', 'linija-8')]
    assert _find_slug_collisions(rows) == {}


def test_find_slug_collisions_groups_three_way():
    rows = [('nis', 'a', 's'), ('nis', 'b', 's'), ('nis', 'c', 's')]
    assert _find_slug_collisions(rows) == {('nis', 's'): ['a', 'b', 'c']}


# ── _audit_data_quality integration ─────────────────────────────────────────

def _audit_conn(tmp_path, monkeypatch):
    monkeypatch.setattr(build_db, 'DATA_QUALITY_FILE', tmp_path / 'dq.json')
    conn = duckdb.connect(':memory:')
    build_db._create_schema(conn)
    return conn


def test_audit_flags_dup_line_slug_half_coord_and_foreign_stop(tmp_path, monkeypatch, capsys):
    conn = _audit_conn(tmp_path, monkeypatch)
    # Two distinct numbers that share a slug → URL collision.
    conn.executemany("INSERT INTO city_lines VALUES (?,?,?,?,?,?,?,?)", [
        (1, 'beograd', '9Л', 'A', 'linija-9l', 'bus', '#000', None),
        (2, 'beograd', '9л', 'B', 'linija-9l', 'bus', '#000', None),
    ])
    conn.executemany("INSERT INTO city_stops VALUES (?,?,?,?,?,?,?)", [
        (1, 'nis', 'Normal', 'normal', 43.3, 21.9, None),   # in Serbia
        (2, 'nis', 'Half', 'half', 43.3, None, None),       # half-coordinate
        (3, 'nis', 'München', 'munchen', 48.1, 11.5, None),  # outside Serbia
    ])

    report = _audit_data_quality(conn)

    assert report['dup_line_slugs'] == 1
    assert report['half_coord_stops'] == 1
    assert report['stops_outside_serbia'] == 1
    assert report['trips_blank_time'] == 0

    out = capsys.readouterr().out
    assert "beograd/linija-9l shared by lines ['9Л', '9л']" in out

    # report persisted to the patched path
    assert (tmp_path / 'dq.json').exists()


def test_audit_clean_db_reports_zeroes(tmp_path, monkeypatch):
    conn = _audit_conn(tmp_path, monkeypatch)
    conn.execute("INSERT INTO city_lines VALUES "
                 "(1,'beograd','7','Sedmica','linija-7','bus','#000',NULL)")
    conn.execute("INSERT INTO city_stops VALUES "
                 "(1,'beograd','Trg','trg',44.8,20.4,NULL)")
    report = _audit_data_quality(conn)
    assert report == {'dup_line_slugs': 0, 'half_coord_stops': 0,
                      'stops_outside_serbia': 0, 'trips_blank_time': 0}

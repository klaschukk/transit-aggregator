"""Unit tests for data/pipelines/enrich_stops_coords.py.

No live OSM: Overpass/Nominatim are monkeypatched. Covers the pure geo logic,
the city-aware dispatch (the fix that lets Novi Sad's stops — previously
unreachable behind a Belgrade-only bbox — be backfilled), and a regression
guard for the NameError that made the `enrich` command crash on every run.
"""
import duckdb
import pytest

from data.pipelines import enrich_stops_coords as esc


# ── pure geo helpers ────────────────────────────────────────────────────────

def test_in_bbox_inside_and_outside():
    bbox = (44.6, 20.2, 44.95, 20.7)  # s, w, n, e
    assert esc.in_bbox(44.8, 20.45, bbox)
    assert not esc.in_bbox(45.25, 19.84, bbox)   # Novi Sad point
    assert not esc.in_bbox(44.8, 21.5, bbox)     # too far east


def test_in_belgrade_bbox_delegates():
    assert esc.in_belgrade_bbox(44.8, 20.45)
    assert not esc.in_belgrade_bbox(45.25, 19.84)


def test_bbox_str_order():
    assert esc.bbox_str((44.6, 20.2, 44.95, 20.7)) == '44.6,20.2,44.95,20.7'


def test_region_for_known_and_unknown():
    assert esc.region_for('beograd')[1] == 'Belgrade, Serbia'
    assert esc.region_for('novi-sad')[1] == 'Novi Sad, Serbia'
    assert esc.region_for('paris') is None


def test_clean_name_strips_noise():
    # quote characters are removed, the words are kept
    assert esc.clean_name('Sajam "Glavni"') == 'Sajam Glavni'
    assert esc.clean_name('“Trg”') == 'Trg'          # smart quotes
    assert esc.clean_name('Trg (centar)') == 'Trg'            # parenthetical dropped
    assert esc.clean_name('Bulevar 12') == 'Bulevar'         # trailing number dropped
    assert esc.clean_name('Stop /smer A/ ime') == 'Stop ime'  # /…/ suffix dropped


# ── city-aware fetch dispatch ───────────────────────────────────────────────

def test_fetch_coords_unknown_city_skips_network(monkeypatch):
    """An unknown city must short-circuit to None without hitting OSM."""
    calls = []
    monkeypatch.setattr(esc, 'query_overpass', lambda *a, **k: calls.append('o') or (1, 1))
    monkeypatch.setattr(esc, 'query_nominatim', lambda *a, **k: calls.append('n') or (1, 1))
    assert esc.fetch_coords('Whatever', 'paris') is None
    assert calls == []  # no geocoding attempted for a region we don't know


def test_fetch_coords_uses_the_citys_bbox(monkeypatch):
    """Novi Sad lookups must run against the Novi Sad bbox, not Belgrade."""
    seen = {}

    def fake_overpass(name, bbox=esc.BELGRADE_BBOX):
        seen['bbox'] = bbox
        return (45.255, 19.845)  # inside Novi Sad

    monkeypatch.setattr(esc, 'query_overpass', fake_overpass)
    monkeypatch.setattr(esc, 'time', _NoSleep())
    coords = esc.fetch_coords('Trg Slobode', 'novi-sad')
    assert coords == (45.255, 19.845)
    assert seen['bbox'] == esc.CITY_REGIONS['novi-sad'][0]


def test_fetch_coords_rejects_out_of_bbox_then_falls_through(monkeypatch):
    """An Overpass hit outside the city bbox is discarded; the chain falls
    through to the next source instead of planting a wrong-city coord."""
    monkeypatch.setattr(esc, 'time', _NoSleep())
    # bus_stop query returns a Belgrade point for a Novi Sad stop → rejected
    monkeypatch.setattr(esc, 'query_overpass', lambda *a, **k: (44.81, 20.46))
    monkeypatch.setattr(esc, 'query_overpass_public_transport', lambda *a, **k: None)
    monkeypatch.setattr(esc, 'query_nominatim', lambda *a, **k: (45.25, 19.84))
    coords = esc.fetch_coords('Centar', 'novi-sad')
    assert coords == (45.25, 19.84)  # the in-bbox Nominatim result wins


# ── Nominatim viewbox + bbox filtering ──────────────────────────────────────

class _FakeResp:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _NoSleep:
    """Drop-in for the module's `time` so sleeps are instant in tests."""
    @staticmethod
    def sleep(_):
        pass

    @staticmethod
    def time():
        return 0.0


def test_query_nominatim_builds_viewbox_from_bbox(monkeypatch):
    captured = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        captured['params'] = params
        return _FakeResp([{'lat': '45.25', 'lon': '19.84'}])

    monkeypatch.setattr(esc.requests, 'get', fake_get)
    monkeypatch.setattr(esc, 'time', _NoSleep())
    bbox = esc.CITY_REGIONS['novi-sad'][0]  # (s, w, n, e)
    coords = esc.query_nominatim('Trg', 'Novi Sad, Serbia', bbox)
    assert coords == (45.25, 19.84)
    s, w, n, e = bbox
    # viewbox is west,north,east,south
    assert captured['params']['viewbox'] == f'{w},{n},{e},{s}'
    assert captured['params']['q'] == 'Trg, Novi Sad, Serbia'


def test_query_nominatim_rejects_result_outside_bbox(monkeypatch):
    # Nominatim returns a Belgrade coord for a Novi Sad query → must be dropped.
    monkeypatch.setattr(esc.requests, 'get',
                        lambda *a, **k: _FakeResp([{'lat': '44.80', 'lon': '20.46'}]))
    monkeypatch.setattr(esc, 'time', _NoSleep())
    bbox = esc.CITY_REGIONS['novi-sad'][0]
    assert esc.query_nominatim('Trg', 'Novi Sad, Serbia', bbox) is None


# ── enrich() integration — NameError regression + city dispatch ─────────────

def _seed_conn():
    conn = duckdb.connect(':memory:')
    conn.execute("""
        CREATE TABLE city_stops (
            id INTEGER, city VARCHAR, name VARCHAR, slug VARCHAR,
            lat DOUBLE, lon DOUBLE, code VARCHAR)
    """)
    conn.executemany("INSERT INTO city_stops VALUES (?,?,?,?,?,?,?)", [
        (1, 'beograd', 'Sajam', 'sajam', None, None, None),
        (2, 'novi-sad', 'Trg Slobode', 'trg-slobode', None, None, None),
        (3, 'paris', 'Eiffel', 'eiffel', None, None, None),   # no region → skip
        (4, 'beograd', 'Has Coords', 'has-coords', 44.8, 20.4, None),
    ])
    return conn


def test_enrich_runs_without_nameerror_and_is_city_aware(monkeypatch, tmp_path):
    """The headline regression: enrich() used to reference undefined
    total_stops/with_coords and crash with NameError before touching a single
    stop. It must now run, update resolvable stops keyed on their city, and
    skip cities with no region."""
    monkeypatch.setattr(esc, 'PROGRESS_FILE', tmp_path / 'progress.json')
    monkeypatch.setattr(esc, 'time', _NoSleep())

    seen_cities = []

    def fake_fetch(name, city='beograd'):
        seen_cities.append(city)
        return {'beograd': (44.81, 20.46), 'novi-sad': (45.25, 19.84)}.get(city)

    monkeypatch.setattr(esc, 'fetch_coords', fake_fetch)

    conn = _seed_conn()
    esc.enrich(conn)  # must NOT raise

    # paris (unknown region) never reached fetch_coords; the two known cities did
    assert set(seen_cities) == {'beograd', 'novi-sad'}
    rows = dict((r[0], (r[1], r[2])) for r in
                conn.execute("SELECT id, lat, lon FROM city_stops").fetchall())
    assert rows[1] == (44.81, 20.46)   # Belgrade stop filled
    assert rows[2] == (45.25, 19.84)   # Novi Sad stop filled (was impossible before)
    assert rows[3] == (None, None)     # paris left untouched (no region)
    assert rows[4] == (44.8, 20.4)     # already-good stop unchanged


def test_enrich_no_missing_stops_is_noop(monkeypatch, tmp_path):
    monkeypatch.setattr(esc, 'PROGRESS_FILE', tmp_path / 'p.json')
    monkeypatch.setattr(esc, 'time', _NoSleep())
    monkeypatch.setattr(esc, 'fetch_coords', lambda *a, **k: pytest.fail('should not fetch'))
    conn = duckdb.connect(':memory:')
    conn.execute("CREATE TABLE city_stops (id INTEGER, city VARCHAR, name VARCHAR, "
                 "slug VARCHAR, lat DOUBLE, lon DOUBLE, code VARCHAR)")
    conn.execute("INSERT INTO city_stops VALUES (1,'beograd','X','x',44.8,20.4,NULL)")
    esc.enrich(conn)  # all have coords → returns early, no fetch

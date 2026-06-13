"""Data quality tests — verify DB has sufficient and valid data.

These assert production-scale thresholds (hundreds of routes, thousands of
stops), so they only make sense against the FULL DuckDB. Run against the tiny
tests/seed.duckdb (a few rows, used by CI) every threshold would fail — which
is why CI used to ``--ignore`` this whole file. Instead of hiding the file, the
autouse guard below SKIPS it when the DB is clearly a seed: the tests stay
collected and visible, run for real whenever a full DB is present (local dev,
the prod box), and quietly skip on the seed.
"""

import pytest

# Below this many city_stops the DB is a seed/fixture, not the real dataset.
_SEED_STOPS_CEILING = 500


@pytest.fixture(autouse=True)
def _require_full_db(db):
    """Skip every data-quality test when the DB looks like a seed fixture."""
    row = db.one("SELECT COUNT(*) AS c FROM city_stops")
    count = row['c'] if row else 0
    if count < _SEED_STOPS_CEILING:
        pytest.skip(
            f"seed DB ({count} stops < {_SEED_STOPS_CEILING}) "
            "— data-quality thresholds need the full dataset"
        )


def test_routes_count(db):
    row = db.one("SELECT COUNT(*) as c FROM routes WHERE type = 'intercity'")
    assert row['c'] >= 100, f"Only {row['c']} routes"


def test_trips_count(db):
    row = db.one("SELECT COUNT(*) as c FROM trips")
    assert row['c'] >= 1000, f"Only {row['c']} trips"


def test_operators_count(db):
    row = db.one("SELECT COUNT(*) as c FROM operators")
    assert row['c'] >= 10, f"Only {row['c']} operators"


def test_city_lines_count(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines")
    assert row['c'] >= 500, f"Only {row['c']} city lines"


def test_city_stops_count(db):
    row = db.one("SELECT COUNT(*) as c FROM city_stops")
    assert row['c'] >= 2000, f"Only {row['c']} city stops"


def test_city_line_stops_count(db):
    row = db.one("SELECT COUNT(*) as c FROM city_line_stops")
    assert row['c'] >= 10000, f"Only {row['c']} line-stop links"


def test_stations_count(db):
    row = db.one("SELECT COUNT(*) as c FROM stations")
    assert row['c'] >= 5, f"Only {row['c']} stations"


# ── Field completeness ──


def test_routes_have_slugs(db):
    row = db.one("SELECT COUNT(*) as c FROM routes WHERE slug IS NULL OR slug = ''")
    assert row['c'] == 0, f"{row['c']} routes missing slug"


def test_routes_have_cities(db):
    row = db.one("SELECT COUNT(*) as c FROM routes WHERE from_city IS NULL OR to_city IS NULL")
    assert row['c'] == 0


def test_routes_have_city_slugs(db):
    row = db.one("SELECT COUNT(*) as c FROM routes WHERE from_city_slug IS NULL OR to_city_slug IS NULL")
    assert row['c'] == 0


def test_trips_have_departure_time(db):
    row = db.one("SELECT COUNT(*) as c FROM trips WHERE departure_time IS NULL OR departure_time = ''")
    assert row['c'] == 0


def test_trips_have_route_id(db):
    row = db.one("SELECT COUNT(*) as c FROM trips WHERE route_id IS NULL")
    assert row['c'] == 0


def test_city_lines_have_number(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines WHERE number IS NULL OR number = ''")
    assert row['c'] == 0


def test_city_lines_have_name(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines WHERE name IS NULL OR name = ''")
    assert row['c'] == 0


def test_city_lines_have_slug(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines WHERE slug IS NULL OR slug = ''")
    assert row['c'] == 0


def test_city_stops_have_name(db):
    row = db.one("SELECT COUNT(*) as c FROM city_stops WHERE name IS NULL OR name = ''")
    assert row['c'] == 0


def test_city_stops_have_slug(db):
    row = db.one("SELECT COUNT(*) as c FROM city_stops WHERE slug IS NULL OR slug = ''")
    assert row['c'] == 0


# ── GPS coverage ──


def test_gps_coverage_overall(db):
    total = db.one("SELECT COUNT(*) as c FROM city_stops")['c']
    with_gps = db.one("SELECT COUNT(*) as c FROM city_stops WHERE lat IS NOT NULL")['c']
    pct = 100 * with_gps / total if total else 0
    assert pct >= 80, f"GPS coverage {pct:.0f}% < 80%"


def test_gps_coverage_beograd(db):
    total = db.one("SELECT COUNT(*) as c FROM city_stops WHERE city = 'beograd'")['c']
    with_gps = db.one("SELECT COUNT(*) as c FROM city_stops WHERE city = 'beograd' AND lat IS NOT NULL")['c']
    pct = 100 * with_gps / total if total else 0
    assert pct >= 90, f"Beograd GPS {pct:.0f}%"


def test_novi_sad_stops_exist(db):
    total = db.one("SELECT COUNT(*) as c FROM city_stops WHERE city = 'novi-sad'")['c']
    assert total >= 30, f"Only {total} Novi Sad stops"


def test_nis_stops_exist(db):
    total = db.one("SELECT COUNT(*) as c FROM city_stops WHERE city = 'nis'")['c']
    assert total >= 50, f"Only {total} Nis stops"


# ── Referential integrity ──


def test_trips_reference_valid_routes(db):
    row = db.one("""
        SELECT COUNT(*) as c FROM trips t
        LEFT JOIN routes r ON r.id = t.route_id
        WHERE r.id IS NULL
    """)
    assert row['c'] == 0, f"{row['c']} orphan trips"


def test_line_stops_reference_valid_lines(db):
    row = db.one("""
        SELECT COUNT(*) as c FROM city_line_stops cls
        LEFT JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cl.id IS NULL
    """)
    assert row['c'] == 0, f"{row['c']} orphan line-stop links"


def test_line_stops_reference_valid_stops(db):
    row = db.one("""
        SELECT COUNT(*) as c FROM city_line_stops cls
        LEFT JOIN city_stops cs ON cs.id = cls.stop_id
        WHERE cs.id IS NULL
    """)
    assert row['c'] == 0, f"{row['c']} orphan line-stop links"


# ── Per-city line counts ──


def test_beograd_lines(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines WHERE city = 'beograd'")
    assert row['c'] >= 400, f"Only {row['c']} Beograd lines"


def test_novi_sad_lines(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines WHERE city = 'novi-sad'")
    assert row['c'] >= 10, f"Only {row['c']} Novi Sad lines"


def test_nis_lines(db):
    row = db.one("SELECT COUNT(*) as c FROM city_lines WHERE city = 'nis'")
    assert row['c'] >= 10, f"Only {row['c']} Nis lines"


# ── No duplicate slugs ──


def test_no_duplicate_route_slugs(db):
    rows = db.q("SELECT slug, COUNT(*) as c FROM routes GROUP BY slug HAVING COUNT(*) > 1")
    assert len(rows) == 0, f"Duplicate route slugs: {[r['slug'] for r in rows]}"


def test_no_duplicate_city_line_slugs(db):
    rows = db.q("""
        SELECT city, slug, COUNT(*) as c FROM city_lines
        GROUP BY city, slug HAVING COUNT(*) > 1
    """)
    # Some duplicates are expected (direction variants sharing a slug)
    assert len(rows) <= 20, f"Too many duplicate line slugs ({len(rows)}): {[(r['city'], r['slug']) for r in rows[:5]]}"

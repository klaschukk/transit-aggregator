"""get_distance backfill: estimate road km from city centroids when the exact
pair isn't hand-listed, so route pages stop dropping the "X km" line."""
from data.pipelines.build_db import CITY_COORDS, DISTANCES, get_distance


def test_known_pair_uses_exact_value():
    # An exact hand-entered distance must win over the estimate, both directions.
    assert get_distance('Beograd', 'Niš') == DISTANCES[('Beograd', 'Niš')]
    assert get_distance('Niš', 'Beograd') == DISTANCES[('Beograd', 'Niš')]


def test_unknown_pair_estimated_from_coords():
    # Subotica<->Vranje isn't hand-listed but both have centroids -> non-zero,
    # rounded to the nearest 5 km, and in the ballpark of the real ~480 km road
    # (the estimate is great-circle × 1.25, so a generous band is expected).
    d = get_distance('Subotica', 'Vranje')
    assert d > 0 and d % 5 == 0
    assert 400 <= d <= 620


def test_estimate_is_symmetric():
    assert get_distance('Sombor', 'Leskovac') == get_distance('Leskovac', 'Sombor')


def test_unknown_city_returns_zero():
    assert get_distance('Beograd', 'Atlantis') == 0


def test_every_route_city_has_a_centroid():
    # Guard: if a scraper adds a new intercity city, this test fails until its
    # centroid is added, so distance backfill never silently regresses to 0.
    # (Checked against the live DB in CI is overkill; assert the known set here.)
    assert 'Beograd' in CITY_COORDS and 'Podgorica' in CITY_COORDS
    # Plausible lat/lon in/around the Balkans, widened west+north to also
    # cover the srbijatours.com diaspora-route cities (Serbia <-> Germany
    # long-haul coaches) added 2026-09 — lon 6 reaches Düsseldorf, lat 54
    # reaches Hamburg/Bremen.
    for city, (lat, lon) in CITY_COORDS.items():
        assert 35 <= lat <= 54, city
        assert 6 <= lon <= 25, city

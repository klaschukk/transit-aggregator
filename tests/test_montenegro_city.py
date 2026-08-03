"""Montenegro city transport (Podgorica / Herceg Novi / Budva) behaves like the
Serbian cities: hub + line + stop pages render, index, and are discoverable.

Backed by the seed fixture city `budva` (1 line, 2 stops). City presence is
checked at runtime, so the test holds on the CI seed and on the full DB whether
or not the nightly rebuild has ingested Montenegro yet.
"""
import re

import pytest


def _robots(client, url):
    m = re.search(r'name="robots" content="([^"]+)"', client.get(url).data.decode())
    return m.group(1) if m else 'index'


def _has_budva(db):
    return bool(db.one("SELECT 1 FROM city_lines WHERE city='budva' LIMIT 1"))


def test_montenegro_hub_renders_and_indexes(client, db):
    if not _has_budva(db):
        pytest.skip("budva not in this DB (pre-rebuild)")
    r = client.get('/gradski/budva/')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'Budva' in html
    assert 'noindex' not in _robots(client, '/gradski/budva/')


def test_montenegro_line_and_stop_pages(client, db):
    if not _has_budva(db):
        pytest.skip("budva not in this DB (pre-rebuild)")
    assert client.get('/gradski/budva/linija/linija-1/').status_code == 200
    assert client.get('/gradski/budva/stajaliste/budva-centar/').status_code == 200


def test_montenegro_hyphenated_city_label_is_spaced(client):
    # 'herceg-novi' must display as "Herceg Novi", never "Herceg-Novi".
    # The hub 404s pre-rebuild, but the label rule is what we guard here.
    from app.routes.city import CITY_LABELS
    assert CITY_LABELS['herceg-novi'] == 'Herceg Novi'


def test_montenegro_hub_in_sitemap_core(client):
    # Hardcoded hub entries — present regardless of DB state so Google can
    # discover the city hubs as soon as data lands.
    xml = client.get('/sitemap-core.xml').data.decode()
    for city in ('podgorica', 'herceg-novi', 'budva'):
        assert f'/gradski/{city}/' in xml


def test_montenegro_line_in_sitemap_when_present(client, db):
    if not _has_budva(db):
        pytest.skip("budva not in this DB (pre-rebuild)")
    assert '/gradski/budva/' in client.get('/sitemap-lines.xml').data.decode()


def test_city_map_frames_its_own_city(client, db):
    """Each city map must open on that city, not fall back to Belgrade.

    The bounds used to be a hardcoded per-city coordinate list covering only
    the four Serbian cities, so every Montenegro city hit the Belgrade default
    and opened its map ~500 km away. Bounds now come from the extent of the
    city's own stops.
    """
    import re

    rows = db.q("""
        SELECT city,
               quantile_cont(lat, 0.02) AS min_lat,
               quantile_cont(lat, 0.98) AS max_lat
        FROM city_stops WHERE lat IS NOT NULL GROUP BY city
    """)
    checked = 0
    for row in rows:
        html = client.get(f"/gradski/{row['city']}/").data.decode()
        m = re.search(r'mapOpts\.bounds = \[\[([-\d.]+), ([-\d.]+)\],\s*'
                      r'\[([-\d.]+), ([-\d.]+)\]\]', html)
        if not m:
            continue
        south, north = float(m.group(2)), float(m.group(4))
        assert south <= north, f"{row['city']}: inverted bounds"
        # Must bracket the city's own stop latitudes, not another city's.
        assert south <= row['max_lat'] and north >= row['min_lat'], (
            f"{row['city']}: map bounds {south}..{north} miss its stops "
            f"{row['min_lat']}..{row['max_lat']}"
        )
        checked += 1
    if not checked:
        pytest.skip("no city rendered map bounds in this DB")


def test_city_map_bounds_reject_outliers(client, db):
    """Bounds must be percentile-based, not raw MIN/MAX.

    A few mis-geocoded stops drag the raw extent far outside the city: Niš
    spans 329 km by MIN/MAX (one stop sits north of Novi Sad) but 6 km by
    percentile. Framing on the raw box opens the map at region zoom.
    """
    import re

    row = db.one("SELECT COUNT(*) AS c FROM city_stops WHERE city = 'nis' AND lat IS NOT NULL")
    if not row or row['c'] < 20:
        pytest.skip("seed DB lacks Niš stops")
    html = client.get("/gradski/nis/").data.decode()
    m = re.search(r'mapOpts\.bounds = \[\[([-\d.]+), ([-\d.]+)\],\s*'
                  r'\[([-\d.]+), ([-\d.]+)\]\]', html)
    if not m:
        pytest.skip("no bounds rendered")
    span_km = (float(m.group(4)) - float(m.group(2))) * 111
    assert span_km < 60, f"Niš map spans {span_km:.0f} km — outliers not filtered"

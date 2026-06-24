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

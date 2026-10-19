"""Foreign-language titles/H1 use names searchers type (app/city_names.py)."""
import re

from app.city_names import NAMES, city_name
from app.db import query


def _page(client, path):
    h = client.get(path).get_data(as_text=True)
    return (re.search(r'<title>([^<]*)', h).group(1),
            re.search(r'<h1[^>]*>\s*([^<]*)', h).group(1).strip())


def test_lookup():
    assert city_name('Beograd', 'beograd', 'en') == 'Belgrade'
    assert city_name('Budva', 'budva', 'en') == 'Budva'          # same in English
    assert city_name('Budva', 'budva', 'ru') == 'Будва'
    assert city_name('Solun', 'solun', 'bg') == 'Солун'
    assert city_name('Beograd', 'beograd', 'sr') == 'Beograd'
    assert city_name('Nepoznato', 'nepoznato', 'ru') == 'Nepoznato'


def test_table_rows_complete():
    for slug, (en, ru, bg) in NAMES.items():
        assert ru and bg, slug
        assert not re.search(r'[A-Za-z]', ru + bg), slug


def test_route_cities_covered(app):
    with app.app_context():
        rows = query("SELECT DISTINCT from_city_slug AS s FROM routes WHERE type='intercity' "
                     "UNION SELECT DISTINCT to_city_slug FROM routes WHERE type='intercity'")
    slugs = {r['s'] for r in rows if r['s']}
    missing = slugs - set(NAMES)
    assert len(missing) <= 0.05 * len(slugs), sorted(missing)


def test_foreign_titles_and_h1(client):
    t, h1 = _page(client, '/en/rute/budva-kotor/')
    assert t.startswith('Budva to Kotor bus:') and h1 == 'Budva → Kotor'
    t, h1 = _page(client, '/ru/rute/budva-kotor/')
    assert t.startswith('Автобус Будва — Котор:') and h1 == 'Будва → Котор'
    t, _ = _page(client, '/en/rute/beograd-novi-sad/')
    assert t.startswith('Belgrade to Novi Sad bus')
    t, h1 = _page(client, '/en/voznja/kotor-do-dubrovnik/')
    assert t.startswith('Kotor to Dubrovnik') and h1 == 'Kotor → Dubrovnik'


def test_serbian_titles_unchanged(client):
    t, h1 = _page(client, '/rute/beograd-novi-sad/')
    assert t.startswith('Beograd → Novi Sad: ') and 'polazaka dnevno' in t and h1 == 'Beograd → Novi Sad'
    t, _ = _page(client, '/voznja/beograd-do-budva/')
    assert t.startswith('Beograd → Budva ')


def test_foreign_titles_fit():
    from app import create_app
    c = create_app('development').test_client()
    for path in ('/en/rute/budva-kotor/', '/ru/rute/budva-kotor/', '/bg/rute/podgorica-budva/',
                 '/ru/rute/podgorica-sarajevo/', '/en/rute/mostar-budva/'):
        t, _ = _page(c, path)
        assert len(t) <= 62, (path, t)

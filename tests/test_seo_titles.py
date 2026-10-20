"""Serbian /rute/ title test (app/seo_titles.py)."""
import re

from app.seo_titles import route_title_variant, sr_departures_word


def _title(client, path):
    return re.search(r'<title>([^<]*)', client.get(path).get_data(as_text=True)).group(1)


def test_assignment_is_stable_and_euro_always_in_test():
    assert route_title_variant('niksic-podgorica', 'niksic', 'podgorica') == 'rv'
    assert route_title_variant('budva-kotor', 'budva', 'kotor') == 'rv'
    a = route_title_variant('beograd-kragujevac', 'beograd', 'kragujevac')
    assert a == route_title_variant('beograd-kragujevac', 'beograd', 'kragujevac')
    assert {route_title_variant(f'x-{i}', 'x', str(i)) for i in range(50)} == {'rv', 'control'}


def test_serbian_plural():
    assert [sr_departures_word(n) for n in (1, 2, 4, 5, 11, 12, 21, 22, 25)] == [
        'polazak', 'polaska', 'polaska', 'polazaka', 'polazaka', 'polazaka', 'polazak', 'polaska', 'polazaka']


def test_rv_titles(client):
    t = _title(client, '/rute/niksic-podgorica/')
    assert t.startswith('Red vožnje Nikšić – Podgorica ') and len(t) <= 62 and '€' in t


def test_control_titles_unchanged(client):
    slug = 'beograd-kragujevac'
    if route_title_variant(slug, 'beograd', 'kragujevac') == 'control':
        assert _title(client, f'/rute/{slug}/').startswith('Beograd → Kragujevac: ')


def test_variant_only_on_serbian(client):
    assert not _title(client, '/en/rute/niksic-podgorica/').startswith('Red vožnje')

"""Titles/meta of routes outside Serbia quote euro (app/snippet_price.py)."""
import re

from app.snippet_price import is_euro_pair, snippet_price


def _title(client, path):
    return re.search(r'<title>([^<]*)', client.get(path).get_data(as_text=True)).group(1)


def test_euro_only_when_both_ends_abroad(app):
    with app.app_context():
        assert is_euro_pair('budva', 'kotor') and is_euro_pair('mostar', 'budva')
        assert not is_euro_pair('beograd', 'budva') and not is_euro_pair('kotor', '')
        assert snippet_price(409, 'budva', 'kotor') == '3.5 €'
        assert snippet_price(3393, 'kotor', 'dubrovnik') == '29 €'
        assert snippet_price(1170, 'herceg-novi', 'podgorica') == '10 €'
        assert snippet_price(500, 'beograd', 'novi-sad') == '500 RSD'


def test_route_titles(client):
    t = _title(client, '/en/rute/budva-kotor/')
    assert re.search(r'from [\d.]+ €', t) and 'RSD' not in t
    assert 'RSD' in _title(client, '/rute/beograd-novi-sad/')


def test_pair_title_translated_and_in_euro(client):
    t = _title(client, '/en/voznja/kotor-do-dubrovnik/')
    assert ' od ' not in t and 'from' in t and '€' in t


def test_single_departure_is_singular(client):
    html = client.get('/en/rute/mostar-budva/').get_data(as_text=True)
    assert '1 departures' not in html.split('</head>')[0]


def test_euro_routes_default_body_prices_to_euro(client):
    euro = client.get('/en/rute/budva-kotor/').get_data(as_text=True)
    rsd = client.get('/en/rute/beograd-novi-sad/').get_data(as_text=True)
    assert "else if (true)" in euro.split('</head>')[0]
    assert "else if (false)" in rsd.split("</head>")[0]


def test_currency_cookie_only_on_explicit_pick():
    js = open('app/static/js/ui-behavior.js', encoding='utf-8').read()
    assert 'setCcy(initial);' in js and 'setCcy(b.dataset.ccy, true);' in js
    assert 'if (persist)' in js

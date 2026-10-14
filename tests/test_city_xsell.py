"""Intercity cross-sell on /gradski/ pages (app/city_xsell.py, _city_xsell.html)."""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from flask import render_template_string

from app import city_xsell, create_app

BG = ZoneInfo('Europe/Belgrade')
MONDAY_10 = datetime(2026, 10, 12, 10, 0, tzinfo=BG)
MONDAY_2359 = datetime(2026, 10, 12, 23, 59, tzinfo=BG)


@pytest.fixture
def pinned(monkeypatch):
    def _pin(now, clicks=None):
        monkeypatch.setattr(city_xsell, '_now_belgrade', lambda: now)
        monkeypatch.setattr(city_xsell, '_route_clicks', lambda: clicks or {})
    return _pin


def test_routes_from_city_with_next_departure(app, pinned):
    pinned(MONDAY_10)
    with app.app_context():
        rows = city_xsell.intercity_from_city('beograd')
    assert 0 < len(rows) <= 3
    for r in rows:
        assert r['slug'].startswith('beograd-') and r['from_slug'] == 'beograd'
        assert r['trips_today'] > 0
        if r['next_time']:
            assert r['next_time'] > '10:00'
            assert r['next_in_min'] == int(r['next_time'][:2]) * 60 + int(r['next_time'][3:]) - 600
        assert r['date'] == '2026-10-12'


def test_ranking_follows_buy_clicks(app, pinned):
    with app.app_context():
        pinned(MONDAY_10, {'beograd-novi-sad': 50})
        first = city_xsell.intercity_from_city('beograd')[0]['slug']
        pinned(MONDAY_10, {'beograd-sabac': 50})
        other = city_xsell.intercity_from_city('beograd')[0]['slug']
    assert first == 'beograd-novi-sad'
    assert other == 'beograd-sabac'


def test_late_night_keeps_routes_without_inventing_times(app, pinned):
    pinned(MONDAY_2359)
    with app.app_context():
        rows = city_xsell.intercity_from_city('beograd')
    assert rows
    assert all(r['next_time'] is None and r['bt4_line_id'] is None for r in rows)


def test_unknown_city_is_empty(app, pinned):
    pinned(MONDAY_10)
    with app.app_context():
        assert city_xsell.intercity_from_city('atlantida') == []


@pytest.mark.parametrize('path', [
    '/gradski/beograd/',
    '/gradski/beograd/linija/linija-a1/',
    '/gradski/beograd/stajaliste/bas/',
])
def test_block_on_city_pages(client, pinned, path):
    pinned(MONDAY_10)
    html = client.get(path).get_data(as_text=True)
    assert 'class="xsell fade-in"' in html
    assert 'class="xsell__link js-xsell" href="/rute/beograd-' in html


@pytest.mark.parametrize('slug,hub', [
    ('bas', True), ('beogradska-autobuska-stanica', True), ('novi-sad-autobuska-stanica', True),
    ('petrovaradin-zeleznicka-stanica', True), ('zeleznicka-stanica-dunav', True), ('beograd-centar', True),
    ('tosin-bunar', False), ('basta', False), ('veterinarska-stanica', False), ('umka-centar', False),
])
def test_hub_stop_detection(slug, hub):
    assert city_xsell.is_hub_stop(slug) is hub


def test_hub_stop_puts_block_above_lines(client, pinned):
    pinned(MONDAY_10)
    hub = client.get('/gradski/beograd/stajaliste/bas/').get_data(as_text=True)
    plain = client.get('/gradski/beograd/stajaliste/tosin-bunar/').get_data(as_text=True)
    assert hub.index('class="xsell fade-in"') < hub.index('id="arrivalsList"')
    assert plain.index('class="xsell fade-in"') > plain.index('id="arrivalsList"')


def test_partial_buy_button_only_for_exact_departure(app):
    rows = [
        {'slug': 'beograd-novi-sad', 'to_city': 'Novi Sad', 'to_slug': 'novi-sad', 'from_slug': 'beograd',
         'date': '2099-01-05', 'next_time': '10:30', 'next_in_min': 30, 'price_min': 500, 'bt4_line_id': 5123},
        {'slug': 'beograd-sabac', 'to_city': 'Šabac', 'to_slug': 'sabac', 'from_slug': 'beograd',
         'date': '2099-01-05', 'next_time': '11:00', 'next_in_min': 60, 'price_min': None, 'bt4_line_id': None},
    ]
    with app.test_request_context('/gradski/beograd/'):
        html = render_template_string("{% include '_partials/_city_xsell.html' %}",
                                      xsell=rows, city_label='Beograd')
    assert html.count('class="xsell__buy"') == 1
    assert 'data-surface="city_xsell"' in html and 'data-partner="busticket4"' in html
    assert 'lineId=5123' in html and 'departureDate=05-01-2099' in html
    assert 'href="/rute/beograd-sabac/"' in html
    assert '500 RSD' in html


def test_partial_renders_nothing_without_routes(app):
    with app.test_request_context('/'):
        html = render_template_string("{% include '_partials/_city_xsell.html' %}", xsell=[], city_label='X')
    assert 'xsell' not in html


@pytest.fixture
def ana_client(tmp_path):
    """Own app with a throwaway analytics DB — never the live analytics.sqlite."""
    application = create_app('development')
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False, RATELIMIT_ENABLED=False,
                              ANALYTICS_DB_PATH=str(tmp_path / 'analytics.sqlite'), IP_HASH_SALT='t')
    from app import analytics_db
    with application.app_context():
        analytics_db.init_schema()
    return application


@pytest.mark.parametrize('surface', ['city_xsell', 'city_xsell_route'])
def test_new_surfaces_are_allowlisted(ana_client, surface):
    r = ana_client.test_client().post('/api/ba-click', json={
        'route_slug': 'beograd-novi-sad', 'surface': surface, 'partner': 'busticket4'})
    assert r.status_code == 204
    with ana_client.app_context():
        from app import analytics_db
        rows = analytics_db.query("SELECT surface FROM ba_clicks")
    assert [x['surface'] for x in rows] == [surface]


def test_tracker_wires_xsell():
    js = open('app/static/js/analytics-tracker.js', encoding='utf-8').read()
    assert '.xsell__buy' in js and "'city_xsell_route'" in js and '.js-xsell' in js

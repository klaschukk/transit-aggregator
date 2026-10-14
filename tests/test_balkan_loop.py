"""Balkan Loop planner (/balkan-loop/): itineraries come only from direct legs
that exist, the page stays up on bad input, and partner offers are dormant
until a link is configured."""
import pytest

from app import planner


def _leg(slug, duration=120, price=1170, trips=4):
    return {'slug': slug, 'trips': trips, 'duration_min': duration, 'price_rsd': price,
            'first_dep': '07:00', 'last_dep': '18:30'}


def _chain(*slugs, **kw):
    """Two-way legs along a chain of stops."""
    legs = {}
    for a, b in zip(slugs, slugs[1:]):
        legs[(a, b)] = _leg(f'{a}-{b}', **kw)
        legs[(b, a)] = _leg(f'{b}-{a}', **kw)
    return legs


LEGS = _chain('dubrovnik', 'kotor', 'budva', 'podgorica', 'tirana', 'ohrid')


def test_plan_uses_only_existing_legs():
    p = planner.plan('dubrovnik', 'tirana', 10, LEGS, 'en')
    assert [s['slug'] for s in p['stops']] == ['dubrovnik', 'kotor', 'budva', 'podgorica', 'tirana']
    assert all((leg['from'], leg['to']) in LEGS for leg in p['legs'])
    assert len(p['legs']) == len(p['stops']) - 1


def test_nights_add_up_to_the_requested_days():
    for days in (8, 10, 14, 21):
        p = planner.plan('dubrovnik', 'tirana', days, LEGS, 'en')
        assert sum(s['nights'] for s in p['stops']) + p['spare_days'] == days
        assert p['stops'][0]['day_from'] == 1
        for prev, nxt in zip(p['stops'], p['stops'][1:]):
            assert prev['day_to'] == nxt['day_from']


def test_no_plan_when_days_cannot_cover_the_minimum_stays():
    # Dubrovnik (2) + Tirana (2) alone fill 4 days and there is no direct leg.
    assert planner.plan('dubrovnik', 'tirana', 4, LEGS, 'en') is None


def test_no_plan_without_a_connection():
    assert planner.plan('dubrovnik', 'sarajevo', 10, LEGS, 'en') is None
    assert planner.plan('dubrovnik', 'nowhere', 10, LEGS, 'en') is None


def test_loop_returns_to_start():
    legs = dict(LEGS)
    legs[('budva', 'dubrovnik')] = _leg('budva-dubrovnik')
    p = planner.plan('dubrovnik', 'dubrovnik', 9, legs, 'en')
    assert p['loop'] and p['legs'][-1]['to'] == 'dubrovnik'
    assert len(p['legs']) == len(p['stops'])
    assert [s['slug'] for s in p['stops']].count('dubrovnik') == 1


def test_overlong_leg_is_not_planned():
    legs = _chain('beograd', 'kotor', duration=planner.MAX_LEG_MIN + 60)
    assert planner.plan('beograd', 'kotor', 10, legs, 'en') is None


def test_unknown_fare_is_not_summed_as_a_total():
    legs = dict(LEGS)
    legs[('kotor', 'budva')] = _leg('kotor-budva', price=None)
    p = planner.plan('dubrovnik', 'tirana', 10, legs, 'en')
    assert p['bus_eur_partial'] is True
    assert next(leg for leg in p['legs'] if leg['from'] == 'kotor')['price_eur'] is None


def test_localised_stop_names():
    assert planner.stop_name('beograd', 'en') == 'Belgrade'
    assert planner.stop_name('skadar', 'en') == 'Shkodër'
    assert planner.stop_name('beograd', 'sr') == 'Beograd'


@pytest.fixture()
def loop_legs(monkeypatch):
    monkeypatch.setattr(planner, 'load_legs', lambda: LEGS)


@pytest.mark.parametrize('prefix', ['', '/en', '/ru', '/bg'])
def test_page_renders_in_every_language(client, loop_legs, prefix):
    r = client.get(f'{prefix}/balkan-loop/')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'name="from"' in html and 'name="days"' in html
    assert f'{prefix}/rute/dubrovnik-kotor/' in html
    assert 'planner.' not in html  # no untranslated key leaked


def test_page_without_matching_data_says_so(client, monkeypatch):
    # No loop corridors in the DB (e.g. the CI seed): the form still renders.
    monkeypatch.setattr(planner, 'load_legs', lambda: {})
    r = client.get('/en/balkan-loop/')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'No chain of direct buses' in html and 'loop-steps' not in html


@pytest.mark.parametrize('qs', ['?from=zzz&to=<script>&days=abc', '?days=9999', '?days=-3',
                                '?from=tirana&to=tirana&days=4'])
def test_bad_input_never_errors(client, loop_legs, qs):
    r = client.get('/en/balkan-loop/' + qs)
    assert r.status_code == 200
    assert '<script>&' not in r.data.decode()


def test_query_variants_share_one_canonical(client, loop_legs):
    html = client.get('/en/balkan-loop/?from=kotor&to=tirana&days=8').data.decode()
    assert 'rel="canonical" href="' in html
    canonical = html.split('rel="canonical" href="')[1].split('"')[0]
    assert canonical.endswith('/en/balkan-loop/')


def test_offers_are_dormant_by_default(client, loop_legs):
    html = client.get('/en/balkan-loop/').data.decode()
    assert 'loop-offer__btn' not in html


def test_configured_offers_render_as_sponsored_links(app, client, loop_legs):
    cfg = {'AFF_STAY_URL': 'https://example.com/stay?q={city}', 'AFF_STAY_NAME': 'Partner',
           'AFF_ESIM_URL': 'https://example.com/esim', 'AFF_TOURS_URL': 'javascript:alert(1)'}
    old = {k: app.config.get(k) for k in cfg}
    app.config.update(cfg)
    try:
        html = client.get('/en/balkan-loop/').data.decode()
    finally:
        app.config.update(old)
    assert 'https://example.com/stay?q=Dubrovnik' in html
    assert 'data-partner="stay"' in html and 'data-partner="esim"' in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert 'javascript:' not in html and 'data-partner="tours"' not in html
    assert 'Sponsored links' in html


def test_in_sitemap_and_footer(client):
    assert '/balkan-loop/' in client.get('/sitemap-core.xml').data.decode()
    assert '/en/balkan-loop/' in client.get('/en/').data.decode()


def test_planner_partners_are_accepted_by_click_log(client):
    r = client.post('/api/ba-click', json={'route_slug': 'kotor', 'surface': 'planner', 'partner': 'stay'})
    assert r.status_code == 204

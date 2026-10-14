"""Balkan Loop planner (/balkan-loop/): itineraries come only from direct legs
that exist, the page stays up on bad input, and partner offers are dormant
until a link is configured."""
import re

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


def test_route_does_not_double_back():
    # Budva is past Kotor on the way from Dubrovnik: a plan ending in Kotor must
    # not overshoot to Budva and come back.
    legs = _chain('dubrovnik', 'herceg-novi', 'kotor', 'budva')
    legs.update(_chain('dubrovnik', 'budva'))
    legs.update(_chain('dubrovnik', 'kotor'))
    p = planner.plan('dubrovnik', 'kotor', 6, legs, 'en')
    slugs = [s['slug'] for s in p['stops']]
    assert slugs[0] == 'dubrovnik' and slugs[-1] == 'kotor' and 'budva' not in slugs


def test_preset_slugs_round_trip():
    for slug, (a, b, n) in planner.PRESET_BY_SLUG.items():
        assert planner.preset_slug(a, b, n) == slug
        assert a in planner.STOPS and b in planner.STOPS
        assert planner.MIN_DAYS <= n <= planner.MAX_DAYS


@pytest.fixture()
def loop_legs(monkeypatch):
    monkeypatch.setattr(planner, 'load_legs', lambda: LEGS)


PRESET = '/balkan-loop/dubrovnik-tirana-10-days/'


def _head(html, pattern):
    import re
    m = re.search(pattern, html, re.S)
    return m.group(1) if m else None


@pytest.mark.parametrize('prefix', ['', '/en', '/ru', '/bg'])
def test_hub_renders_in_every_language(client, loop_legs, prefix):
    r = client.get(f'{prefix}/balkan-loop/')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'name="from"' in html and 'name="days"' in html
    assert f'{prefix}{PRESET}' in html                  # curated itinerary card
    assert f'{prefix}/rute/dubrovnik-kotor/' in html    # direct-leg index
    assert 'loop-steps' not in html                     # no itinerary duplicated on the hub
    assert not re.search(r'planner\.(?!css|png)[a-z_]', html)      # no untranslated key leaked
    assert _head(html, r'name="robots" content="([^"]+)"').startswith('index')


@pytest.mark.parametrize('prefix', ['', '/en', '/ru', '/bg'])
def test_preset_page_renders_in_every_language(client, loop_legs, prefix):
    r = client.get(f'{prefix}{PRESET}')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'loop-steps' in html and f'{prefix}/rute/dubrovnik-kotor/' in html
    assert not re.search(r'planner\.(?!css|png)[a-z_]', html)
    assert _head(html, r'rel="canonical" href="([^"]+)"').endswith(f'{prefix}{PRESET}')
    assert _head(html, r'name="robots" content="([^"]+)"').startswith('index')


def test_preset_head_is_specific_and_within_limits(client, loop_legs):
    html = client.get(f'/en{PRESET}').data.decode()
    title = _head(html, r'<title>(.*?)</title>')
    desc = _head(html, r'name="description" content="([^"]+)"')
    assert 'Dubrovnik to Tirana' in title and '10-Day' in title and len(title) <= 62
    assert 'Dubrovnik' in desc and 70 <= len(desc) <= 160
    assert html.count('<h1') == 1
    hub_title = _head(client.get('/en/balkan-loop/').data.decode(), r'<title>(.*?)</title>')
    assert hub_title != title and len(hub_title) <= 62


def test_preset_structured_data_is_valid_and_matches_the_page(client, loop_legs):
    import json
    import re
    html = client.get(f'/en{PRESET}').data.decode()
    blocks = [json.loads(b) for b in
              re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S)]
    by_type = {b['@type']: b for b in blocks}
    trip = by_type['TouristTrip']
    names = [i['item']['name'] for i in trip['itinerary']['itemListElement']]
    assert names == ['Dubrovnik', 'Kotor', 'Budva', 'Podgorica', 'Tirana']
    faq = by_type['FAQPage']['mainEntity']
    assert faq and all(q['acceptedAnswer']['text'] for q in faq)
    for q in faq:   # every marked-up answer is visible on the page
        assert q['name'] in html
    assert [i['name'] for i in by_type['BreadcrumbList']['itemListElement']][1] == 'Trip planner'


def test_unknown_or_unchainable_preset_is_404(client, monkeypatch):
    assert client.get('/en/balkan-loop/nowhere-nowhere-5-days/').status_code == 404
    monkeypatch.setattr(planner, 'load_legs', lambda: {})
    assert client.get(f'/en{PRESET}').status_code == 404


def test_query_matching_a_preset_redirects_to_its_clean_url(client, loop_legs):
    r = client.get('/en/balkan-loop/?from=dubrovnik&to=tirana&days=10')
    assert r.status_code == 301 and r.headers['Location'].endswith(f'/en{PRESET}')


def test_other_query_variants_are_noindex(client, loop_legs):
    html = client.get('/en/balkan-loop/?from=kotor&to=tirana&days=8').data.decode()
    assert 'loop-steps' in html
    assert _head(html, r'name="robots" content="([^"]+)"') == 'noindex, follow'


def test_result_without_matching_data_says_so(client, monkeypatch):
    monkeypatch.setattr(planner, 'load_legs', lambda: {})
    r = client.get('/en/balkan-loop/?from=kotor&to=tirana&days=8')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'No chain of direct buses' in html and 'loop-steps' not in html


@pytest.mark.parametrize('qs', ['?from=zzz&to=<script>&days=abc', '?days=9999', '?days=-3',
                                '?from=tirana&to=tirana&days=4'])
def test_bad_input_never_errors(client, loop_legs, qs):
    r = client.get('/en/balkan-loop/' + qs, follow_redirects=True)
    assert r.status_code == 200
    assert '<script>&' not in r.data.decode()


def test_offers_are_dormant_by_default(client, loop_legs):
    html = client.get(f'/en{PRESET}').data.decode()
    assert 'loop-offer__btn' not in html


def test_configured_offers_render_as_sponsored_links(app, client, loop_legs):
    cfg = {'AFF_STAY_URL': 'https://example.com/stay?q={city}', 'AFF_STAY_NAME': 'Partner',
           'AFF_ESIM_URL': 'https://example.com/esim', 'AFF_TOURS_URL': 'javascript:alert(1)'}
    old = {k: app.config.get(k) for k in cfg}
    app.config.update(cfg)
    try:
        html = client.get(f'/en{PRESET}').data.decode()
    finally:
        app.config.update(old)
    assert 'https://example.com/stay?q=Dubrovnik' in html
    assert 'data-partner="stay"' in html and 'data-partner="esim"' in html
    assert 'rel="sponsored nofollow noopener"' in html
    assert 'javascript:' not in html and 'data-partner="tours"' not in html
    assert 'Sponsored links' in html


def test_sitemap_lists_hub_and_resolvable_presets(client, loop_legs):
    xml = client.get('/sitemap-core.xml').data.decode()
    assert '/balkan-loop/</loc>' in xml
    assert f'{PRESET}</loc>' in xml
    assert 'hreflang="en" href="' in xml and f'/en{PRESET}' in xml
    # LEGS has no Sarajevo: that preset cannot be chained, so it is not submitted.
    assert 'kotor-sarajevo-7-days' not in xml


def test_linked_from_nav_footer_and_destinations(client):
    home = client.get('/en/').data.decode()
    assert home.count('/en/balkan-loop/') >= 2          # header nav + footer
    assert '/en/balkan-loop/' in client.get('/en/destinacije/').data.decode()


def test_og_image_for_preset(client, loop_legs):
    r = client.get('/og/balkan-loop/dubrovnik-tirana-10-days.png')
    assert r.status_code == 200 and r.mimetype == 'image/png'
    assert client.get('/og/balkan-loop/nope.png').status_code == 200   # static fallback


def test_planner_partners_are_accepted_by_click_log(client):
    r = client.post('/api/ba-click', json={'route_slug': 'kotor', 'surface': 'planner', 'partner': 'stay'})
    assert r.status_code == 204


def test_itinerary_page_has_a_map_with_one_pin_per_stop(client, loop_legs):
    import html as html_mod
    import json
    page = client.get(f'/en{PRESET}').data.decode()
    raw = re.search(r'id="loopMap"[^>]*data-map="([^"]+)"', page).group(1)
    data = json.loads(html_mod.unescape(raw))
    assert data['mode'] == 'route'
    assert [s['name'] for s in data['stops']] == ['Dubrovnik', 'Kotor', 'Budva', 'Podgorica', 'Tirana']
    assert data['legs'] == ['dubrovnik:kotor', 'kotor:budva', 'budva:podgorica', 'podgorica:tirana']
    # The server-drawn sketch is there before (and without) the map library.
    assert page.count('class="loop-map__pin"') == 5 and 'loop-map__line' in page
    assert all(f'id="loopStop{n}"' in page for n in range(1, 6))


def test_hub_map_shows_the_network_and_cards_have_route_thumbnails(client, loop_legs):
    import html as html_mod
    import json
    page = client.get('/en/balkan-loop/').data.decode()
    raw = re.search(r'id="loopMap"[^>]*data-map="([^"]+)"', page).group(1)
    data = json.loads(html_mod.unescape(raw))
    assert data['mode'] == 'network' and len(data['stops']) == len(planner.STOPS)
    assert len(data['edges']) == 5          # LEGS is a 6-stop chain, both directions
    assert 'loop-card__thumb' in page and 'loop-form__swap' in page


def test_map_library_is_never_loaded_eagerly(client, loop_legs):
    for url in ('/en/balkan-loop/', f'/en{PRESET}'):
        page = client.get(url).data.decode()
        assert '<script src="https://api.mapbox.com' not in page
        assert 'planner.css' in page


def test_sketch_fits_its_box_and_keeps_north_up():
    pts = planner.sketch([(42.65, 18.09), (41.33, 19.82)], 600, 400, 40)   # Dubrovnik, Tirana
    assert all(40 <= x <= 560 and 40 <= y <= 360 for x, y in pts)
    assert pts[0][1] < pts[1][1] and pts[0][0] < pts[1][0]   # north-west of Tirana
    assert planner.sketch([]) == []


def test_planner_pages_carry_one_ad_slot_each(app, client, loop_legs):
    old = app.config.get('ADSENSE_ID')
    app.config['ADSENSE_ID'] = 'ca-pub-test'
    try:
        hub = client.get('/en/balkan-loop/').data.decode()
        preset = client.get(f'/en{PRESET}').data.decode()
        result = client.get('/en/balkan-loop/?from=kotor&to=tirana&days=8').data.decode()
    finally:
        app.config['ADSENSE_ID'] = old
    assert hub.count('data-slot="planner_hub"') == 1 and 'data-slot="planner_mid"' not in hub
    assert preset.count('data-slot="planner_mid"') == 1 and 'data-slot="planner_hub"' not in preset
    assert 'class="ad-slot' not in result          # noindex page: no ads


def test_route_page_between_loop_stops_links_to_the_planner(client):
    assert 'loopTeaserH' not in client.get('/en/rute/beograd-novi-sad/').data.decode()


def test_copy_link_and_map_tools_are_present(client, loop_legs):
    page = client.get(f'/en{PRESET}').data.decode()
    assert f'data-copy-url="http://localhost:5000/en{PRESET}"' in page
    assert 'data-map-reset' in page and 'data-map-expand' in page
    assert page.count('class="loop-stop__locate"') == 5

"""P28 mobile polish — markup-hook assertions for Home + route_detail +
city_pair + city_transport.

We can't assert visual layout from pytest, but we CAN assert the markup
hooks are in place: data-collapse, data-collapse-toggle, the home stats
strip, and that desktop hide-rules are present in app.css. This catches
regressions where a future linter pass strips a hook silently.
"""
from __future__ import annotations

import pytest


# ── Home: one credibility strip, not two ──────────────────────────────


def test_home_has_a_single_stats_strip(client):
    """The hero used to carry a mobile-only .hero__valueprop strip
    (routes / carriers / countries / free) directly above .home-stats
    (routes / lines / stops / cities) — two rows of numbers, back to
    back, saying the same thing on the only viewport where space is
    scarce. .home-stats renders on both breakpoints and is the one that
    survived."""
    resp = client.get('/')
    assert resp.status_code == 200
    body = resp.data.decode('utf-8')
    assert 'hero__valueprop' not in body, \
        'duplicate hero stats strip is back — one credibility row is enough'
    # The section wrapper, not its __item / __num children.
    assert body.count('class="home-stats container') == 1


def test_home_stats_strip_localised(client):
    """The surviving strip still renders real numbers with localised
    labels on every locale."""
    for path, word in (('/', 'stajali'), ('/en/', 'stops'), ('/ru/', 'останов')):
        body = client.get(path).data.decode('utf-8')
        assert 'home-stats__num' in body, path
        assert word in body, path


def test_home_drops_duplicate_feature_cards(client):
    """The three .home-feat-card links (city transport / destinations /
    routes) pointed at pages already reachable from the header nav, the
    hero tabs AND the two-column section right below them. Third copy
    removed."""
    body = client.get('/').data.decode('utf-8')
    assert 'home-feat-card' not in body


# ── Prose-collapse hook on long-form pages ─────────────────────────────


@pytest.mark.parametrize('path', [
    '/rute/beograd-novi-sad/',
    '/voznja/beograd-do-novi-sad/',
    '/gradski/beograd/',
])
def test_prose_collapse_data_attr_present(client, path):
    """Every page with a .seo-block must mark its content with
    data-collapse="1" so app.mobile.css can clip it on phones. Desktop
    is unaffected (the clip is inside @media max-width:767px)."""
    resp = client.get(path)
    if resp.status_code == 404:
        pytest.skip(f'page {path} absent in test data')
    assert resp.status_code == 200, path
    assert b'data-collapse="1"' in resp.data, \
        f'{path} missing data-collapse hook'


@pytest.mark.parametrize('path', [
    '/rute/beograd-novi-sad/',
    '/voznja/beograd-do-novi-sad/',
    '/gradski/beograd/',
])
def test_prose_collapse_toggle_button_present(client, path):
    """Each .seo-block must render a `[data-collapse-toggle]` button so
    the delegated handler in mobile.js finds something to toggle."""
    resp = client.get(path)
    if resp.status_code == 404:
        pytest.skip(f'page {path} absent in test data')
    assert b'data-collapse-toggle' in resp.data, \
        f'{path} missing toggle button'
    # Both labels must ship in data-* so the JS toggle has both copies.
    assert b'data-more-label=' in resp.data, path
    assert b'data-less-label=' in resp.data, path


def test_prose_collapse_button_localised(client):
    """SR default → 'Pročitaj više' on the toggle. EN → 'Read more'.
    Sanity check that the i18n key is wired."""
    resp_sr = client.get('/rute/beograd-novi-sad/')
    if resp_sr.status_code != 200:
        pytest.skip('route page absent in test data')
    body_sr = resp_sr.data.decode('utf-8')
    # Either "Pročitaj više" (SR) appears in either the visible button
    # text or the data-more-label attribute. Both come from the same
    # i18n key so one match is enough.
    assert 'Pročitaj više' in body_sr

    resp_en = client.get('/en/rute/beograd-novi-sad/')
    if resp_en.status_code == 200:
        assert b'Read more' in resp_en.data


# ── Desktop guard rails ────────────────────────────────────────────────


def test_no_valueprop_css_left_behind(client):
    """The strip's rules went with its markup — in both stylesheets, so
    the dead selectors don't sit in the CSS budget forever."""
    for name in ('app.css', 'app.mobile.css'):
        resp = client.get(f'/static/css/{name}')
        assert resp.status_code == 200
        assert 'hero__valueprop' not in resp.data.decode('utf-8'), name


def test_desktop_css_hides_seo_more_button(client):
    """app.css must hide the .seo-block__more button on desktop so the
    "Read more" affordance never shows when the prose is fully visible."""
    resp = client.get('/static/css/app.css')
    assert resp.status_code == 200
    body = resp.data.decode('utf-8')
    assert '.seo-block__more { display: none; }' in body \
        or '.seo-block__more{display:none' in body


# ── Mobile CSS ships the new sections ──────────────────────────────────


def test_app_mobile_css_contains_p28_sections(client):
    """app.mobile.css must contain the page-polish block markers — gives
    a fast signal in CI when an over-eager refactor strips them."""
    resp = client.get('/static/css/app.mobile.css')
    assert resp.status_code == 200
    body = resp.data.decode('utf-8')
    assert 'Page polish — home' in body, 'home polish section missing'
    assert 'Page polish — route_detail' in body, 'route_detail polish section missing'
    assert '.faq-item__q' in body
    assert '.seo-block__content[data-collapse=' in body

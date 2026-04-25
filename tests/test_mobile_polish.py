"""P28 mobile polish — markup-hook assertions for Home + route_detail +
city_pair + city_transport.

We can't assert visual layout from pytest, but we CAN assert the markup
hooks are in place: data-collapse, data-collapse-toggle, value-prop
strip, and that desktop hide-rules are present in app.css. This catches
regressions where a future linter pass strips a hook silently.
"""
from __future__ import annotations

import pytest


# ── Home: hero value-prop strip ────────────────────────────────────────


def test_home_renders_valueprop_strip(client):
    """The mobile-only value-prop strip ships in the markup; CSS hides
    it on desktop. Test asserts presence of the wrapper class."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'class="hero__valueprop"' in resp.data, \
        'home hero is missing the value-prop strip — P28 polish hook'


def test_home_valueprop_includes_carriers_count(client):
    """Strip must contain "70+" + the i18n word for carriers in the
    rendered language. Validates i18n keys + the b/span structure
    survive a future template tweak."""
    resp = client.get('/')
    assert b'70+' in resp.data
    # SR is default locale → "prevoznika"
    assert b'prevoznika' in resp.data


def test_home_valueprop_en_locale(client):
    resp = client.get('/en/')
    assert resp.status_code == 200
    assert b'carriers' in resp.data
    assert b'free' in resp.data


def test_home_valueprop_ru_locale(client):
    resp = client.get('/ru/')
    assert resp.status_code == 200
    # b'\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb2\xd0\xbe\xd0\xb7\xd1\x87\xd0\xb8\xd0\xba\xd0\xbe\xd0\xb2'
    # = 'перевозчиков' encoded as utf-8.
    body = resp.data.decode('utf-8')
    assert 'перевозчиков' in body
    assert 'бесплатно' in body


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


def test_desktop_css_hides_valueprop_strip(client):
    """app.css must contain the rule that hides .hero__valueprop on
    desktop — otherwise the mobile strip leaks into desktop hero."""
    resp = client.get('/static/css/app.css')
    assert resp.status_code == 200
    body = resp.data.decode('utf-8')
    # The mobile-only strip is hidden by default; app.mobile.css un-hides
    # only at ≤767px viewports.
    assert '.hero__valueprop { display: none; }' in body \
        or '.hero__valueprop{display:none' in body \
        or '.hero__valueprop' in body and 'display: none' in body


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
    assert '.hero__valueprop' in body
    assert '.faq-item__q' in body
    assert '.seo-block__content[data-collapse=' in body

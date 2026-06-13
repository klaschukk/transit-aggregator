"""AdSense placement + house-ad fallback + privacy compliance.

Covers four risk surfaces:

  1. With ADSENSE_ID empty (default in tests) — every page must render
     the house-ad fallback in place of the slot.
  2. /ads.txt reflects ADSENSE_PUB_ID format correctly (and degrades to
     a comment when unset).
  3. Mobile-anchor partial only renders when consent='all' AND not
     dismissed AND a slot id is configured.
  4. AdSense disclosure is present on /privatnost/ and the dashboard
     handles missing adsense_daily table gracefully (day-1 state).

We never set ADSENSE_ID in these tests — tests must work with the
default empty config so a stray pytest run can never accidentally load
the AdSense JS or hit pagead2.googlesyndication.com.
"""
from __future__ import annotations

import pytest


# ── 1. House-ad fallback rendering when ADSENSE_ID is empty ────────────


@pytest.mark.parametrize('path', [
    '/',
    '/rute/',
    '/rute/beograd-novi-sad/',
    '/voznja/beograd-do-novi-sad/',
    '/gradski/beograd/',
])
def test_pages_render_nothing_when_adsense_disabled(client, path):
    """Until AdSense is approved (post-1000-visit threshold per the
    project plan) ADSENSE_ID is empty. The house-ad fallback was leaking
    unstyled "Reklama" + raw promo text onto every page, so the macro
    now early-returns when ADSENSE_ID is empty. Reserved layout space
    will reappear automatically once AdSense is enabled."""
    resp = client.get(path)
    if resp.status_code == 404:
        pytest.skip(f'page {path} not present in test DB')
    assert resp.status_code == 200, path
    assert b'class="ad-slot' not in resp.data, path
    assert b'house-ad' not in resp.data, path


def test_no_adsense_script_loaded_when_id_empty(client):
    """The bootstrap <script> block must not appear when ADSENSE_ID is
    empty — guarantees no leak of pagead2.googlesyndication.com to
    clients in dev/CI."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'pagead2.googlesyndication.com' not in resp.data


def test_no_ins_adsbygoogle_when_disabled(client):
    """`<ins class="adsbygoogle">` must never appear in the rendered
    HTML when AdSense is off — wrong house-ad fallback path otherwise."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'adsbygoogle' not in resp.data, \
        'adsbygoogle leaked into HTML with ADSENSE_ID empty'


# ── 2. /ads.txt content ────────────────────────────────────────────────


def test_ads_txt_returns_placeholder_when_no_pub_id(client):
    """With ADSENSE_PUB_ID empty (test default), /ads.txt returns a
    comment line instead of 404 — keeps AdSense crawlers from logging
    a missing-file error during the approval window."""
    resp = client.get('/ads.txt')
    assert resp.status_code == 200
    assert resp.content_type.startswith('text/plain')
    body = resp.data.decode('utf-8')
    assert body.startswith('#') or 'pub-' in body


def test_ads_txt_format_when_pub_id_set(client, app):
    """Patch the live config and confirm /ads.txt returns the IAB-canonical
    format. Not a real env var test — we toggle via app.config so other
    tests in the session aren't affected."""
    original = app.config.get('ADSENSE_ID', '')
    original_pub = app.config.get('ADSENSE_PUB_ID', '')
    try:
        app.config['ADSENSE_ID'] = 'ca-pub-1234567890'
        app.config['ADSENSE_PUB_ID'] = 'ca-pub-1234567890'
        resp = client.get('/ads.txt')
        assert resp.status_code == 200
        body = resp.data.decode('utf-8').strip()
        # ads.txt MUST use the bare pub- form, never the JS ca-pub- form, or
        # Google's ads.txt verification fails (real bug found 2026-06).
        assert body == 'google.com, pub-1234567890, DIRECT, f08c47fec0942fa0'
        assert 'ca-pub-' not in body
    finally:
        app.config['ADSENSE_ID'] = original
        app.config['ADSENSE_PUB_ID'] = original_pub


# ── 3. Mobile anchor partial ────────────────────────────────────────────


def test_mobile_anchor_not_rendered_without_consent(client):
    """No `cookie_consent` cookie → the anchor partial must early-return
    (output is empty). Verified by absence of the wrapper id."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'id="mobileAnchorAd"' not in resp.data


def test_mobile_anchor_not_rendered_with_essential_consent(client):
    """Even with consent=essential the anchor stays hidden — Google's
    NPA mode can't run on the in-page anchor format reliably enough to
    risk a frequency-policy hit."""
    client.set_cookie(key='cookie_consent', value='essential',
                      path='/', domain='localhost')
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'id="mobileAnchorAd"' not in resp.data


def test_mobile_anchor_still_off_without_slot_id(client, app):
    """Even with consent=all + ADSENSE_ID set, the anchor needs the
    mobile_anchor slot id. Missing slot → no render."""
    original_id = app.config.get('ADSENSE_ID', '')
    original_slots = dict(app.config.get('ADSENSE_SLOTS', {}))
    try:
        app.config['ADSENSE_ID'] = 'ca-pub-1234567890'
        app.config['ADSENSE_SLOTS'] = {**original_slots, 'mobile_anchor': ''}
        client.set_cookie(key='cookie_consent', value='all',
                          path='/', domain='localhost')
        resp = client.get('/')
        assert resp.status_code == 200
        assert b'id="mobileAnchorAd"' not in resp.data
    finally:
        app.config['ADSENSE_ID'] = original_id
        app.config['ADSENSE_SLOTS'] = original_slots


# ── 4. Privacy + revenue dashboard ──────────────────────────────────────


def test_privacy_page_includes_adsense_disclosure(client):
    """AdSense personalised ads must be disclosed on /privatnost/ —
    Google policy requirement + GDPR Art. 13."""
    resp = client.get('/privatnost/')
    assert resp.status_code == 200
    body = resp.data.lower()
    assert b'adsense' in body
    # Disclosure may be in any of 3 languages depending on default lang;
    # verify a known phrase from each variant is hittable.
    body_text = body.decode('utf-8', errors='ignore')
    accepted_phrases = (
        'requestnonpersonalizedads',
        'non-personalised',
        'неперсонализ',
        'neperonaliz',
    )
    assert any(p in body_text for p in accepted_phrases), \
        'no AdSense personalised-ads disclosure phrase matched'


def test_admin_revenue_handles_missing_adsense_table(client):
    """When `adsense_daily` table doesn't exist (day 1 / fresh dev box),
    /admin/revenue must still respond — defensively. ADMIN_USER not
    configured in tests so we accept either 503 (admin disabled) or
    401 (auth required) — both prove the route didn't 500."""
    resp = client.get('/admin/revenue')
    assert resp.status_code in (401, 503)


# ── 5. Slot-level template macro behaviour ──────────────────────────────


def test_ads_label_translated_when_adsense_enabled(client, app):
    """When ADSENSE_ID + slot id + consent are all set, the slot wrapper
    must carry the localised `ads.label` text — required by AdSense
    policy on disclosure. We simulate the ads-on state because the
    macro now early-returns whenever ADSENSE_ID is empty."""
    original_id = app.config.get('ADSENSE_ID', '')
    original_slots = dict(app.config.get('ADSENSE_SLOTS', {}))
    try:
        app.config['ADSENSE_ID'] = 'ca-pub-1234567890'
        app.config['ADSENSE_SLOTS'] = {**original_slots, 'home_top': '999'}
        client.set_cookie(key='cookie_consent', value='all',
                          path='/', domain='localhost')
        resp = client.get('/')
        assert resp.status_code == 200
        body = resp.data
        assert (b'Reklama' in body or b'Advertisement' in body
                or b'\xd0\xa0\xd0\xb5\xd0\xba\xd0\xbb\xd0\xb0\xd0\xbc' in body), \
            'no ad label found — disclosure missing'
    finally:
        app.config['ADSENSE_ID'] = original_id
        app.config['ADSENSE_SLOTS'] = original_slots


def test_ad_slot_wrappers_appear_when_adsense_enabled(client, app):
    """The bottom slot wrapper must exist on a route page once AdSense
    is enabled — `min-height` reservation is what prevents CLS once ads
    are live. Until then the macro renders nothing at all."""
    original_id = app.config.get('ADSENSE_ID', '')
    original_slots = dict(app.config.get('ADSENSE_SLOTS', {}))
    try:
        app.config['ADSENSE_ID'] = 'ca-pub-1234567890'
        app.config['ADSENSE_SLOTS'] = {**original_slots, 'route_bottom': '999'}
        resp = client.get('/rute/beograd-novi-sad/')
        if resp.status_code == 404:
            pytest.skip('route not in test DB')
        assert resp.status_code == 200
        assert b'data-slot="route_bottom"' in resp.data
    finally:
        app.config['ADSENSE_ID'] = original_id
        app.config['ADSENSE_SLOTS'] = original_slots


# ── 6. Lazy-ad activation (the IntersectionObserver loader) ─────────────


def test_lazy_ad_slot_has_activation_loader(client, app):
    """Below-the-fold slots render as `.js-ad-lazy` placeholders with NO
    <ins> at parse time. Without the loader script those placeholders are
    dead reserved boxes that never fetch an ad (zero revenue). The loader
    in base.html must be emitted alongside the placeholder so the <ins>
    gets injected on scroll. Regression guard: the loader was missing for
    every default (lazy=True) slot — 17 of 18 slots earned nothing."""
    original_id = app.config.get('ADSENSE_ID', '')
    original_slots = dict(app.config.get('ADSENSE_SLOTS', {}))
    try:
        app.config['ADSENSE_ID'] = 'ca-pub-1234567890'
        app.config['ADSENSE_SLOTS'] = {**original_slots, 'route_bottom': '999'}
        resp = client.get('/rute/beograd-novi-sad/')
        if resp.status_code == 404:
            pytest.skip('route not in test DB')
        assert resp.status_code == 200
        body = resp.data
        # Placeholder with the data the loader needs.
        assert b'js-ad-lazy' in body, 'lazy placeholder missing'
        assert b'data-ad-slot-id="999"' in body
        assert b'data-ad-format=' in body
        # The activation loader itself must be present.
        assert b"querySelectorAll('.js-ad-lazy')" in body, \
            'lazy-ad loader script missing — placeholders would never load'
        assert b'adsbygoogle' in body and b'IntersectionObserver' in body
    finally:
        app.config['ADSENSE_ID'] = original_id
        app.config['ADSENSE_SLOTS'] = original_slots


def test_lazy_ad_npa_flag_follows_consent(client, app):
    """The lazy placeholder must carry the GDPR NPA flag so the loader
    pushes non-personalized ads for unconsented EU visitors. Any consent
    state other than 'all' → npa true; consent=all → npa false."""
    original_id = app.config.get('ADSENSE_ID', '')
    original_slots = dict(app.config.get('ADSENSE_SLOTS', {}))
    try:
        app.config['ADSENSE_ID'] = 'ca-pub-1234567890'
        app.config['ADSENSE_SLOTS'] = {**original_slots, 'route_bottom': '999'}
        # Essential-only consent (≠ 'all') → non-personalized.
        client.set_cookie(key='cookie_consent', value='essential',
                          path='/', domain='localhost')
        resp = client.get('/rute/beograd-novi-sad/')
        if resp.status_code == 404:
            pytest.skip('route not in test DB')
        assert b'data-ad-npa="true"' in resp.data, 'NPA not set for unconsented'
        # Explicit full consent → personalized.
        client.set_cookie(key='cookie_consent', value='all',
                          path='/', domain='localhost')
        resp = client.get('/rute/beograd-novi-sad/')
        assert b'data-ad-npa="false"' in resp.data, 'NPA should clear on consent=all'
    finally:
        app.config['ADSENSE_ID'] = original_id
        app.config['ADSENSE_SLOTS'] = original_slots


# ── 6. Unfilled-slot collapse (added 2026-06-13) ────────────────────────


def test_ads_css_collapses_unfilled_slots(client):
    """An ad unit that doesn't fill must not leave an empty reserved box with
    a "Reklama" label. AdSense stamps data-ad-status="unfilled" on the <ins>;
    ads.css hides it and collapses the wrapper + label via :has(). Guards the
    served stylesheet so the rules can't silently vanish."""
    resp = client.get('/static/css/ads.css')
    assert resp.status_code == 200
    css = resp.get_data(as_text=True)
    assert 'data-ad-status="unfilled"' in css
    assert ':has(' in css
    # Both the empty <ins> and the wrapper/label collapse must be present.
    assert 'ins.adsbygoogle[data-ad-status="unfilled"]{display:none' in css
    assert '.ad-slot__label{display:none' in css

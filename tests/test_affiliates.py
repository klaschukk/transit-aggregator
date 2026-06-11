"""Tests for app.affiliates — plugin base, partner plugins, resolver, A/B."""
import pytest

from app.affiliates import (
    Bookaway,
    BusTicket4,
    FlixBus,
    Offer,
    ab_partner_order,
    bt4_checkout_url,
    primary_offer,
    resolve_offers,
)


# ── Partner.has_route() ───────────────────────────────────────────────

def test_bookaway_active_only_for_far_destinations():
    # Bookaway is FAR-ONLY now (owner decision): it covers a pair only when an
    # endpoint is a far/long-haul destination (Asia etc.) from bookaway_far.json.
    from app.affiliates.partners import FAR_DESTINATIONS
    far = next(iter(FAR_DESTINATIONS))
    assert Bookaway().has_route('beograd', far) is True
    assert Bookaway().has_route(far, 'beograd') is True


def test_bookaway_not_used_for_balkan_routes():
    # Regular Balkan routes go to BusTicket4 — Bookaway must NOT cover them.
    assert Bookaway().has_route('beograd', 'nis') is False
    assert Bookaway().has_route('beograd', 'sarajevo') is False
    assert Bookaway().has_route('podgorica', 'dubrovnik') is False


def test_bookaway_skips_fully_unknown_pair():
    # Neither endpoint is a far destination → not eligible
    assert Bookaway().has_route('foobar', 'bazqux') is False


def test_flixbus_skips_intra_serbia():
    # FlixBus doesn't run domestic Serbian routes
    assert FlixBus().has_route('beograd', 'nis') is False
    assert FlixBus().has_route('novi-sad', 'kragujevac') is False


def test_flixbus_covers_cross_border():
    # Belgrade ↔ Sarajevo / Zagreb / Sofia / Skopje are FlixBus corridors
    assert FlixBus().has_route('beograd', 'sarajevo') is True
    assert FlixBus().has_route('beograd', 'zagreb') is True
    assert FlixBus().has_route('beograd', 'sofija') is True


def test_flixbus_requires_both_endpoints_in_network():
    # Tiny Serbian village → nowhere-to-be-found hub
    assert FlixBus().has_route('obrenovac', 'sarajevo') is False


# ── Partner.build_url() ───────────────────────────────────────────────

def _dest(url: str) -> str:
    """Decode the deep-link destination from the aff_c `url=` param."""
    from urllib.parse import parse_qs, unquote, urlparse
    return unquote(parse_qs(urlparse(url).query).get('url', [''])[0])


def test_bookaway_url_routes_through_tune_tracker():
    # Links MUST go through the TUNE click tracker (aff_c) so a click is
    # registered and the conversion cookie is set — otherwise nothing is
    # ever attributed (the "362 clicks, 0 conversions" root cause).
    url = Bookaway().build_url(
        'beograd', 'nis', 'Beograd', 'Niš', 'route-detail',
    )
    assert url.startswith('https://bookaway2.go2cloud.org/aff_c?')
    assert 'offer_id=34' in url
    assert 'aff_id=4033' in url
    # Per-route / per-surface attribution via sub IDs.
    assert 'aff_sub=beograd-nis' in url
    assert 'aff_sub2=route-detail' in url
    # The destination deep-link is carried (encoded) in url=. beograd:nis is a
    # verified pair, so it deep-links to the exact route using Bookaway's
    # ENGLISH slug (belgrade-to-nis), never our raw 'beograd-to-nis' (404s).
    dest = _dest(url)
    assert dest.startswith('https://www.bookaway.com/routes/serbia/')
    assert 'beograd-to-nis' not in dest
    assert 'utm_source=prevozni' in dest
    assert 'utm_medium=route-detail' in dest


def test_bookaway_verified_pair_uses_english_slug_under_from_country():
    # A verified pair deep-links to the EXACT route (best conversion), using
    # Bookaway's English slug under the DEPARTURE country: beograd->belgrade,
    # serbia (from), even for a cross-border pair like beograd->sarajevo.
    from app.affiliates.partners import _VERIFIED_PAIRS
    assert 'beograd:sarajevo' in _VERIFIED_PAIRS, "allowlist not loaded"
    dest = _dest(Bookaway().build_url(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo', 'trip-card',
    ))
    assert dest.startswith(
        'https://www.bookaway.com/routes/serbia/belgrade-to-sarajevo')
    assert 'beograd-to-sarajevo' not in dest  # never our raw slug


def test_bookaway_falls_back_to_country_page_for_partial_match():
    # mladenovac is NOT in Bookaway's inventory, so no verified pair exists.
    # Destination falls back to the country listing page (always 200). The
    # click still goes through the tracker, so attribution survives.
    from app.affiliates.partners import _VERIFIED_PAIRS
    assert 'mladenovac:beograd' not in _VERIFIED_PAIRS
    url = Bookaway().build_url(
        'mladenovac', 'beograd', 'Mladenovac', 'Beograd', 'trip-card',
    )
    assert url.startswith('https://bookaway2.go2cloud.org/aff_c?')
    dest = _dest(url)
    assert dest.startswith('https://www.bookaway.com/routes/serbia/?')
    assert 'mladenovac-to-beograd' not in dest  # no dead pair path


def test_bookaway_unverified_pair_never_emits_404_pair_path():
    # Invariant: a pair path is emitted ONLY for allowlisted pairs. An eligible
    # but UNVERIFIED pair (Bookaway has no inventory for it) must fall back to
    # the country page, never a guessed /{from}-to-{to} path that 404s.
    from app.affiliates.partners import _VERIFIED_PAIRS, _BOOKAWAY_COUNTRY_MAP
    pair = next(
        (a, b)
        for a in _BOOKAWAY_COUNTRY_MAP for b in _BOOKAWAY_COUNTRY_MAP
        if a != b and f'{a}:{b}' not in _VERIFIED_PAIRS
    )
    dest = _dest(Bookaway().build_url(pair[0], pair[1], 'A', 'B', 'trip-card'))
    path = dest.split('?')[0].split('bookaway.com')[1]
    assert path.startswith('/routes/')
    assert '-to-' not in path  # country listing, not a pair path


def test_flixbus_placeholder_does_not_leak_param():
    # While AWIN_ID='PLACEHOLDER' the URL must not contain awin_id=
    url = FlixBus().build_url(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo', 'trip-card',
    )
    assert 'awin_id=' not in url
    assert 'flixbus.com/bus/beograd-sarajevo' in url


# ── BusTicket4 (per-trip partner, via bt4_checkout_url) ────────────────

def test_busticket4_covers_pair_with_known_city_ids():
    assert BusTicket4().has_route('beograd', 'nis') is True
    assert BusTicket4().has_route('podgorica', 'budva') is True
    # Unknown city → can't build a checkout URL → not covered.
    assert BusTicket4().has_route('foobar', 'nis') is False


def test_busticket4_resolves_dj_cities_in_db_slug_form():
    # bt4_cities.json keys đ-cities đ→"dj" (Aranđelovac="arandjelovac"), but our
    # routes/DB slugify đ→"d" ("arandelovac"). The loader registers the đ→d form
    # as an alias so these 13 bookable pairs don't silently fall to Bookaway.
    from app.affiliates.partners import _BT4_CITY_ID
    assert _BT4_CITY_ID.get('arandelovac') == _BT4_CITY_ID.get('arandjelovac') == 1326
    assert _BT4_CITY_ID.get('indija') == _BT4_CITY_ID.get('indjija') == 1365
    # Pairs in the DB's đ→d slug form are now BT4-eligible with a real lineId.
    assert BusTicket4().has_route('beograd', 'arandelovac') is True
    assert BusTicket4().has_route('indija', 'beograd') is True
    url = BusTicket4().build_url('beograd', 'arandelovac', '', '', 'route-detail')
    assert 'arrivalCityId=1326' in url and 'affiliateId=735' in url
    assert '&lineId=' in url  # populated checkout, never an empty 0.00 € shell


def test_busticket4_dj_alias_never_clobbers_real_city():
    # "durdevac" is a real distinct city; aliasing "djurdjevac"→"durdevac" must
    # NOT overwrite it (setdefault + original-keys snapshot keep it additive).
    import json
    import os
    from app.affiliates.partners import _BT4_CITY_ID
    raw = json.load(open(os.path.join(
        os.path.dirname(__file__), '..', 'app', 'affiliates', 'bt4_cities.json'),
        encoding='utf-8'))
    assert _BT4_CITY_ID['durdevac'] == raw['durdevac']
    assert _BT4_CITY_ID['durdevac'] != _BT4_CITY_ID['djurdjevac']


def test_busticket4_url_is_affiliate_checkout():
    import re
    url = BusTicket4().build_url('beograd', 'nis', 'Beograd', 'Niš', 'route-detail')
    assert url.startswith('https://busticket4.me/en/checkout?')
    assert 'departureCityId=1213' in url   # Beograd
    assert 'arrivalCityId=1243' in url     # Niš
    assert 'affiliateId=735' in url        # prevozni.com attribution
    assert 'tripType=one-way' in url
    assert 'passengers=1' in url
    assert re.search(r'departureDate=\d{2}-\d{2}-\d{4}', url)  # DD-MM-YYYY


def test_busticket4_commission_is_two_percent():
    # Cassiopeia agreement: 2% of every ticket sold.
    assert BusTicket4().commission_midpoint == 2.0


def test_busticket4_build_url_appends_line_id():
    url = BusTicket4().build_url('beograd', 'nis', 'B', 'N', 'trip-card', line_id=909)
    assert '&lineId=909' in url


def test_bt4_checkout_url_pins_the_exact_trip():
    # The per-trip helper deep-links to ONE departure (lineId) so the checkout
    # shows a real trip + price instead of the empty 0.00 € pair page.
    url = bt4_checkout_url('beograd', 'nis', 909)
    assert url.startswith('https://busticket4.me/en/checkout?')
    assert 'lineId=909' in url and 'affiliateId=735' in url
    assert 'departureCityId=1213' in url and 'arrivalCityId=1243' in url


def test_bt4_checkout_url_empty_without_line_id_or_known_city():
    # No line id → no usable checkout (avoid the empty 0.00 € page entirely).
    assert bt4_checkout_url('beograd', 'nis', None) == ''
    assert bt4_checkout_url('beograd', 'nis', 0) == ''
    # Unknown city → can't resolve a city id.
    assert bt4_checkout_url('foobar', 'nis', 909) == ''


def test_busticket4_leads_pair_level_when_line_id_known():
    # BusTicket4 is now a pair-level partner for pairs we hold a line_id for
    # (bt4_lineids.json). Its checkout deep-link is then guaranteed populated,
    # so it LEADS the buy button; Bookaway stays in the list as fallback.
    from app.affiliates.partners import _BT4_PAIR_LINEID, _BT4_CITY_ID
    f, t = 'beograd', 'kragujevac'
    assert f'{f}-{t}' in _BT4_PAIR_LINEID and f in _BT4_CITY_ID and t in _BT4_CITY_ID
    offers = resolve_offers(f, t, 'Beograd', 'Kragujevac')
    keys = [o.partner_key for o in offers]
    assert keys == ['busticket4']           # only active partner; exact checkout
    assert 'lineId=' in offers[0].url       # ...and it opens a real departure


def test_busticket4_absent_when_no_line_id_known():
    # A pair with no pre-resolved line_id (international, BT4 has no inventory
    # mapped) now yields NO offer at all — Bookaway was removed, so there is no
    # fallback; the template hides the buy button.
    offers = resolve_offers('beograd', 'sofia', 'Beograd', 'Sofia')
    assert offers == []


# ── resolve_offers() ──────────────────────────────────────────────────

def test_resolver_returns_empty_for_degenerate_pair():
    assert resolve_offers('', '') == []
    assert resolve_offers('beograd', 'beograd') == []


def test_resolver_returns_empty_when_no_partner_covers():
    # Without Omio as a universal fallback, unknown city pairs simply
    # have no offer — templates guard `{% if _buy_href %}` and hide.
    # Use clearly-fake slugs to avoid colliding with real Bookaway cities
    # like 'bar' (Bar, Montenegro).
    offers = resolve_offers('foobar', 'bazqux')
    assert offers == []


def test_resolver_orders_by_checkout_quality_then_commission():
    # With Bookaway removed, BusTicket4 is the sole offer for a BT4-eligible SR
    # pair (exact checkout, ux_rank 0). The old two-partner ordering is moot.
    offers = resolve_offers('beograd', 'kragujevac', 'Beograd', 'Kragujevac')
    keys = [o.partner_key for o in offers]
    assert keys == ['busticket4']
    assert offers[0].ux_rank == 0


def test_resolver_cross_border_excludes_flixbus():
    # No FlixBus agreement and Bookaway removed → only BusTicket4 may appear. It
    # sells this cross-border pair (line_id known) so it is the sole offer.
    offers = resolve_offers(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo', 'trip-card',
    )
    keys = [o.partner_key for o in offers]
    assert 'flixbus' not in keys
    assert 'bookaway' not in keys
    assert keys == ['busticket4']


def test_resolver_ab_ignored_when_partner_ineligible():
    # AB names flixbus, which is never eligible → the default checkout-quality
    # ordering applies and the direct-checkout partner (BT4) leads.
    offers = resolve_offers(
        'beograd', 'kragujevac', ab_choice='flixbus',
    )
    assert offers[0].partner_key == 'busticket4'


def test_primary_offer_helper():
    offers = resolve_offers('beograd', 'sarajevo')
    assert primary_offer(offers) is offers[0]
    assert primary_offer([]) is None


def test_offer_is_frozen_dataclass():
    # Offers must be hashable / immutable (templates cache them per-request)
    o = Offer(
        partner_key='x', partner_name='X', url='https://x/',
        brand_color='#000', commission_pct=1.0, ux_rank=1,
    )
    with pytest.raises(Exception):
        o.url = 'https://y/'  # type: ignore


# ── A/B assignment ───────────────────────────────────────────────────

def test_ab_honours_existing_cookie():
    # A cookie naming the current valid variant sticks across requests.
    assert ab_partner_order({'ab_partner': 'busticket4'}, seed='1.2.3.4') == 'busticket4'


def test_ab_stale_cookie_falls_back():
    # 'bookaway'/'flixbus' are no longer the active variant → an old cookie must
    # not stick; the user is reassigned to the current arm.
    assert ab_partner_order({'ab_partner': 'flixbus'}, seed='1.2.3.4') == 'busticket4'
    assert ab_partner_order({'ab_partner': 'bookaway'}, seed='1.2.3.4') == 'busticket4'


def test_ab_ignores_garbage_cookie_value():
    assert ab_partner_order({'ab_partner': 'hax0r'}, seed='') == 'busticket4'


def test_ab_deterministic_from_seed():
    # Same seed → same variant across calls (stickiness without cookies)
    a = ab_partner_order({}, seed='10.0.0.1')
    b = ab_partner_order({}, seed='10.0.0.1')
    assert a == b


def test_ab_writes_cookie_when_asked():
    captured = {}
    ab_partner_order(
        {}, response_setter=lambda k, v: captured.update({k: v}), seed='1.1.1.1',
    )
    assert captured.get('ab_partner') == 'busticket4'


def test_ab_single_arm_always_busticket4():
    # Single active arm: prefer the direct-checkout partner → every seed → it.
    from collections import Counter
    c = Counter(ab_partner_order({}, seed=f'10.0.0.{i}') for i in range(200))
    assert c['busticket4'] == 200
    assert 'bookaway' not in c and 'flixbus' not in c

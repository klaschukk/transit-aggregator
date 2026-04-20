"""Tests for app.affiliates — plugin base, partner plugins, resolver, A/B."""
import pytest

from app.affiliates import (
    Bookaway,
    FlixBus,
    Offer,
    Omio,
    ab_partner_order,
    primary_offer,
    resolve_offers,
)


# ── Partner.has_route() ───────────────────────────────────────────────

def test_bookaway_covers_serbian_domestic():
    assert Bookaway().has_route('beograd', 'nis') is True


def test_bookaway_covers_balkan_cross_border():
    assert Bookaway().has_route('beograd', 'sarajevo') is True
    assert Bookaway().has_route('podgorica', 'dubrovnik') is True


def test_bookaway_skips_fully_unknown_pair():
    # Neither endpoint is in the country map → no deep link could be built
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


def test_omio_matches_any_non_empty_pair():
    # Multi-modal fallback must cover everything
    assert Omio().has_route('beograd', 'nis') is True
    assert Omio().has_route('foo', 'bar') is True


def test_omio_rejects_self_and_empty():
    assert Omio().has_route('', '') is False
    assert Omio().has_route('beograd', '') is False
    assert Omio().has_route('beograd', 'beograd') is False


# ── Partner.build_url() ───────────────────────────────────────────────

def test_bookaway_url_keeps_offer_and_aff_ids():
    url = Bookaway().build_url(
        'beograd', 'nis', 'Beograd', 'Niš', 'route-detail',
    )
    assert 'offer_id=34' in url
    assert 'aff_id=4033' in url
    assert 'utm_source=prevozni' in url
    assert 'utm_medium=route-detail' in url
    assert '/routes/serbia/beograd-to-nis' in url


def test_bookaway_url_picks_destination_country():
    url = Bookaway().build_url(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo', 'trip-card',
    )
    # Destination country wins (Bookaway groups URLs by arrival country)
    assert '/routes/bosnia-and-herzegovina/' in url


def test_flixbus_placeholder_does_not_leak_param():
    # While AWIN_ID='PLACEHOLDER' the URL must not contain awin_id=
    url = FlixBus().build_url(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo', 'trip-card',
    )
    assert 'awin_id=' not in url
    assert 'flixbus.com/bus/beograd-sarajevo' in url


def test_omio_url_encodes_city_names():
    # Diacritics must survive round-trip through URL-encoding
    url = Omio().build_url(
        'nis', 'uzice', 'Niš', 'Užice', 'trip-card',
    )
    # Ni%C5%A1 == "Niš"; U%C5%BEice == "Užice"
    assert 'Ni%C5%A1' in url
    assert 'U%C5%BEice' in url
    assert 'utm_source=prevozni' in url


# ── resolve_offers() ──────────────────────────────────────────────────

def test_resolver_returns_empty_for_degenerate_pair():
    assert resolve_offers('', '') == []
    assert resolve_offers('beograd', 'beograd') == []


def test_resolver_always_returns_at_least_omio():
    # Omio's universal has_route means the resolver never returns []
    offers = resolve_offers('foo', 'bar')
    assert len(offers) >= 1
    assert offers[-1].partner_key == 'omio'


def test_resolver_orders_by_commission_then_ux():
    # For a SR domestic pair, all three partners might claim the pair?
    # Bookaway yes, FlixBus no (intra-SR), Omio yes.
    offers = resolve_offers('beograd', 'nis', 'Beograd', 'Niš')
    keys = [o.partner_key for o in offers]
    assert keys[0] == 'bookaway'  # highest commission (~7.5%) + best UX
    # FlixBus skipped for SR↔SR → Omio is the sole fallback
    assert 'flixbus' not in keys
    assert 'omio' in keys


def test_resolver_cross_border_includes_flixbus():
    offers = resolve_offers(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo', 'trip-card',
    )
    keys = [o.partner_key for o in offers]
    assert 'bookaway' in keys
    assert 'flixbus' in keys
    assert 'omio' in keys
    # Primary is Bookaway by default ranking
    assert keys[0] == 'bookaway'


def test_resolver_ab_promotes_flixbus():
    # With ab_choice='flixbus', FlixBus should lead even though Bookaway
    # has a higher commission — A/B must override default ranking.
    offers = resolve_offers(
        'beograd', 'sarajevo', 'Beograd', 'Sarajevo',
        ab_choice='flixbus',
    )
    assert offers[0].partner_key == 'flixbus'


def test_resolver_ab_ignored_when_partner_ineligible():
    # AB says flixbus, but flixbus doesn't cover intra-SR → Bookaway wins
    offers = resolve_offers(
        'beograd', 'nis', ab_choice='flixbus',
    )
    assert offers[0].partner_key == 'bookaway'


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
    assert ab_partner_order({'ab_partner': 'flixbus'}, seed='1.2.3.4') == 'flixbus'


def test_ab_ignores_garbage_cookie_value():
    assert ab_partner_order({'ab_partner': 'hax0r'}, seed='') == 'bookaway'


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
    assert captured.get('ab_partner') in ('bookaway', 'flixbus')


def test_ab_splits_roughly_50_50_over_many_seeds():
    # 200 IPs → neither variant should dominate (>70%) if hash is uniform
    from collections import Counter
    c = Counter(ab_partner_order({}, seed=f'10.0.0.{i}') for i in range(200))
    assert c['bookaway'] > 50 and c['flixbus'] > 50

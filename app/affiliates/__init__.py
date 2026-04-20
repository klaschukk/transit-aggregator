"""
Affiliate partner plugins.

Each partner is a subclass of `Partner` with `has_route()` / `build_url()`
hooks; `resolve_offers()` walks the active partner list for a given
origin→destination pair and returns every applicable `Offer`, ordered by
priority (availability → commission → UX rank).

Templates consume the resolved list — the Bookaway-specific URL composition
that used to live in route_detail.html / city_pair.html / search_results.html
moved into `partners.Bookaway.build_url`. Old callers can still pass a
manual `ba_url` to the trip_card macro for the legacy code path.

Typical use from a route handler:

    from app.affiliates import resolve_offers

    offers = resolve_offers(
        from_slug=route['from_city_slug'],
        to_slug=route['to_city_slug'],
        from_city=route['from_city'],
        to_city=route['to_city'],
        utm_medium='route-detail',
    )
    return render_template('route_detail.html', offers=offers, ...)
"""
from app.affiliates.base import Offer, Partner
from app.affiliates.partners import Bookaway, FlixBus, Omio
from app.affiliates.resolve import (
    ACTIVE_PARTNERS,
    ab_partner_order,
    primary_offer,
    resolve_offers,
)

__all__ = [
    'ACTIVE_PARTNERS',
    'Bookaway',
    'FlixBus',
    'Offer',
    'Omio',
    'Partner',
    'ab_partner_order',
    'primary_offer',
    'resolve_offers',
]

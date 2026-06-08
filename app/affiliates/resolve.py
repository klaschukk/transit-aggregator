"""
Pick the best affiliate offer for a route, and the full ranked list.

Selection priority:
  1. `has_route(from, to)` — partner must actually sell the pair
  2. ux_rank (lower wins) — a partner that opens an exact, populated
     checkout (BusTicket4 with a known line_id, ux_rank 0) outconverts one
     that drops the user on a listing/country page (Bookaway, ux_rank 1),
     so checkout quality leads. This deliberately ranks above commission:
     expected revenue is conversion × commission, and a working checkout's
     conversion edge dwarfs Bookaway's higher nominal band on a page that
     historically converted ~0 (the "362 clicks, 0 conversions" fallback).
  3. commission_pct midpoint (higher wins) — tiebreak within an equal ux_rank.

The resolver may return an empty list when no partner covers a pair —
templates already guard with `{% if _buy_href %}` and simply hide the
button. Bookaway is the broadest fallback (its country-page URL covers
any pair where at least one endpoint is in its inventory map).

The A/B stub (`ab_partner_order`) is a cookie-driven pre-sort. With a single
active variant it is effectively a deterministic "prefer the direct-checkout
partner" nudge: it floats the named key to the front _if eligible_, never
disables a partner, so the Bookaway fallback chain stays intact.
"""
from __future__ import annotations

import hashlib

from app.affiliates.base import Offer, Partner
from app.affiliates.partners import Bookaway, BusTicket4, FlixBus

# Instantiate once — partners are stateless, single instances are fine.
# BusTicket4 is now ACTIVE as a pair-level partner: it only reports has_route()
# True for pairs we hold a pre-resolved line_id for (app/affiliates/bt4_lineids.json,
# 406 pairs), so its checkout deep-link always opens a populated departure — the
# old "empty 0.00 € shell" risk that kept it disabled is gone. Where BT4 is
# eligible it LEADS the "Kupi" button (an exact-trip checkout converts better
# than Bookaway's listing fallback, even at a lower commission band — see the
# sort in resolve_offers). Pairs with no known line_id fall through to Bookaway.
# FlixBus is NOT active — we have no affiliate agreement with them, so their
# links earn nothing (just free traffic to FlixBus). The class stays imported
# so it can be re-added here if/when a deal is signed.
ACTIVE_PARTNERS: tuple[Partner, ...] = (
    BusTicket4(),
    Bookaway(),
)


def resolve_offers(
    from_slug: str,
    to_slug: str,
    from_city: str = '',
    to_city: str = '',
    utm_medium: str = 'trip-card',
    ab_choice: str | None = None,
) -> list[Offer]:
    """Return all applicable offers, primary first.

    `ab_choice` is the value of the `ab_partner` cookie (or None).
    When set to a valid partner key, that partner is promoted to the
    front _if_ it is eligible for the route; otherwise the default
    ranking applies.
    """
    if not from_slug or not to_slug or from_slug == to_slug:
        return []

    eligible: list[tuple[Partner, float, int]] = []
    for partner in ACTIVE_PARTNERS:
        if partner.has_route(from_slug, to_slug):
            eligible.append((partner, partner.commission_midpoint, partner.ux_rank))

    # Sort: best checkout quality first (lower ux_rank), then higher commission
    # as a tiebreak. A working exact-trip checkout (BT4 + line_id) leads a
    # listing fallback (Bookaway) regardless of the nominal commission band.
    eligible.sort(key=lambda t: (t[2], -t[1]))

    # A/B promotion: if `ab_choice` names an eligible partner, float it
    # to position 0 (keep others in their checkout-quality order).
    if ab_choice:
        eligible.sort(
            key=lambda t: (0 if t[0].key == ab_choice else 1, t[2], -t[1])
        )

    return [
        p.make_offer(from_slug, to_slug, from_city, to_city, utm_medium)
        for p, _, _ in eligible
    ]


def primary_offer(offers: list[Offer]) -> Offer | None:
    """The single "Kupi" button target. Returns None for empty pairs."""
    return offers[0] if offers else None


# ── A/B assignment ───────────────────────────────────────────────────

_AB_COOKIE = 'ab_partner'
# Single arm: prefer the direct-checkout partner. 'busticket4' floats to the
# front wherever it is eligible (pair has a known line_id); everywhere else only
# Bookaway is eligible, so it leads anyway. A stale 'bookaway' cookie from the
# previous arm is no longer in this tuple, so it's ignored and reassigned. Add a
# real second key here to run an actual partner-order experiment.
_AB_VARIANTS: tuple[str, ...] = ('busticket4',)


def ab_partner_order(
    request_cookies: dict | None,
    response_setter=None,
    seed: str = '',
) -> str:
    """Decide which partner goes first for this user.

    Priority:
      1. Explicit cookie value (stickiness across sessions).
      2. Deterministic hash of `seed` (user IP or session id) — keeps
         the same user on the same variant without needing cookies for
         privacy reasons.
      3. Default → 'bookaway'.

    `response_setter`, if provided, is called with (key, value) to write
    the chosen variant back as a cookie so the next request skips the
    hash. The caller decides cookie attributes (Secure/SameSite/maxage).
    """
    cookies = request_cookies or {}
    existing = cookies.get(_AB_COOKIE)
    if existing in _AB_VARIANTS:
        return existing

    # Deterministic assignment from seed (stable without writing cookies)
    if seed:
        h = int(hashlib.sha256(seed.encode('utf-8')).hexdigest()[:8], 16)
        choice = _AB_VARIANTS[h % len(_AB_VARIANTS)]
    else:
        choice = _AB_VARIANTS[0]

    if response_setter is not None:
        response_setter(_AB_COOKIE, choice)
    return choice

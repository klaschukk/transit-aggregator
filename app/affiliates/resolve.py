"""
Pick the best affiliate offer for a route, and the full ranked list.

Selection priority (spec):
  1. `has_route(from, to)` — partner must actually sell the pair
  2. commission_pct midpoint (higher wins)
  3. ux_rank (lower wins — 1 is best)

The resolver may return an empty list when no partner covers a pair —
templates already guard with `{% if _buy_href %}` and simply hide the
button. Bookaway is the broadest fallback (its country-page URL covers
any pair where at least one endpoint is in its inventory map).

The A/B stub (`ab_partner_order`) is a cookie-driven pre-sort that flips
Bookaway ↔ FlixBus for half the traffic. The resolver applies it as a
"promote this key to the front if it's eligible" nudge — it does not
disable partners, so the fallback chain stays intact.
"""
from __future__ import annotations

import hashlib

from app.affiliates.base import Offer, Partner
from app.affiliates.partners import Bookaway, FlixBus

# Instantiate once — partners are stateless, single instances are fine.
ACTIVE_PARTNERS: tuple[Partner, ...] = (
    Bookaway(),
    FlixBus(),
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

    # Sort: higher commission first, then lower ux_rank first.
    eligible.sort(key=lambda t: (-t[1], t[2]))

    # A/B promotion: if `ab_choice` names an eligible partner, float it
    # to position 0 (keep others in their scored order).
    if ab_choice:
        eligible.sort(
            key=lambda t: (0 if t[0].key == ab_choice else 1, -t[1], t[2])
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
_AB_VARIANTS: tuple[str, ...] = ('bookaway', 'flixbus')


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

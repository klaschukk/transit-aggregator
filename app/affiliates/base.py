"""
Partner / Offer base classes shared by every affiliate plugin.

A `Partner` captures the _static_ properties of an affiliate program
(commission band, cookie window, UX rank) and the _routing_ logic for
deciding whether a given origin→destination pair is worth handing off.
`has_route()` is the fast filter that the resolver uses first; the
heavier commission + UX scoring only runs on partners that pass it.

An `Offer` is the frozen per-request output — what the template actually
renders. It carries the final URL (already UTM-stamped), the partner's
display name, brand colour, and the commission estimate used for
ordering. Offers are intentionally immutable so the resolver can return
a tuple safely.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Offer:
    """Concrete, ready-to-render affiliate offer for one route."""
    partner_key: str        # 'bookaway', 'flixbus'
    partner_name: str       # 'Bookaway', 'FlixBus'
    url: str                # full URL with affiliate IDs + UTM params
    brand_color: str        # CSS colour for the button (hex)
    commission_pct: float   # midpoint of declared band — for ordering only
    ux_rank: int            # 1 = best, 5 = worst (tiebreak after commission)


class Partner:
    """Base class for affiliate partners.

    Subclasses set class-level config (`key`, `name`, `brand_color`,
    `commission_band`, `ux_rank`) and override the two hot-path methods
    below. Everything else is shared.
    """
    key: str = ''
    name: str = ''
    brand_color: str = '#0d9488'
    # (min, max) — midpoint feeds Offer.commission_pct for ordering
    commission_band: tuple[float, float] = (0.0, 0.0)
    ux_rank: int = 3

    # ── override in subclass ─────────────────────────────────────────

    def has_route(self, from_slug: str, to_slug: str) -> bool:
        """Return True if the partner sells tickets for this pair.

        Keep this cheap — it runs on every trip card. Don't hit network
        or DB; rely on the city-country mapping baked into the subclass.
        """
        raise NotImplementedError

    def build_url(
        self,
        from_slug: str,
        to_slug: str,
        from_city: str,
        to_city: str,
        utm_medium: str,
    ) -> str:
        """Return the deep-link URL (affiliate IDs + UTM params included)."""
        raise NotImplementedError

    # ── shared helpers ───────────────────────────────────────────────

    @property
    def commission_midpoint(self) -> float:
        lo, hi = self.commission_band
        return (lo + hi) / 2

    def make_offer(
        self,
        from_slug: str,
        to_slug: str,
        from_city: str,
        to_city: str,
        utm_medium: str,
    ) -> Offer:
        """Factory — subclasses rarely override this."""
        return Offer(
            partner_key=self.key,
            partner_name=self.name,
            url=self.build_url(from_slug, to_slug, from_city, to_city, utm_medium),
            brand_color=self.brand_color,
            commission_pct=self.commission_midpoint,
            ux_rank=self.ux_rank,
        )

"""
Concrete affiliate-partner plugins: Bookaway, FlixBus.

Each class declares (1) which origin→destination pairs it can monetise
via `has_route()` and (2) how to build the deep-link URL with tracking
params. Coverage maps are intentionally hand-curated rather than
derived from the route DB — the answer to "does partner X sell
tickets for SR↔TR?" is a _business_ fact, not a transit-schedule fact,
and shouldn't change just because we rescrape tonight.

When adding a new partner:
  1. Subclass `Partner`, set key/name/brand_color/commission_band/ux_rank.
  2. Implement `has_route()` using slug inclusion against your country
     set — keep it O(1), this runs per trip card.
  3. Implement `build_url()` — if the partner requires a real affiliate
     ID you don't have yet, use a placeholder constant at the top of the
     file and write `# TODO: replace once approved` next to it. The
     URL will still be valid (points to the partner site), just
     untracked.
  4. Add the class to `ACTIVE_PARTNERS` in resolve.py.
"""
from __future__ import annotations

from app.affiliates.base import Partner

# ── Bookaway — primary partner (already approved) ──────────────────
_BOOKAWAY_COUNTRY_MAP: dict[str, str] = {
    # Serbia
    'beograd': 'serbia', 'novi-sad': 'serbia', 'nis': 'serbia',
    'subotica': 'serbia', 'kragujevac': 'serbia', 'uzice': 'serbia',
    'valjevo': 'serbia', 'sabac': 'serbia', 'cacak': 'serbia',
    'kraljevo': 'serbia', 'krusevac': 'serbia', 'leskovac': 'serbia',
    'vranje': 'serbia', 'pirot': 'serbia', 'sombor': 'serbia',
    'zrenjanin': 'serbia', 'pancevo': 'serbia', 'smederevo': 'serbia',
    'novi-pazar': 'serbia', 'loznica': 'serbia', 'kikinda': 'serbia',
    'jagodina': 'serbia', 'pozarevac': 'serbia', 'zajecar': 'serbia',
    'sremska-mitrovica': 'serbia', 'bor': 'serbia', 'vrsac': 'serbia',
    # Montenegro
    'podgorica': 'montenegro', 'budva': 'montenegro', 'bar': 'montenegro',
    'herceg-novi': 'montenegro', 'kotor': 'montenegro', 'tivat': 'montenegro',
    'niksic': 'montenegro', 'ulcinj': 'montenegro',
    # Bosnia
    'sarajevo': 'bosnia-and-herzegovina', 'banja-luka': 'bosnia-and-herzegovina',
    'tuzla': 'bosnia-and-herzegovina', 'mostar': 'bosnia-and-herzegovina',
    'trebinje': 'bosnia-and-herzegovina', 'zenica': 'bosnia-and-herzegovina',
    'bihac': 'bosnia-and-herzegovina', 'brcko': 'bosnia-and-herzegovina',
    # Croatia
    'zagreb': 'croatia', 'split': 'croatia', 'dubrovnik': 'croatia',
    'rijeka': 'croatia', 'osijek': 'croatia', 'zadar': 'croatia',
    'pula': 'croatia',
    # North Macedonia
    'skopje': 'north-macedonia', 'skoplje': 'north-macedonia',
    'ohrid': 'north-macedonia', 'bitola': 'north-macedonia',
    'bitolj': 'north-macedonia', 'kumanovo': 'north-macedonia',
    'tetovo': 'north-macedonia', 'prilep': 'north-macedonia',
    'stip': 'north-macedonia',
    # Others Bookaway covers
    'budapest': 'hungary', 'budimpesta': 'hungary', 'szeged': 'hungary',
    'segedin': 'hungary', 'pecs': 'hungary',
    'sofia': 'bulgaria', 'sofija': 'bulgaria', 'plovdiv': 'bulgaria',
    'varna': 'bulgaria',
    'athens': 'greece', 'atina': 'greece', 'thessaloniki': 'greece',
    'solun': 'greece',
    'istanbul': 'turkey', 'ankara': 'turkey', 'izmir': 'turkey',
    'vienna': 'austria',
    'ljubljana': 'slovenia', 'maribor': 'slovenia',
    'timisoara': 'romania', 'bucharest': 'romania', 'bukurest': 'romania',
    'brasov': 'romania',
    'tirana': 'albania', 'drac': 'albania', 'valona': 'albania',
}


class Bookaway(Partner):
    """Primary partner. Strongest Balkans coverage, highest commission band."""
    key = 'bookaway'
    name = 'Bookaway'
    # Bookaway brand is emerald-600 (#059669); at 13.6 px normal white its
    # ratio on white text is 3.76:1 (WCAG AA fail). Stepping down one tone
    # to emerald-700 (#047857) clears 4.65:1 and is virtually indistinguishable
    # to the eye — and matches the old :hover, so there's no flicker. The
    # primary revenue CTA must pass AA first; brand exactness second.
    brand_color = '#047857'
    commission_band = (5.0, 10.0)
    ux_rank = 1

    OFFER_ID = 34       # approved
    AFF_ID = 4033       # approved

    def has_route(self, from_slug: str, to_slug: str) -> bool:
        # Bookaway covers a pair if *either* endpoint is in its inventory.
        # When only one endpoint matches, build_url falls back to the
        # country listing page (a URL that always exists) — that keeps
        # the affiliate query string alive instead of letting Bookaway's
        # own redirect strip it on a non-existent route page.
        return from_slug in _BOOKAWAY_COUNTRY_MAP or to_slug in _BOOKAWAY_COUNTRY_MAP

    def build_url(
        self,
        from_slug: str,
        to_slug: str,
        from_city: str,
        to_city: str,
        utm_medium: str,
    ) -> str:
        from_country = _BOOKAWAY_COUNTRY_MAP.get(from_slug)
        to_country = _BOOKAWAY_COUNTRY_MAP.get(to_slug)
        country = to_country or from_country or 'serbia'
        tracking = (
            f'?offer_id={self.OFFER_ID}&aff_id={self.AFF_ID}'
            f'&utm_source=prevozni&utm_medium={utm_medium}'
        )
        # Both endpoints in inventory → deep-link to the route page.
        # Otherwise fall back to the country listing — Bookaway has no
        # page for e.g. mladenovac-to-beograd and their redirect strips
        # query params, so we'd lose attribution. The country page exists
        # and preserves ?offer_id/aff_id, so the cookie still gets set.
        if from_country and to_country:
            path = f'/routes/{country}/{from_slug}-to-{to_slug}'
        else:
            path = f'/routes/{country}/'
        return f'https://www.bookaway.com{path}{tracking}'


# ── FlixBus — cross-border corridors (owned operator) ──────────────
_FLIXBUS_COUNTRY_HUBS: frozenset[str] = frozenset({
    # FlixBus sells on these slugs (cross-border Balkan + Central Europe
    # corridors). They do not run intra-Serbia trips, so has_route
    # returns False when *both* endpoints are Serbian.
    'beograd', 'novi-sad', 'nis', 'subotica',
    'zagreb', 'split', 'dubrovnik', 'rijeka', 'zadar', 'osijek', 'pula',
    'sarajevo', 'banja-luka', 'tuzla', 'mostar',
    'podgorica', 'budva', 'herceg-novi', 'kotor',
    'skopje', 'skoplje', 'ohrid',
    'sofia', 'sofija', 'plovdiv', 'varna', 'burgas',
    'athens', 'atina', 'thessaloniki', 'solun',
    'ljubljana', 'maribor',
    'budapest', 'budimpesta', 'szeged', 'segedin',
    'bucharest', 'bukurest', 'timisoara', 'brasov',
    'tirana', 'drac',
    'istanbul', 'ankara', 'izmir',
    'vienna', 'munich', 'frankfurt', 'berlin', 'prague', 'bratislava',
})

_SERBIAN_CITIES: frozenset[str] = frozenset({
    'beograd', 'novi-sad', 'nis', 'subotica', 'kragujevac', 'uzice',
    'valjevo', 'sabac', 'cacak', 'kraljevo', 'krusevac', 'leskovac',
    'vranje', 'pirot', 'sombor', 'zrenjanin', 'pancevo', 'smederevo',
    'novi-pazar', 'loznica', 'kikinda', 'jagodina', 'pozarevac',
    'zajecar', 'sremska-mitrovica', 'bor', 'vrsac',
})


class FlixBus(Partner):
    """Cross-border Balkan + CEE corridors. No intra-Serbia coverage."""
    key = 'flixbus'
    name = 'FlixBus'
    brand_color = '#73d700'
    commission_band = (3.0, 5.0)
    ux_rank = 2

    # TODO: replace once Awin approval lands — until then the URL still
    # works, just without click attribution. No revenue but no breakage.
    AWIN_ID: str = 'PLACEHOLDER'

    def has_route(self, from_slug: str, to_slug: str) -> bool:
        # Both endpoints must be in FlixBus's network, and at least one
        # must be non-Serbian (they don't run domestic SR).
        if from_slug not in _FLIXBUS_COUNTRY_HUBS or to_slug not in _FLIXBUS_COUNTRY_HUBS:
            return False
        if from_slug in _SERBIAN_CITIES and to_slug in _SERBIAN_CITIES:
            return False
        return True

    def build_url(
        self,
        from_slug: str,
        to_slug: str,
        from_city: str,
        to_city: str,
        utm_medium: str,
    ) -> str:
        # Direct deep-link to FlixBus search; Awin wraps this with a click
        # redirector once the placeholder ID is replaced with a real one.
        base = (
            f'https://global.flixbus.com/bus/{from_slug}-{to_slug}'
            f'?utm_source=prevozni&utm_medium={utm_medium}'
            f'&utm_campaign=affiliate'
        )
        if self.AWIN_ID != 'PLACEHOLDER':
            base += f'&awin_id={self.AWIN_ID}'
        return base



"""Door-to-door offers (private transfer, rental car) for tourist corridors.

Dormant by default: nothing renders until the owner pastes an affiliate link
into the environment (see config.py). The corridor list is business knowledge,
not derived from the timetable DB — these are the pairs where visitors, in
practice English-speaking tourists on the Montenegrin coast / Bosnia / Dubrovnik
side, want a ride from door to door or a car rather than a scheduled bus.

The click is logged by the same tracker as bus CTAs (data-partner = 'transfer'
or 'cars'), so /admin shows per-route CTR before any revenue arrives.
"""
from __future__ import annotations

from urllib.parse import quote

from flask import current_app

# Cities whose mutual pairs make sense for a transfer / rental car. Both ends
# must be in the set: Belgrade <-> Budva is a 10 h coach trip, not a transfer.
TOURIST_CITIES: frozenset[str] = frozenset({
    'kotor', 'budva', 'tivat', 'herceg-novi', 'bar', 'ulcinj', 'podgorica',
    'cetinje', 'niksic', 'dubrovnik', 'mostar', 'sarajevo', 'trebinje',
    'skadar', 'shkoder', 'tirana', 'split',
})

# (partner key used in ba_clicks, config URL key, config name key)
_KINDS = (
    ('transfer', 'AFF_TRANSFER_URL', 'AFF_TRANSFER_NAME'),
    ('cars', 'AFF_CARS_URL', 'AFF_CARS_NAME'),
)


def is_tourist_corridor(from_slug: str, to_slug: str) -> bool:
    return bool(from_slug and to_slug and from_slug != to_slug
                and from_slug in TOURIST_CITIES and to_slug in TOURIST_CITIES)


def _fill(template: str, from_slug: str, to_slug: str, from_name: str, to_name: str) -> str:
    """Optional placeholders so a deep link can carry the pair; a plain link works too."""
    for token, value in (('{from}', from_slug), ('{to}', to_slug),
                         ('{from_name}', from_name), ('{to_name}', to_name)):
        template = template.replace(token, quote(value or '', safe=''))
    return template


def transfer_offers(from_slug: str, to_slug: str,
                    from_name: str = '', to_name: str = '') -> list[dict]:
    """Configured offers for this pair, or [] (not a corridor / nothing configured)."""
    if not is_tourist_corridor(from_slug, to_slug):
        return []
    cfg = current_app.config
    offers = []
    for key, url_key, name_key in _KINDS:
        url = (cfg.get(url_key) or '').strip()
        # https only: the value comes from the environment, but never emit a
        # javascript:/data: href into a page.
        if not url.startswith('https://'):
            continue
        offers.append({
            'key': key,
            'name': (cfg.get(name_key) or '').strip(),
            'url': _fill(url, from_slug, to_slug, from_name, to_name),
        })
    return offers

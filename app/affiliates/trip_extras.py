"""Per-stop and per-trip offers on the Balkan Loop planner (app/planner.py).

Same contract as transfers.py: dormant until the owner pastes an https
affiliate link into data/affiliates.local.json (or the environment). A stay
and a tours link are rendered once per stop, eSIM and insurance once per trip.
Clicks are logged through /api/ba-click with the kind as the partner key.
"""
from __future__ import annotations

from urllib.parse import quote

from flask import current_app

# (partner key in ba_clicks, config URL key, config name key)
STOP_KINDS = (
    ('stay', 'AFF_STAY_URL', 'AFF_STAY_NAME'),
    ('tours', 'AFF_TOURS_URL', 'AFF_TOURS_NAME'),
)
TRIP_KINDS = (
    ('esim', 'AFF_ESIM_URL', 'AFF_ESIM_NAME'),
    ('insurance', 'AFF_INSURANCE_URL', 'AFF_INSURANCE_NAME'),
)
PARTNER_KEYS = tuple(k for k, _u, _n in STOP_KINDS + TRIP_KINDS)


def _offers(kinds: tuple, city: str = '') -> list[dict]:
    cfg = current_app.config
    offers = []
    for key, url_key, name_key in kinds:
        url = (cfg.get(url_key) or '').strip()
        # https only: never emit a javascript:/data: href into a page.
        if not url.startswith('https://'):
            continue
        offers.append({
            'key': key,
            'name': (cfg.get(name_key) or '').strip(),
            # Optional {city} placeholder so a search deep link lands on the stop.
            'url': url.replace('{city}', quote(city, safe='')),
        })
    return offers


def stop_offers(city: str) -> list[dict]:
    """Configured stay/tours offers for one stop, or []."""
    return _offers(STOP_KINDS, city)


def trip_offers() -> list[dict]:
    """Configured whole-trip offers (eSIM, insurance), or []."""
    return _offers(TRIP_KINDS)

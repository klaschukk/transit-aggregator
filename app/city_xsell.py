"""Intercity cross-sell for city-transport pages (/gradski/...).

City pages bring most of the site's Google traffic but carry no partner link.
This picks the few intercity routes leaving that city that people actually
buy (ba_clicks, 30 days), then most departures, and attaches today's next
departure and the cheapest known fare. Real timetable rows only: a route with
nothing left today still shows, without a time, and no price is ever guessed.
"""
import re
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from app.db import cached_query, db_ready

_CLICKS_TTL = 6 * 3600

# Stops at intercity bus / train stations, where a visitor is most likely
# about to leave town: the block moves above the line list there.
_HUB_STOP = re.compile(r'(^|-)(bas|lasta|beograd-centar)$|autobuska-stanica|zeleznicka-stanica')


def is_hub_stop(stop_slug: str) -> bool:
    return bool(_HUB_STOP.search(stop_slug or ''))
_clicks_lock = threading.Lock()
_clicks_cache: dict = {'expires': 0.0, 'data': {}}


def _now_belgrade() -> datetime:
    """Serbia wall clock. Wrapped so tests can pin the time of day."""
    return datetime.now(ZoneInfo('Europe/Belgrade'))


def _route_clicks() -> dict[str, int]:
    """Buy clicks per route slug over 30 days, cached for 6 h. Empty on any
    analytics-DB problem: ranking then falls back to departure counts."""
    now = time.time()
    with _clicks_lock:
        if now < _clicks_cache['expires']:
            return _clicks_cache['data']
    from app import analytics_db
    rows = analytics_db.query(
        "SELECT route_slug, COUNT(*) AS n FROM ba_clicks "
        "WHERE ts > datetime('now', '-30 days') AND route_slug != '' GROUP BY route_slug")
    data = {r['route_slug']: r['n'] for r in rows}
    with _clicks_lock:
        _clicks_cache.update(expires=now + _CLICKS_TTL, data=data)
    return data


def intercity_from_city(city: str, limit: int = 3) -> list[dict]:
    """Top intercity routes from `city` (a /gradski/ slug) with today's next
    departure. Each item: slug, to_city, to_slug, from_slug, next_time,
    next_in_min, price_min, bt4_line_id (of the next departure), left_today,
    trips_today, date (ISO, Serbia's today — the checkout's travel day)."""
    if not db_ready():
        return []
    trips = cached_query("""
        SELECT r.slug, r.to_city, r.to_city_slug, t.departure_time, t.price_rsd,
               t.days_of_week, t.bt4_line_id
        FROM routes r JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity' AND r.from_city_slug = ?
          AND t.departure_time IS NOT NULL AND t.departure_time != ''
        ORDER BY r.slug, t.departure_time
    """, [city], ttl=1800)
    if not trips:
        return []

    now = _now_belgrade()
    weekday = str(now.isoweekday())
    now_hhmm = now.strftime('%H:%M')
    now_min = now.hour * 60 + now.minute

    routes: dict[str, dict] = {}
    for t in trips:
        r = routes.setdefault(t['slug'], {
            'slug': t['slug'], 'to_city': t['to_city'], 'to_slug': t['to_city_slug'],
            'from_slug': city, 'date': now.date().isoformat(), 'trips_today': 0, 'left_today': 0, 'next_time': None,
            'next_in_min': None, 'price_min': None, 'bt4_line_id': None,
        })
        if t['price_rsd'] and t['price_rsd'] > 0:
            r['price_min'] = t['price_rsd'] if r['price_min'] is None else min(r['price_min'], t['price_rsd'])
        if weekday not in (t['days_of_week'] or '1234567'):
            continue
        r['trips_today'] += 1
        dep = t['departure_time'][:5]
        if len(dep) == 5 and dep > now_hhmm:
            r['left_today'] += 1
            if r['next_time'] is None:
                r['next_time'] = dep
                r['next_in_min'] = int(dep[:2]) * 60 + int(dep[3:5]) - now_min
                # Buy link only for the departure shown: a lineId preselects
                # that exact trip in the BT4 checkout, so borrowing another
                # trip's id would sell a different time than the row says.
                r['bt4_line_id'] = t['bt4_line_id']

    clicks = _route_clicks()
    ranked = sorted((r for r in routes.values() if r['trips_today']),
                    key=lambda r: (-clicks.get(r['slug'], 0), -r['trips_today'], r['slug']))
    return ranked[:limit]

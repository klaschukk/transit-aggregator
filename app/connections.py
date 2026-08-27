"""1-hop connection suggestions for /pretraga/ when no direct route exists.

Search only ever matched an EXACT (from_city, to_city) pair — most city
combinations have no direct route (591 direct routes over ~80 cities), so a
search like "Zaječar -> Kraljevo" returned a bare "no results" even though
a same-day connection through Beograd is completely real: Zaječar->Beograd
and Beograd->Kraljevo both run, scraped, in the DB right now. Rome2Rio's
whole reason to exist is exactly this — "no direct route" isn't "no route".

Deliberately NOT a general N-hop pathfinder: that's real routing-engine
work (weighted graph search, city-transit legs, multi-day itineraries).
This is one honest hop — from_city -> via_city -> to_city — computed from
data already in DuckDB, live at request time (plain SQL + Python, not a
3rd-party call, so no cache-only constraint applies here unlike
ai_compose.py or the Directions-based route geometry).

Known limitation: does not filter trips.days_of_week, so a suggested
connection could nominally include a leg that doesn't run on the searched
date. Acceptable for a first pass — flagged, not silently pretended away.
"""
from app.db import query

MIN_CONNECTION_MIN = 20    # shortest sane wait to catch the next leg
MAX_CONNECTION_MIN = 240   # longest wait still worth suggesting (4h)
MAX_VIA_CANDIDATES = 8     # cap the via-city fan-out query scans
MAX_RESULTS = 3            # via-cities shown to the user


def _to_minutes(hhmm: str) -> int | None:
    try:
        h, m = hhmm.split(':')
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return None


def _best_pairing(leg1_trips: list, leg2_trips: list) -> dict | None:
    """Cheapest-total-time (leg1.departure -> leg2.arrival) same-day pairing
    across every leg1 x leg2 combination, or None if nothing connects within
    MIN/MAX_CONNECTION_MIN. O(n*m) but n and m are single-route trip counts
    (tens, not thousands) — fine at request time."""
    best = None
    best_span = None
    for t1 in leg1_trips:
        arr1 = _to_minutes(t1.get('arrival_time'))
        dep1 = _to_minutes(t1.get('departure_time'))
        if arr1 is None or dep1 is None:
            continue
        for t2 in leg2_trips:
            dep2 = _to_minutes(t2.get('departure_time'))
            arr2 = _to_minutes(t2.get('arrival_time'))
            if dep2 is None or arr2 is None:
                continue
            wait = dep2 - arr1
            if wait < MIN_CONNECTION_MIN or wait > MAX_CONNECTION_MIN:
                continue
            span = arr2 - dep1 if arr2 >= dep1 else arr2 + 24 * 60 - dep1
            if best_span is None or span < best_span:
                best_span = span
                best = {'leg1': t1, 'leg2': t2, 'wait_min': wait}
    return best


def find_connections(from_city: str, to_city: str) -> list[dict]:
    """Up to MAX_RESULTS one-hop connections, each:
    {'via_city', 'via_slug', 'leg1_route_slug', 'leg2_route_slug',
     'leg1': trip row, 'leg2': trip row, 'wait_min', 'total_price_rsd'}
    ranked by shortest total journey time. Empty list if nothing connects
    (or a direct route exists — callers should only reach for this on a
    genuinely empty direct search)."""
    vias = query("""
        SELECT DISTINCT r1.to_city AS via_city, r1.to_city_slug AS via_slug,
               r1.id AS leg1_id, r2.id AS leg2_id,
               r1.slug AS leg1_route_slug, r2.slug AS leg2_route_slug
        FROM routes r1
        JOIN routes r2 ON r2.from_city = r1.to_city
        WHERE lower(r1.from_city) = lower(?) AND lower(r2.to_city) = lower(?)
          AND r1.type = 'intercity' AND r2.type = 'intercity'
          AND lower(r1.from_city) != lower(r2.to_city)
        LIMIT ?
    """, [from_city, to_city, MAX_VIA_CANDIDATES])

    out = []
    for via in vias:
        leg1_trips = query("""
            SELECT t.departure_time, t.arrival_time, t.price_rsd,
                   COALESCE(o.name, '') AS operator
            FROM trips t LEFT JOIN operators o ON o.id = t.operator_id
            WHERE t.route_id = ? AND t.departure_time IS NOT NULL AND t.departure_time != ''
            ORDER BY t.departure_time
        """, [via['leg1_id']])
        leg2_trips = query("""
            SELECT t.departure_time, t.arrival_time, t.price_rsd,
                   COALESCE(o.name, '') AS operator
            FROM trips t LEFT JOIN operators o ON o.id = t.operator_id
            WHERE t.route_id = ? AND t.departure_time IS NOT NULL AND t.departure_time != ''
            ORDER BY t.departure_time
        """, [via['leg2_id']])
        if not leg1_trips or not leg2_trips:
            continue
        pairing = _best_pairing(leg1_trips, leg2_trips)
        if not pairing:
            continue
        p1, p2 = pairing['leg1'].get('price_rsd'), pairing['leg2'].get('price_rsd')
        out.append({
            'via_city': via['via_city'], 'via_slug': via['via_slug'],
            'leg1_route_slug': via['leg1_route_slug'],
            'leg2_route_slug': via['leg2_route_slug'],
            'leg1': pairing['leg1'], 'leg2': pairing['leg2'],
            'wait_min': pairing['wait_min'],
            'total_price_rsd': (p1 + p2) if (p1 and p2) else None,
        })

    out.sort(key=lambda c: _to_minutes(c['leg2']['arrival_time']) or 9999)
    return out[:MAX_RESULTS]

"""Balkan Loop planner: a multi-stop itinerary built from real direct buses.

Visitors on the tourist corridors (Kotor, Mostar, Tirana, Dubrovnik ...) are
mostly doing the same multi-country loop and today plan it one leg at a time.
This turns "start, end, N days" into an ordered list of stops where every leg
is a direct route that exists in the timetable DB right now — departures, the
shortest duration and the lowest known fare all come from `routes`/`trips`.

Deterministic on purpose (no model call): a small search over the stop graph,
so the page is cache-friendly and never invents a connection. What IS
editorial is the stop list itself (which cities belong on the loop, how much
they are worth a stop and how many nights they usually take) — see STOPS.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.db import cached_query

MIN_DAYS = 4
MAX_DAYS = 21
DEFAULT_PLAN = ('dubrovnik', 'tirana', 10)

# Curated itineraries with their own indexable URL (/balkan-loop/<slug>/).
# Everything else is a query variant of the hub and stays out of the index.
PRESETS: tuple[tuple[str, str, int], ...] = (
    ('dubrovnik', 'tirana', 10),
    ('split', 'tirana', 14),
    ('dubrovnik', 'ohrid', 14),
    ('dubrovnik', 'dubrovnik', 14),
    ('kotor', 'sarajevo', 7),
    ('tirana', 'skoplje', 7),
    ('beograd', 'tirana', 21),
)


def preset_slug(start: str, end: str, days: int) -> str:
    if start == end:
        return f'{start}-loop-{days}-days'
    return f'{start}-{end}-{days}-days'


PRESET_BY_SLUG: dict[str, tuple[str, str, int]] = {preset_slug(*p): p for p in PRESETS}

MAX_LEG_MIN = 540          # longest single bus leg worth planning around (9 h)
UNKNOWN_LEG_MIN = 240      # scoring stand-in when the source has no duration
MAX_STOPS = 8
HOUR_TAX = 1.25            # appeal points one hour on a bus costs
STOP_COST = 2.5            # appeal points one more change of bed costs
TURN_COST = 6.0            # appeal points doubling back on yourself costs
SEARCH_BUDGET = 150_000    # node expansions; the stop graph is tiny but dense

# slug -> (country, appeal 1-10, minimum nights, comfortable nights).
# Slugs are the DB's city slugs (Serbian exonyms: skadar = Shkodër).
STOPS: dict[str, tuple[str, int, int, int]] = {
    'dubrovnik':   ('HR', 10, 2, 3),
    'split':       ('HR', 8, 2, 3),
    'kotor':       ('ME', 10, 2, 3),
    'budva':       ('ME', 6, 1, 2),
    'herceg-novi': ('ME', 3, 1, 1),
    'podgorica':   ('ME', 2, 1, 1),
    'skadar':      ('AL', 6, 1, 2),
    'tirana':      ('AL', 7, 2, 2),
    'ohrid':       ('MK', 8, 2, 3),
    'skoplje':     ('MK', 5, 1, 2),
    'mostar':      ('BA', 9, 1, 2),
    'sarajevo':    ('BA', 9, 2, 3),
    'beograd':     ('RS', 7, 2, 3),
}

# Approximate (lat, lon), used only to notice a route doubling back on itself.
_COORDS: dict[str, tuple[float, float]] = {
    'dubrovnik': (42.65, 18.09), 'split': (43.51, 16.44), 'kotor': (42.42, 18.77),
    'budva': (42.29, 18.84), 'herceg-novi': (42.45, 18.54), 'podgorica': (42.44, 19.26),
    'skadar': (42.07, 19.51), 'tirana': (41.33, 19.82), 'ohrid': (41.12, 20.80),
    'skoplje': (42.00, 21.43), 'mostar': (43.34, 17.81), 'sarajevo': (43.86, 18.41),
    'beograd': (44.82, 20.46),
}

# Display names where the DB's Serbian exonym is not what a visitor expects.
_NAMES: dict[str, dict[str, str]] = {
    'beograd': {'en': 'Belgrade', 'ru': 'Белград', 'bg': 'Белград'},
    'skadar': {'en': 'Shkodër', 'ru': 'Шкодер', 'bg': 'Шкодра'},
    'skoplje': {'en': 'Skopje', 'ru': 'Скопье', 'bg': 'Скопие'},
    'dubrovnik': {'ru': 'Дубровник', 'bg': 'Дубровник'},
    'split': {'ru': 'Сплит', 'bg': 'Сплит'},
    'kotor': {'ru': 'Котор', 'bg': 'Котор'},
    'budva': {'ru': 'Будва', 'bg': 'Будва'},
    'herceg-novi': {'ru': 'Херцег-Нови', 'bg': 'Херцег Нови'},
    'podgorica': {'ru': 'Подгорица', 'bg': 'Подгорица'},
    'tirana': {'ru': 'Тирана', 'bg': 'Тирана'},
    'ohrid': {'ru': 'Охрид', 'bg': 'Охрид'},
    'mostar': {'ru': 'Мостар', 'bg': 'Мостар'},
    'sarajevo': {'ru': 'Сараево', 'bg': 'Сараево'},
}
_DB_NAMES = {
    'dubrovnik': 'Dubrovnik', 'split': 'Split', 'kotor': 'Kotor', 'budva': 'Budva',
    'herceg-novi': 'Herceg Novi', 'podgorica': 'Podgorica', 'skadar': 'Skadar',
    'tirana': 'Tirana', 'ohrid': 'Ohrid', 'skoplje': 'Skoplje', 'mostar': 'Mostar',
    'sarajevo': 'Sarajevo', 'beograd': 'Beograd',
}


def stop_name(slug: str, lang: str = 'sr') -> str:
    return _NAMES.get(slug, {}).get(lang) or _DB_NAMES.get(slug, slug)


def load_legs() -> dict[tuple[str, str], dict]:
    """Direct bus legs between loop stops: (from, to) -> leg facts from the DB.

    Only routes with at least one active trip. Where a pair has more than one
    route row, the one with the most departures wins.
    """
    slugs = list(STOPS)
    marks = ','.join('?' * len(slugs))
    rows = cached_query(f"""
        SELECT r.from_city_slug AS f, r.to_city_slug AS t, r.slug,
               COUNT(t.id) AS trips,
               MIN(t.duration_min) FILTER (WHERE t.duration_min > 0) AS duration_min,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) AS price_rsd,
               MIN(t.departure_time) AS first_dep,
               MAX(t.departure_time) AS last_dep
        FROM routes r JOIN trips t ON t.route_id = r.id AND t.is_active
        WHERE r.type = 'intercity'
          AND r.from_city_slug IN ({marks}) AND r.to_city_slug IN ({marks})
          AND r.from_city_slug != r.to_city_slug
        GROUP BY r.from_city_slug, r.to_city_slug, r.slug
    """, slugs + slugs, ttl=3600)
    legs: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (row['f'], row['t'])
        if key not in legs or row['trips'] > legs[key]['trips']:
            legs[key] = dict(row)
    return legs


def _usable(leg: dict) -> bool:
    return not leg.get('duration_min') or leg['duration_min'] <= MAX_LEG_MIN


def _turn_back(a: str, b: str, c: str) -> bool:
    """True when a -> b -> c reverses direction (b is a dead-end detour)."""
    (la, lo), (lb, lob), (lc, loc) = _COORDS[a], _COORDS[b], _COORDS[c]
    k = 0.74  # cos(latitude ~42.5): shrink longitude degrees to latitude scale
    v1, v2 = (lb - la, (lob - lo) * k), (lc - lb, (loc - lob) * k)
    n1 = (v1[0] ** 2 + v1[1] ** 2) ** 0.5
    n2 = (v2[0] ** 2 + v2[1] ** 2) ** 0.5
    if not n1 or not n2:
        return False
    return (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2) < -0.5


def _score(path: tuple[str, ...], minutes: int, days: int, loop: bool) -> float:
    """Appeal of the stops, minus a fixed cost per stop (so a short trip is not
    chopped into one-night hops), minus an hour-on-the-bus tax, minus idle days
    the stops cannot comfortably absorb (14 days in two towns is a bad plan)."""
    stops = path[:-1] if loop else path
    appeal = sum(STOPS[s][1] - STOP_COST for s in stops)
    absorbable = sum(STOPS[s][3] + 1 for s in stops)
    turns = sum(_turn_back(a, b, c) for a, b, c in zip(path, path[1:], path[2:]))
    return (appeal - HOUR_TAX * minutes / 60.0 - TURN_COST * turns
            - 2.0 * max(0, days - absorbable))


def _search(graph: dict[str, tuple[tuple[str, int], ...]], start: str, end: str,
            days: int, via: frozenset[str] = frozenset()) -> tuple[str, ...] | None:
    loop = start == end
    best: tuple[float, tuple[str, ...]] | None = None
    budget = SEARCH_BUDGET

    def walk(path: tuple[str, ...], nights: int, minutes: int) -> None:
        nonlocal best, budget
        budget -= 1
        if budget < 0:
            return
        here = path[-1]
        for nxt, dur in graph.get(here, ()):
            if nxt == end and len(path) >= (3 if loop else 1):
                done = path + (nxt,)
                total = nights + (0 if loop else STOPS[nxt][2])
                if total <= days and via.issubset(done):
                    sc = _score(done, minutes + dur, days, loop)
                    if best is None or sc > best[0]:
                        best = (sc, done)
            if nxt in path or nxt == end:
                continue
            n2 = nights + STOPS[nxt][2]
            # Leave room for the end stop's own minimum on a one-way plan.
            if n2 + (0 if loop else STOPS[end][2]) > days or len(path) >= MAX_STOPS:
                continue
            walk(path + (nxt,), n2, minutes + dur)

    walk((start,), STOPS[start][2], 0)
    return best[1] if best else None


def _nights(stops: tuple[str, ...], days: int) -> tuple[list[int], int]:
    """Minimum nights each, then fill towards the comfortable number by appeal,
    then one bonus night each. Whatever is still left is returned as spare days."""
    nights = [STOPS[s][2] for s in stops]
    spare = days - sum(nights)
    order = sorted(range(len(stops)), key=lambda i: -STOPS[stops[i]][1])
    for cap_extra in (0, 1):
        for i in order:
            cap = STOPS[stops[i]][3] + cap_extra
            while spare > 0 and nights[i] < cap:
                nights[i] += 1
                spare -= 1
    return nights, spare


@lru_cache(maxsize=4096)
def _best_path(graph_key: tuple, start: str, end: str, days: int,
               via: tuple[str, ...] = ()) -> tuple[str, ...] | None:
    graph: dict[str, list[tuple[str, int]]] = {}
    for f, t, dur in graph_key:
        graph.setdefault(f, []).append((t, dur))
    # Most appealing neighbour first, so a budget cut-off still returns a good plan.
    ordered = {f: tuple(sorted(v, key=lambda x: -STOPS[x[0]][1])) for f, v in graph.items()}
    return _search(ordered, start, end, days, frozenset(via))


MAX_VIA = 5


def clean_via(values, start: str, end: str) -> tuple[str, ...]:
    """Must-see stops from user input: known slugs only, not the endpoints,
    de-duplicated, sorted (stable cache key and URL), capped at MAX_VIA."""
    seen = {v for v in values if v in STOPS and v not in (start, end)}
    return tuple(sorted(seen))[:MAX_VIA]


def plan(start: str, end: str, days: int, legs: dict[tuple[str, str], dict] | None = None,
         lang: str = 'sr', eur_rsd: float = 117.0, via: tuple[str, ...] = ()) -> dict | None:
    """Itinerary dict for the template, or None when no chain of direct buses
    fits (including: fits only without one of the must-see `via` stops)."""
    if start not in STOPS or end not in STOPS:
        return None
    days = max(MIN_DAYS, min(MAX_DAYS, int(days)))
    legs = load_legs() if legs is None else legs
    graph_key = tuple(sorted(
        (f, t, leg.get('duration_min') or UNKNOWN_LEG_MIN)
        for (f, t), leg in legs.items() if _usable(leg)))
    path = _best_path(graph_key, start, end, days, clean_via(via, start, end))
    if not path:
        return None

    loop = start == end
    stops = path[:-1] if loop else path
    nights, spare = _nights(stops, days)

    out_stops, day = [], 1
    for slug, n in zip(stops, nights):
        out_stops.append({
            'slug': slug, 'name': stop_name(slug, lang), 'db_name': _DB_NAMES[slug],
            'country': STOPS[slug][0], 'nights': n, 'day_from': day, 'day_to': day + n,
            'lat': _COORDS[slug][0], 'lon': _COORDS[slug][1],
        })
        day += n

    out_legs, minutes, price_rsd, price_known = [], 0, 0, True
    for a, b in zip(path, path[1:]):
        leg = legs[(a, b)]
        dur = leg.get('duration_min')
        minutes += dur or 0
        if leg.get('price_rsd'):
            price_rsd += leg['price_rsd']
        else:
            price_known = False
        out_legs.append({
            'from': a, 'to': b, 'from_name': stop_name(a, lang), 'to_name': stop_name(b, lang),
            'route_slug': leg['slug'], 'trips': leg['trips'], 'duration_min': dur,
            'price_eur': round(leg['price_rsd'] / eur_rsd) if leg.get('price_rsd') else None,
            'first_dep': leg.get('first_dep'), 'last_dep': leg.get('last_dep'),
        })

    direct = None if loop else legs.get((start, end))
    return {
        'start': start, 'end': end, 'days': days, 'loop': loop,
        'start_name': stop_name(start, lang), 'end_name': stop_name(end, lang),
        'stops': out_stops, 'legs': out_legs, 'spare_days': spare,
        'min_days': sum(STOPS[s][2] for s in stops),
        'longest_leg': max(out_legs, key=lambda leg: leg['duration_min'] or 0),
        'priced_legs': sum(1 for leg in out_legs if leg['price_eur'] is not None),
        'direct': {'trips': direct['trips'], 'duration_min': direct.get('duration_min'),
                   'route_slug': direct['slug']} if direct else None,
        'countries': list(dict.fromkeys(s['country'] for s in out_stops)),
        'bus_minutes': minutes,
        'bus_eur': round(price_rsd / eur_rsd) if price_rsd else None,
        'bus_eur_partial': not price_known,
    }


def leg_groups(legs: dict[tuple[str, str], dict] | None = None, lang: str = 'sr',
               eur_rsd: float = 117.0) -> list[dict]:
    """Every direct leg between loop stops, grouped by origin, for the hub page."""
    legs = load_legs() if legs is None else legs
    groups: dict[str, list[dict]] = {}
    for (a, b), leg in legs.items():
        groups.setdefault(a, []).append({
            'to_name': stop_name(b, lang), 'route_slug': leg['slug'],
            'duration_min': leg.get('duration_min'),
            'price_eur': round(leg['price_rsd'] / eur_rsd) if leg.get('price_rsd') else None,
        })
    out = [{'slug': a, 'name': stop_name(a, lang),
            'legs': sorted(items, key=lambda x: x['to_name'])} for a, items in groups.items()]
    return sorted(out, key=lambda g: g['name'])


def sketch(points: list[tuple[float, float]], width: int = 600, height: int = 400,
           pad: int = 40) -> list[tuple[float, float]]:
    """Project (lat, lon) points into an SVG box, north up, aspect preserved.
    Drawn server-side as the map's instant poster and as itinerary thumbnails,
    so the route shape is on screen before (or without) the map library."""
    if not points:
        return []
    k = 0.74  # cos(latitude ~42.5)
    xs = [lon * k for _lat, lon in points]
    ys = [-lat for lat, _lon in points]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    scale = min((width - 2 * pad) / span, (height - 2 * pad) / span)
    off_x = (width - (max(xs) - min(xs)) * scale) / 2
    off_y = (height - (max(ys) - min(ys)) * scale) / 2
    return [(round(off_x + (x - min(xs)) * scale, 1), round(off_y + (y - min(ys)) * scale, 1))
            for x, y in zip(xs, ys)]


def route_points(itinerary: dict) -> list[tuple[float, float]]:
    """(lat, lon) along the itinerary, closing the ring for a loop."""
    pts = [(s['lat'], s['lon']) for s in itinerary['stops']]
    return pts + pts[:1] if itinerary['loop'] else pts


def network(legs: dict[tuple[str, str], dict] | None = None, lang: str = 'sr') -> dict:
    """Every loop stop and every stop pair with a direct bus, for the hub map."""
    legs = load_legs() if legs is None else legs
    slugs = list(STOPS)
    index = {slug: i for i, slug in enumerate(slugs)}
    edges = sorted({tuple(sorted((index[a], index[b]))) for a, b in legs})
    return {
        'stops': [{'slug': slug, 'name': stop_name(slug, lang),
                   'lat': _COORDS[slug][0], 'lon': _COORDS[slug][1]} for slug in slugs],
        'edges': [list(e) for e in edges],
    }


_PHOTOS_FILE = Path(__file__).parent / 'content' / 'planner_photos.json'


@lru_cache(maxsize=1)
def _photo_credits() -> dict:
    try:
        return json.loads(_PHOTOS_FILE.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def photo(slug: str) -> dict | None:
    """One Wikimedia Commons photo per stop (app/static/img/planner/<slug>-{640,1280}.webp,
    16:9 crops) with the attribution its CC BY-SA licence requires, or None."""
    credit = _photo_credits().get(slug)
    if not credit:
        return None
    return dict(credit, small=f'img/planner/{slug}-640.webp', large=f'img/planner/{slug}-1280.webp')


def cover_slug(itinerary: dict) -> str:
    """The stop whose photo stands for the whole itinerary: the most appealing one."""
    return max((s['slug'] for s in itinerary['stops']), key=lambda slug: STOPS[slug][1])

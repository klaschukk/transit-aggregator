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

from functools import lru_cache

from app.db import cached_query

MIN_DAYS = 4
MAX_DAYS = 21
DEFAULT_PLAN = ('dubrovnik', 'tirana', 10)

MAX_LEG_MIN = 540          # longest single bus leg worth planning around (9 h)
UNKNOWN_LEG_MIN = 240      # scoring stand-in when the source has no duration
MAX_STOPS = 8
HOUR_TAX = 1.25            # appeal points one hour on a bus costs
SEARCH_BUDGET = 150_000    # node expansions; the stop graph is tiny but dense

# slug -> (country, appeal 1-10, minimum nights, comfortable nights).
# Slugs are the DB's city slugs (Serbian exonyms: skadar = Shkodër).
STOPS: dict[str, tuple[str, int, int, int]] = {
    'dubrovnik':   ('HR', 10, 2, 3),
    'split':       ('HR', 8, 2, 3),
    'kotor':       ('ME', 10, 2, 3),
    'budva':       ('ME', 6, 1, 2),
    'herceg-novi': ('ME', 4, 1, 1),
    'podgorica':   ('ME', 3, 1, 1),
    'skadar':      ('AL', 6, 1, 2),
    'tirana':      ('AL', 7, 2, 2),
    'ohrid':       ('MK', 8, 2, 3),
    'skoplje':     ('MK', 5, 1, 2),
    'mostar':      ('BA', 9, 1, 2),
    'sarajevo':    ('BA', 9, 2, 3),
    'beograd':     ('RS', 7, 2, 3),
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


def _score(path: tuple[str, ...], minutes: int, days: int, loop: bool) -> float:
    """Appeal of the stops, minus an hour-on-the-bus tax, minus idle days the
    stops cannot comfortably absorb (a 14-day plan with two towns is a bad plan)."""
    stops = path[:-1] if loop else path
    appeal = sum(STOPS[s][1] for s in stops)
    absorbable = sum(STOPS[s][3] + 1 for s in stops)
    return appeal - HOUR_TAX * minutes / 60.0 - 2.0 * max(0, days - absorbable)


def _search(graph: dict[str, tuple[tuple[str, int], ...]], start: str, end: str,
            days: int) -> tuple[str, ...] | None:
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
                if total <= days:
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
def _best_path(graph_key: tuple, start: str, end: str, days: int) -> tuple[str, ...] | None:
    graph: dict[str, list[tuple[str, int]]] = {}
    for f, t, dur in graph_key:
        graph.setdefault(f, []).append((t, dur))
    # Most appealing neighbour first, so a budget cut-off still returns a good plan.
    ordered = {f: tuple(sorted(v, key=lambda x: -STOPS[x[0]][1])) for f, v in graph.items()}
    return _search(ordered, start, end, days)


def plan(start: str, end: str, days: int, legs: dict[tuple[str, str], dict] | None = None,
         lang: str = 'sr', eur_rsd: float = 117.0) -> dict | None:
    """Itinerary dict for the template, or None when no chain of direct buses fits."""
    if start not in STOPS or end not in STOPS:
        return None
    days = max(MIN_DAYS, min(MAX_DAYS, int(days)))
    legs = load_legs() if legs is None else legs
    graph_key = tuple(sorted(
        (f, t, leg.get('duration_min') or UNKNOWN_LEG_MIN)
        for (f, t), leg in legs.items() if _usable(leg)))
    path = _best_path(graph_key, start, end, days)
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

    return {
        'start': start, 'end': end, 'days': days, 'loop': loop,
        'stops': out_stops, 'legs': out_legs, 'spare_days': spare,
        'countries': list(dict.fromkeys(s['country'] for s in out_stops)),
        'bus_minutes': minutes,
        'bus_eur': round(price_rsd / eur_rsd) if price_rsd else None,
        'bus_eur_partial': not price_known,
    }

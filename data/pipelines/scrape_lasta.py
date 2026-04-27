"""
Scraper for Serbian intercity buses — polazak.rs (via lasta.rs widget).

polazak.rs is the largest Serbian bus schedule aggregator with 575 operators.
lasta.rs uses it as backend. We scrape polazak.rs directly via __NEXT_DATA__
embedded in SSR pages.

URL pattern:
  /sr/red-voznje/{dep_settlement}-RS/{dep_station}/{arr_settlement}-RS/{arr_station}/{date}/{time}

Output: data/raw/lasta/routes.json  (nested format)
        data/raw/lasta/trips.json   (flat format for build_db.py)
"""
import json
import logging
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.slug import normalize_slug  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://polazak.rs'
RAW_DIR = Path(__file__).parent.parent / 'raw'
OUT_DIR = RAW_DIR / 'lasta'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept-Language': 'sr,en;q=0.9',
}

# City name → (settlement_slug, station_slug)
# Settlement slug = ASCII city name; station = AS (generic) or BAS/MAS for hubs
CITIES: dict[str, tuple[str, str]] = {
    'Beograd':            ('Beograd',            'BAS'),
    'Novi Sad':           ('Novi-Sad',            'MAS'),
    'Niš':                ('Nis',                 'AS'),
    'Kragujevac':         ('Kragujevac',          'AS'),
    'Subotica':           ('Subotica',            'AS'),
    'Zrenjanin':          ('Zrenjanin',           'AS'),
    'Pančevo':            ('Pancevo',             'AS'),
    'Čačak':              ('Cacak',               'AS'),
    'Novi Pazar':         ('Novi-Pazar',          'AS'),
    'Kraljevo':           ('Kraljevo',            'AS'),
    'Smederevo':          ('Smederevo',           'AS'),
    'Leskovac':           ('Leskovac',            'AS'),
    'Užice':              ('Uzice',               'AS'),
    'Vranje':             ('Vranje',              'AS'),
    'Valjevo':            ('Valjevo',             'AS'),
    'Kruševac':           ('Krusevac',            'AS'),
    'Šabac':              ('Sabac',               'AS'),
    'Sombor':             ('Sombor',              'AS'),
    'Požarevac':          ('Pozarevac',           'AS'),
    'Pirot':              ('Pirot',               'AS'),
    'Zaječar':            ('Zajecar',             'AS'),
    'Kikinda':            ('Kikinda',             'AS'),
    'Sremska Mitrovica':  ('Sremska-Mitrovica',   'AS'),
    'Jagodina':           ('Jagodina',            'AS'),
    'Loznica':            ('Loznica',             'AS'),
    # New cities (population > 20K)
    'Vršac':              ('Vrsac',               'AS'),
    'Bor':                ('Bor',                 'AS'),
    'Negotin':            ('Negotin',             'AS'),
    'Priboj':             ('Priboj',              'AS'),
    'Ivanjica':           ('Ivanjica',            'AS'),
    'Gornji Milanovac':   ('Gornji-Milanovac',    'AS'),
    'Aranđelovac':        ('Arandjelovac',        'AS'),
    'Smederevska Palanka': ('Smederevska-Palanka', 'AS'),
    'Mladenovac':         ('Mladenovac',          'AS'),
    'Lazarevac':          ('Lazarevac',           'AS'),
    'Obrenovac':          ('Obrenovac',           'AS'),
    'Inđija':             ('Indjija',             'AS'),
    'Stara Pazova':       ('Stara-Pazova',        'AS'),
    'Ruma':               ('Ruma',                'AS'),
    'Bačka Palanka':      ('Backa-Palanka',       'AS'),
    'Apatin':             ('Apatin',              'AS'),
    'Temerin':            ('Temerin',             'AS'),
    'Vrbas':              ('Vrbas',               'AS'),
    'Bečej':              ('Becej',               'AS'),
    'Kanjiža':            ('Kanjiza',             'AS'),
    'Senta':              ('Senta',               'AS'),
    'Ada':                ('Ada',                 'AS'),
    'Novi Miloševo':      ('Novo-Milosevo',       'AS'),
}

# Hub cities get paired with ALL other cities.
# Non-hubs get paired with hubs + regional neighbors.
HUBS = {'Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica'}

NEIGHBORS: dict[str, set[str]] = {
    'Zrenjanin': {'Kikinda', 'Pančevo', 'Sombor'},
    'Pančevo': {'Zrenjanin', 'Smederevo'},
    'Čačak': {'Kraljevo', 'Užice', 'Kruševac'},
    'Novi Pazar': {'Kraljevo', 'Kruševac', 'Čačak'},
    'Kraljevo': {'Čačak', 'Kruševac', 'Novi Pazar', 'Užice', 'Vranje'},
    'Smederevo': {'Požarevac', 'Jagodina', 'Pančevo'},
    'Leskovac': {'Vranje', 'Pirot', 'Kruševac'},
    'Užice': {'Čačak', 'Valjevo', 'Kraljevo', 'Loznica'},
    'Vranje': {'Leskovac', 'Pirot'},
    'Valjevo': {'Šabac', 'Užice', 'Loznica'},
    'Kruševac': {'Kraljevo', 'Čačak', 'Jagodina', 'Novi Pazar'},
    'Šabac': {'Valjevo', 'Sremska Mitrovica', 'Loznica'},
    'Sombor': {'Kikinda', 'Zrenjanin', 'Sremska Mitrovica'},
    'Požarevac': {'Smederevo', 'Jagodina', 'Zaječar'},
    'Pirot': {'Leskovac', 'Vranje', 'Zaječar'},
    'Zaječar': {'Pirot', 'Požarevac'},
    'Kikinda': {'Zrenjanin', 'Sombor'},
    'Sremska Mitrovica': {'Šabac', 'Sombor'},
    'Jagodina': {'Kruševac', 'Požarevac', 'Smederevo'},
    'Loznica': {'Šabac', 'Valjevo', 'Užice'},
    'Vršac': {'Pančevo', 'Zrenjanin'},
    'Bor': {'Zaječar', 'Negotin', 'Požarevac'},
    'Negotin': {'Zaječar', 'Bor'},
    'Priboj': {'Užice', 'Novi Pazar'},
    'Ivanjica': {'Čačak', 'Kraljevo', 'Užice'},
    'Gornji Milanovac': {'Čačak', 'Kragujevac', 'Aranđelovac'},
    'Aranđelovac': {'Kragujevac', 'Mladenovac', 'Gornji Milanovac'},
    'Smederevska Palanka': {'Smederevo', 'Kragujevac', 'Mladenovac'},
    'Mladenovac': {'Aranđelovac', 'Smederevska Palanka'},
    'Lazarevac': {'Obrenovac', 'Valjevo', 'Aranđelovac'},
    'Obrenovac': {'Lazarevac', 'Šabac'},
    'Inđija': {'Stara Pazova', 'Sremska Mitrovica', 'Ruma'},
    'Stara Pazova': {'Inđija', 'Ruma'},
    'Ruma': {'Sremska Mitrovica', 'Inđija', 'Stara Pazova'},
    'Bačka Palanka': {'Sombor', 'Vrbas'},
    'Apatin': {'Sombor'},
    'Temerin': {'Vrbas', 'Bečej'},
    'Vrbas': {'Bačka Palanka', 'Temerin', 'Bečej'},
    'Bečej': {'Vrbas', 'Temerin', 'Zrenjanin'},
    'Kanjiža': {'Senta', 'Ada'},
    'Senta': {'Kanjiža', 'Ada', 'Kikinda'},
    'Ada': {'Senta', 'Kanjiža'},
    'Novi Miloševo': {'Kikinda', 'Zrenjanin'},
}


def _build_pairs() -> list[tuple[str, str]]:
    """Generate city pairs to scrape (same logic as scrape_intercity.py)."""
    all_cities = list(CITIES.keys())
    pairs: set[tuple[str, str]] = set()

    for city in all_cities:
        if city in HUBS:
            for other in all_cities:
                if other != city:
                    pairs.add((city, other))
        else:
            for hub in HUBS:
                pairs.add((city, hub))
            for neighbor in NEIGHBORS.get(city, set()):
                if neighbor != city:
                    pairs.add((city, neighbor))

    return sorted(pairs)


def _city_to_slug(name: str) -> str:
    """Unified slug — single source of truth is app.slug.normalize_slug.

    The previous local implementation did not handle cyrillic at all —
    if Lasta ever returned a cyrillic city name, a raw cyrillic slug
    would land in the output JSON and later in city_stops.slug.
    """
    return normalize_slug(name)


# ── Scraping ──────────────────────────────────────────────────────────────

def fetch_schedule(
    session: requests.Session,
    from_city: str,
    to_city: str,
    travel_date: date,
) -> list[dict]:
    """Fetch schedule from polazak.rs and return parsed trips."""
    from_info = CITIES.get(from_city)
    to_info = CITIES.get(to_city)
    if not from_info or not to_info:
        return []

    from_settlement, from_station = from_info
    to_settlement, to_station = to_info
    date_str = travel_date.strftime('%d.%m.%Y.')

    url = (
        f'{BASE_URL}/sr/red-voznje/'
        f'{from_settlement}-RS/{from_station}/'
        f'{to_settlement}-RS/{to_station}/'
        f'{date_str}/00:00'
    )

    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return []
    except Exception as e:
        log.error(f'  Request failed {from_city}→{to_city}: {e}')
        return []

    # Parse __NEXT_DATA__
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        resp.text,
    )
    if not m:
        return []

    try:
        data = json.loads(m.group(1))
        lines = data['props']['pageProps'].get('lines', [])
    except (json.JSONDecodeError, KeyError):
        return []

    trips = []
    for line in lines:
        dep_time = line.get('departureTime', '')
        arr_time = line.get('arrivalTime', '')
        operator = line.get('operator', {})
        op_name = operator.get('name', '').strip()
        op_type = operator.get('operatorType', 'bus')

        # Price
        price_info = line.get('priceOneway', {}) or {}
        price_rsd = int(price_info.get('ticket_price_rsd', 0) or 0)

        # Duration from timetable (last stop distance or time diff)
        timetable = line.get('timetable', [])
        distance_km = 0
        if timetable:
            last_stop = timetable[-1]
            distance_km = int(float(last_stop.get('distance', 0) or 0))

        # Calculate duration in minutes from departure/arrival times
        duration_min = 0
        if dep_time and arr_time:
            try:
                dh, dm = map(int, dep_time.split(':'))
                ah, am = map(int, arr_time.split(':'))
                duration_min = (ah * 60 + am) - (dh * 60 + dm)
                if duration_min < 0:
                    duration_min += 24 * 60
            except ValueError:
                pass

        if dep_time and arr_time and op_name:
            trips.append({
                'departure': dep_time[:5],
                'arrival': arr_time[:5],
                'duration': duration_min,
                'price': price_rsd,
                'operator': op_name,
                'type': op_type if op_type in ('bus', 'train') else 'bus',
                'distance_km': distance_km,
            })

    return trips


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    pairs = _build_pairs()
    travel_date = date.today() + timedelta(days=1)

    log.info(f'Cities: {len(CITIES)}, pairs: {len(pairs)}')
    log.info(f'Date: {travel_date.isoformat()}\n')

    routes: list[dict] = []
    total = len(pairs)

    for i, (from_city, to_city) in enumerate(pairs, 1):
        trips = fetch_schedule(session, from_city, to_city, travel_date)
        # Per-row scraped_at — see scrape_intercity for rationale.
        scraped_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        for trip in trips:
            trip['scraped_at'] = scraped_at

        if trips:
            route = {
                'from_city': from_city,
                'to_city': to_city,
                'slug': f'{_city_to_slug(from_city)}-{_city_to_slug(to_city)}',
                'distance_km': trips[0].get('distance_km', 0),
                'trips': trips,
                'scraped_at': scraped_at,
            }
            routes.append(route)
            log.info(f'[{i}/{total}] {from_city} → {to_city}: {len(trips)} departures')
        else:
            if i % 50 == 0:
                log.info(f'[{i}/{total}] progress... {len(routes)} routes so far')

        time.sleep(0.5)

    # Write flat trips (for build_db.py)
    flat_trips = []
    for route in routes:
        for trip in route['trips']:
            flat_trips.append({
                'from_city': route['from_city'],
                'to_city': route['to_city'],
                'departure_time': trip['departure'],
                'arrival_time': trip['arrival'],
                'duration_min': trip['duration'],
                'price_rsd': trip['price'],
                'operator': trip['operator'],
                'type': trip['type'],
                'scraped_at': trip.get('scraped_at') or route.get('scraped_at'),
            })

    # Save nested routes
    routes_path = OUT_DIR / 'routes.json'
    with open(routes_path, 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    # Save flat trips
    flat_path = OUT_DIR / 'trips.json'
    with open(flat_path, 'w', encoding='utf-8') as f:
        json.dump(flat_trips, f, ensure_ascii=False, indent=2)

    # Collect unique operators
    operators = {}
    for route in routes:
        for trip in route['trips']:
            op = trip['operator']
            if op not in operators:
                operators[op] = trip['type']
    ops_path = OUT_DIR / 'operators.json'
    with open(ops_path, 'w', encoding='utf-8') as f:
        json.dump(operators, f, ensure_ascii=False, indent=2)

    log.info(f'\n=== Done ===')
    log.info(f'Pairs scraped : {total}')
    log.info(f'Routes found  : {len(routes)}')
    log.info(f'Total trips   : {len(flat_trips)}')
    log.info(f'Operators     : {len(operators)} — {", ".join(sorted(operators))}')
    log.info(f'Saved         : {routes_path}')
    log.info(f'Saved         : {flat_path}')


if __name__ == '__main__':
    main()

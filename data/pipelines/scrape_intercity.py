"""
Scraper for intercity buses — busticket4.me JSON API.

Uses the public bus-search API to fetch real schedules, prices, and carriers
for intercity bus routes in Serbia.

Pipeline:
  1. GET  /api/proxy/cities           → resolve city name → API id
  2. POST /api/proxy/bus-search       → fetch departures per city pair
  3. Group by route, write nested JSON

Output: data/raw/intercity/routes.json
Format: [{from_city, to_city, slug, distance_km, trips: [
    {departure, arrival, duration, price, operator, type}
]}]
"""
import json
import logging
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://busticket4.me'
RAW_DIR = Path(__file__).parent.parent / 'raw'
OUT_DIR = RAW_DIR / 'intercity'
CITY_CACHE_PATH = RAW_DIR / 'city_ids.json'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Accept-Language': 'sr,en;q=0.9',
}

# busticket4.me constants
COMPANY_ID = 132
SERBIA_COUNTRY_ID = 208

# All Serbian cities with population > 20K (48 cities)
ALL_CITIES: list[str] = [
    # Original 25
    'Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica',
    'Zrenjanin', 'Pančevo', 'Čačak', 'Novi Pazar', 'Kraljevo',
    'Smederevo', 'Leskovac', 'Užice', 'Vranje', 'Valjevo',
    'Kruševac', 'Šabac', 'Sombor', 'Požarevac', 'Pirot',
    'Zaječar', 'Kikinda', 'Sremska Mitrovica', 'Jagodina', 'Loznica',
    # New 23
    'Vršac', 'Bor', 'Negotin', 'Priboj', 'Ivanjica',
    'Gornji Milanovac', 'Aranđelovac', 'Smederevska Palanka',
    'Mladenovac', 'Lazarevac', 'Obrenovac', 'Inđija',
    'Stara Pazova', 'Ruma', 'Bačka Palanka', 'Apatin',
    'Temerin', 'Vrbas', 'Bečej', 'Kanjiža', 'Senta', 'Ada',
    'Novi Miloševo',
]

# Hub cities get paired with ALL other cities.
# Non-hub cities get paired with hubs + regional neighbors.
HUBS = {'Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica'}

# Regional neighbors: city → set of nearby cities to also scrape
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
    # New cities — neighbors
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

# Road distances (km) between Serbian cities
DISTANCES: dict[tuple[str, str], int] = {
    # From Beograd
    ('Beograd', 'Novi Sad'): 90,
    ('Beograd', 'Niš'): 250,
    ('Beograd', 'Kragujevac'): 145,
    ('Beograd', 'Subotica'): 185,
    ('Beograd', 'Čačak'): 155,
    ('Beograd', 'Kruševac'): 210,
    ('Beograd', 'Vranje'): 340,
    ('Beograd', 'Šabac'): 100,
    ('Beograd', 'Smederevo'): 65,
    ('Beograd', 'Valjevo'): 105,
    ('Beograd', 'Leskovac'): 285,
    ('Beograd', 'Zrenjanin'): 75,
    ('Beograd', 'Sombor'): 200,
    ('Beograd', 'Novi Pazar'): 285,
    ('Beograd', 'Pančevo'): 20,
    ('Beograd', 'Užice'): 200,
    ('Beograd', 'Jagodina'): 140,
    ('Beograd', 'Pirot'): 320,
    ('Beograd', 'Kraljevo'): 185,
    ('Beograd', 'Požarevac'): 80,
    ('Beograd', 'Zaječar'): 250,
    ('Beograd', 'Kikinda'): 150,
    ('Beograd', 'Sremska Mitrovica'): 80,
    ('Beograd', 'Loznica'): 145,
    # From Novi Sad
    ('Novi Sad', 'Niš'): 330,
    ('Novi Sad', 'Subotica'): 100,
    ('Novi Sad', 'Kragujevac'): 225,
    ('Novi Sad', 'Zrenjanin'): 75,
    ('Novi Sad', 'Sombor'): 110,
    ('Novi Sad', 'Kikinda'): 120,
    ('Novi Sad', 'Sremska Mitrovica'): 55,
    ('Novi Sad', 'Šabac'): 100,
    ('Novi Sad', 'Valjevo'): 160,
    ('Novi Sad', 'Čačak'): 240,
    ('Novi Sad', 'Kraljevo'): 270,
    # From Niš
    ('Niš', 'Kragujevac'): 125,
    ('Niš', 'Leskovac'): 40,
    ('Niš', 'Vranje'): 100,
    ('Niš', 'Pirot'): 70,
    ('Niš', 'Zaječar'): 110,
    ('Niš', 'Kruševac'): 75,
    ('Niš', 'Jagodina'): 115,
    ('Niš', 'Kraljevo'): 115,
    ('Niš', 'Novi Pazar'): 200,
    ('Niš', 'Požarevac'): 175,
    # From Kragujevac
    ('Kragujevac', 'Kraljevo'): 60,
    ('Kragujevac', 'Čačak'): 70,
    ('Kragujevac', 'Jagodina'): 55,
    ('Kragujevac', 'Kruševac'): 75,
    ('Kragujevac', 'Novi Pazar'): 155,
    ('Kragujevac', 'Užice'): 130,
    # From Subotica
    ('Subotica', 'Sombor'): 85,
    ('Subotica', 'Kikinda'): 80,
    ('Subotica', 'Zrenjanin'): 130,
    ('Subotica', 'Sremska Mitrovica'): 155,
    # Regional
    ('Čačak', 'Kraljevo'): 40,
    ('Čačak', 'Užice'): 70,
    ('Čačak', 'Kruševac'): 90,
    ('Kraljevo', 'Kruševac'): 50,
    ('Kraljevo', 'Novi Pazar'): 100,
    ('Kraljevo', 'Užice'): 100,
    ('Kraljevo', 'Vranje'): 200,
    ('Kruševac', 'Jagodina'): 60,
    ('Leskovac', 'Vranje'): 55,
    ('Leskovac', 'Pirot'): 85,
    ('Pirot', 'Zaječar'): 100,
    ('Pirot', 'Vranje'): 130,
    ('Požarevac', 'Zaječar'): 170,
    ('Požarevac', 'Smederevo'): 40,
    ('Požarevac', 'Jagodina'): 65,
    ('Šabac', 'Sremska Mitrovica'): 50,
    ('Šabac', 'Valjevo'): 55,
    ('Šabac', 'Loznica'): 50,
    ('Valjevo', 'Užice'): 90,
    ('Valjevo', 'Loznica'): 65,
    ('Sombor', 'Kikinda'): 110,
    ('Sombor', 'Sremska Mitrovica'): 100,
    ('Zrenjanin', 'Kikinda'): 55,
    ('Zrenjanin', 'Pančevo'): 55,
    ('Smederevo', 'Jagodina'): 90,
    ('Loznica', 'Užice'): 110,
    ('Novi Pazar', 'Kruševac'): 110,
    # New cities — distances to hubs
    ('Beograd', 'Vršac'): 85, ('Beograd', 'Bor'): 240,
    ('Beograd', 'Negotin'): 260, ('Beograd', 'Priboj'): 280,
    ('Beograd', 'Ivanjica'): 200, ('Beograd', 'Gornji Milanovac'): 120,
    ('Beograd', 'Aranđelovac'): 75, ('Beograd', 'Smederevska Palanka'): 85,
    ('Beograd', 'Mladenovac'): 55, ('Beograd', 'Lazarevac'): 55,
    ('Beograd', 'Obrenovac'): 30, ('Beograd', 'Inđija'): 40,
    ('Beograd', 'Stara Pazova'): 30, ('Beograd', 'Ruma'): 65,
    ('Beograd', 'Bačka Palanka'): 120, ('Beograd', 'Apatin'): 200,
    ('Beograd', 'Temerin'): 85, ('Beograd', 'Vrbas'): 120,
    ('Beograd', 'Bečej'): 120, ('Beograd', 'Kanjiža'): 190,
    ('Beograd', 'Senta'): 175, ('Beograd', 'Ada'): 160,
    ('Beograd', 'Novi Miloševo'): 130,
    ('Novi Sad', 'Inđija'): 40, ('Novi Sad', 'Stara Pazova'): 50,
    ('Novi Sad', 'Ruma'): 60, ('Novi Sad', 'Bačka Palanka'): 40,
    ('Novi Sad', 'Apatin'): 120, ('Novi Sad', 'Temerin'): 15,
    ('Novi Sad', 'Vrbas'): 45, ('Novi Sad', 'Bečej'): 60,
    ('Novi Sad', 'Kanjiža'): 120, ('Novi Sad', 'Senta'): 100,
    ('Novi Sad', 'Ada'): 95, ('Novi Sad', 'Novi Miloševo'): 80,
    ('Niš', 'Bor'): 170, ('Niš', 'Negotin'): 200,
    ('Bor', 'Zaječar'): 50, ('Bor', 'Negotin'): 55,
    ('Priboj', 'Užice'): 80, ('Priboj', 'Novi Pazar'): 100,
    ('Ivanjica', 'Čačak'): 45, ('Ivanjica', 'Kraljevo'): 55,
    ('Gornji Milanovac', 'Čačak'): 35, ('Gornji Milanovac', 'Kragujevac'): 50,
    ('Aranđelovac', 'Kragujevac'): 55, ('Aranđelovac', 'Mladenovac'): 25,
    ('Smederevska Palanka', 'Smederevo'): 30, ('Smederevska Palanka', 'Kragujevac'): 60,
    ('Inđija', 'Stara Pazova'): 15, ('Ruma', 'Sremska Mitrovica'): 20,
    ('Bačka Palanka', 'Sombor'): 80, ('Vrbas', 'Bečej'): 30,
    ('Senta', 'Kikinda'): 50, ('Kanjiža', 'Senta'): 15,
}

# Serbian Cyrillic → Latin transliteration (for matching API city names)
_CYR_TO_LAT: dict[str, str] = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'đ',
    'е': 'e', 'ж': 'ž', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k',
    'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'ć', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'č', 'џ': 'dž', 'ш': 'š',
}


def _normalize(name: str) -> str:
    """Normalize city name to lowercase ASCII for fuzzy matching."""
    result = name.lower()
    # Cyrillic → Latin
    for cyr, lat in _CYR_TO_LAT.items():
        result = result.replace(cyr, lat)
    # Strip diacritics
    for k, v in {'š': 's', 'đ': 'dj', 'ž': 'z', 'ć': 'c', 'č': 'c'}.items():
        result = result.replace(k, v)
    return result.strip()


def _city_to_slug(name: str) -> str:
    """Convert city name to URL slug."""
    norm = _normalize(name)
    return re.sub(r'[^a-z0-9]+', '-', norm).strip('-')


def _get_distance(from_city: str, to_city: str) -> int:
    return DISTANCES.get((from_city, to_city)) or DISTANCES.get((to_city, from_city)) or 0


def _build_pairs() -> list[tuple[str, str]]:
    """Generate city pairs to scrape.

    Hubs get paired with ALL other cities.
    Non-hubs get paired with all hubs + their regional neighbors.
    Both directions are generated for hubs; only origin→hub for non-hubs
    (the reverse hub→origin is already covered by hub expansion).
    """
    pairs: set[tuple[str, str]] = set()

    for city in ALL_CITIES:
        if city in HUBS:
            # Hub → every other city
            for other in ALL_CITIES:
                if other != city:
                    pairs.add((city, other))
        else:
            # Non-hub → all hubs
            for hub in HUBS:
                pairs.add((city, hub))
            # Non-hub → regional neighbors
            for neighbor in NEIGHBORS.get(city, set()):
                if neighbor != city:
                    pairs.add((city, neighbor))

    return sorted(pairs)


# ── City ID resolution ────────────────────────────────────────────────────

def _load_city_cache() -> dict[str, int]:
    """Load cached city name→id mapping."""
    if CITY_CACHE_PATH.exists():
        with open(CITY_CACHE_PATH, encoding='utf-8') as f:
            return {k: int(v) for k, v in json.load(f).items()}
    return {}


def _save_city_cache(cache: dict[str, int]) -> None:
    with open(CITY_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def fetch_cities_from_api(session: requests.Session) -> dict[str, dict]:
    """Fetch all Serbian cities from API. Returns normalized_name → {code, name}."""
    url = f'{BASE_URL}/api/proxy/cities'
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        cities = body.get('data', []) if isinstance(body, dict) else body
    except Exception as e:
        log.error(f'Failed to fetch cities: {e}')
        return {}

    # Filter to Serbia (country_id=208) and build lookup
    lookup: dict[str, dict] = {}
    for city in cities:
        if city.get('country_id') != SERBIA_COUNTRY_ID:
            continue
        norm = _normalize(city['name'])
        lookup[norm] = {'code': int(city['code']), 'name': city['name']}
    log.info(f'Fetched {len(lookup)} Serbian cities from API')
    return lookup


def resolve_city_ids(
    session: requests.Session,
    needed: set[str],
) -> dict[str, int]:
    """Return city_name → bt4_id for all needed cities."""
    cache = _load_city_cache()

    # Find which cities are missing from cache
    missing = needed - set(cache.keys())
    if not missing:
        return {c: cache[c] for c in needed if c in cache}

    log.info(f'Resolving {len(missing)} missing city IDs: {missing}')
    api_cities = fetch_cities_from_api(session)

    for city in missing:
        norm = _normalize(city)
        match = api_cities.get(norm)
        if match:
            cache[city] = match['code']
            log.info(f'  {city} → id={match["code"]} (API name: {match["name"]})')
        else:
            log.warning(f'  {city} not found in API')

    _save_city_cache(cache)
    return {c: cache[c] for c in needed if c in cache}


# ── Bus search API ────────────────────────────────────────────────────────

def search_departures(
    session: requests.Session,
    from_city: str,
    from_id: int,
    to_city: str,
    to_id: int,
    travel_date: date,
) -> list[dict]:
    """Call bus-search API and return parsed trip dicts."""
    url = f'{BASE_URL}/api/proxy/bus-search'
    body = {
        'departure_place_id': from_id,
        'arrival_place_id': to_id,
        'departure_place_name': from_city,
        'arrival_place_name': to_city,
        'departure_date': travel_date.strftime('%d.%m.%Y'),
        'departure_country_id': SERBIA_COUNTRY_ID,
        'arrival_country_id': SERBIA_COUNTRY_ID,
        'return_ticket': 'NE',
        'number_of_passengers': 1,
        'company_admin_id': COMPANY_ID,
        'company_id': COMPANY_ID,
        'carrier_id': 0,
        'carrier_parent_company_id': 0,
        'affiliate_line_id': None,
        'affiliate_id': None,
        'ticket_type': 0,
    }

    try:
        resp = session.post(url, json=body, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        body_resp = resp.json()
        data = body_resp.get('data', []) if isinstance(body_resp, dict) else body_resp
    except Exception as e:
        log.error(f'  bus-search failed {from_city}→{to_city}: {e}')
        return []

    if not isinstance(data, list):
        return []

    trips = []
    for dep in data:
        schedule = dep.get('schedule', {})
        pricing = dep.get('pricing', {})
        carrier = dep.get('carrier', {})
        booking = dep.get('booking', {})

        # Skip cancelled departures
        if booking.get('departure_cancelled'):
            continue

        departure_time = schedule.get('departure_time', '')
        arrival_time = schedule.get('arrival_time', '')
        duration_min = schedule.get('duration_minutes', 0)

        # Price is in RSD (currency_symbol="Din.")
        price_rsd = int(pricing.get('ticket_price', 0) or 0)

        # Carrier name comes uppercase — title-case it
        operator_name = carrier.get('name', '').strip().title()

        if departure_time and arrival_time:
            trips.append({
                'departure': departure_time[:5],  # HH:MM
                'arrival': arrival_time[:5],
                'duration': duration_min,
                'price': price_rsd,
                'operator': operator_name,
                'type': 'bus',
            })

    return trips


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    # Collect all unique cities needed
    pairs = _build_pairs()
    needed_cities: set[str] = set()
    for from_city, to_city in pairs:
        needed_cities.add(from_city)
        needed_cities.add(to_city)

    log.info(f'Cities: {len(needed_cities)}, pairs to scrape: {len(pairs)}')

    # Resolve city IDs (cached + API fallback)
    city_ids = resolve_city_ids(session, needed_cities)
    log.info(f'Resolved {len(city_ids)}/{len(needed_cities)} city IDs')

    # Search for tomorrow's date (to get a full day of departures)
    travel_date = date.today() + timedelta(days=1)
    log.info(f'Searching departures for {travel_date.isoformat()}\n')

    routes: list[dict] = []
    route_keys: set[tuple[str, str]] = set()
    failed: list[str] = []
    skipped = 0
    total = len(pairs)

    for i, (from_city, to_city) in enumerate(pairs, 1):
        from_id = city_ids.get(from_city)
        to_id = city_ids.get(to_city)

        if not from_id or not to_id:
            skipped += 1
            continue

        trips = search_departures(session, from_city, from_id, to_city, to_id, travel_date)

        if trips:
            route_keys.add((from_city, to_city))
            route = {
                'from_city': from_city,
                'to_city': to_city,
                'slug': f'{_city_to_slug(from_city)}-{_city_to_slug(to_city)}',
                'distance_km': _get_distance(from_city, to_city),
                'trips': trips,
            }
            routes.append(route)
            log.info(f'[{i}/{total}] {from_city} → {to_city}: {len(trips)} departures')
        else:
            failed.append(f'{from_city}→{to_city}')
            if i % 50 == 0:
                log.info(f'[{i}/{total}] progress... {len(routes)} routes so far')

        time.sleep(0.5)

    # Also write flat format for build_db.py compatibility
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
            })

    # Save nested routes
    routes_path = OUT_DIR / 'routes.json'
    with open(routes_path, 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    # Save flat trips (backward compat with build_db.py)
    flat_path = RAW_DIR / 'intercity_routes.json'
    with open(flat_path, 'w', encoding='utf-8') as f:
        json.dump(flat_trips, f, ensure_ascii=False, indent=2)

    log.info(f'\n=== Done ===')
    log.info(f'Pairs scraped : {total}')
    log.info(f'Skipped (no ID): {skipped}')
    log.info(f'Routes found  : {len(routes)}')
    log.info(f'Total trips   : {sum(len(r["trips"]) for r in routes)}')
    log.info(f'Empty pairs   : {len(failed)}')
    log.info(f'Saved         : {routes_path}')
    log.info(f'Saved         : {flat_path}')


if __name__ == '__main__':
    main()

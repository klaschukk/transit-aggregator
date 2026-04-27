"""
Scraper for intercity buses (Serbia) — busticket4.me JSON API.

Reads the bt4 city catalog (built by discover_cities.py) for city→code
lookups, so adding a new Serbian city only requires naming it in
discover_cities.SR_WIDE and rerunning the catalog.

Pipeline:
  1. Load data/raw/bt4_cities_catalog.json (run discover_cities first)
  2. Build pairs: hubs × everyone + non-hub → neighbor mini-graph
  3. POST /api/proxy/bus-search per pair, parse trips
  4. Write flat + nested JSON for build_db

Output:
  data/raw/intercity_routes.json     (flat — consumed by build_db)
  data/raw/intercity/routes.json     (nested — for ad-hoc inspection)
"""
import json
import logging
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.slug import normalize_slug  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://busticket4.me'
RAW_DIR = Path(__file__).parent.parent / 'raw'
OUT_DIR = RAW_DIR / 'intercity'
CATALOG_PATH = RAW_DIR / 'bt4_cities_catalog.json'

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

# Regional neighbor mini-graph — non-hub cities get scraped against their
# geographic neighbors in addition to the hubs, so Užice→Valjevo shows up
# even though neither is a hub. Kept here (not in catalog) because it is
# SR-specific geography, not just a city list.
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
}

# Approximate road distances (km) — used for /rute/ cards + SEO markup.
# Missing pairs default to 0; build_db uses its own distance table too.
DISTANCES: dict[tuple[str, str], int] = {
    ('Beograd', 'Novi Sad'): 90, ('Beograd', 'Niš'): 250,
    ('Beograd', 'Kragujevac'): 145, ('Beograd', 'Subotica'): 185,
    ('Beograd', 'Čačak'): 155, ('Beograd', 'Kruševac'): 210,
    ('Beograd', 'Vranje'): 340, ('Beograd', 'Šabac'): 100,
    ('Beograd', 'Smederevo'): 65, ('Beograd', 'Valjevo'): 105,
    ('Beograd', 'Leskovac'): 285, ('Beograd', 'Zrenjanin'): 75,
    ('Beograd', 'Sombor'): 200, ('Beograd', 'Novi Pazar'): 285,
    ('Beograd', 'Pančevo'): 20, ('Beograd', 'Užice'): 200,
    ('Beograd', 'Jagodina'): 140, ('Beograd', 'Pirot'): 320,
    ('Beograd', 'Kraljevo'): 185, ('Beograd', 'Požarevac'): 80,
    ('Beograd', 'Zaječar'): 250, ('Beograd', 'Kikinda'): 150,
    ('Beograd', 'Sremska Mitrovica'): 80, ('Beograd', 'Loznica'): 145,
    ('Novi Sad', 'Niš'): 330, ('Novi Sad', 'Subotica'): 100,
    ('Novi Sad', 'Kragujevac'): 225, ('Novi Sad', 'Zrenjanin'): 75,
    ('Novi Sad', 'Sombor'): 110, ('Novi Sad', 'Kikinda'): 120,
    ('Novi Sad', 'Sremska Mitrovica'): 55, ('Novi Sad', 'Šabac'): 100,
    ('Novi Sad', 'Valjevo'): 160, ('Novi Sad', 'Čačak'): 240,
    ('Novi Sad', 'Kraljevo'): 270,
    ('Niš', 'Kragujevac'): 125, ('Niš', 'Leskovac'): 40,
    ('Niš', 'Vranje'): 100, ('Niš', 'Pirot'): 70,
    ('Niš', 'Zaječar'): 110, ('Niš', 'Kruševac'): 75,
    ('Niš', 'Jagodina'): 115, ('Niš', 'Kraljevo'): 115,
    ('Niš', 'Novi Pazar'): 200, ('Niš', 'Požarevac'): 175,
    ('Kragujevac', 'Kraljevo'): 60, ('Kragujevac', 'Čačak'): 70,
    ('Kragujevac', 'Jagodina'): 55, ('Kragujevac', 'Kruševac'): 75,
    ('Kragujevac', 'Novi Pazar'): 155, ('Kragujevac', 'Užice'): 130,
    ('Subotica', 'Sombor'): 85, ('Subotica', 'Kikinda'): 80,
    ('Subotica', 'Zrenjanin'): 130, ('Subotica', 'Sremska Mitrovica'): 155,
    ('Čačak', 'Kraljevo'): 40, ('Čačak', 'Užice'): 70,
    ('Čačak', 'Kruševac'): 90, ('Kraljevo', 'Kruševac'): 50,
    ('Kraljevo', 'Novi Pazar'): 100, ('Kraljevo', 'Užice'): 100,
    ('Kraljevo', 'Vranje'): 200, ('Kruševac', 'Jagodina'): 60,
    ('Leskovac', 'Vranje'): 55, ('Leskovac', 'Pirot'): 85,
    ('Pirot', 'Zaječar'): 100, ('Pirot', 'Vranje'): 130,
    ('Požarevac', 'Zaječar'): 170, ('Požarevac', 'Smederevo'): 40,
    ('Požarevac', 'Jagodina'): 65, ('Šabac', 'Sremska Mitrovica'): 50,
    ('Šabac', 'Valjevo'): 55, ('Šabac', 'Loznica'): 50,
    ('Valjevo', 'Užice'): 90, ('Valjevo', 'Loznica'): 65,
    ('Sombor', 'Kikinda'): 110, ('Sombor', 'Sremska Mitrovica'): 100,
    ('Zrenjanin', 'Kikinda'): 55, ('Zrenjanin', 'Pančevo'): 55,
    ('Smederevo', 'Jagodina'): 90, ('Loznica', 'Užice'): 110,
    ('Novi Pazar', 'Kruševac'): 110,
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
    ('Novi Sad', 'Inđija'): 40, ('Novi Sad', 'Stara Pazova'): 50,
    ('Novi Sad', 'Ruma'): 60, ('Novi Sad', 'Bačka Palanka'): 40,
    ('Novi Sad', 'Apatin'): 120, ('Novi Sad', 'Temerin'): 15,
    ('Novi Sad', 'Vrbas'): 45, ('Novi Sad', 'Bečej'): 60,
    ('Novi Sad', 'Kanjiža'): 120, ('Novi Sad', 'Senta'): 100,
    ('Novi Sad', 'Ada'): 95,
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


# ── Catalog loading ───────────────────────────────────────────────────────

def load_catalog() -> dict:
    if not CATALOG_PATH.exists():
        raise SystemExit(
            f'{CATALOG_PATH} not found — run '
            'python data/pipelines/discover_cities.py first'
        )
    with open(CATALOG_PATH, encoding='utf-8') as f:
        return json.load(f)


def _get_distance(from_city: str, to_city: str) -> int:
    return (DISTANCES.get((from_city, to_city))
            or DISTANCES.get((to_city, from_city))
            or 0)


def _build_pairs(all_cities: list[str], hubs: set[str]) -> list[tuple[str, str]]:
    """Generate SR pairs: hubs × everyone + non-hub → neighbors."""
    pairs: set[tuple[str, str]] = set()
    city_set = set(all_cities)

    for city in all_cities:
        if city in hubs:
            for other in all_cities:
                if other != city:
                    pairs.add((city, other))
        else:
            for hub in hubs:
                if hub in city_set:
                    pairs.add((city, hub))
            for neighbor in NEIGHBORS.get(city, set()):
                if neighbor in city_set and neighbor != city:
                    pairs.add((city, neighbor))

    return sorted(pairs)


# ── Bus search API ────────────────────────────────────────────────────────

def search_departures(
    session: requests.Session,
    from_city: str,
    from_id: int,
    to_city: str,
    to_id: int,
    travel_date: date,
) -> list[dict]:
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

        if booking.get('departure_cancelled'):
            continue

        departure_time = schedule.get('departure_time', '')
        arrival_time = schedule.get('arrival_time', '')
        duration_min = schedule.get('duration_minutes', 0)
        price_rsd = int(pricing.get('ticket_price', 0) or 0)
        operator_name = carrier.get('name', '').strip().title()

        if departure_time and arrival_time:
            trips.append({
                'departure': departure_time[:5],
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

    catalog = load_catalog()
    sr_wide = catalog['sr_wide']
    # Primary hubs for SR — the 5-hub "spine". Kragujevac joins the 4 intl hubs.
    hub_names = set(catalog['hubs_intl'].get('SR', [])) | {'Kragujevac'}

    # city → bt4 code. Only keep cities that exist in the catalog.
    cities_map = catalog['cities']
    usable = [c for c in sr_wide if c in cities_map]
    missing_catalog = [c for c in sr_wide if c not in cities_map]
    if missing_catalog:
        log.warning(f'Not in catalog (dropped): {missing_catalog}')

    pairs = _build_pairs(usable, hub_names & set(usable))
    log.info(
        f'Cities: {len(usable)}, hubs: {len(hub_names & set(usable))}, '
        f'pairs to scrape: {len(pairs)}'
    )

    travel_date = date.today() + timedelta(days=1)
    log.info(f'Searching departures for {travel_date.isoformat()}\n')

    routes: list[dict] = []
    failed: list[str] = []
    total = len(pairs)

    for i, (from_city, to_city) in enumerate(pairs, 1):
        from_id = cities_map[from_city]['code']
        to_id = cities_map[to_city]['code']

        trips = search_departures(session, from_city, from_id, to_city, to_id, travel_date)

        # Per-row scraped_at — every trip carries the wall-clock at the
        # moment its parent pair was fetched. Different pairs in the
        # same run land seconds apart; that's the granularity we need
        # so a partial-rerun (e.g. retry of one pair) surfaces its own
        # newer timestamp without bumping the whole file's mtime.
        scraped_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        for trip in trips:
            trip['scraped_at'] = scraped_at

        if trips:
            routes.append({
                'from_city': from_city,
                'to_city': to_city,
                'slug': f'{normalize_slug(from_city)}-{normalize_slug(to_city)}',
                'distance_km': _get_distance(from_city, to_city),
                'trips': trips,
                'scraped_at': scraped_at,
            })
            log.info(f'[{i}/{total}] {from_city} → {to_city}: {len(trips)} departures')
        else:
            failed.append(f'{from_city}→{to_city}')
            if i % 50 == 0:
                log.info(f'[{i}/{total}] progress... {len(routes)} routes so far')

        time.sleep(0.5)

    # Flat format for build_db
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

    with open(OUT_DIR / 'routes.json', 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)
    with open(RAW_DIR / 'intercity_routes.json', 'w', encoding='utf-8') as f:
        json.dump(flat_trips, f, ensure_ascii=False, indent=2)

    log.info('')
    log.info('=== Done ===')
    log.info(f'Pairs scraped : {total}')
    log.info(f'Routes found  : {len(routes)}')
    log.info(f'Total trips   : {sum(len(r["trips"]) for r in routes)}')
    log.info(f'Empty pairs   : {len(failed)}')


if __name__ == '__main__':
    main()

"""
Scrape international bus routes via busticket4.me API.

Reads the bt4 city catalog (built by discover_cities.py) and generates:
  * Intra-country pairs  — all top-N hub combinations within each non-SR
                           target country (Sarajevo↔Mostar, Split↔Zagreb, …)
  * Inter-country pairs  — each country's intl hubs × each neighbor country's
                           intl hubs (hub-spoke via geographic corridors).

Serbia intra-country pairs are handled by scrape_intercity.py — this script
covers every other pair touching a non-SR city.

Output: data/raw/international_routes.json (flat; consumed by build_db)
Usage:  python -u data/pipelines/scrape_international.py

Budget: capped at MAX_PAIRS per run (default 2000) × 1 date, rate-limited to
0.5s between calls, so a full run is ≲ 20 min.
"""
import json
import logging
import random
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.slug import normalize_slug  # noqa: E402 — import for future use / parity
from data.pipelines.http_util import post_with_retry  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://busticket4.me'
RAW_DIR = Path(__file__).parent.parent / 'raw'
CATALOG_PATH = RAW_DIR / 'bt4_cities_catalog.json'
COMPANY_ID = 132
MAX_PAIRS = 2000
EUR_TO_RSD = 117  # API returns EUR for intl routes; rough display-conversion

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

# Geographic neighbor graph (ISO2). Inter-country pairs are generated only
# between neighbors — prevents combinatorial blow-up (6500+ pairs) while
# still covering every realistic bus corridor. SR connects to all targets
# (diaspora corridors + tourist ferries).
NEIGHBORS: dict[str, set[str]] = {
    'SR': {'ME', 'BA', 'HR', 'MK', 'HU', 'RO', 'BG', 'AL', 'SI', 'TR', 'GR'},
    'ME': {'SR', 'BA', 'HR', 'AL'},
    'BA': {'SR', 'HR', 'ME'},
    'HR': {'SR', 'BA', 'ME', 'SI', 'HU'},
    'MK': {'SR', 'BG', 'AL', 'GR'},
    'AL': {'SR', 'ME', 'MK', 'GR'},
    'SI': {'SR', 'HR', 'HU'},
    'BG': {'SR', 'MK', 'RO', 'GR', 'TR'},
    'RO': {'SR', 'HU', 'BG'},
    'HU': {'SR', 'SI', 'HR', 'RO'},
    'GR': {'SR', 'MK', 'AL', 'BG', 'TR'},
    'TR': {'SR', 'BG', 'GR'},
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


def build_pairs(catalog: dict) -> list[tuple[str, str]]:
    """Return ordered city-pair list.

    Intra-country non-SR: every (hub_a, hub_b) with a != b per country.
    Inter-country: every pair (a, b) where a∈intl_hubs[A], b∈intl_hubs[B],
    and B is a geographic neighbor of A. Both directions produced.
    """
    hubs_intra = catalog['hubs_intra']
    hubs_intl = catalog['hubs_intl']
    cities = catalog['cities']

    pairs: set[tuple[str, str]] = set()

    # Intra-country (skip SR — covered by scrape_intercity)
    for cc, hubs in hubs_intra.items():
        if cc == 'SR':
            continue
        valid = [h for h in hubs if h in cities]
        for a in valid:
            for b in valid:
                if a != b:
                    pairs.add((a, b))

    # Inter-country: NEIGHBORS × intl hubs
    for a_cc, neighbors in NEIGHBORS.items():
        a_hubs = [h for h in hubs_intl.get(a_cc, []) if h in cities]
        for b_cc in neighbors:
            b_hubs = [h for h in hubs_intl.get(b_cc, []) if h in cities]
            for a in a_hubs:
                for b in b_hubs:
                    if a != b:
                        pairs.add((a, b))

    ordered = sorted(pairs)
    if len(ordered) > MAX_PAIRS:
        log.warning(f'Pair count {len(ordered)} > MAX_PAIRS {MAX_PAIRS}; sampling')
        rng = random.Random(42)
        ordered = sorted(rng.sample(ordered, MAX_PAIRS))
    return ordered


# ── Bus search API ────────────────────────────────────────────────────────

def search(session, from_name, from_code, from_country,
           to_name, to_code, to_country, dt):
    body = {
        'departure_place_id': from_code, 'arrival_place_id': to_code,
        'departure_place_name': from_name, 'arrival_place_name': to_name,
        'departure_date': dt.strftime('%d.%m.%Y'),
        'departure_country_id': from_country, 'arrival_country_id': to_country,
        'return_ticket': 'NE', 'number_of_passengers': 1,
        'company_admin_id': COMPANY_ID, 'company_id': COMPANY_ID,
        'carrier_id': 0, 'carrier_parent_company_id': 0,
    }
    try:
        r = post_with_retry(
            session, f'{BASE_URL}/api/proxy/bus-search',
            json=body, headers=HEADERS, timeout=30,
        )
        data = r.json()
        return data.get('data', []) if isinstance(data, dict) else []
    except Exception:
        return []


def parse_trips(raw_trips, from_city, to_city):
    result = []
    for t in raw_trips:
        sched = t.get('schedule', {})
        pricing = t.get('pricing', {})
        carrier = t.get('carrier', {})
        booking = t.get('booking', {})
        if booking.get('departure_cancelled'):
            continue

        # .get('k', default) returns None when the key exists but value is null,
        # so coerce to '' explicitly — build_db.py has NOT NULL on arrival_time.
        dep_time = sched.get('departure_time') or ''
        arr_time = sched.get('arrival_time') or ''
        duration = sched.get('duration_minutes') or 0

        # API returns EUR for intl; convert for display consistency
        price_eur = pricing.get('display_price', 0) or pricing.get('ticket_price', 0)
        price_rsd = int(float(price_eur) * EUR_TO_RSD) if price_eur else 0
        carrier_name = carrier.get('name', '')

        if dep_time and arr_time:
            result.append({
                'from_city': from_city, 'to_city': to_city,
                'departure_time': dep_time, 'arrival_time': arr_time,
                'duration_min': duration, 'price_rsd': price_rsd,
                'operator': carrier_name, 'type': 'bus',
            })
    return result


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    dt = date.today() + timedelta(days=1)

    catalog = load_catalog()
    cities = catalog['cities']

    pairs = build_pairs(catalog)
    log.info(
        f'Catalog: {len(cities)} cities, '
        f'{sum(len(v) for v in catalog["hubs_intra"].values())} intra hubs, '
        f'{sum(len(v) for v in catalog["hubs_intl"].values())} intl hubs'
    )
    log.info(f'Pairs: {len(pairs)}, date: {dt}')

    all_trips: list[dict] = []
    found = 0
    total = len(pairs)

    for i, (fn, tn) in enumerate(pairs, 1):
        fc = cities[fn]['code']
        fco = cities[fn]['country_id']
        tc = cities[tn]['code']
        tco = cities[tn]['country_id']

        raw = search(session, fn, fc, fco, tn, tc, tco, dt)
        if raw:
            trips = parse_trips(raw, fn, tn)
            if trips:
                all_trips.extend(trips)
                found += 1
                log.info(f'[{i}/{total}] {fn} → {tn}: {len(trips)} departures')

        if i % 100 == 0:
            log.info(f'  progress... {i}/{total}, {found} routes, {len(all_trips)} trips')

        time.sleep(0.5)

    out = RAW_DIR / 'international_routes.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_trips, f, ensure_ascii=False, indent=2)

    log.info('')
    log.info(f'Done: {found} routes, {len(all_trips)} trips → {out}')


if __name__ == '__main__':
    main()

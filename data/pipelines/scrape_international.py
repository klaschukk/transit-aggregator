"""
Scrape international bus routes via busticket4.me API.

Output: data/raw/international_routes.json
Usage: python -u data/pipelines/scrape_international.py
"""
import json
import logging
import time
from datetime import date, timedelta
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://busticket4.me'
RAW_DIR = Path(__file__).parent.parent / 'raw'
COMPANY_ID = 132
SERBIA_COUNTRY = 208

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

# city → (code, country_id) — verified from API
INTL = {
    'Podgorica': (1121, 42), 'Budva': (1139, 42), 'Herceg Novi': (1148, 42),
    'Kotor': (1150, 42), 'Tivat': (2976, 42),
    'Sarajevo': (1309, 31), 'Banja Luka': (1283, 31), 'Tuzla': (2089, 31), 'Mostar': (1276, 31),
    'Zagreb': (1371, 86), 'Split': (1349, 86), 'Dubrovnik': (1346, 86), 'Rijeka': (1352, 86),
    'Istanbul': (1582, 228), 'Ljubljana': (1730, 195), 'Ohrid': (1557, 128),
    'Timisoara': (6440, 174),
}


def load_sr_ids():
    """Load Serbian city IDs from existing cache."""
    path = RAW_DIR / 'city_ids.json'
    if path.exists():
        cache = json.load(open(path))
        # Keep cities that have IDs
        return {name: (cid, SERBIA_COUNTRY) for name, cid in cache.items()
                if name in ['Beograd', 'Novi Sad', 'Niš', 'Subotica', 'Užice', 'Novi Pazar',
                            'Kragujevac', 'Čačak', 'Kraljevo', 'Kruševac']}
    return {}


def search(session, from_name, from_code, from_country, to_name, to_code, to_country, dt):
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
        r = session.post(f'{BASE_URL}/api/proxy/bus-search', json=body, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data.get('data', []) if isinstance(data, dict) else []
    except Exception:
        return []


def parse_trips(raw_trips, from_city, to_city):
    """Parse API response into flat trip dicts."""
    EUR_TO_RSD = 117  # approximate exchange rate
    result = []
    for t in raw_trips:
        sched = t.get('schedule', {})
        pricing = t.get('pricing', {})
        carrier = t.get('carrier', {})

        dep_time = sched.get('departure_time', '')
        arr_time = sched.get('arrival_time', '')
        duration = sched.get('duration_minutes', 0)

        # Price: API returns EUR for international routes
        price_eur = pricing.get('display_price', 0) or pricing.get('ticket_price', 0)
        price_rsd = int(float(price_eur) * EUR_TO_RSD) if price_eur else 0

        carrier_name = carrier.get('name', '')

        if dep_time:
            result.append({
                'from_city': from_city, 'to_city': to_city,
                'departure_time': dep_time, 'arrival_time': arr_time,
                'duration_min': duration, 'price_rsd': price_rsd,
                'operator': carrier_name, 'type': 'bus',
            })
    return result


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    dt = date.today() + timedelta(days=1)

    sr_cities = load_sr_ids()
    log.info(f'Serbian cities: {len(sr_cities)}')
    log.info(f'International cities: {len(INTL)}')

    # Build pairs
    pairs = []
    for sr_name, (sr_code, sr_country) in sr_cities.items():
        for intl_name, (intl_code, intl_country) in INTL.items():
            pairs.append((sr_name, sr_code, sr_country, intl_name, intl_code, intl_country))
            pairs.append((intl_name, intl_code, intl_country, sr_name, sr_code, sr_country))

    # Key international ↔ international
    cross = [
        ('Podgorica', 'Budva'), ('Budva', 'Kotor'), ('Herceg Novi', 'Kotor'),
        ('Sarajevo', 'Mostar'), ('Sarajevo', 'Dubrovnik'), ('Zagreb', 'Split'),
        ('Split', 'Dubrovnik'), ('Mostar', 'Dubrovnik'),
    ]
    for a, b in cross:
        if a in INTL and b in INTL:
            ac, acountry = INTL[a]
            bc, bcountry = INTL[b]
            pairs.append((a, ac, acountry, b, bc, bcountry))
            pairs.append((b, bc, bcountry, a, ac, acountry))

    log.info(f'Pairs: {len(pairs)}, date: {dt}')

    all_trips = []
    found = 0

    for i, (fn, fc, fco, tn, tc, tco) in enumerate(pairs):
        raw = search(session, fn, fc, fco, tn, tc, tco, dt)
        if raw:
            trips = parse_trips(raw, fn, tn)
            if trips:
                all_trips.extend(trips)
                found += 1
                log.info(f'[{i+1}/{len(pairs)}] {fn} → {tn}: {len(trips)} departures')

        if (i + 1) % 50 == 0:
            log.info(f'  progress... {i+1}/{len(pairs)}, {found} routes')

        time.sleep(0.5)

    out = RAW_DIR / 'international_routes.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_trips, f, ensure_ascii=False, indent=2)

    log.info(f'\nDone: {found} routes, {len(all_trips)} trips → {out}')


if __name__ == '__main__':
    main()

"""
Scraper for Srbija Voz (Serbian Railways) — w3.srbvoz.rs.
Output: data/raw/srbvoz_trains.json

Station API:  GET  /api/stanica/?term={name}
Schedule URL: GET  /direktni/{from_name}/{from_code}/{to_name}/{to_code}/{date}/{time}/sr
Rows alternate: odd=data, even=mobile duplicate (skip even rows).
"""
import json
import logging
import re
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://w3.srbvoz.rs/redvoznje'
RAW_DIR = Path(__file__).parent.parent / 'raw'

SESSION_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,*/*',
}

# City pairs with known train service (verified against w3.srbvoz.rs).
# Use display names for from_city/to_city, but override station lookup where
# the actual railway station name differs (e.g. Novi Sad → PETROVARADIN).
CITY_PAIRS: list[tuple[str, str]] = [
    ('Beograd', 'Nis'),
    ('Beograd', 'Valjevo'),
    ('Beograd', 'Uzice'),
    ('Beograd', 'Vrsac'),
    ('Beograd', 'Šid'),
    ('Beograd', 'Sremska Mitrovica'),
    ('Beograd', 'Priboj'),
    ('Beograd', 'Novi Sad'),      # resolves to PETROVARADIN
    ('Beograd', 'Subotica'),      # may be indirect
    ('Nis', 'Vranje'),
]

# Some cities map to a different railway station name in w3.srbvoz.rs.
STATION_OVERRIDES: dict[str, str] = {
    'Novi Sad': 'Petrovaradin',    # station name is PETROVARADIN
    'Šid': 'Si',                   # API only finds ŠID when searching "Si"
}


def to_ascii(name: str) -> str:
    """Convert Serbian special chars to ASCII for URL."""
    replacements = {
        'š': 's', 'đ': 'd', 'ž': 'z', 'ć': 'c', 'č': 'c',
        'Š': 'S', 'Đ': 'D', 'Ž': 'Z', 'Ć': 'C', 'Č': 'C',
    }
    for k, v in replacements.items():
        name = name.replace(k, v)
    return name


def get_station(session: requests.Session, city: str) -> dict | None:
    """Fetch station name + code from autocomplete API."""
    # Use override name if available (e.g. Novi Sad → Petrovaradin)
    lookup_name = STATION_OVERRIDES.get(city, city)
    ascii_city = to_ascii(lookup_name)
    try:
        resp = session.get(
            f'{BASE_URL}/api/stanica/',
            params={'term': ascii_city},
            headers=SESSION_HEADERS,
            verify=False,  # w3.srbvoz.rs has SSL issues
            timeout=15,
        )
        resp.raise_for_status()
        stations = resp.json()
        if not stations:
            log.warning(f'No stations found for: {city}')
            return None
        # Exact match by city name — try both with and without diacritics
        city_upper = city.upper()
        city_ascii = to_ascii(city).upper()
        for station in stations:
            sn = station['naziv'].upper()
            if sn in (city_upper, city_ascii) or to_ascii(sn) == city_ascii:
                return station
        # Prefer main passenger station (skip freight/sorting yards)
        skip_keywords = ['TERETNA', 'RANŽIRNA', 'RANZIIRNA']
        preferred_keywords = ['CENTAR', 'PUTNICKI']
        for station in stations:
            naziv = station['naziv'].upper()
            if any(kw in naziv for kw in preferred_keywords):
                return station
        # Fall back to first non-freight station
        for station in stations:
            naziv = station['naziv'].upper()
            if not any(kw in naziv for kw in skip_keywords):
                return station
        return stations[0]
    except Exception as e:
        log.error(f'Station lookup failed for {city}: {e}')
        return None


def build_url(from_station: dict, to_station: dict, travel_date: date) -> str:
    """Build schedule URL for a station pair."""
    from_name = from_station['naziv'].replace(' ', '-')
    to_name = to_station['naziv'].replace(' ', '-')
    from_code = from_station['sifra']
    to_code = to_station['sifra']
    date_str = travel_date.strftime('%d.%m.%Y')
    return f'{BASE_URL}/direktni/{from_name}/{from_code}/{to_name}/{to_code}/{date_str}/00:00/sr'


def parse_schedule(html: str, from_city: str, to_city: str) -> list[dict]:
    """Parse train schedule table from HTML page."""
    trips = []

    table_match = re.search(
        r'<table[^>]*class="tabela"[^>]*>(.*?)</table>', html, re.DOTALL
    )
    if not table_match:
        return trips

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_match.group(1), re.DOTALL)

    # Data rows come in pairs: [data_row, mobile_duplicate] — skip header (class="tsmall") and even rows
    data_rows = []
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if cells and len(cells) >= 4:
            clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            # Skip the mobile duplicate rows (they contain full text like "Voz broj: ...")
            if clean[0].isdigit() or (len(clean[0]) <= 5 and clean[0].strip()):
                data_rows.append(clean)

    for row in data_rows:
        try:
            train_number = row[0].strip()
            dep_time = row[1].strip()  # HH:MM
            arr_time = row[3].strip()  # HH:MM
            duration_raw = row[6].strip() if len(row) > 6 else ''

            if not re.match(r'\d{1,2}:\d{2}', dep_time):
                continue

            # Parse duration "HH:MM" → minutes
            duration_min = 0
            if re.match(r'\d{1,2}:\d{2}', duration_raw):
                h, m = map(int, duration_raw.split(':'))
                duration_min = h * 60 + m

            trips.append({
                'from_city': from_city,
                'to_city': to_city,
                'train_number': train_number,
                'departure_time': dep_time,
                'arrival_time': arr_time,
                'duration_min': duration_min,
                'operator': 'Srbija Voz',
                'type': 'train',
            })
        except (IndexError, ValueError) as e:
            log.debug(f'Skip row parse error: {e}')

    return trips


def scrape_pair(session: requests.Session, from_station: dict, to_station: dict,
                from_city: str, to_city: str) -> list[dict]:
    """Scrape one city pair."""
    travel_date = date.today() + timedelta(days=1)
    url = build_url(from_station, to_station, travel_date)
    log.info(f'  {from_city} → {to_city}: {url}')

    try:
        resp = session.get(url, headers=SESSION_HEADERS, verify=False, timeout=30)
        resp.raise_for_status()
        trips = parse_schedule(resp.text, from_city, to_city)
        log.info(f'  → {len(trips)} trains')
        return trips
    except Exception as e:
        log.error(f'  Failed {from_city} → {to_city}: {e}')
        return []


def main() -> None:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    # Collect unique cities
    cities = sorted(set(c for pair in CITY_PAIRS for c in pair))
    log.info('Looking up station codes...')
    station_map: dict[str, dict] = {}
    for city in cities:
        station = get_station(session, city)
        if station:
            station_map[city] = station
            log.info(f'  {city}: {station["naziv"]} ({station["sifra"]})')
        time.sleep(0.3)

    # Save station map
    with open(RAW_DIR / 'srbvoz_stations.json', 'w', encoding='utf-8') as f:
        json.dump(station_map, f, ensure_ascii=False, indent=2)

    log.info(f'\nScraping {len(CITY_PAIRS)} train route pairs...')
    all_trips: list[dict] = []

    for from_city, to_city in CITY_PAIRS:
        from_st = station_map.get(from_city)
        to_st = station_map.get(to_city)
        if not from_st or not to_st:
            log.warning(f'Skipping {from_city} → {to_city}: missing station')
            continue
        trips = scrape_pair(session, from_st, to_st, from_city, to_city)
        # Per-row scraped_at — see scrape_intercity for rationale.
        scraped_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        for trip in trips:
            trip['scraped_at'] = scraped_at
        all_trips.extend(trips)
        time.sleep(1.0)

    out_path = RAW_DIR / 'srbvoz_trains.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_trips, f, ensure_ascii=False, indent=2)

    log.info(f'\nSaved {len(all_trips)} trains → {out_path}')


if __name__ == '__main__':
    main()

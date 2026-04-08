"""
Scrape international Balkan bus routes from GetByBus.

Covers routes between Serbia and: Montenegro, Bosnia, Croatia,
North Macedonia, Albania, Kosovo, Hungary, Romania, Bulgaria.

Output: data/raw/balkan_routes.json

Usage: python -u data/pipelines/scrape_balkan.py
"""
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

RAW_DIR = Path(__file__).parent.parent / 'raw'

GREEN = '\033[92m'
RED = '\033[91m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Accept-Language': 'en',
})

# Serbian cities that have international connections
SR_CITIES = [
    'Belgrade', 'Novi Sad', 'Niš', 'Subotica', 'Novi Pazar',
    'Kragujevac', 'Užice', 'Vranje', 'Pirot', 'Šabac',
]

# International destinations grouped by country
INTL_CITIES = {
    'Montenegro': ['Podgorica', 'Budva', 'Herceg Novi', 'Bar', 'Kotor', 'Tivat', 'Nikšić', 'Ulcinj'],
    'Bosnia': ['Sarajevo', 'Banja Luka', 'Tuzla', 'Mostar', 'Bijeljina', 'Trebinje', 'Brčko'],
    'Croatia': ['Zagreb', 'Split', 'Dubrovnik', 'Rijeka', 'Osijek', 'Vukovar'],
    'North Macedonia': ['Skopje', 'Ohrid', 'Bitola', 'Kumanovo'],
    'Hungary': ['Budapest', 'Szeged', 'Pécs'],
    'Romania': ['Bucharest', 'Timișoara', 'Cluj-Napoca'],
    'Bulgaria': ['Sofia', 'Plovdiv'],
    'Albania': ['Tirana', 'Durrës'],
    'Slovenia': ['Ljubljana', 'Maribor'],
    'Greece': ['Thessaloniki', 'Athens'],
    'Austria': ['Vienna', 'Graz'],
    'Germany': ['Munich', 'Frankfurt', 'Berlin', 'Stuttgart'],
}

CITY_SLUG_MAP = {
    'Belgrade': 'beograd', 'Novi Sad': 'novi-sad', 'Niš': 'nis',
    'Subotica': 'subotica', 'Novi Pazar': 'novi-pazar',
    'Kragujevac': 'kragujevac', 'Užice': 'uzice',
    'Vranje': 'vranje', 'Pirot': 'pirot', 'Šabac': 'sabac',
    'Podgorica': 'podgorica', 'Budva': 'budva',
    'Herceg Novi': 'herceg-novi', 'Bar': 'bar', 'Kotor': 'kotor',
    'Tivat': 'tivat', 'Nikšić': 'niksic', 'Ulcinj': 'ulcinj',
    'Sarajevo': 'sarajevo', 'Banja Luka': 'banja-luka',
    'Tuzla': 'tuzla', 'Mostar': 'mostar', 'Bijeljina': 'bijeljina',
    'Trebinje': 'trebinje', 'Brčko': 'brcko',
    'Zagreb': 'zagreb', 'Split': 'split', 'Dubrovnik': 'dubrovnik',
    'Rijeka': 'rijeka', 'Osijek': 'osijek', 'Vukovar': 'vukovar',
    'Skopje': 'skopje', 'Ohrid': 'ohrid', 'Bitola': 'bitola',
    'Kumanovo': 'kumanovo',
    'Budapest': 'budapest', 'Szeged': 'szeged', 'Pécs': 'pecs',
    'Bucharest': 'bucharest', 'Timișoara': 'timisoara',
    'Cluj-Napoca': 'cluj-napoca',
    'Sofia': 'sofia', 'Plovdiv': 'plovdiv',
    'Tirana': 'tirana', 'Durrës': 'durres',
    'Ljubljana': 'ljubljana', 'Maribor': 'maribor',
    'Thessaloniki': 'thessaloniki', 'Athens': 'athens',
    'Vienna': 'vienna', 'Graz': 'graz',
    'Munich': 'munich', 'Frankfurt': 'frankfurt',
    'Berlin': 'berlin', 'Stuttgart': 'stuttgart',
}


def to_slug(city: str) -> str:
    return CITY_SLUG_MAP.get(city, city.lower().replace(' ', '-')
                             .replace('š', 's').replace('č', 'c')
                             .replace('ć', 'c').replace('ž', 'z')
                             .replace('đ', 'dj').replace('ș', 's')
                             .replace('ț', 't'))


def search_getbybus(from_city: str, to_city: str) -> dict | None:
    """Search GetByBus for a route, return trip count and price range."""
    from_slug = to_slug(from_city)
    to_slug_ = to_slug(to_city)
    url = f'https://getbybus.com/en/bus-from-{from_slug}-to-{to_slug_}'

    try:
        r = SESSION.get(url, timeout=15, allow_redirects=True)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, 'html.parser')

        # Look for trip count or "no results"
        no_results = soup.find(string=re.compile(r'no.*results|not.*found|no.*buses', re.I))
        if no_results:
            return None

        # Count trip cards
        trips = soup.find_all('div', class_=re.compile(r'trip|result|departure', re.I))
        trip_count = len(trips) if trips else 0

        # If page loaded and has content, assume route exists
        if trip_count == 0 and len(r.text) > 10000:
            trip_count = 1  # at least exists

        if trip_count == 0:
            return None

        # Try to extract price
        prices = re.findall(r'(\d+[.,]\d{2})\s*€|€\s*(\d+[.,]\d{2})', r.text)
        min_price = None
        if prices:
            nums = [float(p[0] or p[1]) for p in prices if (p[0] or p[1])]
            if nums:
                min_price = min(nums)

        return {
            'trip_count': max(trip_count, 1),
            'min_price_eur': min_price,
        }

    except Exception:
        return None


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    routes = []

    # Build pair list
    pairs = []
    for sr_city in SR_CITIES:
        for country, cities in INTL_CITIES.items():
            for intl_city in cities:
                pairs.append((sr_city, intl_city, country))
                pairs.append((intl_city, sr_city, country))

    total = len(pairs)
    print(f'\n  {BOLD}BALKAN ROUTES SCRAPER{RESET}')
    print(f'  {"=" * 50}')
    print(f'  Pairs to check: {total}')
    print(f'  {"=" * 50}\n')

    found = 0
    for i, (from_city, to_city, country) in enumerate(pairs):
        result = search_getbybus(from_city, to_city)

        if result:
            from_slug = to_slug(from_city)
            to_slug_ = to_slug(to_city)
            route_slug = f'{from_slug}-{to_slug_}'

            route = {
                'from_city': from_city,
                'to_city': to_city,
                'from_city_slug': from_slug,
                'to_city_slug': to_slug_,
                'slug': route_slug,
                'country': country,
                'type': 'international',
                'trip_count': result['trip_count'],
                'min_price_eur': result.get('min_price_eur'),
            }
            routes.append(route)
            found += 1

            price_str = f" {result['min_price_eur']:.0f}€" if result.get('min_price_eur') else ''
            print(f'  {DIM}{i+1:>4}/{total}{RESET}  {GREEN}+{RESET} {from_city} → {to_city}{price_str}')
        else:
            if (i + 1) % 50 == 0:
                print(f'  {DIM}{i+1:>4}/{total}{RESET}  ... {found} routes found')

        time.sleep(0.5)

    out_path = RAW_DIR / 'balkan_routes.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    print(f'\n  {"=" * 50}')
    print(f'  {BOLD}DONE{RESET}')
    print(f'  Routes found: {found}')
    print(f'  Saved: {out_path}')
    print(f'  {"=" * 50}\n')


if __name__ == '__main__':
    main()

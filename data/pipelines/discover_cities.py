"""
Discover all busticket4.me cities for target countries.

Runs once (weekly cron) to snapshot the bt4 city catalog — 8000+ cities across
Europe. Downstream scrapers (scrape_intercity, scrape_international) read the
catalog instead of maintaining hardcoded ALL_CITIES + city_ids.json caches,
so adding coverage for a new city only requires listing it in HUBS below.

Output: data/raw/bt4_cities_catalog.json

Format:
    {
      "meta": {"fetched_at": "...", "total_cities": N, "filtered": M},
      "countries": {"SR": {"id": 208, "name": "Srbija"}, ...},
      "cities": {
         "Beograd": {"code": 1213, "country": "SR", "country_id": 208},
         ...
      },
      "hubs_intra": {"SR": [...7 cities...], "ME": [...], ...},
      "hubs_intl":  {"SR": [...4 cities...], "ME": [...], ...},
      "sr_wide":    [...48 Serbian cities for intra-country programmatic SEO...]
    }

The bt4 /cities endpoint does not expose population, so hubs are a curated
short list per country (names exactly as returned by the API — run this
script once and inspect logs to confirm every hub resolves).
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://busticket4.me'
RAW_DIR = Path(__file__).parent.parent / 'raw'
CATALOG_PATH = RAW_DIR / 'bt4_cities_catalog.json'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0',
    'Accept': 'application/json',
}

# ISO2 code → bt4 country_id. These IDs are assigned server-side; verify on
# fetch and log any drift. 12 countries covering Serbia + diaspora corridors.
TARGET_COUNTRIES: dict[str, int] = {
    'SR': 208,  # Srbija
    'ME': 42,   # Crna Gora
    'BA': 31,   # Bosna i Hercegovina
    'HR': 86,   # Hrvatska
    'MK': 185,  # Sjeverna Makedonija
    'AL': 4,    # Albanija
    'SI': 205,  # Slovenija
    'BG': 36,   # Bugarska
    'RO': 187,  # Rumunija
    'HU': 149,  # Mađarska
    'GR': 74,   # Grčka
    'TR': 228,  # Turska
}

# Top intra-country hubs (≈7 per country). Names MUST match bt4 catalog
# exactly — the API uses Serbian transliterations (Skoplje not Skopje,
# Bukurešt not Bucharest, Sofija not Sofia). Missing hubs are logged at
# runtime so the curated list can be fixed.
HUBS_INTRA: dict[str, list[str]] = {
    'SR': ['Beograd', 'Novi Sad', 'Niš', 'Kragujevac',
           'Subotica', 'Novi Pazar', 'Užice'],
    'ME': ['Podgorica', 'Budva', 'Herceg Novi', 'Kotor',
           'Tivat', 'Bar', 'Nikšić'],
    'BA': ['Sarajevo', 'Banja Luka', 'Tuzla', 'Mostar',
           'Zenica', 'Bihać', 'Trebinje'],
    'HR': ['Zagreb', 'Split', 'Dubrovnik', 'Rijeka',
           'Zadar', 'Osijek', 'Pula'],
    'MK': ['Skoplje', 'Ohrid', 'Bitolj', 'Tetovo',
           'Kumanovo', 'Štip', 'Prilep'],
    'AL': ['Tirana', 'Drač', 'Valona', 'Skadar',
           'Elbasan', 'Sarande'],
    'SI': ['Ljubljana', 'Maribor', 'Celje', 'Kranj',
           'Novo Mesto', 'Ptuj'],
    'BG': ['Sofija', 'Plovdiv', 'Varna', 'Burgas',
           'Ruse', 'Stara Zagora', 'Pleven'],
    'RO': ['Bukurešt', 'Timisoara', 'Brasov', 'Constanta',
           'Arad'],
    'HU': ['Budimpešta', 'Segedin', 'Debrecen', 'Pecs'],
    'GR': ['Solun', 'Atina', 'Patras', 'Larisa',
           'Kavala', 'Volos', 'Janjina'],
    'TR': ['Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Antalya'],
}

# International-pair hubs (smaller subset — controls inter-country blast
# radius). ~3 per country keeps total pair count under the 2000 cap.
HUBS_INTL: dict[str, list[str]] = {
    'SR': ['Beograd', 'Novi Sad', 'Niš', 'Subotica'],
    'ME': ['Podgorica', 'Budva', 'Herceg Novi', 'Kotor'],
    'BA': ['Sarajevo', 'Banja Luka', 'Mostar', 'Tuzla'],
    'HR': ['Zagreb', 'Split', 'Dubrovnik', 'Rijeka'],
    'MK': ['Skoplje', 'Ohrid', 'Bitolj'],
    'AL': ['Tirana', 'Drač', 'Valona'],
    'SI': ['Ljubljana', 'Maribor', 'Celje'],
    'BG': ['Sofija', 'Plovdiv', 'Varna'],
    'RO': ['Bukurešt', 'Timisoara', 'Brasov'],
    'HU': ['Budimpešta', 'Segedin'],
    'GR': ['Solun', 'Atina', 'Patras'],
    'TR': ['Istanbul', 'Ankara'],
}

# Wide SR list for programmatic-SEO intra-country pairs. Curated (48 cities,
# all with population > ~20K) — stays here so discover_cities is the single
# source of "which cities do we care about".
SR_WIDE: list[str] = [
    'Beograd', 'Novi Sad', 'Niš', 'Kragujevac', 'Subotica',
    'Zrenjanin', 'Pančevo', 'Čačak', 'Novi Pazar', 'Kraljevo',
    'Smederevo', 'Leskovac', 'Užice', 'Vranje', 'Valjevo',
    'Kruševac', 'Šabac', 'Sombor', 'Požarevac', 'Pirot',
    'Zaječar', 'Kikinda', 'Sremska Mitrovica', 'Jagodina', 'Loznica',
    'Vršac', 'Bor', 'Negotin', 'Priboj', 'Ivanjica',
    'Gornji Milanovac', 'Aranđelovac', 'Smederevska Palanka',
    'Mladenovac', 'Lazarevac', 'Obrenovac', 'Inđija',
    'Stara Pazova', 'Ruma', 'Bačka Palanka', 'Apatin',
    'Temerin', 'Vrbas', 'Bečej', 'Kanjiža', 'Senta', 'Ada',
    'Novi Miloševo',
]


def fetch_all_cities(session: requests.Session) -> list[dict]:
    url = f'{BASE_URL}/api/proxy/cities'
    resp = session.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    body = resp.json()
    cities = body.get('data', []) if isinstance(body, dict) else body
    log.info(f'Fetched {len(cities)} cities from bt4 API')
    return cities


def build_catalog(cities: list[dict]) -> dict:
    """Filter to target countries and resolve hub names → codes."""
    target_ids = {v: k for k, v in TARGET_COUNTRIES.items()}  # id → ISO2

    # name → record (strip trailing whitespace; bt4 has "Kotor ", "Tivat ",
    # "Dubrovnik " with padding that breaks exact-match lookups)
    by_name: dict[str, dict] = {}
    countries_meta: dict[str, dict] = {}
    total_filtered = 0

    for c in cities:
        cid = c.get('country_id')
        if cid not in target_ids:
            continue
        name = (c.get('name') or '').strip()
        if not name:
            continue
        iso2 = target_ids[cid]
        countries_meta.setdefault(iso2, {
            'id': cid,
            'name': (c.get('country_name') or '').strip(),
            'code': (c.get('country_code') or '').strip(),
        })
        # First occurrence wins (dedup same-name cities in different subregions —
        # the pair-search API is tolerant but we want a stable code)
        if name not in by_name:
            by_name[name] = {
                'code': int(c['code']),
                'country': iso2,
                'country_id': cid,
            }
            total_filtered += 1

    # Resolve hubs — warn on any miss so the curated list can be fixed
    resolved_intra: dict[str, list[str]] = {}
    resolved_intl: dict[str, list[str]] = {}
    for cc, names in HUBS_INTRA.items():
        found = [n for n in names if n in by_name]
        missing = [n for n in names if n not in by_name]
        resolved_intra[cc] = found
        if missing:
            log.warning(f'  {cc} hubs_intra miss: {missing}')
        else:
            log.info(f'  {cc} hubs_intra: {len(found)}/{len(names)} resolved')

    for cc, names in HUBS_INTL.items():
        found = [n for n in names if n in by_name]
        missing = [n for n in names if n not in by_name]
        resolved_intl[cc] = found
        if missing:
            log.warning(f'  {cc} hubs_intl miss: {missing}')

    # SR wide list — log any gaps so we can find the right API spelling
    sr_wide_found = [n for n in SR_WIDE if n in by_name]
    sr_wide_miss = [n for n in SR_WIDE if n not in by_name]
    if sr_wide_miss:
        log.warning(f'  SR wide miss ({len(sr_wide_miss)}): {sr_wide_miss}')
    log.info(f'  SR wide: {len(sr_wide_found)}/{len(SR_WIDE)} resolved')

    catalog = {
        'meta': {
            'fetched_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'total_cities_api': len(cities),
            'filtered_cities': total_filtered,
            'target_countries': list(TARGET_COUNTRIES.keys()),
        },
        'countries': countries_meta,
        'cities': by_name,
        'hubs_intra': resolved_intra,
        'hubs_intl': resolved_intl,
        'sr_wide': sr_wide_found,
    }
    return catalog


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    cities = fetch_all_cities(session)
    catalog = build_catalog(cities)

    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    log.info('')
    log.info(f'=== Catalog saved: {CATALOG_PATH} ===')
    log.info(f'Countries     : {len(catalog["countries"])}')
    log.info(f'Cities total  : {catalog["meta"]["filtered_cities"]}')
    log.info(f'Intra hubs    : {sum(len(v) for v in catalog["hubs_intra"].values())}')
    log.info(f'Intl hubs     : {sum(len(v) for v in catalog["hubs_intl"].values())}')
    log.info(f'SR wide       : {len(catalog["sr_wide"])}')


if __name__ == '__main__':
    main()

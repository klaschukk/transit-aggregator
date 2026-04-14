"""
Scraper for Belgrade city transport (bgprevoz.rs).

Sources:
  1. POST /linije/red-voznje/tip  → all lines by type (CSRF required)
  2. GET  /linije/red-voznje/smer-a/{kod} → stops per line (HTML table)
  3. GET  /api/stajalista/{id} → stop coords + lines (JSON, no auth)

Output:
  data/raw/gsp_lines.json   — line metadata + ordered stop IDs/names
  data/raw/gsp_stops.json   — all stops with lat/lon

Usage:
  python -u data/pipelines/scrape_gsp.py
  python -u data/pipelines/scrape_gsp.py --stops-only   # re-fetch stops only
"""
import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://bgprevoz.rs'
RAW_DIR = Path(__file__).parent.parent / 'raw'
PROGRESS_FILE = RAW_DIR / 'gsp_scrape_progress.json'

LINE_TYPES = [
    'аутобус',
    'трамвај',
    'тролејбус',
    'ноћне-линије',
    'БГ-воз',
    'E linije',
]

TYPE_SLUG_MAP = {
    'аутобус': 'bus',
    'трамвај': 'tram',
    'тролејбус': 'trolleybus',
    'ноћне-линије': 'night',
    'БГ-воз': 'bg-voz',
    'E linije': 'e-bus',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': f'{BASE_URL}/linije/linije',
}

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'


# -- Session / CSRF ------------------------------------------------------------

def get_session_with_csrf() -> tuple[requests.Session, str]:
    """Initialize session and extract CSRF token from main page."""
    session = requests.Session()
    session.headers.update({'User-Agent': HEADERS['User-Agent']})
    resp = session.get(f'{BASE_URL}/linije/linije', timeout=30)
    resp.raise_for_status()
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', resp.text)
    if not match:
        raise RuntimeError('CSRF token not found')
    csrf = match.group(1)
    log.info(f'CSRF token obtained: {csrf[:20]}...')
    return session, csrf


# -- Phase 1: line list --------------------------------------------------------

def fetch_lines(session: requests.Session, csrf: str, tip: str) -> list[dict]:
    resp = session.post(
        f'{BASE_URL}/linije/red-voznje/tip',
        data={'_token': csrf, 'tip': tip},
        headers={**HEADERS, 'X-CSRF-TOKEN': csrf},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get('linije', [])


def normalize_line(raw: dict, tip: str) -> dict:
    verzija = raw.get('verzije', [{}])[-1] if raw.get('verzije') else {}
    number = raw.get('prikazan_kod_linije_prikaz') or raw.get('prikazan_kod_linije', '')
    slug = f"linija-{number.lower().replace(' ', '-')}"
    name = raw.get('pocetni_terminus_prikaz') or raw.get('pocetni_terminus', '')
    return {
        'id': raw['kod_linije'],
        'number': number,
        'slug': slug,
        'name': name,
        'type': TYPE_SLUG_MAP.get(tip, tip),
        'verzija_id': verzija.get('id'),
        'route_description': verzija.get('spisak_ulica_smer_a', '') or '',
    }


def scrape_lines(session: requests.Session, csrf: str) -> list[dict]:
    all_lines = []
    for tip in LINE_TYPES:
        log.info(f'Fetching lines type: {tip}')
        try:
            raw_lines = fetch_lines(session, csrf, tip)
            lines = [normalize_line(r, tip) for r in raw_lines]
            log.info(f'  -> {len(lines)} lines')
            all_lines.extend(lines)
            time.sleep(0.5)
        except Exception as e:
            log.error(f'  Failed for tip={tip}: {e}')
    return all_lines


# -- Phase 2: stops per line (HTML table) --------------------------------------

def fetch_line_stops(session: requests.Session, line_id: int) -> list[dict]:
    """Scrape ordered stop list for a line from the daljinari HTML table."""
    url = f'{BASE_URL}/linije/red-voznje/smer-a/{line_id}'
    try:
        r = session.get(url, timeout=20)
        r.raise_for_status()
    except Exception as e:
        log.warning(f'  Stop fetch failed for line {line_id}: {e}')
        return []

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', class_='daljinari-table')
    if not table:
        return []

    stops = []
    for row in table.find_all('tr')[1:]:  # skip header
        cells = row.find_all('td')
        if len(cells) < 5:
            continue
        order = cells[1].get_text(strip=True)
        name = cells[2].get_text(strip=True)
        code_raw = cells[4].get_text(strip=True)
        code = code_raw.replace('#', '').strip()
        if code.isdigit():
            stops.append({'order': int(order) if order.isdigit() else 0,
                          'name': name, 'stop_id': int(code)})
    return stops


def enrich_lines_with_stops(session: requests.Session, lines: list[dict]) -> list[dict]:
    """Attach ordered stop_id list to each line."""
    total = len(lines)
    for idx, line in enumerate(lines):
        n = idx + 1
        stops = fetch_line_stops(session, line['id'])
        line['stops'] = stops
        status = f'{GREEN}{len(stops)} stops{RESET}' if stops else f'{RED}no stops{RESET}'
        print(f'  {DIM}{n:>4}/{total}{RESET}  {BOLD}{line["number"]}{RESET} {line["name"][:40]}  {status}')
        time.sleep(0.3)
    return lines


# -- Phase 3: stop coords from /api/stajalista/{id} ----------------------------

def fetch_stop(session: requests.Session, stop_id: int) -> dict | None:
    """Fetch stop metadata from bgprevoz.rs stop API."""
    for attempt in range(3):
        try:
            r = session.get(f'{BASE_URL}/api/stajalista/{stop_id}', timeout=10)
            if r.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            if r.status_code != 200:
                return None
            d = r.json()
            if not d.get('naziv'):
                return None
            lines_at_stop = []
            for l in d.get('linije', []):
                num = l.get('prikazan_kod_linije_prikaz') or l.get('prikazan_kod_linije', '')
                if num:
                    lines_at_stop.append(num)
            return {
                'id': stop_id,
                'name': d['naziv'],
                'lat': float(d['sirina']) if d.get('sirina') else None,
                'lon': float(d['duzina']) if d.get('duzina') else None,
                'zone': d.get('zona', ''),
                'lines': lines_at_stop,
            }
        except requests.exceptions.ConnectionError:
            time.sleep(2 * (attempt + 1))
        except Exception:
            return None
    return None


def load_stop_progress() -> dict:
    """Load set of already-fetched stop IDs and results."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {'fetched': {}, 'failed': []}


def save_stop_progress(progress: dict) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False)


def scrape_stops_from_lines(session: requests.Session, lines: list[dict]) -> list[dict]:
    """Fetch coords for all unique stop IDs referenced in lines."""
    # Collect all unique stop IDs
    all_stop_ids: set[int] = set()
    for line in lines:
        for stop in line.get('stops', []):
            sid = stop.get('stop_id')
            if sid:
                all_stop_ids.add(sid)

    # Load progress
    progress = load_stop_progress()
    already_fetched = set(int(k) for k in progress['fetched'])
    already_failed = set(progress['failed'])

    todo = sorted(all_stop_ids - already_fetched - already_failed)
    total = len(all_stop_ids)
    done_before = len(already_fetched)

    print()
    print(f'  {BOLD}STOP COORDINATES{RESET}')
    print(f'  {"=" * 50}')
    print(f'  Unique stop IDs in lines:  {CYAN}{total}{RESET}')
    print(f'  Already fetched:           {GREEN}{done_before}{RESET}')
    print(f'  To fetch now:              {BOLD}{len(todo)}{RESET}')
    print(f'  {"=" * 50}')
    print()

    found = 0
    not_found = 0

    for i, stop_id in enumerate(todo):
        n = done_before + i + 1
        stop = fetch_stop(session, stop_id)

        sys.stdout.write('\r\033[K')

        if stop and stop.get('lat'):
            progress['fetched'][str(stop_id)] = stop
            found += 1
            print(f'  {DIM}{n:>5}/{total}{RESET}  {GREEN}\u2714{RESET}  '
                  f'{BOLD}{stop["name"]}{RESET}  '
                  f'{DIM}{stop["lat"]:.4f}, {stop["lon"]:.4f}{RESET}')
        else:
            progress['failed'].append(stop_id)
            not_found += 1
            name = stop['name'] if stop else f'ID {stop_id}'
            print(f'  {DIM}{n:>5}/{total}{RESET}  {RED}\u2718{RESET}  {DIM}{name}{RESET}')

        # Progress bar every 50
        if (i + 1) % 50 == 0:
            total_found = done_before + found
            pct = (done_before + i + 1) * 100 // total if total else 0
            print(f'  {CYAN}{"─" * 50}{RESET}')
            print(f'  {pct}%  {GREEN}+{found}{RESET} {RED}-{not_found}{RESET}  '
                  f'total with coords: {total_found}/{total}')
            print(f'  {CYAN}{"─" * 50}{RESET}')

        # Save every 100
        if (i + 1) % 100 == 0:
            save_stop_progress(progress)

        time.sleep(0.15)

    save_stop_progress(progress)

    # Build final stops list from all fetched data
    all_stops = list(progress['fetched'].values())
    total_with_coords = sum(1 for s in all_stops if s.get('lat'))

    print()
    print(f'  {BOLD}DONE{RESET}  +{found} new, {total_with_coords}/{total} with coords')

    return all_stops


# -- Main ----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--stops-only', action='store_true',
                        help='Skip line scraping, re-fetch stops from existing lines.json')
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session, csrf = get_session_with_csrf()

    lines_path = RAW_DIR / 'gsp_lines.json'

    if args.stops_only and lines_path.exists():
        log.info('Loading existing lines from gsp_lines.json...')
        with open(lines_path, encoding='utf-8') as f:
            lines = json.load(f)
        log.info(f'Loaded {len(lines)} lines')
    else:
        # Phase 1: line list
        print(f'\n  {BOLD}PHASE 1: LINE LIST{RESET}\n')
        lines = scrape_lines(session, csrf)
        log.info(f'Total lines: {len(lines)}')

        # Phase 2: stops per line
        print(f'\n  {BOLD}PHASE 2: STOP ORDER PER LINE{RESET}\n')
        lines = enrich_lines_with_stops(session, lines)

        with open(lines_path, 'w', encoding='utf-8') as f:
            json.dump(lines, f, ensure_ascii=False, indent=2)
        log.info(f'Saved {len(lines)} lines -> {lines_path}')

    # Phase 3: fetch coords for all stop IDs found in lines
    print(f'\n  {BOLD}PHASE 3: STOP COORDINATES{RESET}\n')
    stops = scrape_stops_from_lines(session, lines)

    stops_path = RAW_DIR / 'gsp_stops.json'
    with open(stops_path, 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=2)
    log.info(f'Saved {len(stops)} stops -> {stops_path}')

    # Summary
    with_coords = sum(1 for s in stops if s.get('lat'))
    lines_with_stops = sum(1 for l in lines if l.get('stops'))
    print()
    print(f'  {"=" * 50}')
    print(f'  {BOLD}SUMMARY{RESET}')
    print(f'  Lines:            {len(lines)} ({lines_with_stops} with stops)')
    print(f'  Stops:            {len(stops)} ({with_coords} with coords)')
    print(f'  {"=" * 50}')


if __name__ == '__main__':
    main()

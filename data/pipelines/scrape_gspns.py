"""
Scrape JGSP Novi Sad (gspns.co.rs) — city and suburban bus lines.

Uses the schedule API (/red-voznje/lista-linija) for the line list
and the network page (/mreza) for stop-to-line mappings.

The line list API only returns data for a schedule-validity date ("vaziod")
that JGSP currently publishes; a stale date yields an empty <select>. The
current date is therefore discovered from the schedule page on every run.

Output: data/raw/novi-sad/lines.json

Usage:
    python -u data/pipelines/scrape_gspns.py
"""
import html as html_mod
import json
import re
import sys
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / 'raw' / 'novi-sad'

BASE_URL = 'https://www.gspns.co.rs'
LINES_API = f'{BASE_URL}/red-voznje/lista-linija'
NETWORK_URL = f'{BASE_URL}/mreza'
SCHEDULE_PAGE = f'{BASE_URL}/red-voznje/gradski'

# Used only if the schedule page cannot be parsed; JGSP rotates this date
# whenever a new timetable takes effect, so it goes stale on its own.
FALLBACK_VAZIOD = '2026-06-22'

HEADERS = {'User-Agent': 'TransitSerbia/1.0 (transit aggregator)'}
REQUEST_DELAY = 1.5

GREEN = '\033[92m'
RED = '\033[91m'
CYAN = '\033[96m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'


def fetch(url: str, params: dict | None = None) -> str | None:
    """GET with retry. gspns.co.rs has a self-signed cert so verify=False."""
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, headers=HEADERS,
                                timeout=15, verify=False)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            if attempt < 2:
                time.sleep(REQUEST_DELAY * (attempt + 1))
            else:
                print(f'{RED}  Failed: {url} — {e}{RESET}', file=sys.stderr)
                return None
    return None


def parse_vaziod(text: str) -> str | None:
    """Extract the current schedule-validity date from the <select id='vaziod'>.

    Prefers the option marked ``selected``; otherwise takes the first one.
    Returns None when the select is absent or holds no date-shaped value.
    """
    select = re.search(r"<select[^>]*id=['\"]?vaziod['\"]?[^>]*>(.*?)</select>",
                       text, re.DOTALL | re.IGNORECASE)
    if not select:
        return None

    options = re.findall(r'<option([^>]*)>', select.group(1), re.IGNORECASE)
    dates: list[str] = []
    for attrs in options:
        value = re.search(r"value=['\"]?(\d{4}-\d{2}-\d{2})['\"]?", attrs)
        if not value:
            continue
        if re.search(r'\bselected\b', attrs, re.IGNORECASE):
            return value.group(1)
        dates.append(value.group(1))

    return dates[0] if dates else None


def parse_line_list(text: str) -> list[dict]:
    """Parse <option value="CODE">NUMBER NAME</option> into line dicts."""
    lines = []
    for m in re.finditer(r'<option\s+value="([^"]+)">([^<]+)</option>', text):
        code = m.group(1)
        full_name = html_mod.unescape(m.group(2)).strip()

        parts = full_name.split(' ', 1)
        number = parts[0].rstrip('.')
        name = parts[1] if len(parts) > 1 else full_name
        name = re.sub(r'\s*-\s*', ' — ', name)

        lines.append({'number': number, 'name': name, 'code': code})
    return lines


def parse_network_stops(text: str) -> dict[str, list[str]]:
    """Parse /mreza table rows to get stop lists per line direction."""
    stops_by_dir: dict[str, list[str]] = {}
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)

    for row in rows:
        clean = re.sub(r'<[^>]+>', ' ', row).strip()
        clean = re.sub(r'\s+', ' ', clean).strip()
        if len(clean) < 5:
            continue
        m = re.match(r'^(\d+\w*)\s+(.*)', clean)
        if m:
            line_code = m.group(1)
            stops = [s.strip() for s in m.group(2).split('-') if s.strip()]
            stops_by_dir[line_code] = stops

    return stops_by_dir


def main() -> None:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print(f'  {BOLD}SCRAPE JGSP NOVI SAD{RESET}')
    print(f'  {"=" * 50}')

    # 1. Discover the schedule-validity date the API currently serves
    schedule_html = fetch(SCHEDULE_PAGE)
    vaziod = parse_vaziod(schedule_html) if schedule_html else None
    if vaziod:
        print(f'  Schedule valid from {GREEN}{vaziod}{RESET}')
    else:
        vaziod = FALLBACK_VAZIOD
        print(f'{RED}  Could not read vaziod — falling back to {vaziod}{RESET}',
              file=sys.stderr)
    time.sleep(REQUEST_DELAY)

    # 2. Fetch city + suburban line lists from schedule API
    all_lines: list[dict] = []

    for rv, label, line_type in [('rvg', 'Gradski', 'bus'),
                                  ('rvp', 'Prigradski', 'suburban')]:
        print(f'  Fetching {label} lines...')
        text = fetch(LINES_API, params={'rv': rv, 'vaziod': vaziod, 'dan': 'R'})
        if not text:
            continue
        lines = parse_line_list(text)
        for line in lines:
            line['type'] = line_type
        all_lines.extend(lines)
        print(f'  {GREEN}{len(lines)}{RESET} {label} lines')
        time.sleep(REQUEST_DELAY)

    if not all_lines:
        print(f'{RED}  No lines found — aborting{RESET}')
        sys.exit(1)

    # 3. Fetch stop lists from /mreza
    print(f'  Fetching network map (stops)...')
    mreza_html = fetch(NETWORK_URL)
    if mreza_html:
        stops_by_dir = parse_network_stops(mreza_html)
        print(f'  {GREEN}{len(stops_by_dir)}{RESET} direction entries')

        for line in all_lines:
            num = line['number']
            stops = stops_by_dir.get(f'{num}A', stops_by_dir.get(num, []))
            line['stops'] = stops
    else:
        for line in all_lines:
            line['stops'] = []

    # 4. Save — strip internal 'code' field
    for line in all_lines:
        line.pop('code', None)

    out_path = OUT_DIR / 'lines.json'

    # JGSP /mreza gives stop NAMES only. The richer stop lists (with
    # coordinates) come from the OSM importer that runs right after this,
    # writing the same file — so overwriting wholesale throws them away and the
    # city depends on Overpass succeeding every single night. It did not on
    # 2026-08-07 (504 on the route query) and Novi Sad dropped from 286 stops
    # to 66. Carry the existing stop list over for any line whose fresh scrape
    # has fewer stops; the OSM run then updates them in place.
    if out_path.exists():
        try:
            with open(out_path, encoding='utf-8') as f:
                previous = {l['number']: l for l in json.load(f)}
        except (OSError, ValueError, KeyError):
            previous = {}
        for line in all_lines:
            old = previous.get(line['number'])
            if not old:
                continue
            if len(old.get('stops') or []) > len(line.get('stops') or []):
                line['stops'] = old['stops']

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_lines, f, ensure_ascii=False, indent=2)

    city_count = sum(1 for l in all_lines if l['type'] == 'bus')
    sub_count = sum(1 for l in all_lines if l['type'] == 'suburban')
    with_stops = sum(1 for l in all_lines if l.get('stops'))

    print(f'  {"=" * 50}')
    print(f'  {BOLD}DONE{RESET}')
    print(f'  City: {GREEN}{city_count}{RESET}, Suburban: {GREEN}{sub_count}{RESET}')
    print(f'  With stops: {with_stops}')
    print(f'  Saved: {CYAN}{out_path}{RESET}')
    print()


if __name__ == '__main__':
    main()

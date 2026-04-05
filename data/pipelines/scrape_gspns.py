"""
Scrape JGSP Novi Sad (gspns.co.rs) — city and suburban bus lines.

Uses the schedule API (/red-voznje/lista-linija) for the line list
and the network page (/mreza) for stop-to-line mappings.

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

    # 1. Fetch city + suburban line lists from schedule API
    all_lines: list[dict] = []

    for rv, label, line_type in [('rvg', 'Gradski', 'bus'),
                                  ('rvp', 'Prigradski', 'suburban')]:
        print(f'  Fetching {label} lines...')
        text = fetch(LINES_API, params={'rv': rv, 'vaziod': '2026-04-01', 'dan': 'R'})
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

    # 2. Fetch stop lists from /mreza
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

    # 3. Save — strip internal 'code' field
    for line in all_lines:
        line.pop('code', None)

    out_path = OUT_DIR / 'lines.json'
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

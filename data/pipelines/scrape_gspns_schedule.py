"""
Scrape JGSP Novi Sad departure schedules from gspns.co.rs.

Endpoints:
  GET /red-voznje/gradski (main page, contains vaziod dates)
  GET /red-voznje/lista-linija?rv=rvg&vaziod=DATE&dan=R  → line list HTML <select>
  GET /red-voznje/ispis-polazaka?rv=rvg&vaziod=DATE&dan=R&linija[]=CODE  → timetable HTML

Output:
  data/raw/novi-sad/schedule.json

Usage:
  python -u data/pipelines/scrape_gspns_schedule.py
"""
import json
import re
import sys
import time
import urllib3
from pathlib import Path

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://www.gspns.co.rs'
RAW_DIR = Path(__file__).parent.parent / 'raw' / 'novi-sad'

DAY_TYPES = ['R', 'S', 'N']  # Radni, Subota, Nedelja
DAY_LABELS = {'R': 'RD', 'S': 'S', 'N': 'N'}  # Map to our service_id format
RV_TYPES = ['rvg', 'rvp']
RV_LABELS = {'rvg': 'urban', 'rvp': 'suburban'}

GREEN = '\033[92m'
RED = '\033[91m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0 Transit-Serbia-Bot/1.0'})
SESSION.verify = False


def find_vaziod() -> str:
    """Extract valid vaziod date from the schedule page."""
    r = SESSION.get(f'{BASE_URL}/red-voznje/gradski', timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    select = soup.find('select', id='vaziod')
    if select:
        opt = select.find('option')
        if opt:
            return opt.get('value', '').strip()
    # Fallback: find in raw HTML
    match = re.search(r'value="(\d{4}-\d{2}-\d{2})"', r.text)
    return match.group(1) if match else '2026-04-01'


def fetch_line_list(rv: str, dan: str, vaziod: str) -> list[dict]:
    """Fetch line codes from /red-voznje/lista-linija."""
    r = SESSION.get(f'{BASE_URL}/red-voznje/lista-linija',
                    params={'rv': rv, 'vaziod': vaziod, 'dan': dan}, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    lines = []
    for opt in soup.find_all('option'):
        code = opt.get('value', '').strip()
        text = opt.get_text(strip=True)
        if code:
            parts = text.split(' ', 1)
            number = parts[0].strip().rstrip('.*')
            name = parts[1].strip() if len(parts) > 1 else ''
            lines.append({'code': code, 'number': number, 'name': name})
    return lines


def fetch_departures(rv: str, vaziod: str, dan: str, line_code: str) -> dict:
    """Fetch departure times for a line."""
    r = SESSION.get(f'{BASE_URL}/red-voznje/ispis-polazaka',
                    params={'rv': rv, 'vaziod': vaziod, 'dan': dan, 'linija[]': line_code},
                    timeout=15)
    r.raise_for_status()
    return parse_timetable_html(r.text)


def parse_timetable_html(html: str) -> dict:
    """Parse hour-minute timetable HTML into departure time lists.

    Format: each <td> contains <b>HH</b><sup>MM</sup> sequences.
    """
    soup = BeautifulSoup(html, 'html.parser')
    result = {'smer_a': [], 'smer_b': []}

    table = soup.find('table')
    if not table:
        return result

    rows = table.find_all('tr')
    for row in rows[1:]:  # skip header
        cells = row.find_all('td')
        for ci, cell in enumerate(cells):
            direction = 'smer_a' if ci == 0 else 'smer_b'
            current_hour = None
            for child in cell.children:
                if child.name == 'b':
                    h = child.get_text(strip=True)
                    if h.isdigit():
                        current_hour = int(h)
                elif child.name == 'sup' and current_hour is not None:
                    m = child.get_text(strip=True)
                    if m.isdigit():
                        result[direction].append(f'{current_hour:02d}:{int(m):02d}')

    return result


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    vaziod = find_vaziod()
    all_schedules = []
    total_lines = 0
    total_departures = 0

    print(f'\n  {BOLD}GSPNS SCHEDULE SCRAPER{RESET}')
    print(f'  {"=" * 50}')
    print(f'  vaziod: {vaziod}')
    print(f'  {"=" * 50}\n')

    for rv in RV_TYPES:
        rv_label = RV_LABELS[rv]
        lines = fetch_line_list(rv, 'R', vaziod)
        print(f'  {BOLD}{rv_label.upper()}{RESET}: {len(lines)} lines\n')

        for i, line in enumerate(lines):
            n = i + 1
            line_departures = 0

            for dan in DAY_TYPES:
                try:
                    deps = fetch_departures(rv, vaziod, dan, line['code'])
                    a_count = len(deps['smer_a'])
                    b_count = len(deps['smer_b'])

                    if a_count > 0 or b_count > 0:
                        all_schedules.append({
                            'line_number': line['number'],
                            'line_code': line['code'],
                            'line_name': line['name'],
                            'rv_type': rv_label,
                            'service': DAY_LABELS[dan],
                            'smer_a': deps['smer_a'],
                            'smer_b': deps['smer_b'],
                        })
                        line_departures += a_count + b_count

                    time.sleep(0.3)
                except Exception as e:
                    print(f'  {RED}!{RESET} {line["number"]} dan={dan}: {e}')
                    time.sleep(1)

            status = f'{GREEN}{line_departures} dep{RESET}' if line_departures else f'{RED}empty{RESET}'
            print(f'  {DIM}{n:>4}/{len(lines)}{RESET}  {BOLD}{line["number"]:>4}{RESET} {line["name"][:35]:35s}  {status}')
            total_departures += line_departures
            total_lines += 1

        print()

    out_path = RAW_DIR / 'schedule.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_schedules, f, ensure_ascii=False, indent=2)

    print(f'  {"=" * 50}')
    print(f'  {BOLD}DONE{RESET}')
    print(f'  Lines:      {total_lines}')
    print(f'  Schedules:  {len(all_schedules)}')
    print(f'  Departures: {total_departures}')
    print(f'  Saved:      {out_path}')
    print(f'  {"=" * 50}\n')


if __name__ == '__main__':
    main()

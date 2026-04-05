"""
Scrape JGSP Novi Sad departure schedules from gspns.co.rs.

Endpoints:
  GET /red-voznje/lista-linija?rv=rvg&vaziod=DATE&dan=R  → line list HTML <select>
  GET /red-voznje/ispis-polazaka?rv=rvg&vaziod=DATE&dan=R&linija[]=CODE  → timetable HTML

Output:
  data/raw/novi-sad/schedule.json — departure times per line/direction/day

Usage:
  python -u data/pipelines/scrape_gspns_schedule.py
"""
import json
import re
import sys
import time
import urllib3
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://www.gspns.co.rs'
RAW_DIR = Path(__file__).parent.parent / 'raw' / 'novi-sad'

DAY_TYPES = ['R', 'S', 'N']  # Radni, Subota, Nedelja
RV_TYPES = ['rvg', 'rvp']    # gradski, prigradski
RV_LABELS = {'rvg': 'urban', 'rvp': 'suburban'}

GREEN = '\033[92m'
RED = '\033[91m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0 Transit-Serbia-Bot/1.0'})
SESSION.verify = False


def fetch_line_list(rv: str, dan: str, date: str) -> list[dict]:
    """Fetch line codes from /red-voznje/lista-linija."""
    r = SESSION.get(f'{BASE_URL}/red-voznje/lista-linija',
                    params={'rv': rv, 'vaziod': date, 'dan': dan}, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    lines = []
    for opt in soup.find_all('option'):
        code = opt.get('value', '').strip()
        text = opt.get_text(strip=True)
        if code:
            # text format: "1 - Centar - Liman" or "3A - Novo Naselje - Centar"
            parts = text.split(' - ', 1)
            number = parts[0].strip().rstrip('.*')
            name = parts[1].strip() if len(parts) > 1 else ''
            lines.append({'code': code, 'number': number, 'name': name})
    return lines


def fetch_departures(rv: str, date: str, dan: str, line_code: str) -> dict:
    """Fetch departure times for a line. Returns {smer_a: [times], smer_b: [times]}."""
    r = SESSION.get(f'{BASE_URL}/red-voznje/ispis-polazaka',
                    params={'rv': rv, 'vaziod': date, 'dan': dan, 'linija[]': line_code},
                    timeout=15)
    r.raise_for_status()
    return parse_timetable_html(r.text)


def parse_timetable_html(html: str) -> dict:
    """Parse hour-minute timetable HTML into departure time lists."""
    soup = BeautifulSoup(html, 'html.parser')
    result = {'smer_a': [], 'smer_b': []}

    tables = soup.find_all('table')
    if not tables:
        return result

    # Usually 1 table with rows: each row has Smer A times (left) and Smer B times (right)
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            for cell_idx, cell in enumerate(cells):
                direction = 'smer_a' if cell_idx == 0 else 'smer_b'
                # Format: <b>05</b><sup>00</sup> <sup>19</sup> <sup>38</sup>
                bold = cell.find('b')
                if not bold:
                    continue
                hour = bold.get_text(strip=True)
                if not hour.isdigit():
                    continue
                hour = int(hour)
                for sup in cell.find_all('sup'):
                    minute = sup.get_text(strip=True)
                    if minute.isdigit():
                        result[direction].append(f'{hour:02d}:{int(minute):02d}')

    return result


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    all_schedules = []
    total_lines = 0
    total_departures = 0

    print(f'\n  {BOLD}GSPNS SCHEDULE SCRAPER{RESET}')
    print(f'  {"=" * 50}')
    print(f'  Date: {today}')
    print(f'  Day types: {", ".join(DAY_TYPES)}')
    print(f'  {"=" * 50}\n')

    for rv in RV_TYPES:
        rv_label = RV_LABELS[rv]
        # Fetch line list once (using workday)
        lines = fetch_line_list(rv, 'R', today)
        print(f'  {BOLD}{rv_label.upper()}{RESET}: {len(lines)} lines')

        for i, line in enumerate(lines):
            n = i + 1
            line_departures = 0

            for dan in DAY_TYPES:
                try:
                    deps = fetch_departures(rv, today, dan, line['code'])
                    a_count = len(deps['smer_a'])
                    b_count = len(deps['smer_b'])

                    if a_count > 0 or b_count > 0:
                        schedule_entry = {
                            'line_number': line['number'],
                            'line_code': line['code'],
                            'line_name': line['name'],
                            'rv_type': rv_label,
                            'service': dan,
                            'smer_a': deps['smer_a'],
                            'smer_b': deps['smer_b'],
                        }
                        all_schedules.append(schedule_entry)
                        line_departures += a_count + b_count

                    time.sleep(0.3)
                except Exception as e:
                    print(f'  {RED}Error{RESET} {line["number"]} dan={dan}: {e}')
                    time.sleep(1)

            status = f'{GREEN}{line_departures} dep{RESET}' if line_departures else f'{RED}empty{RESET}'
            print(f'  {DIM}{n:>4}/{len(lines)}{RESET}  {BOLD}{line["number"]:>4}{RESET} {line["name"][:35]:35s}  {status}')
            total_departures += line_departures
            total_lines += 1

        print()

    # Save
    out_path = RAW_DIR / 'schedule.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_schedules, f, ensure_ascii=False, indent=2)

    print(f'  {"=" * 50}')
    print(f'  {BOLD}DONE{RESET}')
    print(f'  Lines:      {total_lines}')
    print(f'  Schedules:  {len(all_schedules)} (lines x day types)')
    print(f'  Departures: {total_departures}')
    print(f'  Saved:      {out_path}')
    print(f'  {"=" * 50}\n')


if __name__ == '__main__':
    main()

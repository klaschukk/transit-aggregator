"""
Scraper for JGSP Novi Sad city bus lines — gspns.co.rs.

Fetches the line network page (/mreza) and parses the HTML to extract
all urban ("grad") bus lines with their numbers and route names.

Output: data/raw/novi-sad/lines.json
"""
import json
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'http://www.gspns.co.rs'
RAW_DIR = Path(__file__).parent.parent / 'raw' / 'novi-sad'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept-Language': 'sr,en;q=0.9',
}


def scrape_lines() -> list[dict]:
    """Scrape urban bus lines from GSPNS network page."""
    resp = requests.get(
        f'{BASE_URL}/mreza', headers=HEADERS, verify=False, timeout=30,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'lxml')

    lines = []
    for a in soup.select('a.button-linija.grad'):
        classes = a.get('class', [])
        number = a.get_text(strip=True)
        name = a.get('title', '')

        if not number or not name:
            continue

        lines.append({
            'number': number,
            'name': name,
            'type': 'bus',
            'stops': [],
        })

    log.info(f'Parsed {len(lines)} urban lines from /mreza')
    return lines


def main() -> None:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    lines = scrape_lines()

    out_path = RAW_DIR / 'lines.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(lines, f, ensure_ascii=False, indent=2)

    log.info(f'Saved {len(lines)} lines → {out_path}')


if __name__ == '__main__':
    main()

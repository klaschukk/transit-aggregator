"""
Scraper for JGP Niš (Naissus) city bus lines — jgpnis.rs.

Fetches the urban lines page and parses numbered line entries
with their route names from the HTML.

Output: data/raw/nis/lines.json
"""
import json
import logging
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://jgpnis.rs'
RAW_DIR = Path(__file__).parent.parent / 'raw' / 'nis'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept-Language': 'sr,en;q=0.9',
}


def scrape_lines() -> list[dict]:
    """Scrape urban bus lines from JGP Niš website."""
    resp = requests.get(
        f'{BASE_URL}/linije/gradske-linije/',
        headers=HEADERS, timeout=30,
    )
    resp.raise_for_status()

    text = BeautifulSoup(resp.text, 'lxml').get_text('\n')

    lines = []
    current_number = None

    for raw_line in text.split('\n'):
        raw_line = raw_line.strip()
        if not raw_line:
            continue

        # Match "ЛИНИЈА 1" or "ЛИНИЈА 34"
        m = re.match(
            r'ЛИНИЈА\s+(\d+[А-Яа-яA-Za-z]*)', raw_line, re.IGNORECASE,
        )
        if m:
            current_number = m.group(1)
            continue

        # The line after ЛИНИЈА N is the route name (e.g., "БУБАЊ - ДОЊА ВРЕЖИНА")
        if current_number and re.match(r'^[А-ЯЁЋЂЉЊШЖ]', raw_line):
            # Skip route detail lines (long descriptions with street names)
            if len(raw_line) > 80:
                continue
            # Must contain a dash separator
            if ' - ' in raw_line or ' – ' in raw_line:
                name = raw_line.replace('–', '-').strip()
                lines.append({
                    'number': current_number,
                    'name': name,
                    'type': 'bus',
                    'stops': [],
                })
                current_number = None

    # Deduplicate by number (keep first)
    seen = set()
    unique = []
    for line in lines:
        if line['number'] not in seen:
            seen.add(line['number'])
            unique.append(line)

    log.info(f'Parsed {len(unique)} urban lines from /linije/gradske-linije/')
    return unique


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    lines = scrape_lines()

    out_path = RAW_DIR / 'lines.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(lines, f, ensure_ascii=False, indent=2)

    log.info(f'Saved {len(lines)} lines → {out_path}')


if __name__ == '__main__':
    main()

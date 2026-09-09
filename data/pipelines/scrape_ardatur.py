"""
Scraper for ArdaTur (ardatur.bg) — Bulgaria <-> wider-Europe/Turkey coaches.

Scoped to Bulgaria-international pairs only (Sofia/Plovdiv/Varna as origins):
Bulgaria-domestic is already covered by union-ivkoni.com (scrape_ivkoni.py).
ArdaTur's real value-add is destinations neither existing source has yet —
Istanbul, Prague, Budapest, Vienna — plus a second real operator's own
departures/prices on Athens/Thessaloniki/Munich/Berlin (genuinely useful:
a traveler comparing options, not duplicate data, since times/prices differ
by operator).

GET https://ardatur.bg/en/search/{fromId}/{toId}/ is a plain server-rendered
page — no JS, no session, no POST — verified with a bare `requests.get()`.
City IDs come from the <select id="bgn"> options on the homepage (harvested
by hand 2026-09-09, see CITIES below). Each real departure is one
`<tr data-id="...">` in `.result-table`; a route with no service that day
renders zero such rows (verified against a known-unserved pair). The arrival
time is followed by an explicit `+1` marker when the bus arrives the next
day — no guessing needed, unlike srbijatours.com's schedule (which had to
be fixed after shipping — see that scraper's commit history).

robots.txt (https://ardatur.bg/robots.txt) is fully open (`Disallow:` empty).

Output: data/raw/ardatur/routes.json  (nested format)
        data/raw/ardatur/trips.json   (flat format for build_db.py)
        data/raw/ardatur/operators.json
"""
import json
import logging
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.slug import normalize_slug  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://ardatur.bg'
RAW_DIR = Path(__file__).parent.parent / 'raw'
OUT_DIR = RAW_DIR / 'ardatur'

OPERATOR_NAME = 'ArdaTur'
EUR_RSD_RATE = 117  # matches config.py's default; site only publishes EUR

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept-Language': 'en,bg;q=0.9',
}

# City display name (Latin, matching prevozni's existing Balkan naming) ->
# ArdaTur's internal numeric city id (from <select id="bgn"> on
# https://ardatur.bg/, harvested by hand 2026-09-09).
CITIES: dict[str, int] = {
    'Sofija': 1, 'Plovdiv': 2, 'Varna': 3,
    'Atina': 105, 'Solun': 173, 'Istanbul': 30,
    'Prag': 149, 'Budimpešta': 146, 'Beč': 143,
    'Minhen': 130, 'Berlin': 165,
}

_BG_FROM = ['Sofija', 'Plovdiv', 'Varna']
_INTL_TO = ['Atina', 'Solun', 'Istanbul', 'Prag', 'Budimpešta', 'Beč', 'Minhen', 'Berlin']

PAIRS: list[tuple[str, str]] = (
    [(f, t) for f in _BG_FROM for t in _INTL_TO]
    + [(t, f) for f in _BG_FROM for t in _INTL_TO]
)

ROW_RE = re.compile(r'<tr data-id="\d+">(.*?)</tr>', re.S)
TIME_RE = re.compile(r'<b>(\d{2}:\d{2})</b>')
ARRIVE_RE = re.compile(r'station-time">\s*(\d{2}:\d{2})\s*(\+1)?\s*</div>', re.S)
DURATION_RE = re.compile(r'(\d+)\s*hours?\s*(\d+)?\s*minutes?', re.I)
# The fare sits inside the tooltip-triggering <a> ("61&nbsp;&euro;</a>"), NOT
# in the neighbouring .total-price-column — that column is the shopping
# cart's running total (always "0 €" until something's actually added to
# the cart), and matching it first silently returned a real-looking but
# wrong price of 0 for every single trip, tripping the price<=0 guard below
# and making every pair look like it had no service at all. Caught by
# testing against a route confirmed working live, not by assumption.
PRICE_RE = re.compile(r'(\d+(?:\.\d+)?)\s*&nbsp;&euro;\s*</a>')


def _slug(name: str) -> str:
    return normalize_slug(name)


def parse_results(html: str, from_city: str, to_city: str) -> list[dict]:
    trips = []
    for row in ROW_RE.findall(html):
        times = TIME_RE.findall(row)
        arrivals = ARRIVE_RE.findall(row)
        if len(times) < 1 or len(arrivals) < 1:
            continue
        dep = times[0]
        arr, next_day = arrivals[0]

        dur_m = DURATION_RE.search(row)
        if dur_m:
            hours = int(dur_m.group(1))
            minutes = int(dur_m.group(2)) if dur_m.group(2) else 0
            duration = hours * 60 + minutes
        else:
            # Fall back to the times themselves — always next_day-aware per
            # the explicit "+1" marker, same discipline as srbijatours.
            dh, dm = map(int, dep.split(':'))
            ah, am = map(int, arr.split(':'))
            duration = (ah * 60 + am) - (dh * 60 + dm)
            if next_day or duration < 0:
                duration += 24 * 60

        price_m = PRICE_RE.search(row)
        if not price_m:
            continue
        price_eur = float(price_m.group(1))
        if price_eur <= 0:
            continue

        trips.append({
            'from_city': from_city,
            'to_city': to_city,
            'departure_time': dep,
            'arrival_time': arr,
            'duration_min': duration,
            'price_rsd': round(price_eur * EUR_RSD_RATE),
            'operator': OPERATOR_NAME,
            'type': 'bus',
        })
    return trips


def fetch_schedule(session: requests.Session, from_city: str, to_city: str,
                    travel_date: date) -> list[dict]:
    from_id, to_id = CITIES.get(from_city), CITIES.get(to_city)
    if not from_id or not to_id:
        return []
    # travel_date is accepted for interface symmetry with the other scrapers
    # but ArdaTur's /search/{from}/{to}/ URL always shows the next
    # available date server-side (verified) rather than taking a date
    # param — there is no way to pin a specific day, so this reflects
    # "next departure the site itself would show a visitor today".
    url = f'{BASE_URL}/en/search/{from_id}/{to_id}/'
    try:
        resp = session.get(url, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            return []
    except requests.RequestException as e:
        log.error(f'  Request failed {from_city}->{to_city}: {e}')
        return []
    resp.encoding = 'utf-8'
    return parse_results(resp.text, from_city, to_city)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    travel_date = date.today() + timedelta(days=1)
    log.info(f'Pairs: {len(PAIRS)}\n')

    routes: list[dict] = []
    for i, (from_city, to_city) in enumerate(PAIRS, 1):
        trips = fetch_schedule(session, from_city, to_city, travel_date)
        scraped_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
        for t in trips:
            t['scraped_at'] = scraped_at

        if trips:
            routes.append({
                'from_city': from_city, 'to_city': to_city,
                'slug': f'{_slug(from_city)}-{_slug(to_city)}',
                'trips': trips, 'scraped_at': scraped_at,
            })
            log.info(f'[{i}/{len(PAIRS)}] {from_city} -> {to_city}: {len(trips)} departures')
        else:
            log.info(f'[{i}/{len(PAIRS)}] {from_city} -> {to_city}: none')

        time.sleep(0.5)

    flat_trips = [t for r in routes for t in r['trips']]

    with open(OUT_DIR / 'routes.json', 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / 'trips.json', 'w', encoding='utf-8') as f:
        json.dump(flat_trips, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / 'operators.json', 'w', encoding='utf-8') as f:
        json.dump({OPERATOR_NAME: 'bus'}, f, ensure_ascii=False, indent=2)

    log.info('\n=== Done ===')
    log.info(f'Routes found : {len(routes)}')
    log.info(f'Total trips  : {len(flat_trips)}')


if __name__ == '__main__':
    main()

"""
Scraper for Union Ivkoni (union-ivkoni.com) — Bulgaria's largest bus
carrier. First non-Serbia-anchored content on prevozni: Bulgaria-domestic
routes plus Bulgaria <-> Greece, added at the owner's explicit direction
even though neither touches Serbia (2026-09-06).

The search form (POST https://union-ivkoni.com/bg/routes, fields
type/from/to/sdate/rdate/adults) is a plain server-rendered form — no
JS execution needed, no session/cookies required (verified with a bare
`requests.Session()`, no browser). from/to are numeric city IDs from the
site's own <select> (harvested once by hand, see CITIES below); sdate is
DD-MM-YYYY. Each real result renders as a `.tickets-results-item` with
`data-leave`/`data-arrive` (HH:MM:SS) on the "Избери" (Select) button,
`data-multilink` (0 = direct bus, non-zero = a connection needing a
transfer we don't attempt to model), and a discounted EUR price in
`.result-item-price`.

robots.txt (https://union-ivkoni.com/robots.txt) has no Disallow rules
relevant to this path.

Scope is intentionally a curated set of city pairs, not every possible
combination of the site's ~140 Bulgarian + ~60 Greek cities in its
dropdown — that full cross-product is thousands of queries for mostly
tiny beach-resort towns. This is a hub-and-spoke pattern (Sofia <-> major
BG cities, like scrape_lasta.py does for Beograd) plus the two Greek
cities anyone would actually search for.

Output: data/raw/ivkoni/routes.json  (nested format)
        data/raw/ivkoni/trips.json   (flat format for build_db.py)
        data/raw/ivkoni/operators.json
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

BASE_URL = 'https://union-ivkoni.com'
SEARCH_URL = f'{BASE_URL}/bg/routes'
RAW_DIR = Path(__file__).parent.parent / 'raw'
OUT_DIR = RAW_DIR / 'ivkoni'

OPERATOR_NAME = 'Union Ivkoni'
EUR_RSD_RATE = 117  # matches config.py's default; site only publishes EUR/BGN

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept-Language': 'bg,en;q=0.9',
}

# City display name (Latin, matching prevozni's existing Balkan naming —
# 'Sofija'/'Solun' already exist in app/city_coords.py for other routes)
# -> Union Ivkoni's internal numeric city id (from <select name="from">
# on https://union-ivkoni.com/bg, harvested by hand 2026-09-06).
CITIES: dict[str, int] = {
    'Sofija': 161, 'Plovdiv': 128, 'Burgas': 23, 'Varna': 29,
    'Stara Zagora': 170, 'Pleven': 127, 'Ruse': 144,
    'Blagoevgrad': 15, 'Veliko Tarnovo': 30,
    'Atina': 215, 'Solun': 424,
}

# Sofia hub-and-spoke across Bulgaria (mirrors scrape_lasta.py's pattern
# for Beograd), plus the three BG cities closest to the Greek border
# paired with the two Greek cities anyone would search for.
_BG_HUB = 'Sofija'
_BG_SPOKES = ['Plovdiv', 'Burgas', 'Varna', 'Stara Zagora', 'Pleven',
              'Ruse', 'Blagoevgrad', 'Veliko Tarnovo']
_GR_FROM = ['Sofija', 'Plovdiv', 'Burgas']
_GR_TO = ['Atina', 'Solun']

PAIRS: list[tuple[str, str]] = (
    [(_BG_HUB, s) for s in _BG_SPOKES] + [(s, _BG_HUB) for s in _BG_SPOKES]
    + [(f, t) for f in _GR_FROM for t in _GR_TO]
    + [(t, f) for f in _GR_FROM for t in _GR_TO]
)

RESULT_ITEM_RE = re.compile(
    r'<div class="tickets-results-item[^"]*"[^>]*>(.*?)</div>\s*</div>\s*(?=<div class="tickets-results-item|<p class="small"|$)',
    re.S,
)
CITY_RE = re.compile(r'<div class="result-item-city">([^<]+)<br>')
PRICE_RE = re.compile(r'<div class="result-item-price">\s*([\d.]+)\s*€', re.S)
SELECT_RE = re.compile(
    r'data-leave="(\d{2}:\d{2}):\d{2}"[^>]*data-arrive="(\d{2}:\d{2}):\d{2}"'
    r'[^>]*data-multilink="(\d+)"'
)
# Same attribute order isn't guaranteed by the markup, so also try the
# reverse — leave/arrive found, multilink found separately, on one <a>.
SELECT_ATTRS_RE = re.compile(
    r'<a[^>]+class="[^"]*select-lroute[^"]*"([^>]+)>', re.S
)


def _slug(name: str) -> str:
    return normalize_slug(name)


def _attr(attrs: str, name: str) -> str | None:
    m = re.search(name + r'="([^"]*)"', attrs)
    return m.group(1) if m else None


def parse_results(html: str, from_city: str, to_city: str) -> list[dict]:
    """One <div class="tickets-results-item"> per real departure. Direct
    trips only (data-multilink="0") — a connection needing a transfer has
    pricing/timing semantics this parser hasn't verified, so it's skipped
    rather than guessed at."""
    trips = []
    for a_attrs in SELECT_ATTRS_RE.findall(html):
        multilink = _attr(a_attrs, 'data-multilink')
        if multilink != '0':
            continue
        leave = _attr(a_attrs, 'data-leave')
        arrive = _attr(a_attrs, 'data-arrive')
        if not leave or not arrive:
            continue
        # The price sits in a sibling block just before this <a>, not an
        # attribute on it — scoped by finding the nearest preceding
        # result-item-price within a bounded lookback window rather than
        # a full DOM parse (BeautifulSoup would be cleaner but this file's
        # markup is simple/consistent enough that one more regex per item
        # is not worth the dependency).
        idx = html.find(a_attrs)
        window = html[max(0, idx - 1500):idx]
        price_m = PRICE_RE.findall(window)
        if not price_m:
            continue
        price_eur = float(price_m[-1])

        dep, arr = leave[:5], arrive[:5]
        dh, dm = map(int, dep.split(':'))
        ah, am = map(int, arr.split(':'))
        duration = (ah * 60 + am) - (dh * 60 + dm)
        if duration < 0:
            duration += 24 * 60

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
    data = {
        'type': '1', 'from': str(from_id), 'to': str(to_id),
        'sdate': travel_date.strftime('%d-%m-%Y'), 'rdate': '', 'adults': '1',
    }
    try:
        resp = session.post(SEARCH_URL, data=data, headers=HEADERS, timeout=30)
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

    travel_date = date.today() + timedelta(days=14)
    log.info(f'Pairs: {len(PAIRS)}, date: {travel_date.isoformat()}\n')

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
            log.info(f'[{i}/{len(PAIRS)}] {from_city} -> {to_city}: {len(trips)} direct departures')
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

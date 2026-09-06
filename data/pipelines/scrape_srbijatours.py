"""
Scraper for Serbia -> Western Europe diaspora bus routes — Srbija Tours
International (srbijatours.com, brand "Unaline").

Unlike the other scrapers in this directory, this source needs exactly ONE
HTTP GET: the single page /red-voznje/ is a statically pre-rendered (SSR/SSG)
React page that embeds the FULL timetable for all 5 corridors — real
HH:MM boarding/arrival times for every stop, both directions — directly in
the HTML. No AJAX call, no JS execution, no session/cookies needed. Verified
2026-09-04 by fetching the page with a plain `requests.get()` and a browser
User-Agent: the times below are exactly what a browser renders.

Coverage confirmed on the page (meta description): "5 koridora, 30 gradova
u Nemačkoj, ukrcavanje u 16 mesta u Srbiji" — i.e. 5 corridors, 30 German
cities, boarding at 16 Serbian cities. Each corridor is one daily multi-stop
bus (like a train) — the site gives the real stop-by-stop time, not just
origin/destination, so trips below are derived per (Serbian stop, German
stop) pair using that stop's own listed clock time, exactly like a
real passenger would read the timetable.

No prices are published on this page (booking price only appears in their
checkout flow, which we do not touch).

robots.txt (https://www.srbijatours.com/robots.txt) is fully open
(`Allow: /`) — nothing under /red-voznje/ is disallowed.

Output: data/raw/srbijatours/routes.json  (nested format)
        data/raw/srbijatours/trips.json   (flat format for build_db.py)
        data/raw/srbijatours/operators.json
"""
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.slug import normalize_slug  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

BASE_URL = 'https://www.srbijatours.com'
SCHEDULE_URL = f'{BASE_URL}/red-voznje/'
RAW_DIR = Path(__file__).parent.parent / 'raw'
OUT_DIR = RAW_DIR / 'srbijatours'

OPERATOR_NAME = 'Srbija Tours International'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        'Chrome/122.0 Safari/537.36'
    ),
    'Accept-Language': 'sr,en;q=0.9',
}

ARTICLE_RE = re.compile(
    r'<article class="rounded-2xl border[^"]*"[^>]*>(.*?)</article>', re.S
)
H2_RE = re.compile(r'<h2[^>]*>Srbija\s*–\s*([^<]+)</h2>')
LIST_HEADING_RE = re.compile(
    r'<h4[^>]*>([^<]+)</h4><ul class="space-y-1\.5">(.*?)</ul>', re.S
)
LI_RE = re.compile(
    r'<li[^>]*><span[^>]*>([0-2]\d:[0-5]\d)</span>'
    r'<span[^>]*>([^<]+)</span></li>'
)

# Maps the Serbian heading text to a direction/kind label.
HEADING_KIND = {
    'Ukrcavanje u Srbiji': ('outbound', 'board'),
    'Dolazak u Nemačku — sledećeg dana': ('outbound', 'arrive'),
    'Polazak iz Nemačke': ('inbound', 'board'),
    'Dolazak u Srbiju — sledećeg dana': ('inbound', 'arrive'),
}


def _slug(name: str) -> str:
    return normalize_slug(name)


def _parse_stop_list(html_fragment: str) -> list[tuple[str, str]]:
    """Extract [(HH:MM, city_name), ...] in document order from one <ul>."""
    return LI_RE.findall(html_fragment)


def _duration_min(dep: str, arr: str, next_day: bool) -> int:
    """dep/arr are both bare clock times (no date). The site's own headings
    say the arrival list is "sledećeg dana" (next day) — unconditionally,
    not just when the raw HH:MM subtraction happens to go negative. A city
    whose local departure clock time is EARLIER than a German city's arrival
    clock time (e.g. Preševo boards 08:00, Minhen's next-day arrival also
    reads 08:15) gave a false same-day "15 min" duration for a ~1500km trip
    before this was next_day-aware — caught by spot-checking real output,
    not by the corridor's own two hand-picked examples where the raw
    subtraction happened to already be negative and masked the bug."""
    dh, dm = map(int, dep.split(':'))
    ah, am = map(int, arr.split(':'))
    duration = (ah * 60 + am) - (dh * 60 + dm)
    if next_day or duration < 0:
        duration += 24 * 60
    return duration


def parse_corridor(article_html: str) -> dict | None:
    """Parse one <article> corridor block into boarding/arrival stop lists."""
    m = H2_RE.search(article_html)
    if not m:
        return None
    dest_name = m.group(1).strip()

    lists: dict[str, list[tuple[str, str]]] = {
        'outbound_board': [], 'outbound_arrive': [],
        'inbound_board': [], 'inbound_arrive': [],
    }
    for heading, ul_html in LIST_HEADING_RE.findall(article_html):
        heading = heading.strip()
        kind = HEADING_KIND.get(heading)
        if not kind:
            continue
        direction, role = kind
        lists[f'{direction}_{role}'] = _parse_stop_list(ul_html)

    return {
        'corridor': dest_name,
        'outbound_board': lists['outbound_board'],      # Serbia stops, dep times
        'outbound_arrive': lists['outbound_arrive'],     # Germany stops, arr times
        'inbound_board': lists['inbound_board'],         # Germany stops, dep times
        'inbound_arrive': lists['inbound_arrive'],       # Serbia stops, arr times
    }


def corridor_to_trips(corridor: dict, scraped_at: str) -> list[dict]:
    """Build one trip per (Serbian stop, German stop) pair, both directions."""
    trips = []

    # Outbound: every Serbian boarding stop -> every German arrival stop
    # that comes after it on the same run (all of them — it's one bus).
    for dep_time, sr_city in corridor['outbound_board']:
        for arr_time, de_city in corridor['outbound_arrive']:
            trips.append({
                'from_city': sr_city.strip(),
                'to_city': de_city.strip(),
                'departure': dep_time,
                'arrival': arr_time,
                'duration': _duration_min(dep_time, arr_time, next_day=True),
                'operator': OPERATOR_NAME,
                'type': 'bus',
                'corridor': corridor['corridor'],
                'scraped_at': scraped_at,
            })

    # Inbound: every German boarding stop -> every Serbian arrival stop.
    for dep_time, de_city in corridor['inbound_board']:
        for arr_time, sr_city in corridor['inbound_arrive']:
            trips.append({
                'from_city': de_city.strip(),
                'to_city': sr_city.strip(),
                'departure': dep_time,
                'arrival': arr_time,
                'duration': _duration_min(dep_time, arr_time, next_day=True),
                'operator': OPERATOR_NAME,
                'type': 'bus',
                'corridor': corridor['corridor'],
                'scraped_at': scraped_at,
            })

    return trips


def fetch_schedule_page(session: requests.Session) -> str:
    resp = session.get(SCHEDULE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    # Server doesn't send a charset in Content-Type, so requests falls back
    # to latin-1 and mangles every ć/č/ž/š/đ and the en-dash in "Srbija – X"
    # (breaks H2_RE). Page is UTF-8 (see <meta charset> in <head>) — force it.
    resp.encoding = 'utf-8'
    return resp.text


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    log.info(f'Fetching {SCHEDULE_URL}')
    html = fetch_schedule_page(session)
    scraped_at = datetime.now(timezone.utc).isoformat(timespec='seconds')

    articles = ARTICLE_RE.findall(html)
    log.info(f'Found {len(articles)} corridor <article> blocks')

    corridors = []
    for article_html in articles:
        corridor = parse_corridor(article_html)
        if corridor and (corridor['outbound_board'] or corridor['inbound_board']):
            corridors.append(corridor)

    log.info(f'Parsed {len(corridors)} corridors with stop data')

    all_trips: list[dict] = []
    routes: list[dict] = []

    for corridor in corridors:
        trips = corridor_to_trips(corridor, scraped_at)
        all_trips.extend(trips)

        sr_stops = [c for _, c in corridor['outbound_board']]
        de_stops = [c for _, c in corridor['outbound_arrive']]
        log.info(
            f"  {corridor['corridor']}: "
            f"{len(sr_stops)} RS stops x {len(de_stops)} DE stops "
            f'= {len(trips)} trip rows (both directions)'
        )

        # One nested "route" per corridor for readability / manual review.
        routes.append({
            'corridor': corridor['corridor'],
            'rs_stops': corridor['outbound_board'],     # [(time, city), ...]
            'de_stops_outbound': corridor['outbound_arrive'],
            'de_stops_inbound': corridor['inbound_board'],
            'rs_stops_inbound': corridor['inbound_arrive'],
            'trips': trips,
            'scraped_at': scraped_at,
        })

    # Flat trips for build_db.py — same shape as other scrapers' output,
    # plus from_city/to_city already city-pair form (no price published
    # on this page, so price_rsd is left at 0 — real price only appears
    # in the booking/checkout flow, which is out of scope here).
    flat_trips = []
    for trip in all_trips:
        flat_trips.append({
            'from_city': trip['from_city'],
            'to_city': trip['to_city'],
            'departure_time': trip['departure'],
            'arrival_time': trip['arrival'],
            'duration_min': trip['duration'],
            'price_rsd': 0,
            'operator': trip['operator'],
            'type': trip['type'],
            'scraped_at': trip['scraped_at'],
        })

    routes_path = OUT_DIR / 'routes.json'
    with open(routes_path, 'w', encoding='utf-8') as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    flat_path = OUT_DIR / 'trips.json'
    with open(flat_path, 'w', encoding='utf-8') as f:
        json.dump(flat_trips, f, ensure_ascii=False, indent=2)

    operators = {OPERATOR_NAME: 'bus'}
    ops_path = OUT_DIR / 'operators.json'
    with open(ops_path, 'w', encoding='utf-8') as f:
        json.dump(operators, f, ensure_ascii=False, indent=2)

    log.info('\n=== Done ===')
    log.info(f'Corridors     : {len(corridors)}')
    log.info(f'Total trips   : {len(flat_trips)}')
    log.info(f'Saved         : {routes_path}')
    log.info(f'Saved         : {flat_path}')
    log.info(f'Saved         : {ops_path}')

    time.sleep(0.5)  # courtesy pause even though this is a single-request run


if __name__ == '__main__':
    main()

"""
Enrich and verify city_stops coordinates from OpenStreetMap.

Three modes:
  audit   — analyze coordinate quality, flag suspicious stops
  enrich  — fill missing coords via Overpass API + Nominatim fallback
  fix     — re-fetch coords for stops flagged as suspicious by audit

Usage:
    python -u data/pipelines/enrich_stops_coords.py audit
    python -u data/pipelines/enrich_stops_coords.py enrich [--limit 200]
    python -u data/pipelines/enrich_stops_coords.py fix [--limit 50]
"""
import argparse
import json
import math
import re
import sys
import time
from pathlib import Path

import duckdb
import requests

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'dbs' / 'transit.duckdb'
PROGRESS_FILE = BASE_DIR / 'raw' / 'enrich_stops_progress.json'
SUSPICIOUS_FILE = BASE_DIR / 'raw' / 'suspicious_stops.json'

# Belgrade bounding box (south, west, north, east)
BELGRADE_BBOX = (44.6, 20.2, 44.95, 20.7)
BBOX_STR = ','.join(str(x) for x in BELGRADE_BBOX)

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'

MAX_RETRIES = 3
REQUEST_DELAY = 1.5  # seconds between API requests
MAX_NEIGHBOR_DISTANCE_KM = 3.0  # flag if consecutive stops are farther apart

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
DIM = '\033[2m'
BOLD = '\033[1m'
RESET = '\033[0m'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km between two GPS points."""
    R = 6371.0
    rlat1, rlon1, rlat2, rlon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def in_belgrade_bbox(lat: float, lon: float) -> bool:
    s, w, n, e = BELGRADE_BBOX
    return s <= lat <= n and w <= lon <= e


def clean_name(name: str) -> str:
    """Strip quotes, parenthesized suffixes, trailing numbers for better OSM matching."""
    name = name.replace('\u201c', '').replace('\u201d', '').replace('"', '')
    name = re.sub(r'\s*/[^/]+/\s*', ' ', name)
    name = re.sub(r'\s*\([^)]+\)\s*', ' ', name)
    name = re.sub(r'\s+\d+$', '', name)
    return name.strip()


def progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / total) if total else 0
    bar = '\u2588' * filled + '\u2591' * (width - filled)
    pct = current * 100 // total if total else 0
    return f'{bar} {pct}%'


# ---------------------------------------------------------------------------
# Progress persistence
# ---------------------------------------------------------------------------

def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {'found': [], 'not_found': []}


def save_progress(progress: dict) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f)


def load_suspicious() -> list[dict]:
    if SUSPICIOUS_FILE.exists():
        with open(SUSPICIOUS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return []


def save_suspicious(entries: list[dict]) -> None:
    SUSPICIOUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUSPICIOUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# API queries
# ---------------------------------------------------------------------------

def _api_request_with_retry(make_request, desc: str = '') -> requests.Response | None:
    """Generic retry wrapper for API calls."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = make_request()
            if resp.status_code == 429:
                wait = REQUEST_DELAY * (2 ** (attempt + 1))
                sys.stdout.write(f'\r{DIM}    \u23f3 rate limited, waiting {wait:.0f}s...{RESET}\033[K')
                sys.stdout.flush()
                time.sleep(wait)
                continue
            if resp.status_code == 504:
                wait = REQUEST_DELAY * (attempt + 2)
                sys.stdout.write(f'\r{DIM}    \u23f3 timeout, retrying in {wait:.0f}s...{RESET}\033[K')
                sys.stdout.flush()
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp
        except requests.exceptions.ConnectionError:
            time.sleep(REQUEST_DELAY * (attempt + 2))
        except requests.exceptions.RequestException:
            break
    return None


def query_overpass(name: str) -> tuple[float, float] | None:
    """Query Overpass API for a bus stop by name in Belgrade area."""
    cleaned = clean_name(name)
    variants = [name]
    if cleaned != name:
        variants.append(cleaned)

    for variant in variants:
        safe = variant.replace('\\', '\\\\').replace('"', '\\"')
        query = (
            f'[out:json][timeout:10];'
            f'node["highway"="bus_stop"]["name"~"{safe}",i]({BBOX_STR});'
            f'out 1;'
        )

        def make_req():
            return requests.post(OVERPASS_URL, data={'data': query}, timeout=30)

        resp = _api_request_with_retry(make_req, f'overpass:{variant}')
        if resp is not None:
            elements = resp.json().get('elements', [])
            if elements:
                el = elements[0]
                return el['lat'], el['lon']

    return None


def query_overpass_public_transport(name: str) -> tuple[float, float] | None:
    """Broader Overpass query: public_transport=platform OR public_transport=stop_position."""
    cleaned = clean_name(name)
    safe = cleaned.replace('\\', '\\\\').replace('"', '\\"')
    query = (
        f'[out:json][timeout:10];'
        f'('
        f'node["public_transport"="platform"]["name"~"{safe}",i]({BBOX_STR});'
        f'node["public_transport"="stop_position"]["name"~"{safe}",i]({BBOX_STR});'
        f');'
        f'out 1;'
    )

    def make_req():
        return requests.post(OVERPASS_URL, data={'data': query}, timeout=30)

    resp = _api_request_with_retry(make_req, f'overpass_pt:{cleaned}')
    if resp is not None:
        elements = resp.json().get('elements', [])
        if elements:
            el = elements[0]
            return el['lat'], el['lon']
    return None


def query_nominatim(name: str) -> tuple[float, float] | None:
    """Geocode a bus stop name via Nominatim, bounded to Belgrade."""
    cleaned = clean_name(name)
    params = {
        'q': f'{cleaned}, Belgrade, Serbia',
        'format': 'json',
        'limit': 1,
        'viewbox': '20.2,44.95,20.7,44.6',
        'bounded': 1,
    }
    headers = {'User-Agent': 'TransitSerbia/1.0 (transit aggregator)'}

    def make_req():
        return requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=15)

    resp = _api_request_with_retry(make_req, f'nominatim:{cleaned}')
    if resp is not None:
        results = resp.json()
        if results:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
            if in_belgrade_bbox(lat, lon):
                return lat, lon
    return None


def fetch_coords(name: str) -> tuple[float, float] | None:
    """Try all sources in order: Overpass bus_stop → Overpass public_transport → Nominatim."""
    coords = query_overpass(name)
    if coords and in_belgrade_bbox(*coords):
        return coords

    time.sleep(REQUEST_DELAY)
    coords = query_overpass_public_transport(name)
    if coords and in_belgrade_bbox(*coords):
        return coords

    time.sleep(REQUEST_DELAY)
    coords = query_nominatim(name)
    if coords:
        return coords

    return None


# ---------------------------------------------------------------------------
# AUDIT: verify coordinate quality
# ---------------------------------------------------------------------------

def audit(conn: duckdb.DuckDBPyConnection) -> list[dict]:
    """Analyze stops and flag suspicious coordinates. Returns list of flagged stops."""
    total = conn.execute("SELECT count(*) FROM city_stops").fetchone()[0]
    with_coords = conn.execute("SELECT count(*) FROM city_stops WHERE lat IS NOT NULL").fetchone()[0]
    without_coords = total - with_coords

    print()
    print(f"  {BOLD}AUDIT: STOP COORDINATES{RESET}")
    print(f"  {'=' * 55}")
    print(f"  Total stops:      {CYAN}{total}{RESET}")
    print(f"  With coordinates: {GREEN}{with_coords}{RESET}")
    print(f"  Without coords:   {YELLOW}{without_coords}{RESET}")
    print(f"  {'=' * 55}")
    print()

    suspicious: list[dict] = []
    reasons_count: dict[str, int] = {
        'outside_bbox': 0,
        'neighbor_too_far': 0,
        'missing_coords': 0,
    }

    # 1. Flag stops outside Belgrade bounding box
    out_of_bounds = conn.execute("""
        SELECT id, name, lat, lon FROM city_stops
        WHERE lat IS NOT NULL
          AND (lat < ? OR lat > ? OR lon < ? OR lon > ?)
    """, [BELGRADE_BBOX[0], BELGRADE_BBOX[2], BELGRADE_BBOX[1], BELGRADE_BBOX[3]]).fetchall()

    for stop_id, name, lat, lon in out_of_bounds:
        suspicious.append({
            'stop_id': stop_id,
            'name': name,
            'lat': lat,
            'lon': lon,
            'reason': 'outside_bbox',
            'detail': f'({lat:.4f}, {lon:.4f}) outside Belgrade bbox',
        })
        reasons_count['outside_bbox'] += 1

    print(f"  {BOLD}1. Out of Belgrade bbox:{RESET} {RED if out_of_bounds else GREEN}"
          f"{len(out_of_bounds)}{RESET} stops")
    for entry in suspicious[:10]:
        print(f"     {RED}\u2718{RESET} {entry['name']} — {DIM}{entry['detail']}{RESET}")
    if len(out_of_bounds) > 10:
        print(f"     {DIM}... and {len(out_of_bounds) - 10} more{RESET}")
    print()

    # 2. Check distances between consecutive stops on each line
    lines = conn.execute("SELECT id, number, name FROM city_lines ORDER BY number").fetchall()
    jump_count = 0
    flagged_ids = {e['stop_id'] for e in suspicious}

    print(f"  {BOLD}2. Checking neighbor distances on {len(lines)} lines:{RESET}")
    for line_id, line_num, line_name in lines:
        stops = conn.execute("""
            SELECT cs.id, cs.name, cs.lat, cs.lon
            FROM city_line_stops cls
            JOIN city_stops cs ON cs.id = cls.stop_id
            WHERE cls.line_id = ?
            ORDER BY cls.stop_order
        """, [line_id]).fetchall()

        line_jumps = []
        for i in range(len(stops) - 1):
            s1_id, s1_name, s1_lat, s1_lon = stops[i]
            s2_id, s2_name, s2_lat, s2_lon = stops[i + 1]

            if s1_lat is None or s2_lat is None:
                continue

            dist = haversine(s1_lat, s1_lon, s2_lat, s2_lon)
            if dist > MAX_NEIGHBOR_DISTANCE_KM:
                line_jumps.append((s1_id, s1_name, s2_id, s2_name, dist))

                for sid, sname, slat, slon in [(s1_id, s1_name, s1_lat, s1_lon),
                                                (s2_id, s2_name, s2_lat, s2_lon)]:
                    if sid not in flagged_ids:
                        suspicious.append({
                            'stop_id': sid,
                            'name': sname,
                            'lat': slat,
                            'lon': slon,
                            'reason': 'neighbor_too_far',
                            'detail': f'line {line_num}: {dist:.1f}km jump',
                            'line_id': line_id,
                            'line_number': line_num,
                        })
                        flagged_ids.add(sid)
                        reasons_count['neighbor_too_far'] += 1

        if line_jumps:
            jump_count += len(line_jumps)
            print(f"     {RED}\u2718{RESET} Line {BOLD}{line_num}{RESET} ({line_name}): "
                  f"{RED}{len(line_jumps)}{RESET} jumps")
            for s1_id, s1_name, s2_id, s2_name, dist in line_jumps[:3]:
                print(f"       {DIM}{s1_name} → {s2_name}: {dist:.1f}km{RESET}")
            if len(line_jumps) > 3:
                print(f"       {DIM}... and {len(line_jumps) - 3} more{RESET}")

    if jump_count == 0:
        print(f"     {GREEN}\u2714 No suspicious jumps found{RESET}")
    print()

    # 3. Stops without coordinates
    missing = conn.execute("SELECT id, name FROM city_stops WHERE lat IS NULL").fetchall()
    reasons_count['missing_coords'] = len(missing)

    print(f"  {BOLD}3. Missing coordinates:{RESET} {YELLOW}{len(missing)}{RESET} stops")
    print()

    # Summary
    unique_suspicious = len({e['stop_id'] for e in suspicious})
    print(f"  {'=' * 55}")
    print(f"  {BOLD}SUMMARY{RESET}")
    print(f"  Outside bbox:      {RED}{reasons_count['outside_bbox']}{RESET}")
    print(f"  Neighbor jumps:    {RED}{reasons_count['neighbor_too_far']}{RESET}")
    print(f"  Missing coords:    {YELLOW}{reasons_count['missing_coords']}{RESET}")
    print(f"  {BOLD}Unique flagged:{RESET}     {BOLD}{unique_suspicious}{RESET}")
    print(f"  {'=' * 55}")
    print()

    save_suspicious(suspicious)
    print(f"  {DIM}Saved to {SUSPICIOUS_FILE}{RESET}")
    print()

    return suspicious


# ---------------------------------------------------------------------------
# ENRICH: fill missing coordinates
# ---------------------------------------------------------------------------

def enrich(conn: duckdb.DuckDBPyConnection, limit: int = 0) -> None:
    progress = load_progress()
    all_processed = set(progress['found'] + progress['not_found'])
    prev_found = len(progress['found'])

    total_stops = conn.execute("SELECT count(*) FROM city_stops").fetchone()[0]
    with_coords = conn.execute("SELECT count(*) FROM city_stops WHERE lat IS NOT NULL").fetchone()[0]

    rows = conn.execute(
        "SELECT id, name FROM city_stops WHERE lat IS NULL ORDER BY id"
    ).fetchall()

    if not rows:
        print(f"  {GREEN}All stops already have coordinates!{RESET}")
        return

    todo = [(sid, name) for sid, name in rows if sid not in all_processed]
    if limit:
        todo = todo[:limit]

    total_todo = len(todo)
    if not total_todo:
        print(f"  {GREEN}All remaining stops already processed (check progress file to reset).{RESET}")
        return

    print()
    print(f"  {BOLD}ENRICH STOPS COORDS{RESET}")
    print(f"  {'=' * 55}")
    print(f"  Total stops:       {CYAN}{total_stops}{RESET}")
    print(f"  Already with GPS:  {GREEN}{with_coords}{RESET}")
    print(f"  Without coords:    {YELLOW}{len(rows)}{RESET}")
    print(f"  Previously done:   {DIM}{len(all_processed)}{RESET}")
    print(f"  To process now:    {BOLD}{total_todo}{RESET}")
    print(f"  Source:            Overpass → public_transport → Nominatim")
    print(f"  {'=' * 55}")
    print()

    found = 0
    not_found = 0
    start_time = time.time()

    for i, (stop_id, name) in enumerate(todo):
        n = i + 1
        coords = fetch_coords(name)

        sys.stdout.write('\r\033[K')

        if coords:
            lat, lon = coords
            conn.execute(
                "UPDATE city_stops SET lat = ?, lon = ? WHERE id = ?",
                [lat, lon, stop_id]
            )
            progress['found'].append(stop_id)
            found += 1
            icon = f'{GREEN}\u2714{RESET}'
            coord_str = f'{DIM}{lat:.4f}, {lon:.4f}{RESET}'
            print(f"  {DIM}{n:>4}/{total_todo}{RESET}  {icon}  {BOLD}{name}{RESET}  {coord_str}")
        else:
            progress['not_found'].append(stop_id)
            not_found += 1
            icon = f'{RED}\u2718{RESET}'
            print(f"  {DIM}{n:>4}/{total_todo}{RESET}  {icon}  {DIM}{name}{RESET}")

        if n % 25 == 0:
            _print_stats(n, total_todo, start_time, with_coords, found, not_found, total_stops)

        if n % 10 == 0:
            save_progress(progress)

        time.sleep(REQUEST_DELAY)

    save_progress(progress)

    _print_final(start_time, with_coords, found, not_found, total_stops)


# ---------------------------------------------------------------------------
# FIX: re-fetch coordinates for suspicious stops
# ---------------------------------------------------------------------------

def fix(conn: duckdb.DuckDBPyConnection, limit: int = 0) -> None:
    suspicious = load_suspicious()
    if not suspicious:
        print(f"  {YELLOW}No suspicious stops found. Run 'audit' first.{RESET}")
        return

    # Only fix stops that have coordinates (outside_bbox, neighbor_too_far)
    # Missing coords are handled by 'enrich'
    to_fix = [s for s in suspicious if s.get('lat') is not None]
    if limit:
        to_fix = to_fix[:limit]

    total_fix = len(to_fix)
    if not total_fix:
        print(f"  {GREEN}No suspicious stops with coords to fix (missing coords → use 'enrich').{RESET}")
        return

    total_stops = conn.execute("SELECT count(*) FROM city_stops").fetchone()[0]
    with_coords = conn.execute("SELECT count(*) FROM city_stops WHERE lat IS NOT NULL").fetchone()[0]

    print()
    print(f"  {BOLD}FIX SUSPICIOUS COORDS{RESET}")
    print(f"  {'=' * 55}")
    print(f"  Suspicious stops:  {RED}{len(suspicious)}{RESET}")
    print(f"  To re-fetch now:   {BOLD}{total_fix}{RESET}")
    print(f"  Source:            Overpass → public_transport → Nominatim")
    print(f"  {'=' * 55}")
    print()

    fixed = 0
    skipped = 0
    start_time = time.time()

    for i, entry in enumerate(to_fix):
        n = i + 1
        stop_id = entry['stop_id']
        name = entry['name']
        old_lat, old_lon = entry['lat'], entry['lon']

        coords = fetch_coords(name)
        sys.stdout.write('\r\033[K')

        if coords:
            new_lat, new_lon = coords
            old_dist = haversine(old_lat, old_lon, new_lat, new_lon) if old_lat else 0

            if old_dist > 0.05:  # only update if moved at least 50m
                conn.execute(
                    "UPDATE city_stops SET lat = ?, lon = ? WHERE id = ?",
                    [new_lat, new_lon, stop_id]
                )
                fixed += 1
                icon = f'{GREEN}\u2714{RESET}'
                delta = f'{DIM}moved {old_dist:.2f}km{RESET}'
                print(f"  {DIM}{n:>4}/{total_fix}{RESET}  {icon}  {BOLD}{name}{RESET}  "
                      f"{DIM}{new_lat:.4f}, {new_lon:.4f}{RESET}  {delta}")
            else:
                skipped += 1
                icon = f'{YELLOW}\u2500{RESET}'
                print(f"  {DIM}{n:>4}/{total_fix}{RESET}  {icon}  {DIM}{name} (same location){RESET}")
        else:
            skipped += 1
            icon = f'{RED}\u2718{RESET}'
            print(f"  {DIM}{n:>4}/{total_fix}{RESET}  {icon}  {DIM}{name} (not found in OSM){RESET}")

        time.sleep(REQUEST_DELAY)

    elapsed = time.time() - start_time
    print()
    print(f"  {'=' * 55}")
    print(f"  {BOLD}DONE{RESET}")
    print(f"  Fixed:   {GREEN}{fixed}{RESET}")
    print(f"  Skipped: {DIM}{skipped}{RESET}")
    print(f"  Time:    {int(elapsed // 60)}m {int(elapsed % 60)}s")
    print(f"  {'=' * 55}")
    print()

    if fixed > 0:
        print(f"  {CYAN}Run 'audit' again to verify fixes.{RESET}")
        print()


# ---------------------------------------------------------------------------
# Stats output
# ---------------------------------------------------------------------------

def _print_stats(n: int, total_todo: int, start_time: float,
                 with_coords: int, found: int, not_found: int, total_stops: int) -> None:
    elapsed = time.time() - start_time
    rate = n / elapsed if elapsed > 0 else 0
    eta_sec = (total_todo - n) / rate if rate > 0 else 0
    eta_min = int(eta_sec // 60)
    total_gps = with_coords + found
    hit = found * 100 // n if n else 0
    bar = progress_bar(n, total_todo)
    print(f"  {CYAN}{'─' * 55}{RESET}")
    print(f"  {bar}  {BOLD}{total_gps}/{total_stops}{RESET} with GPS"
          f"  {GREEN}+{found}{RESET} {RED}-{not_found}{RESET}"
          f"  hit {hit}%  ETA {eta_min}m")
    print(f"  {CYAN}{'─' * 55}{RESET}")


def _print_final(start_time: float, with_coords: int, found: int,
                 not_found: int, total_stops: int) -> None:
    elapsed = time.time() - start_time
    total_gps = with_coords + found
    hit = found * 100 // (found + not_found) if (found + not_found) else 0
    print()
    print(f"  {'=' * 55}")
    print(f"  {BOLD}DONE{RESET}")
    print(f"  Found:     {GREEN}{found}{RESET}")
    print(f"  Not found: {RED}{not_found}{RESET}")
    print(f"  Hit rate:  {BOLD}{hit}%{RESET}")
    print(f"  Total GPS: {CYAN}{total_gps}/{total_stops}{RESET} ({total_gps * 100 // total_stops}%)")
    print(f"  Time:      {int(elapsed // 60)}m {int(elapsed % 60)}s")
    print(f"  {'=' * 55}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Enrich and verify city stop coordinates from OpenStreetMap'
    )
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('audit', help='Analyze coordinate quality, flag suspicious stops')

    p_enrich = sub.add_parser('enrich', help='Fill missing coords via Overpass + Nominatim')
    p_enrich.add_argument('--limit', type=int, default=0, help='Max stops to process (0 = all)')

    p_fix = sub.add_parser('fix', help='Re-fetch coords for suspicious stops')
    p_fix.add_argument('--limit', type=int, default=0, help='Max stops to fix (0 = all)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not DB_PATH.exists():
        print(f"{RED}Database not found: {DB_PATH}{RESET}")
        print(f"Run build_db.py first.")
        sys.exit(1)

    read_only = args.command == 'audit'
    conn = duckdb.connect(str(DB_PATH), read_only=read_only)

    try:
        if args.command == 'audit':
            audit(conn)
        elif args.command == 'enrich':
            enrich(conn, args.limit)
        elif args.command == 'fix':
            fix(conn, args.limit)
    finally:
        conn.close()


if __name__ == '__main__':
    main()

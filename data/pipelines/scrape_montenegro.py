"""
Scraper for Montenegro city bus lines — OpenStreetMap Overpass API.

Same shape as scrape_kragujevac.py (route=bus relations → lines with stops),
generalised to several cities. Launch cities (OSM coverage verified 2026-06):

  - podgorica   — capital, 7 numbered city lines
  - herceg-novi — coast, 4 numbered lines
  - budva       — coast/tourist, ~5 named "Blue Line" routes (Budva → Sveti
                  Stefan / Petrovac / …). Unnumbered routes get a sequential
                  number so the /linija/linija-N/ URL scheme holds; the OSM
                  name is kept as the human label.

Output: data/raw/<city>/lines.json  (schema identical to the Serbian scrapers:
        [{number, name, type, stops:[{name,lat,lon}]}]).

Montenegro OSM data has no timetables, so line pages render stops + map only
(headway "—"), exactly like the Niš/Kragujevac OSM cities.
"""
import json
import re
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
HEADERS = {'User-Agent': 'TransitSerbia/1.0 (transit aggregator)'}

# city slug → bounding box (S,W,N,E). Verified to carry real route=bus relations.
CITIES: dict[str, str] = {
    'podgorica':   '42.40,19.20,42.48,19.32',
    'herceg-novi': '42.43,18.48,42.47,18.58',
    'budva':       '42.26,18.80,42.31,18.88',
}

# Published city lines per city, curated. OSM tags suburban and intercity
# services as route=bus exactly like urban ones, so an Overpass bbox query also
# returns coaches that leave the city — we were publishing "Herceg Novi -
# Kruševice" (a village 10 km inland, up in the hills) as Herceg Novi city
# transport. Distance from the centre does not separate them: HN line 1 runs
# 11.4 km along the coast to Kamenari and IS urban, while the Kruševice line is
# only 9.7 km out and is not. So the set is curated per city rather than
# guessed. A city absent from this map publishes every line found.
# herceg-novi: confirmed by the site owner — the city runs lines 1 and 2 only.
CITY_LINES_ALLOWED: dict[str, set[str]] = {
    'herceg-novi': {'1', '2'},
}

_NUMBERED_RE = re.compile(r'^\d+[A-Za-z]?$')


def _fetch_routes(bbox: str) -> list[dict]:
    query = f"""
    [out:json][timeout:60];
    relation['type'='route']['route'='bus']({bbox});
    out body;
    """
    return _overpass(query).get('elements', [])


def _overpass(query: str, retries: int = 4) -> dict:
    """POST to Overpass with backoff — it 504s under load (esp. big bboxes)."""
    last = None
    for attempt in range(retries):
        try:
            resp = requests.post(OVERPASS_URL, data={'data': query},
                                 headers=HEADERS, timeout=90)
            if resp.status_code == 200:
                return resp.json()
            last = f'HTTP {resp.status_code}'
        except Exception as e:  # noqa: BLE001 — network flakiness, retry
            last = str(e)
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f'Overpass failed after {retries} tries: {last}')


def _fetch_stop_nodes(routes: list[dict]) -> dict[int, dict]:
    # Montenegro routes tag stops with mixed roles (platform / platform_entry_only
    # / stop / ''), so don't filter on role — take every NODE member and keep the
    # named ones at build time. (Way platforms are ignored; the stop node has the
    # name.)
    node_ids = {m['ref'] for r in routes for m in r.get('members', [])
                if m['type'] == 'node'}
    if not node_ids:
        return {}
    nodes: dict[int, dict] = {}
    ids = list(node_ids)
    for i in range(0, len(ids), 300):
        id_str = ','.join(str(x) for x in ids[i:i + 300])
        time.sleep(1.5)
        for e in _overpass(
                f'[out:json][timeout:50];node(id:{id_str});out;').get(
                'elements', []):
            nodes[e['id']] = e
    return nodes


def _clean_name(name: str) -> str:
    short = name.split(':', 1)[-1].strip() if ':' in name else name
    short = re.sub(r'\s*(=>|->|→)\s*', ' — ', short)
    return short.strip()


def _build_lines(routes: list[dict], nodes: dict[int, dict]) -> list[dict]:
    """Merge route directions into unique lines with stops. Numbered lines key
    on their ref; unnumbered (named) routes each become their own line and get
    a synthetic sequential number after the numbered ones."""
    by_key: dict[str, dict] = {}
    named: list[dict] = []

    for r in routes:
        tags = r.get('tags', {})
        ref = (tags.get('ref') or '').strip()
        name = tags.get('name', '')
        if 'Flixbus' in name:
            continue

        stops = []
        seen = set()
        for m in r.get('members', []):
            if m['type'] != 'node':
                continue
            node = nodes.get(m['ref'])
            if not node:
                continue
            sname = node.get('tags', {}).get('name', '')
            if sname and sname not in seen:
                seen.add(sname)
                stops.append({'name': sname,
                              'lat': round(node['lat'], 6),
                              'lon': round(node['lon'], 6)})
        if len(stops) < 2:
            continue  # a route with <2 named stops is too thin to publish

        if _NUMBERED_RE.match(ref):
            if ref not in by_key:
                by_key[ref] = {'number': ref, 'name': _clean_name(name),
                               'type': 'bus', 'stops': stops}
            else:
                existing = {s['name'] for s in by_key[ref]['stops']}
                for s in stops:
                    if s['name'] not in existing:
                        by_key[ref]['stops'].append(s)
                        existing.add(s['name'])
        else:
            named.append({'name': _clean_name(name) or ref,
                          'type': 'bus', 'stops': stops})

    def num_key(x):
        m = re.match(r'(\d+)', x['number'])
        return (int(m.group(1)) if m else 999, x['number'])

    numbered = sorted(by_key.values(), key=num_key)
    # Synthetic numbers for named routes continue after the numbered ones.
    next_n = (max((int(re.match(r'(\d+)', x['number']).group(1))
                   for x in numbered if re.match(r'(\d+)', x['number'])),
                  default=0) + 1)
    # Dedup named routes by name (overlapping directions).
    seen_names = set()
    for nr in named:
        if nr['name'] in seen_names:
            continue
        seen_names.add(nr['name'])
        nr['number'] = str(next_n)
        next_n += 1
        numbered.append(nr)

    # Some OSM route relations carry a ref but no name tag (Herceg Novi line 1).
    # An empty name renders an empty <title>/<h1> on the line page, so fall back
    # to the terminus pair — the same "A — B" shape the named routes already use.
    # Done after the merge so it reflects the full, combined stop list.
    for line in numbered:
        if not line['name'] and len(line['stops']) >= 2:
            line['name'] = f"{line['stops'][0]['name']} — {line['stops'][-1]['name']}"

    return numbered


def scrape_city(city: str, bbox: str) -> list[dict]:
    routes = _fetch_routes(bbox)
    nodes = _fetch_stop_nodes(routes)
    lines = _build_lines(routes, nodes)
    allowed = CITY_LINES_ALLOWED.get(city)
    if allowed:
        dropped = [l['number'] for l in lines if l['number'] not in allowed]
        lines = [l for l in lines if l['number'] in allowed]
        if dropped:
            print(f'  {city}: dropped non-urban lines {sorted(dropped)}')
    out_dir = BASE_DIR / 'raw' / city
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'lines.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(lines, f, ensure_ascii=False, indent=2)
    total_stops = sum(len(l['stops']) for l in lines)
    print(f'  {city}: {len(lines)} lines, {total_stops} stops → {out_path}')
    return lines


def main() -> None:
    for city, bbox in CITIES.items():
        try:
            scrape_city(city, bbox)
        except Exception as e:  # never break the nightly pipeline on one city
            print(f'  {city}: FAILED ({e}) — skipping')
        time.sleep(3)


if __name__ == '__main__':
    main()

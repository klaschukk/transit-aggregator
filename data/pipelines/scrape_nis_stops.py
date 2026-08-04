"""
Enrich Niš city bus lines with stops from OpenStreetMap Overpass API.
Reads data/raw/nis/lines.json (line names), fetches stops, writes back.
"""
import json, sys, time, re
from pathlib import Path
import requests

BASE_DIR = Path(__file__).parent.parent
OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
HEADERS = {'User-Agent': 'TransitSerbia/1.0 (prevozni.com)'}

# City -> generous bounding box. Novi Sad was added because its source (JGSP
# /mreza) ships stop NAMES only: 59 lines carried just 66 stops, 1.1 per line,
# against 3.1 for Niš and 13.5 for Kragujevac. OSM route relations are the
# same source that gave those cities their stops.
CITY_BBOX = {
    'nis': '43.27,21.84,43.38,21.97',
    'novi-sad': '45.18,19.70,45.35,19.95',
}
DEFAULT_CITY = 'nis'


def fetch_routes(bbox):
    q = f'''[out:json][timeout:60];
relation['type'='route']['route'='bus']({bbox});
out body;'''
    r = requests.post(OVERPASS_URL, data={'data': q}, headers=HEADERS, timeout=90)
    r.raise_for_status()
    return r.json().get('elements', [])


def fetch_nodes(routes):
    ids = set()
    for r in routes:
        for m in r.get('members', []):
            if m['type'] == 'node' and m.get('role', '') in ('stop', 'platform', 'stop_entry_only', 'stop_exit_only'):
                ids.add(m['ref'])
    nodes = {}
    id_list = list(ids)
    for i in range(0, len(id_list), 300):
        batch = id_list[i:i+300]
        q = f'[out:json][timeout:30];node(id:{",".join(str(x) for x in batch)});out;'
        # Overpass answers 429/504 under load. Swallowing that per batch left
        # the run with zero stops while still looking successful, which is how
        # Niš went from 345 stops to 0 on 2026-08-03. Retry, then fail loudly.
        for attempt in range(4):
            time.sleep(1 if attempt == 0 else 5.0 * attempt)
            try:
                r = requests.post(OVERPASS_URL, data={'data': q},
                                  headers=HEADERS, timeout=60)
                if r.status_code == 200:
                    for e in r.json().get('elements', []):
                        nodes[e['id']] = e
                    break
                print(f'  Overpass {r.status_code} on node batch '
                      f'{i // 300 + 1} (attempt {attempt + 1}/4)', file=sys.stderr)
            except Exception as e:  # noqa: BLE001 — network flake, retry
                print(f'  batch error: {e} (attempt {attempt + 1}/4)',
                      file=sys.stderr)
        else:
            raise RuntimeError(
                f'Overpass kept refusing node batch {i // 300 + 1} — aborting '
                f'rather than writing the city with missing stops')
    return nodes


def build_lines(routes, nodes):
    by_ref = {}
    for r in routes:
        tags = r.get('tags', {})
        ref = tags.get('ref', '')
        if not ref:
            continue
        stops = []
        seen = set()
        for m in r.get('members', []):
            if m['type'] == 'node' and m.get('role', '') in ('stop', 'platform', 'stop_entry_only', 'stop_exit_only'):
                nd = nodes.get(m['ref'])
                if nd:
                    name = nd.get('tags', {}).get('name', '')
                    if name and name not in seen:
                        seen.add(name)
                        stops.append({'name': name, 'lat': nd['lat'], 'lon': nd['lon']})
        if ref not in by_ref or len(stops) > len(by_ref[ref].get('stops', [])):
            by_ref[ref] = {'number': ref, 'name': tags.get('name', ref), 'type': 'bus', 'stops': stops}
    return list(by_ref.values())


def main():
    city = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CITY
    if city not in CITY_BBOX:
        print(f'unknown city: {city} (known: {list(CITY_BBOX)})', file=sys.stderr)
        sys.exit(2)
    lines_path = BASE_DIR / 'raw' / city / 'lines.json'
    with open(lines_path) as f:
        existing = {l['number']: l for l in json.load(f)}

    print(f'Fetching {city} routes from Overpass...')
    routes = fetch_routes(CITY_BBOX[city])
    print(f'  {len(routes)} route relations found')
    nodes = fetch_nodes(routes)
    print(f'  {len(nodes)} stop nodes fetched')
    osm_lines = build_lines(routes, nodes)
    print(f'  {len(osm_lines)} unique lines')

    # Merge: prefer OSM stops, keep existing line names
    merged = []
    for line in osm_lines:
        ref = line['number']
        base = existing.get(ref, line)
        # Keep the stops already on disk when Overpass returns none for a
        # line: an empty OSM answer is far more often a rate-limited or
        # timed-out batch than a line that genuinely lost all its stops.
        stops = line['stops'] or (base.get('stops') or [])
        merged.append({'number': ref, 'name': base.get('name', line['name']),
                       'type': 'bus', 'stops': stops})
        print(f"  Line {ref}: {len(stops)} stops")

    # Add lines from existing that Overpass didn't find
    osm_refs = {l['number'] for l in merged}
    for ref, line in existing.items():
        if ref not in osm_refs:
            merged.append(line)

    merged.sort(key=lambda l: (len(l['number']), l['number']))

    # Never replace a good file with an emptier one — the same guard
    # scrape_kragujevac carries.
    new_stops = sum(len(l.get('stops') or []) for l in merged)
    old_stops = sum(len(l.get('stops') or []) for l in existing.values())
    if not new_stops:
        print(f'  No stops resolved — keeping existing {lines_path.name}',
              file=sys.stderr)
        sys.exit(1)
    if old_stops and new_stops < old_stops * 0.5:
        print(f'  Only {new_stops} stops vs {old_stops} on disk — refusing '
              f'to overwrite', file=sys.stderr)
        sys.exit(1)

    with open(lines_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f'Written {len(merged)} lines, {new_stops} stops to {lines_path}')


if __name__ == '__main__':
    main()

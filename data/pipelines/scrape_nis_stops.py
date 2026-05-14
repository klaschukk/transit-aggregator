"""
Enrich Niš city bus lines with stops from OpenStreetMap Overpass API.
Reads data/raw/nis/lines.json (line names), fetches stops, writes back.
"""
import json, time, re
from pathlib import Path
import requests

BASE_DIR = Path(__file__).parent.parent
NIS_DIR = BASE_DIR / 'raw' / 'nis'
OVERPASS_URL = 'https://overpass-api.de/api/interpreter'
HEADERS = {'User-Agent': 'TransitSerbia/1.0 (prevozni.com)'}
# Niš bounding box (generous)
BBOX = '43.27,21.84,43.38,21.97'


def fetch_routes():
    q = f'''[out:json][timeout:60];
relation['type'='route']['route'='bus']({BBOX});
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
    for i in range(0, len(ids), 300):
        batch = list(ids)[i:i+300]
        q = f'[out:json][timeout:30];node(id:{",".join(str(x) for x in batch)});out;'
        time.sleep(1)
        try:
            r = requests.post(OVERPASS_URL, data={'data': q}, headers=HEADERS, timeout=60)
            for e in r.json().get('elements', []):
                nodes[e['id']] = e
        except Exception as e:
            print(f'  batch error: {e}')
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
    lines_path = NIS_DIR / 'lines.json'
    with open(lines_path) as f:
        existing = {l['number']: l for l in json.load(f)}

    print('Fetching Niš routes from Overpass...')
    routes = fetch_routes()
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
        merged.append({'number': ref, 'name': base.get('name', line['name']), 'type': 'bus', 'stops': line['stops']})
        print(f"  Line {ref}: {len(line['stops'])} stops")

    # Add lines from existing that Overpass didn't find
    osm_refs = {l['number'] for l in merged}
    for ref, line in existing.items():
        if ref not in osm_refs:
            merged.append(line)

    merged.sort(key=lambda l: (len(l['number']), l['number']))
    with open(lines_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f'Written {len(merged)} lines to {lines_path}')


if __name__ == '__main__':
    main()

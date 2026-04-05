"""
Scraper for Kragujevac city bus lines — OpenStreetMap Overpass API.

Fetches bus route relations in the Kragujevac area, extracts line numbers,
names, and stop coordinates.

Output: data/raw/kragujevac/lines.json
"""
import json
import re
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / 'raw' / 'kragujevac'

OVERPASS_URL = 'https://overpass-api.de/api/interpreter'

# Kragujevac bounding box
BBOX = '44.00,20.85,44.05,20.98'

HEADERS = {'User-Agent': 'TransitSerbia/1.0 (transit aggregator)'}


def fetch_routes() -> list[dict]:
    """Fetch bus route relations from Overpass."""
    query = f'''
    [out:json][timeout:30];
    relation['type'='route']['route'='bus']({BBOX});
    out body;
    '''
    resp = requests.post(OVERPASS_URL, data={'data': query},
                         headers=HEADERS, timeout=60)
    resp.raise_for_status()
    elements = resp.json().get('elements', [])

    # Filter: must have ref, skip Flixbus
    routes = []
    for r in elements:
        tags = r.get('tags', {})
        ref = tags.get('ref', '')
        name = tags.get('name', '')
        if not ref or 'Flixbus' in name:
            continue
        routes.append(r)

    return routes


def fetch_stop_nodes(routes: list[dict]) -> dict[int, dict]:
    """Fetch stop/platform nodes referenced by routes."""
    node_ids = set()
    for r in routes:
        for m in r.get('members', []):
            if m['type'] == 'node' and m.get('role', '') in (
                'stop', 'platform', 'stop_entry_only', 'stop_exit_only',
            ):
                node_ids.add(m['ref'])

    if not node_ids:
        return {}

    nodes = {}
    ids = list(node_ids)
    for i in range(0, len(ids), 300):
        batch = ids[i:i+300]
        id_str = ','.join(str(x) for x in batch)
        query = f'[out:json][timeout:30];node(id:{id_str});out;'
        time.sleep(1.5)
        resp = requests.post(OVERPASS_URL, data={'data': query},
                             headers=HEADERS, timeout=60)
        if resp.status_code == 200:
            for e in resp.json().get('elements', []):
                nodes[e['id']] = e

    return nodes


def build_lines(routes: list[dict], nodes: dict[int, dict]) -> list[dict]:
    """Merge route directions into unique lines with stops."""
    lines_by_ref: dict[str, dict] = {}

    for r in routes:
        tags = r.get('tags', {})
        ref = tags.get('ref', '')
        name = tags.get('name', '')

        stops = []
        seen = set()
        for m in r.get('members', []):
            if m['type'] == 'node' and m.get('role', '') in (
                'stop', 'platform', 'stop_entry_only', 'stop_exit_only',
            ):
                node = nodes.get(m['ref'])
                if node:
                    sname = node.get('tags', {}).get('name', '')
                    if sname and sname not in seen:
                        seen.add(sname)
                        stops.append({
                            'name': sname,
                            'lat': round(node['lat'], 6),
                            'lon': round(node['lon'], 6),
                        })

        if ref not in lines_by_ref:
            short = name.split(':')[-1].strip() if ':' in name else name
            short = re.sub(r'\s*=>\s*', ' - ', short)
            lines_by_ref[ref] = {
                'number': ref,
                'name': short,
                'type': 'bus',
                'stops': stops,
            }
        else:
            existing = {s['name'] for s in lines_by_ref[ref]['stops']}
            for s in stops:
                if s['name'] not in existing:
                    lines_by_ref[ref]['stops'].append(s)
                    existing.add(s['name'])

    def sort_key(ref):
        m = re.match(r'(\d+)', ref)
        return (int(m.group(1)) if m else 999, ref)

    return sorted(lines_by_ref.values(), key=lambda x: sort_key(x['number']))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print('Fetching Kragujevac bus routes from Overpass...')
    routes = fetch_routes()
    print(f'  Routes: {len(routes)}')

    print('Fetching stop nodes...')
    nodes = fetch_stop_nodes(routes)
    print(f'  Nodes: {len(nodes)}')

    lines = build_lines(routes, nodes)
    total_stops = sum(len(l['stops']) for l in lines)

    out_path = OUT_DIR / 'lines.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(lines, f, ensure_ascii=False, indent=2)

    print(f'  Lines: {len(lines)}, stops: {total_stops}')
    print(f'  Saved: {out_path}')


if __name__ == '__main__':
    main()

"""
Post-build enrichment: adds GSPNS OSM stops + links to Novi Sad.
Run after build_db.py, before starting transit service.

This is needed because build_db.py only loads 68 base stops from lines.json,
while GSPNS /mreza API has 774 stops with coords and line mappings.
"""
import duckdb
import json
import math
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
DB = BASE / 'data' / 'dbs' / 'transit.duckdb'
NS_STOPS = BASE / 'data' / 'raw' / 'novi-sad' / 'osm_stops.json'
NS_MAP = BASE / 'data' / 'raw' / 'novi-sad' / 'gspns_id_map.json'


def to_slug(text):
    cyrillic = {
        '\u0161': 's', '\u0111': 'dj', '\u017e': 'z', '\u0107': 'c', '\u010d': 'c',
    }
    r = ''
    for ch in text.lower():
        r += cyrillic.get(ch, ch)
    return re.sub(r'[^a-z0-9]+', '-', r).strip('-')


def gspns_to_num(code):
    return re.sub(r"(GL[AB]|J[AB]|[AB])$", "", code) or None


def main():
    if not NS_STOPS.exists() or not NS_MAP.exists():
        print("  No Novi Sad OSM data cached, skipping post-build enrichment")
        return

    conn = duckdb.connect(str(DB))
    ns_stops = json.load(open(NS_STOPS))
    gspns_map = json.load(open(NS_MAP))

    before = conn.execute("SELECT count(*) FROM city_stops WHERE city='novi-sad'").fetchone()[0]

    existing = set(r[0] for r in conn.execute("SELECT slug FROM city_stops WHERE city='novi-sad'").fetchall())
    max_id = conn.execute("SELECT COALESCE(MAX(id),0) FROM city_stops").fetchone()[0]
    nid = max_id + 1

    inserted = 0
    for name, info in ns_stops.items():
        s = to_slug(name)
        if s in existing:
            continue
        conn.execute("INSERT OR IGNORE INTO city_stops (id,city,name,slug,lat,lon) VALUES (?,?,?,?,?,?)",
                     (nid, 'novi-sad', name, s, info['lat'], info['lon']))
        existing.add(s)
        nid += 1
        inserted += 1

    # Link to lines
    our_lines = {r[1]: r[0] for r in conn.execute("SELECT id, number FROM city_lines WHERE city='novi-sad'").fetchall()}
    our_stops_list = conn.execute("SELECT id, lat, lon FROM city_stops WHERE city='novi-sad' AND lat IS NOT NULL").fetchall()
    grid = {}
    for sid, lat, lon in our_stops_list:
        key = (round(lat, 3), round(lon, 3))
        grid.setdefault(key, []).append((sid, lat, lon))

    new_links = 0
    for name, info in ns_stops.items():
        slat, slon = info['lat'], info['lon']
        key = (round(slat, 3), round(slon, 3))
        best_sid = None
        best_dist = 999
        for dk in [(0, 0), (-0.001, 0), (0.001, 0), (0, -0.001), (0, 0.001),
                   (-0.001, -0.001), (0.001, -0.001), (-0.001, 0.001), (0.001, 0.001)]:
            k = (round(key[0] + dk[0], 3), round(key[1] + dk[1], 3))
            for sid, olat, olon in grid.get(k, []):
                dlat = (slat - olat) * 111320
                dlon = (slon - olon) * 111320 * math.cos(math.radians(slat))
                d = math.sqrt(dlat ** 2 + dlon ** 2)
                if d < 100 and d < best_dist:
                    best_dist = d
                    best_sid = sid
        if not best_sid:
            continue
        line_nums = set()
        for gid in info.get('lines', []):
            code = gspns_map.get(str(gid), '')
            if code:
                num = gspns_to_num(code)
                if num:
                    line_nums.add(num)
        for num in line_nums:
            lid = our_lines.get(num)
            if lid:
                try:
                    conn.execute("INSERT OR IGNORE INTO city_line_stops VALUES (?,?,?)", [lid, best_sid, 0])
                    new_links += 1
                except:
                    pass

    after = conn.execute("SELECT count(*) FROM city_stops WHERE city='novi-sad'").fetchone()[0]
    print(f"  Post-build NS enrichment: {before}→{after} stops (+{inserted}), +{new_links} links")
    conn.close()


if __name__ == '__main__':
    main()

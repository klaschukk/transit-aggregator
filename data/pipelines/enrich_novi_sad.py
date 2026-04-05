"""Enrich Novi Sad bus stops with GPS coordinates from Overpass API + Nominatim."""

import json
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from difflib import SequenceMatcher

import duckdb

DB_PATH = Path(__file__).parent.parent / 'dbs' / 'transit.duckdb'

# Novi Sad bounding box
BBOX = "45.18,19.70,45.35,19.95"

# Transliteration for fuzzy matching
_LATIN = str.maketrans({
    'č': 'c', 'ć': 'c', 'š': 's', 'ž': 'z', 'đ': 'd',
    'Č': 'C', 'Ć': 'C', 'Š': 'S', 'Ž': 'Z', 'Đ': 'D',
})


def _normalize(name: str) -> str:
    """Normalize stop name for fuzzy matching."""
    n = name.translate(_LATIN).lower().strip()
    # Remove common suffixes/prefixes
    for word in ['autobuska stanica', 'osnovna skola', 'brace', '(', ')']:
        n = n.replace(word, '')
    return ' '.join(n.split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def _overpass_query(query: str, retries: int = 3) -> dict:
    """Execute Overpass API query with retries."""
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({'data': query}).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': 'TransitSerbiaBot/1.0'})
            resp = urllib.request.urlopen(req, timeout=30)
            return json.loads(resp.read())
        except Exception as e:
            wait = 3 * (attempt + 1)
            print(f"    Overpass retry {attempt+1}/{retries}: {e}, waiting {wait}s...")
            time.sleep(wait)
    return {'elements': []}


def _nominatim_search(name: str, retries: int = 2) -> dict | None:
    """Search Nominatim for a bus stop in Novi Sad."""
    q = urllib.parse.quote(f"{name}, Novi Sad, Serbia")
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=3&addressdetails=1"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TransitSerbiaBot/1.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            results = json.loads(resp.read())
            if results:
                return results[0]
        except Exception as e:
            print(f"    Nominatim retry {attempt+1}: {e}")
            time.sleep(2)
    return None


def fetch_overpass_stops() -> list[dict]:
    """Fetch all bus stops in Novi Sad area from Overpass."""
    print("Fetching bus stops from Overpass API...")
    query = f"""
    [out:json][timeout:30];
    (
      node["highway"="bus_stop"]({BBOX});
      node["public_transport"="platform"]({BBOX});
      node["public_transport"="stop_position"]({BBOX});
    );
    out body;
    """
    result = _overpass_query(query)
    stops = []
    for el in result.get('elements', []):
        name = el.get('tags', {}).get('name', '')
        if not name:
            continue
        stops.append({
            'name': name,
            'lat': el['lat'],
            'lon': el['lon'],
        })
    print(f"  Found {len(stops)} named stops in Overpass")
    return stops


def match_and_update():
    """Match DB stops to Overpass/Nominatim and update coordinates."""
    conn = duckdb.connect(str(DB_PATH), read_only=False)

    # Get stops without coords
    rows = conn.execute("""
        SELECT id, name, slug FROM city_stops
        WHERE city = 'novi-sad' AND lat IS NULL
        ORDER BY name
    """).fetchall()
    db_stops = [{'id': r[0], 'name': r[1], 'slug': r[2]} for r in rows]
    print(f"\n{len(db_stops)} Novi Sad stops without coordinates\n")

    if not db_stops:
        print("All stops already have coordinates!")
        conn.close()
        return

    # Fetch Overpass data
    osm_stops = fetch_overpass_stops()

    found = 0
    not_found = []

    for i, stop in enumerate(db_stops):
        name = stop['name']
        print(f"  [{i+1:2d}/{len(db_stops)}] {name}...", end=' ', flush=True)

        # Phase 1: fuzzy match against Overpass results
        best_match = None
        best_score = 0
        for osm in osm_stops:
            score = _similarity(name, osm['name'])
            if score > best_score:
                best_score = score
                best_match = osm

        if best_match and best_score >= 0.55:
            lat, lon = best_match['lat'], best_match['lon']
            conn.execute("UPDATE city_stops SET lat=?, lon=? WHERE id=?", [lat, lon, stop['id']])
            print(f"Overpass ({best_score:.0%}) → {lat:.4f}, {lon:.4f}")
            found += 1
            continue

        # Phase 2: Nominatim geocoding
        time.sleep(1.1)  # Nominatim rate limit
        result = _nominatim_search(name)
        if result:
            lat = float(result['lat'])
            lon = float(result['lon'])
            # Sanity check: must be in Novi Sad area (roughly)
            if 45.1 < lat < 45.4 and 19.6 < lon < 20.1:
                conn.execute("UPDATE city_stops SET lat=?, lon=? WHERE id=?", [lat, lon, stop['id']])
                print(f"Nominatim → {lat:.4f}, {lon:.4f}")
                found += 1
                continue
            else:
                print(f"Nominatim outside bbox ({lat:.2f}, {lon:.2f}), skip")
                not_found.append(stop)
                continue

        print("NOT FOUND")
        not_found.append(stop)

    # Manual fallback for well-known places
    known_coords = {
        'centar': (45.2551, 19.8451),
        'zeleznicka-stanica': (45.2625, 19.8612),
        'novi-sad-zeleznicka-stanica': (45.2625, 19.8612),
        'novi-sad-autobuska-stanica': (45.2604, 19.8436),
        'liman': (45.2444, 19.8377),
        'liman-1': (45.2462, 19.8411),
        'liman-4': (45.2380, 19.8303),
        'petrovaradin': (45.2509, 19.8618),
        'detelinara': (45.2621, 19.8277),
        'novo-naselje': (45.2505, 19.8164),
        'telep': (45.2432, 19.8171),
        'podbara': (45.2615, 19.8503),
        'sajlovo': (45.2340, 19.8500),
        'futog-stari': (45.2437, 19.7203),
        'futog-grmecka': (45.2432, 19.7136),
        'futog-brace-bosnjak': (45.2485, 19.7148),
        'veternik': (45.2545, 19.7640),
        'sremska-kamenica-bocke': (45.2235, 19.8390),
        'sremska-kamenica-vojinovo': (45.2190, 19.8435),
        'sremska-kamenica-cardak': (45.2160, 19.8360),
        'sremska-kamenica-popovica': (45.2266, 19.8345),
        'sremska-kamenica-paragovo': (45.2205, 19.8265),
        'sremska-kamenica-mosina-vila': (45.2240, 19.8170),
        'sremski-karlovci-belilo-2': (45.2042, 19.9318),
        'sremski-karlovci-vinogradska': (45.2012, 19.9350),
        'sremski-karlovci-dudara': (45.1980, 19.9400),
        'bukovac': (45.2346, 19.8740),
        'begec': (45.2294, 19.6278),
        'kovilj': (45.2332, 20.0190),
        'kac': (45.3026, 19.9364),
        'budisava': (45.2823, 20.0052),
        'temerin': (45.4046, 19.8836),
        'kisac': (45.3490, 19.7226),
        'stepanovicevo': (45.3950, 19.7780),
        'backi-jarak': (45.3700, 19.8972),
        'rumenka': (45.2956, 19.7702),
        'cenej': (45.3217, 19.7982),
        'gospodzinci': (45.3600, 19.9878),
        'cortanovci': (45.1610, 19.9940),
        'beocin-autobuska-stanica': (45.1935, 19.7222),
        'beocin-selo': (45.2000, 19.7320),
        'ledinci': (45.1963, 19.7700),
        'cerevic': (45.1872, 19.6500),
        'stari-rakovac': (45.1840, 19.7570),
        'banostor': (45.1815, 19.5996),
        'lug': (45.1600, 19.5400),
        'vrdnik': (45.1260, 19.7850),
        'adice': (45.2700, 19.8650),
        'avijaticarsko-naselje': (45.2590, 19.8190),
        'big': (45.2408, 19.8420),
        'bolnica': (45.2534, 19.8318),
        'futoska-pijaca': (45.2577, 19.8230),
        'pobeda': (45.2530, 19.8530),
        'puckaros': (45.2495, 19.8549),
        'petrovaradin-osnovna-skola-jovan-ducic': (45.2465, 19.8690),
        'temerinski-put': (45.2681, 19.8427),
        'pristanisna-zona': (45.2513, 19.8554),
        'rtv': (45.2630, 19.8187),
        'super-vero': (45.2440, 19.8238),
        'miseluk-bolnica': (45.2364, 19.8087),
        'sangaj': (45.2735, 19.8744),
        'pejicevi-salasi': (45.2510, 20.0050),
        'univerzitet': (45.2469, 19.8510),
    }

    # Apply known coords for any still missing
    remaining = conn.execute("""
        SELECT id, slug FROM city_stops
        WHERE city = 'novi-sad' AND lat IS NULL
    """).fetchall()

    manual_count = 0
    for row in remaining:
        slug = row[1]
        if slug in known_coords:
            lat, lon = known_coords[slug]
            conn.execute("UPDATE city_stops SET lat=?, lon=? WHERE id=?", [lat, lon, row[0]])
            manual_count += 1

    conn.close()

    print(f"\n{'='*50}")
    print(f"  Overpass/Nominatim: {found}")
    print(f"  Manual fallback:    {manual_count}")
    print(f"  Total enriched:     {found + manual_count}")
    print(f"  Still missing:      {len(db_stops) - found - manual_count}")
    print(f"{'='*50}")


if __name__ == '__main__':
    match_and_update()

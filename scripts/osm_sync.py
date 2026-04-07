"""Sync bus stops from OpenStreetMap for all cities."""
import duckdb
import requests
import time

DB_PATH = "data/dbs/transit.duckdb"

CITIES = {
    "beograd": (44.65, 20.20, 44.95, 20.65),
    "novi-sad": (45.18, 19.72, 45.32, 19.92),
    "nis": (43.28, 21.82, 43.38, 21.98),
}


def slugify(name):
    s = name.lower().strip()
    for old, new in [(" ", "-"), ("/", "-"), ("č", "c"), ("ć", "c"), ("š", "s"), ("ž", "z"), ("đ", "dj")]:
        s = s.replace(old, new)
    return s


def sync_city(conn, city, bbox):
    s, w, n, e = bbox
    print(f"\n=== {city} ===")

    existing = conn.execute("SELECT COUNT(*) FROM city_stops WHERE city=?", [city]).fetchone()[0]
    print(f"Existing stops: {existing}")

    query = f"[out:json][timeout:60];(node[highway=bus_stop]({s},{w},{n},{e});node[public_transport=platform]({s},{w},{n},{e}););out body;"

    print("Fetching from Overpass...")
    r = requests.get("https://overpass-api.de/api/interpreter", params={"data": query}, timeout=120)
    osm_stops = r.json().get("elements", [])
    print(f"OSM returned: {len(osm_stops)} stops")

    max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM city_stops").fetchone()[0]
    added = 0

    for stop in osm_stops:
        lat = stop["lat"]
        lon = stop["lon"]
        name = stop.get("tags", {}).get("name", "")
        if not name:
            continue

        slug = slugify(name)

        # Check if already exists nearby
        near = conn.execute(
            "SELECT id FROM city_stops WHERE city=? AND lat BETWEEN ?-0.0004 AND ?+0.0004 AND lon BETWEEN ?-0.0004 AND ?+0.0004 LIMIT 1",
            [city, lat, lat, lon, lon]
        ).fetchone()

        if not near:
            max_id += 1
            try:
                conn.execute(
                    "INSERT INTO city_stops (id, city, name, slug, lat, lon) VALUES (?,?,?,?,?,?)",
                    [max_id, city, name, slug, lat, lon]
                )
                added += 1
            except Exception:
                pass

    print(f"Added: {added} new stops")
    total = conn.execute("SELECT COUNT(*) FROM city_stops WHERE city=?", [city]).fetchone()[0]
    print(f"Total now: {total}")


def main():
    print("=== OSM STOP SYNC ===")
    conn = duckdb.connect(DB_PATH)

    for city, bbox in CITIES.items():
        try:
            sync_city(conn, city, bbox)
        except Exception as e:
            print(f"ERROR {city}: {e}")
        time.sleep(5)  # Be nice to Overpass

    conn.close()
    print("\n=== DONE ===")


if __name__ == "__main__":
    main()

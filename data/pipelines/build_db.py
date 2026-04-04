"""
Build transit.duckdb from raw scraped data.

Run order:
  1. python data/pipelines/scrape_gsp.py
  2. python data/pipelines/scrape_intercity.py
  3. python data/pipelines/scrape_srbvoz.py
  4. python data/pipelines/build_db.py

Falls back to sample data if raw files are missing.
"""
import json
import re
from pathlib import Path

import duckdb

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / 'raw'
GTFS_DIR = BASE_DIR / 'gtfs'
DB_PATH = BASE_DIR / 'dbs' / 'transit.duckdb'

# Approximate road distances (km) between Serbian cities
DISTANCES: dict[tuple[str, str], int] = {
    ('Beograd', 'Novi Sad'): 90,
    ('Beograd', 'Niš'): 250,
    ('Beograd', 'Kragujevac'): 145,
    ('Beograd', 'Subotica'): 185,
    ('Beograd', 'Čačak'): 155,
    ('Beograd', 'Kruševac'): 210,
    ('Beograd', 'Vranje'): 340,
    ('Beograd', 'Šabac'): 100,
    ('Beograd', 'Smederevo'): 65,
    ('Beograd', 'Valjevo'): 105,
    ('Beograd', 'Leskovac'): 285,
    ('Beograd', 'Zrenjanin'): 75,
    ('Beograd', 'Sombor'): 200,
    ('Beograd', 'Novi Pazar'): 285,
    ('Novi Sad', 'Niš'): 330,
    ('Novi Sad', 'Subotica'): 100,
    ('Novi Sad', 'Kragujevac'): 225,
    ('Niš', 'Kragujevac'): 125,
    ('Niš', 'Leskovac'): 40,
    ('Niš', 'Vranje'): 100,
    ('Nis', 'Vranje'): 100,
    ('Nis', 'Kragujevac'): 125,
}


def get_distance(from_city: str, to_city: str) -> int:
    """Return distance in km, trying both directions."""
    d = DISTANCES.get((from_city, to_city)) or DISTANCES.get((to_city, from_city))
    return d or 0


def city_to_slug(city: str) -> str:
    """Convert city name (Latin or Cyrillic) to URL slug."""
    cyrillic = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','ђ':'d','е':'e','ж':'z',
        'з':'z','и':'i','ј':'j','к':'k','л':'l','љ':'lj','м':'m','н':'n',
        'њ':'nj','о':'o','п':'p','р':'r','с':'s','т':'t','ћ':'c','у':'u',
        'ф':'f','х':'h','ц':'c','ч':'c','џ':'dz','ш':'s',
        'А':'a','Б':'b','В':'v','Г':'g','Д':'d','Ђ':'d','Е':'e','Ж':'z',
        'З':'z','И':'i','Ј':'j','К':'k','Л':'l','Љ':'lj','М':'m','Н':'n',
        'Њ':'nj','О':'o','П':'p','Р':'r','С':'s','Т':'t','Ћ':'c','У':'u',
        'Ф':'f','Х':'h','Ц':'c','Ч':'c','Џ':'dz','Ш':'s',
        'š': 's', 'đ': 'd', 'ž': 'z', 'ć': 'c', 'č': 'c',
        'Š': 's', 'Đ': 'd', 'Ž': 'z', 'Ć': 'c', 'Č': 'c',
    }
    result = ''
    for ch in city.lower():
        result += cyrillic.get(ch, ch)
    return re.sub(r'[^a-z0-9]+', '-', result).strip('-')


def type_color(line_type: str) -> str:
    colors = {
        'bus': '#0d9488',
        'tram': '#e53e3e',
        'trolleybus': '#d69e2e',
        'night': '#2b2d87',
        'bg-voz': '#7c336e',
        'e-bus': '#38a169',
    }
    return colors.get(line_type, '#0d9488')


def build() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = duckdb.connect(str(DB_PATH))
    _create_schema(conn)

    # Load from real scraped data if available, else fall back to samples
    gsp_path = RAW_DIR / 'gsp_lines.json'
    gsp_stops_path = RAW_DIR / 'gsp_stops.json'
    intercity_path = RAW_DIR / 'intercity_routes.json'
    srbvoz_path = RAW_DIR / 'srbvoz_trains.json'
    stations_path = RAW_DIR / 'srbvoz_stations.json'

    has_real_data = gsp_path.exists() or intercity_path.exists() or srbvoz_path.exists()

    if has_real_data:
        print("Loading real scraped data...")
        _load_operators(conn)
        _load_intercity(conn, intercity_path, srbvoz_path)
        _load_gsp_lines(conn, gsp_path, gsp_stops_path)
        _load_stations(conn, stations_path)
        _load_gtfs(conn)
    else:
        print("No scraped data found — loading sample data...")
        _load_sample_data(conn)

    conn.close()
    print(f"Built {DB_PATH} successfully")


def _create_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE operators (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            slug VARCHAR UNIQUE NOT NULL,
            website VARCHAR,
            type VARCHAR CHECK (type IN ('bus', 'train', 'air'))
        )
    """)
    conn.execute("""
        CREATE TABLE routes (
            id INTEGER PRIMARY KEY,
            slug VARCHAR UNIQUE NOT NULL,
            from_city VARCHAR NOT NULL,
            to_city VARCHAR NOT NULL,
            from_city_slug VARCHAR NOT NULL,
            to_city_slug VARCHAR NOT NULL,
            distance_km INTEGER,
            type VARCHAR CHECK (type IN ('intercity', 'city')) DEFAULT 'intercity'
        )
    """)
    conn.execute("""
        CREATE TABLE trips (
            id INTEGER PRIMARY KEY,
            route_id INTEGER REFERENCES routes(id),
            operator_id INTEGER REFERENCES operators(id),
            departure_time VARCHAR NOT NULL,
            arrival_time VARCHAR NOT NULL,
            duration_min INTEGER,
            price_rsd INTEGER,
            days_of_week VARCHAR DEFAULT '1234567',
            is_active BOOLEAN DEFAULT true
        )
    """)
    conn.execute("""
        CREATE TABLE city_lines (
            id INTEGER PRIMARY KEY,
            city VARCHAR NOT NULL,
            number VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            slug VARCHAR NOT NULL,
            type VARCHAR DEFAULT 'bus',
            color VARCHAR DEFAULT '#0d9488',
            code VARCHAR,
            UNIQUE (city, number)
        )
    """)
    conn.execute("""
        CREATE TABLE city_stops (
            id INTEGER PRIMARY KEY,
            city VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            slug VARCHAR NOT NULL,
            lat DOUBLE,
            lon DOUBLE,
            code VARCHAR,
            UNIQUE (city, slug)
        )
    """)
    conn.execute("""
        CREATE TABLE city_line_stops (
            line_id INTEGER REFERENCES city_lines(id),
            stop_id INTEGER REFERENCES city_stops(id),
            stop_order INTEGER NOT NULL,
            PRIMARY KEY (line_id, stop_id)
        )
    """)
    conn.execute("""
        CREATE TABLE stations (
            id INTEGER PRIMARY KEY,
            city VARCHAR NOT NULL,
            city_slug VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            code VARCHAR,
            type VARCHAR CHECK (type IN ('bus', 'train', 'both')) DEFAULT 'bus',
            lat DOUBLE,
            lon DOUBLE,
            UNIQUE (city_slug, type)
        )
    """)
    conn.execute("""
        CREATE TABLE gtfs_trips (
            trip_id VARCHAR PRIMARY KEY,
            route_id VARCHAR NOT NULL,
            service_id VARCHAR NOT NULL,
            direction_id INTEGER,
            line_id INTEGER REFERENCES city_lines(id)
        )
    """)
    conn.execute("""
        CREATE TABLE gtfs_stop_times (
            trip_id VARCHAR REFERENCES gtfs_trips(trip_id),
            stop_id VARCHAR NOT NULL,
            arrival_time VARCHAR,
            departure_time VARCHAR,
            stop_sequence INTEGER NOT NULL,
            city_stop_id INTEGER REFERENCES city_stops(id),
            PRIMARY KEY (trip_id, stop_sequence)
        )
    """)
    conn.execute("CREATE INDEX idx_routes_slugs ON routes (from_city_slug, to_city_slug)")
    conn.execute("CREATE INDEX idx_trips_route ON trips (route_id)")
    conn.execute("CREATE INDEX idx_city_lines_city ON city_lines (city)")
    conn.execute("CREATE INDEX idx_city_stops_city ON city_stops (city)")
    conn.execute("CREATE INDEX idx_stations_city ON stations (city_slug)")
    conn.execute("CREATE INDEX idx_gtfs_stop_times_trip ON gtfs_stop_times (trip_id)")
    conn.execute("CREATE INDEX idx_gtfs_stop_times_stop ON gtfs_stop_times (stop_id)")
    print("Schema created")


def _load_operators(conn: duckdb.DuckDBPyConnection) -> None:
    operators = [
        (1, 'Lasta', 'lasta', 'https://www.lasta.rs', 'bus'),
        (2, 'Niš-Ekspres', 'nis-ekspres', 'https://www.nis-ekspres.rs', 'bus'),
        (3, 'Srbija Voz', 'srbija-voz', 'https://www.srbvoz.rs', 'train'),
        (4, 'BusTicket4.me', 'busticket4', 'https://www.busticket4.me', 'bus'),
        (5, 'OZT', 'ozt', None, 'bus'),
        (6, 'LAB', 'lab', None, 'bus'),
        (7, 'B21', 'b21', None, 'bus'),
    ]
    conn.executemany("INSERT INTO operators VALUES (?, ?, ?, ?, ?)", operators)
    print(f"Loaded {len(operators)} operators")


def _load_intercity(conn: duckdb.DuckDBPyConnection,
                    intercity_path: Path,
                    srbvoz_path: Path) -> None:
    """Load intercity bus + train trips into routes + trips tables."""
    all_trips: list[dict] = []

    if intercity_path.exists():
        with open(intercity_path, encoding='utf-8') as f:
            bus_trips = json.load(f)
        for t in bus_trips:
            t['type'] = 'bus'
        all_trips.extend(bus_trips)
        print(f"  Bus trips: {len(bus_trips)}")

    if srbvoz_path.exists():
        with open(srbvoz_path, encoding='utf-8') as f:
            train_trips = json.load(f)
        all_trips.extend(train_trips)
        print(f"  Train trips: {len(train_trips)}")

    if not all_trips:
        return

    # Build route registry: (from_city, to_city) → route_id
    route_registry: dict[tuple[str, str], int] = {}
    route_id = 1

    for trip in all_trips:
        key = (trip['from_city'], trip['to_city'])
        if key not in route_registry:
            from_slug = city_to_slug(trip['from_city'])
            to_slug = city_to_slug(trip['to_city'])
            slug = f'{from_slug}-{to_slug}'
            distance = get_distance(trip['from_city'], trip['to_city'])

            # Check for slug collision (e.g. "Nis" vs "Niš" → same slug)
            existing = conn.execute(
                "SELECT id FROM routes WHERE slug = ?", (slug,)
            ).fetchone()
            if existing:
                route_registry[key] = existing[0]
            else:
                conn.execute(
                    "INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (route_id, slug, trip['from_city'], trip['to_city'],
                     from_slug, to_slug, distance, 'intercity')
                )
                route_registry[key] = route_id
                route_id += 1

    # Operator name → id map (Latin + Cyrillic variants)
    op_map: dict[str, int] = {
        'Lasta': 1, 'Lasta Beograd': 1, 'Ласта': 1, 'СП Ласта Београд': 1, 'СП ЛАСТА': 1,
        'Niš-Ekspres': 2, 'NAISTURS': 2,
        'Srbija Voz': 3,
        'OZT': 5, 'LAB': 6, 'B21': 7,
    }
    default_bus_op = 4  # BusTicket4.me

    trip_id = 1
    for trip in all_trips:
        route_id_val = route_registry.get((trip['from_city'], trip['to_city']))
        if not route_id_val:
            continue
        op_name = trip.get('operator', '')
        op_id = op_map.get(op_name, default_bus_op)
        price = trip.get('price_rsd') or 0
        trip_type = trip.get('type', 'bus')

        conn.execute(
            "INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trip_id, route_id_val, op_id,
             trip['departure_time'], trip['arrival_time'],
             trip.get('duration_min', 0), price,
             '1234567', True)
        )
        trip_id += 1

    print(f"  Loaded {route_id - 1} routes, {trip_id - 1} trips")


def _load_gsp_lines(conn: duckdb.DuckDBPyConnection,
                    gsp_path: Path, gsp_stops_path: Path) -> None:
    """Load Belgrade city lines and stops from scraped GSP data."""
    if not gsp_path.exists():
        print("  No GSP data found, skipping city lines")
        return

    with open(gsp_path, encoding='utf-8') as f:
        lines = json.load(f)

    # Build stop registry from gsp_stops.json (has real coords)
    # stop_api_id → db_id, and stop_api_id → {lat, lon, name}
    api_stop_map: dict[int, dict] = {}
    if gsp_stops_path.exists():
        with open(gsp_stops_path, encoding='utf-8') as f:
            raw_stops = json.load(f)
        for s in raw_stops:
            api_stop_map[s['id']] = s
        print(f"  Loaded {len(api_stop_map)} stops with coords from gsp_stops.json")

    # Insert all stops first (from gsp_stops.json if available)
    stop_db_registry: dict[int, int] = {}   # api_stop_id → db_id
    slug_registry: dict[str, int] = {}       # slug → db_id (fallback for name-only)
    stop_db_id = 1

    for api_id, stop in api_stop_map.items():
        slug = city_to_slug(stop['name'])
        if slug in slug_registry:
            stop_db_registry[api_id] = slug_registry[slug]
            continue
        try:
            conn.execute(
                "INSERT OR IGNORE INTO city_stops (id, city, name, slug, lat, lon, code) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (stop_db_id, 'beograd', stop['name'], slug,
                 stop.get('lat'), stop.get('lon'), str(api_id))
            )
            stop_db_registry[api_id] = stop_db_id
            slug_registry[slug] = stop_db_id
            stop_db_id += 1
        except Exception:
            pass

    line_db_id = 1
    for line in lines:
        number = line.get('number', '')
        name = line.get('name', '')
        raw_slug = line.get('slug', f'linija-{number.lower()}')
        slug = city_to_slug(raw_slug)
        line_type = line.get('type', 'bus')
        color = type_color(line_type)

        try:
            conn.execute(
                "INSERT OR IGNORE INTO city_lines (id, city, number, name, slug, type, color) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (line_db_id, 'beograd', number, name, slug, line_type, color)
            )

            # Stops come from the enriched line data (stop_id = bgprevoz API ID)
            for stop_info in line.get('stops', []):
                api_id = stop_info.get('stop_id')
                order = stop_info.get('order', 0)
                stop_name = stop_info.get('name', '').strip()

                if api_id and api_id in stop_db_registry:
                    db_stop_id = stop_db_registry[api_id]
                elif stop_name:
                    # Fallback: insert by name without coords
                    s_slug = city_to_slug(stop_name)
                    if s_slug not in slug_registry:
                        try:
                            conn.execute(
                                "INSERT OR IGNORE INTO city_stops (id, city, name, slug, lat, lon) VALUES (?, ?, ?, ?, ?, ?)",
                                (stop_db_id, 'beograd', stop_name, s_slug, None, None)
                            )
                            slug_registry[s_slug] = stop_db_id
                            stop_db_id += 1
                        except Exception:
                            pass
                    db_stop_id = slug_registry.get(s_slug)
                else:
                    continue

                if db_stop_id:
                    try:
                        conn.execute(
                            "INSERT OR IGNORE INTO city_line_stops VALUES (?, ?, ?)",
                            (line_db_id, db_stop_id, order)
                        )
                    except Exception:
                        pass

            line_db_id += 1
        except Exception as e:
            print(f"  Skip line {number}: {e}")

    print(f"  Loaded {line_db_id - 1} GSP lines, {stop_db_id - 1} stops")


def _load_stations(conn: duckdb.DuckDBPyConnection, stations_path: Path) -> None:
    """Load bus/train stations from scraped data."""
    if not stations_path.exists():
        print("  No stations data found, skipping")
        return

    with open(stations_path, encoding='utf-8') as f:
        stations = json.load(f)

    station_id = 1
    for city, info in stations.items():
        city_slug = city_to_slug(city)
        name = info.get('naziv', city)
        code = info.get('sifra')
        conn.execute(
            "INSERT OR IGNORE INTO stations (id, city, city_slug, name, code, type) VALUES (?, ?, ?, ?, ?, ?)",
            (station_id, city, city_slug, name, code, 'train')
        )
        station_id += 1

    print(f"  Loaded {station_id - 1} stations")


def _load_gtfs(conn: duckdb.DuckDBPyConnection) -> None:
    """Load GTFS data (trips + stop_times) if available."""
    trips_path = GTFS_DIR / 'trips.txt'
    stop_times_path = GTFS_DIR / 'stop_times.txt'

    if not trips_path.exists() or not stop_times_path.exists():
        print("  No GTFS data found, skipping")
        return

    import csv

    # Build line lookup: route_short_name → line_id
    line_map: dict[str, int] = {}
    rows = conn.execute("SELECT id, number FROM city_lines WHERE city = 'beograd'").fetchall()
    for row in rows:
        line_map[row[1]] = row[0]

    # Build stop lookup: gtfs stop_id (code) → city_stop_id
    stop_map: dict[str, int] = {}
    rows = conn.execute("SELECT id, code FROM city_stops WHERE code IS NOT NULL").fetchall()
    for row in rows:
        stop_map[row[1]] = row[0]

    # Load trips
    trip_count = 0
    with open(trips_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trip_id = row['trip_id']
            route_id = row.get('route_id', '')
            service_id = row.get('service_id', '')
            direction_id = int(row['direction_id']) if row.get('direction_id') else None
            # Try to link to city_lines via route_short_name
            line_id = line_map.get(row.get('route_short_name'))
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO gtfs_trips VALUES (?, ?, ?, ?, ?)",
                    (trip_id, route_id, service_id, direction_id, line_id)
                )
                trip_count += 1
            except Exception:
                pass

    # Load stop_times
    st_count = 0
    with open(stop_times_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trip_id = row['trip_id']
            stop_id = row['stop_id']
            arrival = row.get('arrival_time', '')
            departure = row.get('departure_time', '')
            seq = int(row.get('stop_sequence', 0))
            city_stop_id = stop_map.get(stop_id)
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO gtfs_stop_times VALUES (?, ?, ?, ?, ?, ?)",
                    (trip_id, stop_id, arrival, departure, seq, city_stop_id)
                )
                st_count += 1
            except Exception:
                pass

    print(f"  Loaded GTFS: {trip_count} trips, {st_count} stop_times")


def _load_sample_data(conn: duckdb.DuckDBPyConnection) -> None:
    """Fallback sample data when scrapers haven't run yet."""
    conn.executemany("INSERT INTO operators VALUES (?, ?, ?, ?, ?)", [
        (1, 'Lasta', 'lasta', 'https://www.lasta.rs', 'bus'),
        (2, 'Niš-Ekspres', 'nis-ekspres', 'https://www.nis-ekspres.rs', 'bus'),
        (3, 'Srbija Voz', 'srbija-voz', 'https://www.srbvoz.rs', 'train'),
    ])
    conn.executemany("INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, 'beograd-novi-sad', 'Beograd', 'Novi Sad', 'beograd', 'novi-sad', 90, 'intercity'),
        (2, 'beograd-nis', 'Beograd', 'Niš', 'beograd', 'nis', 250, 'intercity'),
        (3, 'beograd-kragujevac', 'Beograd', 'Kragujevac', 'beograd', 'kragujevac', 145, 'intercity'),
        (4, 'beograd-subotica', 'Beograd', 'Subotica', 'beograd', 'subotica', 185, 'intercity'),
        (5, 'beograd-nis-2', 'Beograd', 'Niš', 'beograd', 'nis', 250, 'intercity'),
    ])
    conn.executemany("INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, 1, 1, '06:00', '07:30', 90, 800, '1234567', True),
        (2, 1, 1, '08:00', '09:30', 90, 800, '1234567', True),
        (3, 1, 2, '10:00', '11:30', 90, 750, '1234567', True),
        (4, 2, 1, '07:00', '10:45', 225, 1800, '1234567', True),
        (5, 2, 2, '12:00', '15:45', 225, 1600, '1234567', True),
        (6, 2, 3, '07:30', '14:00', 390, 1400, '1234567', True),
    ])
    conn.executemany("INSERT INTO city_lines VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, 'beograd', '11', 'Zemun — Zeleni Venac', 'linija-11', 'tram', '#e53e3e', None),
        (2, 'beograd', '25', 'Bežanija — Studentski trg', 'linija-25', 'e-bus', '#38a169', None),
        (3, 'beograd', '31', 'Mirijevo — Zeleni Venac', 'linija-31', 'bus', '#0d9488', None),
        (4, 'beograd', '94', 'Batajnica — Zeleni Venac', 'linija-94', 'trolleybus', '#d69e2e', None),
    ])
    print("Sample data loaded")


if __name__ == '__main__':
    build()

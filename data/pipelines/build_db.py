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
    ('Beograd', 'Novi Sad'): 90, ('Beograd', 'Niš'): 250,
    ('Beograd', 'Kragujevac'): 145, ('Beograd', 'Subotica'): 185,
    ('Beograd', 'Čačak'): 155, ('Beograd', 'Kruševac'): 210,
    ('Beograd', 'Vranje'): 340, ('Beograd', 'Šabac'): 100,
    ('Beograd', 'Smederevo'): 65, ('Beograd', 'Valjevo'): 105,
    ('Beograd', 'Leskovac'): 285, ('Beograd', 'Zrenjanin'): 75,
    ('Beograd', 'Sombor'): 200, ('Beograd', 'Novi Pazar'): 285,
    ('Beograd', 'Pančevo'): 20, ('Beograd', 'Užice'): 200,
    ('Beograd', 'Jagodina'): 140, ('Beograd', 'Pirot'): 320,
    ('Beograd', 'Kraljevo'): 185, ('Beograd', 'Požarevac'): 80,
    ('Beograd', 'Zaječar'): 250, ('Beograd', 'Kikinda'): 150,
    ('Beograd', 'Sremska Mitrovica'): 80, ('Beograd', 'Loznica'): 145,
    ('Novi Sad', 'Niš'): 330, ('Novi Sad', 'Subotica'): 100,
    ('Novi Sad', 'Kragujevac'): 225, ('Novi Sad', 'Zrenjanin'): 75,
    ('Novi Sad', 'Sombor'): 110, ('Novi Sad', 'Kikinda'): 120,
    ('Novi Sad', 'Sremska Mitrovica'): 55, ('Novi Sad', 'Šabac'): 100,
    ('Niš', 'Kragujevac'): 125, ('Niš', 'Leskovac'): 40,
    ('Niš', 'Vranje'): 100, ('Niš', 'Pirot'): 70,
    ('Niš', 'Zaječar'): 110, ('Niš', 'Kruševac'): 75,
    ('Niš', 'Jagodina'): 115, ('Niš', 'Kraljevo'): 115,
    ('Niš', 'Novi Pazar'): 200, ('Niš', 'Požarevac'): 175,
    ('Kragujevac', 'Kraljevo'): 60, ('Kragujevac', 'Čačak'): 70,
    ('Kragujevac', 'Jagodina'): 55, ('Kragujevac', 'Kruševac'): 75,
    ('Subotica', 'Sombor'): 85, ('Subotica', 'Kikinda'): 80,
    ('Čačak', 'Kraljevo'): 40, ('Čačak', 'Užice'): 70,
    ('Kraljevo', 'Kruševac'): 50, ('Kraljevo', 'Novi Pazar'): 100,
    ('Leskovac', 'Vranje'): 55, ('Pirot', 'Zaječar'): 100,
    ('Požarevac', 'Smederevo'): 40, ('Šabac', 'Loznica'): 50,
    ('Šabac', 'Sremska Mitrovica'): 50, ('Valjevo', 'Užice'): 90,
    ('Zrenjanin', 'Kikinda'): 55, ('Sombor', 'Kikinda'): 110,
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

    novi_sad_path = RAW_DIR / 'novi-sad' / 'lines.json'
    nis_path = RAW_DIR / 'nis' / 'lines.json'

    if has_real_data:
        print("Loading real scraped data...")
        _load_operators(conn)
        _load_intercity(conn, intercity_path, srbvoz_path)
        _load_gsp_lines(conn, gsp_path, gsp_stops_path)
        _load_city_lines(conn, 'novi-sad', novi_sad_path)
        _load_city_lines(conn, 'nis', nis_path)
        _load_stations(conn, stations_path)
        _load_gtfs(conn)
        _load_city_schedule(conn, 'novi-sad')
        _cleanup(conn)
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
            trip_id VARCHAR NOT NULL,
            stop_id VARCHAR NOT NULL,
            arrival_time VARCHAR,
            departure_time VARCHAR,
            stop_sequence INTEGER NOT NULL,
            city_stop_id INTEGER REFERENCES city_stops(id)
        )
    """)
    conn.execute("CREATE INDEX idx_routes_slugs ON routes (from_city_slug, to_city_slug)")
    conn.execute("CREATE INDEX idx_trips_route ON trips (route_id)")
    conn.execute("CREATE INDEX idx_city_lines_city ON city_lines (city)")
    conn.execute("CREATE INDEX idx_city_stops_city ON city_stops (city)")
    conn.execute("CREATE INDEX idx_stations_city ON stations (city_slug)")
    conn.execute("CREATE INDEX idx_gtfs_stop_times_trip ON gtfs_stop_times (trip_id)")
    conn.execute("CREATE INDEX idx_gtfs_stop_times_stop ON gtfs_stop_times (stop_id)")
    conn.execute("CREATE INDEX idx_gtfs_stop_times_city_stop ON gtfs_stop_times (city_stop_id)")
    conn.execute("CREATE INDEX idx_gtfs_trips_line ON gtfs_trips (line_id)")
    conn.execute("CREATE INDEX idx_gtfs_trips_service ON gtfs_trips (service_id)")
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
        (8, 'Severtrans Sombor', 'severtrans', None, 'bus'),
        (9, 'Jugoprevoz Kruševac', 'jugoprevoz-krusevac', None, 'bus'),
        (10, 'Autoprevoz Čačak', 'autoprevoz-cacak', None, 'bus'),
        (11, 'Kavim Raška', 'kavim-raska', None, 'bus'),
        (12, 'Sandžaktrans', 'sandzaktrans', None, 'bus'),
        (13, 'Frenki Komerc', 'frenki-komerc', None, 'bus'),
        (14, 'Banbus', 'banbus', None, 'bus'),
        (15, 'Sirmiumbus', 'sirmiumbus', None, 'bus'),
        (16, 'Autoprevoz Kikinda', 'autoprevoz-kikinda', None, 'bus'),
    ]
    conn.executemany("INSERT INTO operators VALUES (?, ?, ?, ?, ?)", operators)

    # Auto-register operators from polazak.rs data
    lasta_ops_path = RAW_DIR / 'lasta' / 'operators.json'
    if lasta_ops_path.exists():
        with open(lasta_ops_path, encoding='utf-8') as f:
            polazak_ops = json.load(f)
        next_id = len(operators) + 1
        existing = {row[0] for row in conn.execute("SELECT name FROM operators").fetchall()}
        for name, op_type in polazak_ops.items():
            if name not in existing:
                slug = city_to_slug(name)
                conn.execute(
                    "INSERT OR IGNORE INTO operators VALUES (?, ?, ?, ?, ?)",
                    (next_id, name, slug, None, op_type if op_type in ('bus', 'train') else 'bus')
                )
                existing.add(name)
                next_id += 1

    total = conn.execute("SELECT COUNT(*) FROM operators").fetchone()[0]
    print(f"Loaded {total} operators")


def _load_intercity(conn: duckdb.DuckDBPyConnection,
                    intercity_path: Path,
                    srbvoz_path: Path) -> None:
    """Load intercity bus + train trips from all sources into routes + trips."""
    all_trips: list[dict] = []

    # Source 1: busticket4.me
    if intercity_path.exists():
        with open(intercity_path, encoding='utf-8') as f:
            bus_trips = json.load(f)
        for t in bus_trips:
            t['type'] = 'bus'
            t['_source'] = 'bt4'
        all_trips.extend(bus_trips)
        print(f"  busticket4.me trips: {len(bus_trips)}")

    # Source 2: srbijavoz
    if srbvoz_path.exists():
        with open(srbvoz_path, encoding='utf-8') as f:
            train_trips = json.load(f)
        for t in train_trips:
            t['_source'] = 'srbvoz'
        all_trips.extend(train_trips)
        print(f"  Srbija Voz trips: {len(train_trips)}")

    # Source 3: polazak.rs (via lasta.rs)
    lasta_path = RAW_DIR / 'lasta' / 'trips.json'
    if lasta_path.exists():
        with open(lasta_path, encoding='utf-8') as f:
            lasta_trips = json.load(f)
        for t in lasta_trips:
            t['_source'] = 'polazak'
        all_trips.extend(lasta_trips)
        print(f"  polazak.rs trips: {len(lasta_trips)}")

    if not all_trips:
        return

    # Deduplicate: same from_city + to_city + departure_time → keep first
    seen: set[tuple[str, str, str]] = set()
    unique_trips: list[dict] = []
    dupes = 0
    for trip in all_trips:
        key = (trip['from_city'], trip['to_city'], trip['departure_time'])
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        unique_trips.append(trip)
    if dupes:
        print(f"  Deduplicated: {dupes} duplicate trips removed")

    # Build route registry: (from_city, to_city) → route_id
    route_registry: dict[tuple[str, str], int] = {}
    route_id = 1

    for trip in unique_trips:
        key = (trip['from_city'], trip['to_city'])
        if key not in route_registry:
            from_slug = city_to_slug(trip['from_city'])
            to_slug = city_to_slug(trip['to_city'])
            slug = f'{from_slug}-{to_slug}'
            distance = get_distance(trip['from_city'], trip['to_city'])

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

    # Build operator name → id map from DB
    op_rows = conn.execute("SELECT id, name FROM operators").fetchall()
    op_map: dict[str, int] = {name: oid for oid, name in op_rows}
    # Add common aliases
    op_map.update({
        'Lasta Beograd': op_map.get('Lasta', 1),
        'Ласта': op_map.get('Lasta', 1),
        'СП Ласта Београд': op_map.get('Lasta', 1),
        'СП ЛАСТА': op_map.get('Lasta', 1),
        'Niš-Ekspres': op_map.get('Niš-Ekspres', 2),
        'NAISTURS': op_map.get('Niš-Ekspres', 2),
    })
    default_op = op_map.get('BusTicket4.me', 4)

    trip_id = 1
    for trip in unique_trips:
        route_id_val = route_registry.get((trip['from_city'], trip['to_city']))
        if not route_id_val:
            continue
        op_name = trip.get('operator', '')
        op_id = op_map.get(op_name, default_op)
        price = trip.get('price_rsd') or 0

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


def _load_city_lines(conn: duckdb.DuckDBPyConnection, city: str, lines_path: Path) -> None:
    """Load city bus lines from a simple lines.json (Novi Sad, Niš, etc.)."""
    if not lines_path.exists():
        print(f"  No {city} lines data found, skipping")
        return

    with open(lines_path, encoding='utf-8') as f:
        lines = json.load(f)

    # Get next available IDs
    max_line_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM city_lines").fetchone()[0]
    line_db_id = max_line_id + 1

    # Get next stop ID
    max_stop_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM city_stops").fetchone()[0]
    stop_db_id = max_stop_id + 1

    # Track stops by name to dedup
    stop_name_to_id: dict[str, int] = {}

    count = 0
    stop_count = 0
    link_count = 0
    for line in lines:
        number = line.get('number', '')
        name = line.get('name', '')
        slug = city_to_slug(f'linija-{number}')
        line_type = line.get('type', 'bus')
        color = type_color(line_type)
        current_line_id = line_db_id

        try:
            conn.execute(
                "INSERT OR IGNORE INTO city_lines (id, city, number, name, slug, type, color) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (current_line_id, city, number, name, slug, line_type, color)
            )
            count += 1
            line_db_id += 1
        except Exception as e:
            print(f"  Skip {city} line {number}: {e}")
            continue

        # Load stops for this line
        stops = line.get('stops', [])
        for order, stop_data in enumerate(stops, 1):
            # Handle both string and dict formats
            if isinstance(stop_data, dict):
                stop_name = stop_data.get('name', '')
                lat = stop_data.get('lat')
                lon = stop_data.get('lon')
            else:
                stop_name = str(stop_data).strip()
                lat = None
                lon = None

            if not stop_name:
                continue

            stop_slug = city_to_slug(stop_name)
            stop_key = f"{city}:{stop_slug}"

            if stop_key not in stop_name_to_id:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO city_stops (id, city, name, slug, lat, lon) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (stop_db_id, city, stop_name, stop_slug, lat, lon)
                    )
                    stop_name_to_id[stop_key] = stop_db_id
                    stop_db_id += 1
                    stop_count += 1
                except Exception:
                    pass

            sid = stop_name_to_id.get(stop_key)
            if sid:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO city_line_stops (line_id, stop_id, stop_order) "
                        "VALUES (?, ?, ?)",
                        (current_line_id, sid, order)
                    )
                    link_count += 1
                except Exception:
                    pass

    print(f"  Loaded {count} {city} lines, {stop_count} stops, {link_count} line-stop links")


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
    """Load GTFS schedule data (trips + stop_times) using bulk DuckDB import."""
    trips_path = GTFS_DIR / 'trips.txt'
    stop_times_path = GTFS_DIR / 'stop_times.txt'
    routes_path = GTFS_DIR / 'routes.txt'

    if not trips_path.exists() or not stop_times_path.exists():
        print("  No GTFS data found, skipping")
        return

    # Step 1: Build route_id → line_id mapping via routes.txt route_short_name
    route_to_line: dict[str, int] = {}
    if routes_path.exists():
        line_map: dict[str, int] = {}
        for row in conn.execute("SELECT id, number FROM city_lines WHERE city = 'beograd'").fetchall():
            line_map[row[1]] = row[0]

        import csv
        with open(routes_path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                line_id = line_map.get(row.get('route_short_name', ''))
                if line_id:
                    route_to_line[row['route_id']] = line_id
        print(f"  GTFS route→line mapping: {len(route_to_line)} matched")

    # Step 2: Build gtfs stop_id → city_stop_id mapping via stop_code
    stop_code_map: dict[str, int] = {}
    for row in conn.execute("SELECT id, code FROM city_stops WHERE code IS NOT NULL").fetchall():
        stop_code_map[row[1]] = row[0]

    # Step 3: Bulk load trips via DuckDB read_csv_auto
    conn.execute(f"""
        INSERT INTO gtfs_trips
        SELECT trip_id, route_id, service_id, direction_id::INTEGER, NULL
        FROM read_csv_auto('{trips_path}', header=true)
    """)
    trip_count = conn.execute("SELECT COUNT(*) FROM gtfs_trips").fetchone()[0]

    # Update line_id for matched routes
    for route_id, line_id in route_to_line.items():
        conn.execute(
            "UPDATE gtfs_trips SET line_id = ? WHERE route_id = ?",
            [line_id, route_id]
        )
    linked = conn.execute("SELECT COUNT(*) FROM gtfs_trips WHERE line_id IS NOT NULL").fetchone()[0]
    print(f"  Loaded {trip_count} trips ({linked} linked to city_lines)")

    # Step 4: Bulk load stop_times via DuckDB read_csv_auto
    # Force checkpoint before bulk load to prevent WAL issues
    try:
        conn.execute("CHECKPOINT")
    except Exception:
        pass
    conn.execute(f"""
        INSERT INTO gtfs_stop_times (trip_id, stop_id, arrival_time, departure_time, stop_sequence, city_stop_id)
        SELECT trip_id, stop_id::VARCHAR, arrival_time, departure_time, stop_sequence::INTEGER, NULL
        FROM read_csv_auto('{stop_times_path}', header=true)
    """)
    st_count = conn.execute("SELECT COUNT(*) FROM gtfs_stop_times").fetchone()[0]

    # Step 5: Map gtfs stop_id → city_stop_id using multiple strategies
    stops_path = GTFS_DIR / 'stops.txt'
    if stops_path.exists():
        # Load GTFS stops into temp table (stop_id, stop_code, name, lat, lon)
        conn.execute(f"""
            CREATE TEMP TABLE _gtfs_stops AS
            SELECT stop_id::VARCHAR AS gtfs_stop_id,
                   stop_code::VARCHAR AS stop_code,
                   stop_name AS name,
                   stop_lat::DOUBLE AS lat,
                   stop_lon::DOUBLE AS lon
            FROM read_csv_auto('{stops_path}', header=true)
        """)

        # Strategy A: exact code match (bgprevoz API ID)
        conn.execute("""
            CREATE TEMP TABLE _code_map AS
            SELECT code, id AS city_stop_id FROM city_stops WHERE code IS NOT NULL
        """)
        conn.execute("""
            UPDATE gtfs_stop_times SET city_stop_id = _code_map.city_stop_id
            FROM _gtfs_stops, _code_map
            WHERE gtfs_stop_times.stop_id = _gtfs_stops.gtfs_stop_id
              AND _gtfs_stops.stop_code = _code_map.code
        """)
        mapped_a = conn.execute("SELECT COUNT(*) FROM gtfs_stop_times WHERE city_stop_id IS NOT NULL").fetchone()[0]
        print(f"    Strategy A (exact code):  {mapped_a} rows mapped")

        # Strategy B: neighbor code ±1 (Belgrade paired stops: odd/even sides of street)
        # For unmapped stop_times, try code-1 and code+1
        conn.execute("""
            UPDATE gtfs_stop_times SET city_stop_id = _code_map.city_stop_id
            FROM _gtfs_stops, _code_map
            WHERE gtfs_stop_times.city_stop_id IS NULL
              AND gtfs_stop_times.stop_id = _gtfs_stops.gtfs_stop_id
              AND (CAST(_gtfs_stops.stop_code AS INTEGER) - 1)::VARCHAR = _code_map.code
        """)
        conn.execute("""
            UPDATE gtfs_stop_times SET city_stop_id = _code_map.city_stop_id
            FROM _gtfs_stops, _code_map
            WHERE gtfs_stop_times.city_stop_id IS NULL
              AND gtfs_stop_times.stop_id = _gtfs_stops.gtfs_stop_id
              AND (CAST(_gtfs_stops.stop_code AS INTEGER) + 1)::VARCHAR = _code_map.code
        """)
        mapped_b = conn.execute("SELECT COUNT(*) FROM gtfs_stop_times WHERE city_stop_id IS NOT NULL").fetchone()[0]
        print(f"    Strategy B (code ±1):     {mapped_b} rows mapped (+{mapped_b - mapped_a})")

        # Strategy C: nearest city_stop by coordinates (< 100m) for remaining unmapped
        # Build a mapping table for still-unmapped GTFS stop_ids
        conn.execute("""
            CREATE TEMP TABLE _unmapped_gtfs AS
            SELECT DISTINCT st.stop_id AS gtfs_stop_id, gs.lat, gs.lon
            FROM gtfs_stop_times st
            JOIN _gtfs_stops gs ON gs.gtfs_stop_id = st.stop_id
            WHERE st.city_stop_id IS NULL AND gs.lat IS NOT NULL
        """)
        # For each unmapped GTFS stop, find closest city_stop within ~100m
        # Using degree approximation: 0.001° ≈ 111m
        conn.execute("""
            CREATE TEMP TABLE _coord_map AS
            SELECT u.gtfs_stop_id,
                   (SELECT cs.id FROM city_stops cs
                    WHERE cs.lat IS NOT NULL
                      AND ABS(cs.lat - u.lat) < 0.002
                      AND ABS(cs.lon - u.lon) < 0.002
                    ORDER BY (cs.lat - u.lat)*(cs.lat - u.lat) + (cs.lon - u.lon)*(cs.lon - u.lon)
                    LIMIT 1) AS city_stop_id
            FROM _unmapped_gtfs u
        """)
        conn.execute("""
            UPDATE gtfs_stop_times SET city_stop_id = _coord_map.city_stop_id
            FROM _coord_map
            WHERE gtfs_stop_times.city_stop_id IS NULL
              AND gtfs_stop_times.stop_id = _coord_map.gtfs_stop_id
              AND _coord_map.city_stop_id IS NOT NULL
        """)
        mapped_c = conn.execute("SELECT COUNT(*) FROM gtfs_stop_times WHERE city_stop_id IS NOT NULL").fetchone()[0]
        print(f"    Strategy C (coords <200m): {mapped_c} rows mapped (+{mapped_c - mapped_b})")

        conn.execute("DROP TABLE IF EXISTS _coord_map")
        conn.execute("DROP TABLE IF EXISTS _unmapped_gtfs")
        conn.execute("DROP TABLE _gtfs_stops")
        conn.execute("DROP TABLE _code_map")

    mapped = conn.execute("SELECT COUNT(*) FROM gtfs_stop_times WHERE city_stop_id IS NOT NULL").fetchone()[0]
    unique_stops = conn.execute("SELECT COUNT(DISTINCT city_stop_id) FROM gtfs_stop_times WHERE city_stop_id IS NOT NULL").fetchone()[0]
    print(f"  Loaded {st_count} stop_times ({mapped} mapped [{mapped*100//st_count}%], {unique_stops} unique stops)")


def _load_city_schedule(conn: duckdb.DuckDBPyConnection, city: str) -> None:
    """Load scraped schedule data (departure times) into gtfs_trips + gtfs_stop_times."""
    schedule_path = RAW_DIR / city / 'schedule.json'
    if not schedule_path.exists():
        print(f"  No {city} schedule data, skipping")
        return

    with open(schedule_path, encoding='utf-8') as f:
        schedules = json.load(f)

    # Build line number → line_id mapping for this city
    line_map: dict[str, int] = {}
    for row in conn.execute(
        "SELECT id, number FROM city_lines WHERE city = ?", [city]
    ).fetchall():
        line_map[row[1]] = row[0]

    # Build line_id → ordered stop_ids for distributing stop_times
    line_stops: dict[int, list[int]] = {}
    for row in conn.execute("""
        SELECT cls.line_id, cls.stop_id
        FROM city_line_stops cls
        JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cl.city = ?
        ORDER BY cls.line_id, cls.stop_order
    """, [city]).fetchall():
        line_stops.setdefault(row[0], []).append(row[1])

    trip_count = 0
    st_count = 0

    for entry in schedules:
        line_number = entry['line_number']
        service_id = entry['service']  # RD, S, N
        line_id = line_map.get(line_number)
        if not line_id:
            continue

        stops = line_stops.get(line_id, [])

        for direction, times in [('A', entry.get('smer_a', [])), ('B', entry.get('smer_b', []))]:
            for ti, dep_time in enumerate(times):
                trip_id = f'{city}_{line_number}_{direction}_{service_id}_{ti}'
                route_id = f'{city}_{line_number}'

                conn.execute(
                    "INSERT INTO gtfs_trips VALUES (?, ?, ?, ?, ?)",
                    (trip_id, route_id, service_id, 0 if direction == 'A' else 1, line_id)
                )
                trip_count += 1

                # Distribute departure across stops with 2-min intervals
                if stops:
                    for seq, stop_id in enumerate(stops):
                        h, m = dep_time.split(':')
                        total_min = int(h) * 60 + int(m) + seq * 2
                        stop_h = total_min // 60
                        stop_m = total_min % 60
                        stop_time = f'{stop_h:02d}:{stop_m:02d}:00'

                        conn.execute(
                            "INSERT INTO gtfs_stop_times VALUES (?, ?, ?, ?, ?, ?)",
                            (trip_id, f'{city}_stop_{stop_id}', stop_time, stop_time, seq + 1, stop_id)
                        )
                        st_count += 1
                else:
                    # No stops mapped — at least record the departure
                    conn.execute(
                        "INSERT INTO gtfs_stop_times VALUES (?, ?, ?, ?, ?, ?)",
                        (trip_id, f'{city}_line_{line_number}', f'{dep_time}:00', f'{dep_time}:00', 1, None)
                    )
                    st_count += 1

    print(f"  Loaded {city} schedule: {trip_count} trips, {st_count} stop_times")


def _cleanup(conn: duckdb.DuckDBPyConnection) -> None:
    """Remove orphan routes, operators, and NULL-departure trips."""
    # Remove intercity routes with no trips
    r1 = conn.execute("""
        DELETE FROM routes
        WHERE type = 'intercity'
          AND id NOT IN (SELECT DISTINCT route_id FROM trips)
    """).fetchone()[0]

    # Remove duplicate routes (same from_city+to_city, keep the one with more trips)
    r2 = conn.execute("""
        DELETE FROM routes WHERE id IN (
            SELECT r.id FROM routes r
            JOIN (
                SELECT from_city, to_city, MAX(trip_cnt) AS max_cnt
                FROM (
                    SELECT r2.id, r2.from_city, r2.to_city, COUNT(t.id) AS trip_cnt
                    FROM routes r2 LEFT JOIN trips t ON t.route_id = r2.id
                    WHERE r2.type = 'intercity'
                    GROUP BY r2.id, r2.from_city, r2.to_city
                ) GROUP BY from_city, to_city HAVING COUNT(*) > 1
            ) dup ON r.from_city = dup.from_city AND r.to_city = dup.to_city
            LEFT JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity'
            GROUP BY r.id, dup.max_cnt
            HAVING COUNT(t.id) < dup.max_cnt
        )
    """).fetchone()[0]

    # Remove trips with NULL departure_time
    r3 = conn.execute("DELETE FROM trips WHERE departure_time IS NULL").fetchone()[0]

    # Remove operators without any trips
    r4 = conn.execute("""
        DELETE FROM operators
        WHERE id NOT IN (SELECT DISTINCT operator_id FROM trips WHERE operator_id IS NOT NULL)
    """).fetchone()[0]

    print(f"  Cleanup: -{r1} empty routes, -{r2} duplicate routes, -{r3} null trips, -{r4} orphan operators")


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

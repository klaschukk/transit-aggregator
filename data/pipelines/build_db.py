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
import os
import re
import sys
import time
from pathlib import Path

import duckdb
import contextlib

# Share the one true slug function with the request-time code path
# (app/slug.py). All pipelines must go through this — otherwise drift
# between transliteration maps leaks non-ASCII slugs into the DB.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from app.slug import normalize_slug, transliterate_cyrillic_serbian  # noqa: E402

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / 'raw'
GTFS_DIR = BASE_DIR / 'gtfs'
DB_PATH = BASE_DIR / 'dbs' / 'transit.duckdb'
TMP_PATH = DB_PATH.with_name('transit.duckdb.tmp')

# Official Belgrade GTFS feed (data.gov.rs). _load_gtfs() auto-fetches this when
# GTFS_DIR is empty so the schedule survives every rebuild — see _ensure_gtfs().
GTFS_URL = (
    'https://data.gov.rs/s/resources/gradski-javni-prevoz-u-beogradu-gtfs/'
    '20251031-111721/bgprev-belgrade-rs-2-.zip'
)

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
    """Backwards-compatible alias — single source of truth is app.slug."""
    return normalize_slug(city)


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

    # Clean up any leftover tmp file from a previously failed build.
    for leftover in (TMP_PATH, TMP_PATH.parent / (TMP_PATH.name + '.wal')):
        if leftover.exists():
            leftover.unlink()

    # Preserve line_geometries across rebuilds — the table is populated
    # by the standalone scrape_route_geometries.py script (Overpass /
    # OSM relations, ~30-60 min, ~600 lines). OSM relations change
    # rarely; refetching nightly wastes Overpass quota. Snapshot the
    # rows here so the new DB starts with the same polyline coverage.
    #
    # Apr 25 incident: previous build() did unconditional unlink() →
    # line_geometries wiped → line_detail polyline maps fell back to
    # straight-line-between-stops + 600× ERROR/render in error.log
    # before 9b8a7a4 added the try/except memoise. Root fix is here:
    # carry the rows over so the table never goes empty.
    preserved_geom: list = []
    if DB_PATH.exists():
        try:
            _old = duckdb.connect(str(DB_PATH), read_only=True)
            preserved_geom = _old.execute(
                "SELECT line_id, city, coords_json, way_count, "
                "       node_count, fetched_at "
                "FROM line_geometries"
            ).fetchall()
            _old.close()
            print(f"Snapshotted {len(preserved_geom)} line_geometries rows from old DB")
        except duckdb.Error:
            # First-ever rebuild, or table genuinely missing — fine,
            # the standalone scraper backfills on next run.
            preserved_geom = []

    # Write to a temp file so the live transit.duckdb stays intact and
    # gunicorn workers keep serving during the build (zero downtime).
    # os.replace() at the end is atomic on Linux: workers reconnect on
    # their next IOException instead of getting 502s for 2 minutes.
    conn = duckdb.connect(str(TMP_PATH))
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
    kragujevac_path = RAW_DIR / 'kragujevac' / 'lines.json'

    if has_real_data:
        print("Loading real scraped data...")
        _load_operators(conn)
        _load_intercity(conn, intercity_path, srbvoz_path)
        _load_gsp_lines(conn, gsp_path, gsp_stops_path)
        _load_city_lines(conn, 'novi-sad', novi_sad_path)
        _load_city_lines(conn, 'nis', nis_path)
        _load_city_lines(conn, 'kragujevac', kragujevac_path)
        _load_stations(conn, stations_path)
        _load_balkan(conn)
        _load_gtfs(conn)
        _load_city_schedule(conn, 'novi-sad')
        _cleanup(conn)
    else:
        print("No scraped data found — loading sample data...")
        _load_sample_data(conn)

    _verify_slug_invariant(conn)
    _restore_line_geometries(conn, preserved_geom)

    conn.close()
    # Remove WAL file (checkpointed on close, but clean up before rename).
    tmp_wal = TMP_PATH.parent / (TMP_PATH.name + '.wal')
    if tmp_wal.exists():
        tmp_wal.unlink()
    # Atomic replace: transit.duckdb.tmp → transit.duckdb.
    # Workers holding the old inode continue serving until their next
    # IOException triggers the reconnect in app/db.py.
    os.replace(TMP_PATH, DB_PATH)
    print(f"Built {DB_PATH} successfully")


def _restore_line_geometries(
    conn: duckdb.DuckDBPyConnection,
    preserved: list,
) -> None:
    """Recreate the line_geometries table with the rows snapshotted before
    the unlink. Drops dangling rows whose line_id no longer exists in the
    rebuilt city_lines (a line removed upstream shouldn't keep its old
    polyline).

    The standalone scrape_route_geometries.py creates the same schema with
    `CREATE TABLE IF NOT EXISTS`, so a first-time run with `preserved=[]`
    leaves the table absent here and the scraper builds it on next run.
    """
    if not preserved:
        return
    conn.execute(
        """
        CREATE TABLE line_geometries (
            line_id INTEGER PRIMARY KEY,
            city VARCHAR,
            coords_json VARCHAR,
            way_count INTEGER,
            node_count INTEGER,
            fetched_at TIMESTAMP
        )
        """
    )
    new_line_ids = {
        r[0] for r in conn.execute("SELECT id FROM city_lines").fetchall()
    }
    kept = [row for row in preserved if row[0] in new_line_ids]
    conn.executemany(
        "INSERT INTO line_geometries VALUES (?, ?, ?, ?, ?, ?)",
        kept,
    )
    print(
        f"Restored {len(kept)}/{len(preserved)} line_geometries rows "
        f"(dropped {len(preserved) - len(kept)} dangling)"
    )


def _verify_slug_invariant(conn: duckdb.DuckDBPyConnection) -> None:
    """Fail the build if any slug in public URL tables is non-ASCII.

    Non-ASCII slugs leak into sitemap.xml → Google indexes them → the URL
    later 404s when the DB is rebuilt with a different transliteration,
    costing crawl budget. Guard at the build boundary: each scraper may
    drift independently, but the DB must never ship mojibake.
    """
    checks = [
        ('city_stops', 'slug'),
        ('city_lines', 'slug'),
        ('routes', 'slug'),
        ('routes', 'from_city_slug'),
        ('routes', 'to_city_slug'),
    ]
    offenders: list[tuple[str, str, str]] = []
    for table, col in checks:
        rows = conn.execute(
            f"SELECT {col} FROM {table} WHERE {col} !~ '^[a-z0-9-]+$' LIMIT 5"
        ).fetchall()
        for (slug,) in rows:
            offenders.append((table, col, slug))
    if offenders:
        raise RuntimeError(
            "non-ASCII slugs detected — refusing to ship a DB that would "
            "produce broken sitemap URLs:\n  " + "\n  ".join(
                f"{t}.{c} = {s!r}" for t, c, s in offenders
            )
        )
    print("slug invariant: all URL slugs are ASCII ✓")


# HH:MM, 00:00–23:59. Scrapers all emit this (they slice times to [:5]); a row
# that doesn't is a format regression, not real data.
_TIME_RE = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')


def _validate_intercity_trip(trip: dict) -> str:
    """Return '' if a scraped intercity trip is usable, else a short drop reason.

    build_db merges four feeds (busticket4, srbvoz, polazak, international). A
    single malformed row used to either crash the NOT NULL trips insert (a
    missing departure_time key) or silently plant an unusable value (empty /
    '25:99' time, negative price). Validating up front and tallying the reasons
    turns a scraper-format regression into a visible build-log line instead of
    a corrupt or short DB. price_rsd == 0 is allowed — it's the existing
    "price unknown" convention (~40% of trips), not a broken row.
    """
    if not trip.get('from_city') or not trip.get('to_city'):
        return 'missing_city'
    if not _TIME_RE.match(str(trip.get('departure_time') or '').strip()):
        return 'bad_departure_time'
    if not _TIME_RE.match(str(trip.get('arrival_time') or '').strip()):
        return 'bad_arrival_time'
    try:
        if int(trip.get('price_rsd') or 0) < 0:
            return 'negative_price'
    except (TypeError, ValueError):
        return 'bad_price'
    return ''


_DEFAULT_DAYS = '1234567'  # runs every day — the placeholder mask (see below)


def _normalize_days_of_week(raw) -> str:
    """Coerce a source-provided days-of-week mask to the canonical form.

    The mask is a string of distinct weekday digits 1–7 (1=Mon … 7=Sun),
    sorted, e.g. '12345' for weekdays-only or '67' for weekends.

    DATA GAP: as of 2026-06 no scraper populates this. busticket4's bus-search
    API returns per-date departures (departure/arrival time, duration) with no
    weekly recurrence field, and we scrape one representative weekday — so we
    have no honest way to know which days a given trip actually runs. Until a
    source provides it, every trip falls back to '1234567' (runs every day),
    which means the route_detail day filter shows all trips on any day and must
    be treated as informational, not authoritative.

    This helper is the forward-compatible seam: the moment a scraper emits a
    real mask on a trip, build_db persists it instead of the placeholder — no
    further schema or insert change needed. Garbage in (non-1–7 chars, empties)
    collapses safely to the default rather than shipping a broken mask.
    """
    if not raw:
        return _DEFAULT_DAYS
    digits = ''.join(sorted({c for c in str(raw) if c in '1234567'}))
    return digits or _DEFAULT_DAYS


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
            -- PLACEHOLDER: no source exposes a weekly recurrence pattern and we
            -- scrape a single representative weekday, so every trip currently
            -- carries the '1234567' (runs-every-day) default. The route_detail
            -- day filter is therefore informational-only. See
            -- _normalize_days_of_week() — build_db already persists a real mask
            -- the day a scraper starts providing one.
            days_of_week VARCHAR DEFAULT '1234567',
            is_active BOOLEAN DEFAULT true,
            bt4_line_id INTEGER          -- busticket4 line id for affiliate checkout (NULL if unknown)
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

    # Source 4: international routes (busticket4.me international)
    intl_path = RAW_DIR / 'international_routes.json'
    if intl_path.exists():
        with open(intl_path, encoding='utf-8') as f:
            intl_trips = json.load(f)
        for t in intl_trips:
            t['_source'] = 'intl'
        all_trips.extend(intl_trips)
        print(f"  International trips: {len(intl_trips)}")

    if not all_trips:
        return

    # Validate every row up front; drop and tally the broken ones so a scraper
    # format regression shows up in the build log instead of corrupting the DB.
    valid_trips: list[dict] = []
    dropped: dict[str, int] = {}
    for trip in all_trips:
        reason = _validate_intercity_trip(trip)
        if reason:
            dropped[reason] = dropped.get(reason, 0) + 1
            continue
        valid_trips.append(trip)
    if dropped:
        summary = ', '.join(f'{k}={v}' for k, v in sorted(dropped.items()))
        print(f"  Dropped {sum(dropped.values())} invalid trips ({summary})")

    # Deduplicate: same from_city + to_city + departure_time + TYPE → keep first.
    # type matters: without it a bus and a train leaving the same city pair at
    # the same minute collapse to one row (the first feed — busticket4 bus —
    # wins, the train is silently lost). Keeping type distinct recovers those.
    seen: set[tuple[str, str, str, str]] = set()
    unique_trips: list[dict] = []
    dupes = 0
    for trip in valid_trips:
        key = (trip['from_city'], trip['to_city'],
               trip['departure_time'], trip.get('type', 'bus'))
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

        bt4_line_id = trip.get('bt4_line_id')
        conn.execute(
            "INSERT INTO trips (id, route_id, operator_id, departure_time, "
            "arrival_time, duration_min, price_rsd, days_of_week, is_active, "
            "bt4_line_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trip_id, route_id_val, op_id,
             trip['departure_time'], trip['arrival_time'],
             trip.get('duration_min', 0), price,
             _normalize_days_of_week(trip.get('days_of_week')), True,
             int(bt4_line_id) if bt4_line_id else None)
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
                    with contextlib.suppress(Exception):
                        conn.execute(
                            "INSERT OR IGNORE INTO city_line_stops VALUES (?, ?, ?)",
                            (line_db_id, db_stop_id, order)
                        )

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

    # Load pre-geocoded stop coordinates if available
    coords_path = lines_path.parent / 'stop_coords.json'
    stop_coords: dict[str, dict] = {}
    if coords_path.exists():
        with open(coords_path, encoding='utf-8') as f:
            stop_coords = json.load(f)

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

            # Enrich from pre-geocoded coords
            if lat is None and stop_name in stop_coords:
                lat = stop_coords[stop_name].get('lat')
                lon = stop_coords[stop_name].get('lon')

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

    # Also load standalone stops (e.g. from Overpass bus_stop nodes)
    standalone_path = lines_path.parent / 'stops.json'
    extra_stops = 0
    if standalone_path.exists():
        with open(standalone_path, encoding='utf-8') as f:
            standalone = json.load(f)
        for s in standalone:
            sname = s.get('name', '')
            if not sname:
                continue
            sslug = city_to_slug(sname)
            skey = f"{city}:{sslug}"
            if skey not in stop_name_to_id:
                try:
                    conn.execute(
                        "INSERT OR IGNORE INTO city_stops (id, city, name, slug, lat, lon) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (stop_db_id, city, sname, sslug, s.get('lat'), s.get('lon'))
                    )
                    stop_name_to_id[skey] = stop_db_id
                    stop_db_id += 1
                    extra_stops += 1
                except Exception:
                    pass

    print(f"  Loaded {count} {city} lines, {stop_count}+{extra_stops} stops, {link_count} line-stop links")


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


def _ensure_gtfs() -> None:
    """Fetch the Belgrade GTFS feed into GTFS_DIR when it is missing.

    Root cause of the "every line shows 4 min" bug: the nightly rebuild runs
    build_db.py with an empty data/gtfs/, so _load_gtfs() printed "No GTFS data
    found, skipping" and each rebuild silently wiped the Belgrade schedule —
    leaving stop pages with no real arrivals (only the fabricated headway
    fallback, since removed). Auto-downloading here makes the schedule survive
    rebuilds. Non-fatal by design: any failure keeps existing files (or skips
    GTFS) so a flaky network never breaks the DB build.
    """
    if (GTFS_DIR / 'trips.txt').exists() and (GTFS_DIR / 'stop_times.txt').exists():
        return
    try:
        import io
        import urllib.request
        import zipfile

        GTFS_DIR.mkdir(parents=True, exist_ok=True)
        print("  GTFS files missing — downloading feed from data.gov.rs ...")
        req = urllib.request.Request(
            GTFS_URL, headers={'User-Agent': 'Mozilla/5.0 Transit-Serbia-Bot/1.0'})
        with urllib.request.urlopen(req, timeout=180) as resp:
            blob = resp.read()
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            zf.extractall(GTFS_DIR)
        print(f"  Downloaded + extracted GTFS ({len(blob) // 1024 // 1024} MB)")
    except Exception as exc:  # pragma: no cover - network-dependent
        print(f"  WARN: GTFS download failed ({exc}); proceeding without fresh GTFS")


# Coverage below these floors means the feed or the matching logic regressed —
# the build still ships (stale schedule beats none) but the warning is loud.
_GTFS_MIN_STOP_TIMES_PCT = 85   # % of stop_times linked to a city_stop
_GTFS_MIN_ROUTES_MATCHED = 200  # route_short_name → city_line matches
_GTFS_MAX_FEED_AGE_DAYS = 45    # data.gov.rs publishes a dated feed; stale → warn

GTFS_COVERAGE_FILE = RAW_DIR / 'gtfs_coverage.json'


def _build_line_resolver(line_rows):
    """Build a GTFS route_short_name → city_line_id resolver.

    GTFS route_short_name is Latin ("27N", "102P") while city_lines.number is
    often Cyrillic ("27Н", "102п"). Resolve in priority order:
      1. exact raw match (number as stored),
      2. exact transliterated match (Cyrillic→Latin),
      3. case-insensitive transliterated match, but ONLY when that upper-cased
         key maps to a single line — ambiguous keys are skipped so a route is
         never linked to the wrong line.
    `line_rows` is an iterable of (city_line_id, number). Returns resolve(short).
    """
    line_map: dict[str, int] = {}
    translit_map: dict[str, int] = {}
    ci_map: dict[str, int] = {}
    ci_ambiguous: set[str] = set()
    for lid, number in line_rows:
        line_map[number] = lid
        tl = transliterate_cyrillic_serbian(number)
        translit_map.setdefault(tl, lid)
        up = tl.upper()
        if up in ci_map and ci_map[up] != lid:
            ci_ambiguous.add(up)
        else:
            ci_map.setdefault(up, lid)

    def resolve(short: str) -> int | None:
        if short in line_map:
            return line_map[short]
        if short in translit_map:
            return translit_map[short]
        up = short.upper()
        if up not in ci_ambiguous:
            return ci_map.get(up)
        return None

    return resolve


def _gtfs_coverage_warnings(stop_times_pct: int, routes_matched: int,
                            feed_age_days: float | None) -> list[str]:
    """Flag GTFS coverage/freshness anomalies (pure — easy to test).

    A sudden drop in mapped-stop_times %, in matched routes, or a feed that
    stopped refreshing all mean the schedule users see is silently degrading.
    """
    warnings: list[str] = []
    if stop_times_pct < _GTFS_MIN_STOP_TIMES_PCT:
        warnings.append(
            f"stop_times coverage {stop_times_pct}% < {_GTFS_MIN_STOP_TIMES_PCT}% floor")
    if routes_matched < _GTFS_MIN_ROUTES_MATCHED:
        warnings.append(
            f"only {routes_matched} routes matched < {_GTFS_MIN_ROUTES_MATCHED} floor")
    if feed_age_days is not None and feed_age_days > _GTFS_MAX_FEED_AGE_DAYS:
        warnings.append(
            f"GTFS feed is {feed_age_days:.0f} days old "
            f"(> {_GTFS_MAX_FEED_AGE_DAYS}d) — refresh may have stalled")
    return warnings


def _load_gtfs(conn: duckdb.DuckDBPyConnection) -> None:
    """Load GTFS schedule data (trips + stop_times) using bulk DuckDB import."""
    _ensure_gtfs()
    trips_path = GTFS_DIR / 'trips.txt'
    stop_times_path = GTFS_DIR / 'stop_times.txt'
    routes_path = GTFS_DIR / 'routes.txt'

    if not trips_path.exists() or not stop_times_path.exists():
        print("  No GTFS data found, skipping")
        return

    # Step 1: Build route_id → line_id mapping via routes.txt route_short_name.
    # city_lines.number is often Cyrillic ("27Н" night, "102п") while the GTFS feed
    # is Latin ("27N", "102P"); transliterate so they link. Resolve in priority order:
    # exact raw → exact transliterated → case-insensitive transliterated (only when
    # unambiguous). Recovers ~33 Belgrade lines / ~4k trips that exact-match drops.
    route_to_line: dict[str, int] = {}
    if routes_path.exists():
        line_rows = conn.execute(
            "SELECT id, number FROM city_lines WHERE city = 'beograd'").fetchall()
        resolve_line = _build_line_resolver(line_rows)

        import csv
        with open(routes_path, encoding='utf-8') as f:
            for row in csv.DictReader(f):
                line_id = resolve_line(row.get('route_short_name', '') or '')
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
    with contextlib.suppress(Exception):
        conn.execute("CHECKPOINT")
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

    _report_gtfs_coverage(conn, trip_count, linked, len(route_to_line),
                          st_count, mapped, unique_stops, stop_times_path)


def _report_gtfs_coverage(conn, trip_count, linked, routes_matched,
                          st_count, mapped, unique_stops, stop_times_path) -> None:
    """Persist a GTFS coverage/freshness snapshot + warn on anomalies.

    The mapping percentages were only ever printed and lost. This writes them to
    GTFS_COVERAGE_FILE so a monitor/data_snapshot can read freshness without a
    rebuild, samples WHICH stops fail to map (the unmapped ~6% — usually GTFS
    stops we carry no city_stop for, or coordinate gaps beyond the 200m match),
    and prints loud warnings if coverage or feed age regress.
    """
    st_pct = mapped * 100 // st_count if st_count else 0

    # The unmapped tail: distinct GTFS stop_ids with no city_stop link. Sampling
    # names tells you what the 6% actually are instead of just a percentage.
    unmapped_total = conn.execute(
        "SELECT COUNT(DISTINCT stop_id) FROM gtfs_stop_times "
        "WHERE city_stop_id IS NULL").fetchone()[0]
    unmapped_sample = [r[0] for r in conn.execute(
        "SELECT DISTINCT stop_id FROM gtfs_stop_times "
        "WHERE city_stop_id IS NULL ORDER BY stop_id LIMIT 20").fetchall()]

    feed_age_days = None
    if stop_times_path.exists():
        feed_age_days = (time.time() - os.path.getmtime(stop_times_path)) / 86400

    coverage = {
        'gtfs_trips': trip_count,
        'gtfs_trips_linked': linked,
        'routes_matched': routes_matched,
        'stop_times': st_count,
        'stop_times_mapped': mapped,
        'stop_times_mapped_pct': st_pct,
        'unique_city_stops': unique_stops,
        'unmapped_gtfs_stops': unmapped_total,
        'unmapped_sample': unmapped_sample,
        'feed_age_days': round(feed_age_days, 1) if feed_age_days is not None else None,
    }
    try:
        GTFS_COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(GTFS_COVERAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(coverage, f, ensure_ascii=False, indent=2)
        print(f"  GTFS coverage snapshot → {GTFS_COVERAGE_FILE.name} "
              f"({unmapped_total} GTFS stops unmapped)")
    except OSError as exc:  # pragma: no cover - disk-dependent
        print(f"  WARN: could not write GTFS coverage snapshot: {exc}")

    for w in _gtfs_coverage_warnings(st_pct, routes_matched, feed_age_days):
        print(f"  WARN: GTFS — {w}")


def _load_balkan(conn: duckdb.DuckDBPyConnection) -> None:
    """Load international Balkan routes from balkan_routes.json."""
    balkan_path = RAW_DIR / 'balkan_routes.json'
    if not balkan_path.exists():
        print("  No Balkan routes data, skipping")
        return

    with open(balkan_path, encoding='utf-8') as f:
        routes = json.load(f)

    max_route_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM routes").fetchone()[0]
    route_id = max_route_id + 1

    existing_slugs = set(r[0] for r in conn.execute("SELECT slug FROM routes").fetchall())
    count = 0

    for route in routes:
        slug = route['slug']
        if slug in existing_slugs:
            continue
        try:
            conn.execute(
                "INSERT INTO routes (id, slug, from_city, to_city, from_city_slug, to_city_slug, distance_km, type) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (route_id, slug, route['from_city'], route['to_city'],
                 route['from_city_slug'], route['to_city_slug'],
                 route.get('distance_km', 0), 'intercity')
            )
            existing_slugs.add(slug)
            route_id += 1
            count += 1
        except Exception:
            pass

    print(f"  Loaded {count} international Balkan routes")


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
    # Remove domestic routes with no trips (keep international/balkan)
    balkan_path = RAW_DIR / 'balkan_routes.json'
    balkan_slugs = set()
    if balkan_path.exists():
        import json as _json
        with open(balkan_path) as _f:
            balkan_slugs = {r['slug'] for r in _json.load(_f)}
    r1 = conn.execute("""
        DELETE FROM routes
        WHERE type = 'intercity'
          AND id NOT IN (SELECT DISTINCT route_id FROM trips)
          AND slug NOT IN (SELECT unnest(?::VARCHAR[]))
    """, [list(balkan_slugs)]).fetchone()[0]

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
    conn.executemany(
        "INSERT INTO trips (id, route_id, operator_id, departure_time, "
        "arrival_time, duration_min, price_rsd, days_of_week, is_active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
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

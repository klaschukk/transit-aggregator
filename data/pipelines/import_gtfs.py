"""
Import Belgrade GTFS into transit.duckdb.

Downloads from data.gov.rs and loads:
  - stops → city_stops (replaces scraped data)
  - routes → city_lines (replaces scraped data)
  - trips, stop_times, calendar → new GTFS tables for schedule lookup

Usage:
    python data/pipelines/import_gtfs.py [--gtfs-dir /tmp/gtfs]
"""
import argparse
import logging
import re
import zipfile
from pathlib import Path

import duckdb
import requests

GTFS_URL = (
    'https://data.gov.rs/s/resources/gradski-javni-prevoz-u-beogradu-gtfs/'
    '20251031-111721/bgprev-belgrade-rs-2-.zip'
)
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'dbs' / 'transit.duckdb'

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)

ROUTE_TYPE_MAP = {
    0: 'tram',
    1: 'metro',
    3: 'bus',
    11: 'trolleybus',
    800: 'trolleybus',
    900: 'tram',
}

LINE_COLORS = {
    'bus': '#0d9488',
    'tram': '#e53e3e',
    'trolleybus': '#d69e2e',
    'metro': '#2b2d87',
}


def slug(text: str) -> str:
    cyrillic = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','ђ':'dj','е':'e','ж':'z',
        'з':'z','и':'i','ј':'j','к':'k','л':'l','љ':'lj','м':'m','н':'n',
        'њ':'nj','о':'o','п':'p','р':'r','с':'s','т':'t','ћ':'c','у':'u',
        'ф':'f','х':'h','ц':'c','ч':'c','џ':'dz','ш':'s',
    }
    result = ''
    for ch in text.lower():
        result += cyrillic.get(ch, ch)
    return re.sub(r'[^a-z0-9]+', '-', result).strip('-')


def download_gtfs(dest_zip: Path) -> None:
    log.info(f'Downloading GTFS from data.gov.rs...')
    headers = {'User-Agent': 'Mozilla/5.0 Transit-Serbia-Bot/1.0'}
    r = requests.get(GTFS_URL, headers=headers, timeout=120, stream=True)
    r.raise_for_status()
    with open(dest_zip, 'wb') as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    log.info(f'Downloaded {dest_zip.stat().st_size // 1024 // 1024} MB')


def extract_gtfs(zip_path: Path, dest_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest_dir)
    log.info(f'Extracted to {dest_dir}')


def import_into_db(gtfs_dir: Path) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))

    _clear_city_tables(conn)
    _import_stops(conn, gtfs_dir / 'stops.txt')
    _import_routes(conn, gtfs_dir / 'routes.txt')
    _import_gtfs_tables(conn, gtfs_dir)

    conn.close()
    log.info('GTFS import complete')


def _clear_city_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Drop GTFS-specific tables and clear city_lines/city_stops."""
    for tbl in ('gtfs_stop_times', 'gtfs_trips', 'gtfs_calendar_dates', 'gtfs_calendar'):
        conn.execute(f"DROP TABLE IF EXISTS {tbl}")
    conn.execute("DELETE FROM city_line_stops")
    conn.execute("DELETE FROM city_lines")
    conn.execute("DELETE FROM city_stops")
    log.info('Cleared existing city tables')


def _import_stops(conn: duckdb.DuckDBPyConnection, stops_file: Path) -> None:
    rows = conn.execute(f"""
        SELECT stop_id, stop_code, stop_name, stop_lat, stop_lon
        FROM read_csv_auto('{stops_file}', header=true)
        WHERE location_type = 0 OR location_type IS NULL
    """).fetchall()

    inserted = 0
    seen_slugs: dict[str, int] = {}
    for db_id, (stop_id, stop_code, stop_name, lat, lon) in enumerate(rows, start=1):
        s = slug(stop_name)
        # Deduplicate by slug — keep first occurrence
        if s in seen_slugs:
            continue
        seen_slugs[s] = db_id
        conn.execute(
            "INSERT OR IGNORE INTO city_stops (id, city, name, slug, lat, lon, code) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (db_id, 'beograd', stop_name, s, float(lat) if lat else None, float(lon) if lon else None, str(stop_id))
        )
        inserted += 1

    log.info(f'Imported {inserted} stops')


def _import_routes(conn: duckdb.DuckDBPyConnection, routes_file: Path) -> None:
    rows = conn.execute(f"""
        SELECT route_id, route_short_name, route_long_name, route_type,
               route_color, route_sort_order
        FROM read_csv_auto('{routes_file}', header=true)
    """).fetchall()

    inserted = 0
    seen: set[str] = set()
    for db_id, (route_id, short_name, long_name, route_type, color, sort_order) in enumerate(rows, start=1):
        number = str(short_name or '')
        name = str(long_name or '')
        line_type = ROUTE_TYPE_MAP.get(int(route_type or 3), 'bus')
        line_slug = f'linija-{slug(number)}' if number else f'linija-{db_id}'
        if line_slug in seen:
            continue
        seen.add(line_slug)
        hex_color = f'#{color}' if color and not str(color).startswith('#') else (color or LINE_COLORS[line_type])
        conn.execute(
            "INSERT OR IGNORE INTO city_lines (id, city, number, name, slug, color, code) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (db_id, 'beograd', number, name, line_slug, hex_color, str(route_id))
        )
        inserted += 1

    log.info(f'Imported {inserted} routes (lines)')


def _import_gtfs_tables(conn: duckdb.DuckDBPyConnection, gtfs_dir: Path) -> None:
    """Create full GTFS schedule tables: calendar, trips, stop_times."""

    conn.execute("""
        CREATE TABLE gtfs_calendar (
            service_id VARCHAR PRIMARY KEY,
            monday BOOLEAN,
            tuesday BOOLEAN,
            wednesday BOOLEAN,
            thursday BOOLEAN,
            friday BOOLEAN,
            saturday BOOLEAN,
            sunday BOOLEAN
        )
    """)
    conn.execute(f"""
        INSERT INTO gtfs_calendar
        SELECT service_id,
               monday::BOOLEAN, tuesday::BOOLEAN,
               wednesday::BOOLEAN, thursday::BOOLEAN,
               friday::BOOLEAN, saturday::BOOLEAN, sunday::BOOLEAN
        FROM read_csv_auto('{gtfs_dir}/calendar.txt', header=true)
    """)

    conn.execute("""
        CREATE TABLE gtfs_calendar_dates (
            service_id VARCHAR,
            date VARCHAR,
            exception_type INTEGER
        )
    """)
    conn.execute(f"""
        INSERT INTO gtfs_calendar_dates
        SELECT service_id, date::VARCHAR, exception_type::INTEGER
        FROM read_csv_auto('{gtfs_dir}/calendar_dates.txt', header=true)
    """)

    conn.execute("""
        CREATE TABLE gtfs_trips (
            trip_id VARCHAR PRIMARY KEY,
            route_id VARCHAR NOT NULL,
            service_id VARCHAR NOT NULL,
            direction_id INTEGER,
            trip_headsign VARCHAR
        )
    """)
    conn.execute(f"""
        INSERT INTO gtfs_trips
        SELECT trip_id, route_id, service_id,
               direction_id::INTEGER, trip_headsign
        FROM read_csv_auto('{gtfs_dir}/trips.txt', header=true)
    """)
    trip_count = conn.execute("SELECT COUNT(*) FROM gtfs_trips").fetchone()[0]
    log.info(f'Imported {trip_count} trips')

    conn.execute("""
        CREATE TABLE gtfs_stop_times (
            trip_id VARCHAR NOT NULL,
            arrival_time VARCHAR NOT NULL,
            departure_time VARCHAR NOT NULL,
            stop_id VARCHAR NOT NULL,
            stop_sequence INTEGER NOT NULL
        )
    """)
    conn.execute(f"""
        INSERT INTO gtfs_stop_times
        SELECT trip_id, arrival_time, departure_time,
               stop_id::VARCHAR, stop_sequence::INTEGER
        FROM read_csv_auto('{gtfs_dir}/stop_times.txt', header=true)
    """)
    st_count = conn.execute("SELECT COUNT(*) FROM gtfs_stop_times").fetchone()[0]
    log.info(f'Imported {st_count} stop_times')

    # Index for fast stop lookups
    conn.execute("CREATE INDEX idx_gtfs_stop_times_stop ON gtfs_stop_times (stop_id)")
    conn.execute("CREATE INDEX idx_gtfs_stop_times_trip ON gtfs_stop_times (trip_id)")
    conn.execute("CREATE INDEX idx_gtfs_trips_route ON gtfs_trips (route_id)")
    log.info('Indexes created')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--gtfs-dir', default='/tmp/gtfs',
                        help='Directory with extracted GTFS txt files')
    parser.add_argument('--download', action='store_true',
                        help='Download and extract GTFS before import')
    args = parser.parse_args()

    gtfs_dir = Path(args.gtfs_dir)

    if args.download or not gtfs_dir.exists() or not (gtfs_dir / 'stops.txt').exists():
        zip_path = Path('/tmp/bgprevoz-gtfs.zip')
        download_gtfs(zip_path)
        gtfs_dir.mkdir(parents=True, exist_ok=True)
        extract_gtfs(zip_path, gtfs_dir)

    import_into_db(gtfs_dir)


if __name__ == '__main__':
    main()

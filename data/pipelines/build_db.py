"""
Build transit.duckdb from raw scraped data.
Run: python data/pipelines/build_db.py
"""
import json
import os
from pathlib import Path

import duckdb

BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / 'raw'
DB_PATH = BASE_DIR / 'dbs' / 'transit.duckdb'


def build():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove old DB and rebuild from scratch
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = duckdb.connect(str(DB_PATH))
    _create_schema(conn)
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
            departure_time VARCHAR NOT NULL,   -- HH:MM
            arrival_time VARCHAR NOT NULL,     -- HH:MM
            duration_min INTEGER,
            price_rsd INTEGER,
            days_of_week VARCHAR DEFAULT '1234567',  -- 1=Mon
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
            color VARCHAR DEFAULT '#2563eb',
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

    # Indexes for common queries
    conn.execute("CREATE INDEX idx_routes_slugs ON routes (from_city_slug, to_city_slug)")
    conn.execute("CREATE INDEX idx_trips_route ON trips (route_id)")
    conn.execute("CREATE INDEX idx_city_lines_city ON city_lines (city)")
    conn.execute("CREATE INDEX idx_city_stops_city ON city_stops (city)")

    print("Schema created")


def _load_sample_data(conn: duckdb.DuckDBPyConnection) -> None:
    """Load sample data so the app works before scrapers are ready."""

    # Operators
    conn.execute("INSERT INTO operators VALUES (1, 'Lasta', 'lasta', 'https://www.lasta.rs', 'bus')")
    conn.execute("INSERT INTO operators VALUES (2, 'Niš-Ekspres', 'nis-ekspres', 'https://www.nis-ekspres.rs', 'bus')")
    conn.execute("INSERT INTO operators VALUES (3, 'Srbija Voz', 'srbija-voz', 'https://www.srbvoz.rs', 'train')")

    # Inter-city routes
    routes = [
        (1, 'beograd-novi-sad', 'Beograd', 'Novi Sad', 'beograd', 'novi-sad', 90, 'intercity'),
        (2, 'beograd-nis', 'Beograd', 'Niš', 'beograd', 'nis', 250, 'intercity'),
        (3, 'beograd-kragujevac', 'Beograd', 'Kragujevac', 'beograd', 'kragujevac', 140, 'intercity'),
        (4, 'beograd-subotica', 'Beograd', 'Subotica', 'beograd', 'subotica', 180, 'intercity'),
        (5, 'novi-sad-nis', 'Novi Sad', 'Niš', 'novi-sad', 'nis', 320, 'intercity'),
        (6, 'beograd-cacak', 'Beograd', 'Čačak', 'beograd', 'cacak', 160, 'intercity'),
        (7, 'beograd-valjevo', 'Beograd', 'Valjevo', 'beograd', 'valjevo', 100, 'intercity'),
        (8, 'beograd-sabac', 'Beograd', 'Šabac', 'beograd', 'sabac', 90, 'intercity'),
    ]
    conn.executemany(
        "INSERT INTO routes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", routes
    )

    # Sample trips
    trips = [
        (1, 1, 1, '06:00', '07:30', 90, 800, '1234567', True),
        (2, 1, 1, '07:00', '08:30', 90, 800, '1234567', True),
        (3, 1, 1, '08:30', '10:00', 90, 900, '1234567', True),
        (4, 1, 2, '09:00', '10:30', 90, 750, '1234567', True),
        (5, 1, 1, '12:00', '13:30', 90, 800, '1234567', True),
        (6, 2, 1, '07:00', '10:00', 180, 1800, '1234567', True),
        (7, 2, 1, '09:00', '12:00', 180, 1800, '1234567', True),
        (8, 2, 2, '11:00', '14:00', 180, 1600, '1234567', True),
        (9, 2, 3, '07:30', '11:00', 210, 1400, '1234567', True),
        (10, 3, 1, '06:30', '08:30', 120, 950, '1234567', True),
    ]
    conn.executemany(
        "INSERT INTO trips VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", trips
    )

    # Belgrade city lines (GSP sample)
    city_lines = [
        (1, 'beograd', '11', 'Zemun — Zeleni Venac', 'linija-11', '#e53e3e'),
        (2, 'beograd', '25', 'Bežanija — Studentski trg', 'linija-25', '#38a169'),
        (3, 'beograd', '31', 'Mirijevo — Zeleni Venac', 'linija-31', '#3182ce'),
        (4, 'beograd', '94', 'Batajnica — Zeleni Venac', 'linija-94', '#d69e2e'),
    ]
    conn.executemany(
        "INSERT INTO city_lines VALUES (?, ?, ?, ?, ?, ?)", city_lines
    )

    print("Sample data loaded")


if __name__ == '__main__':
    build()

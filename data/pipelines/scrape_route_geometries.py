"""Scrape OSM route relations to get road-following polylines for each bus line.

Currently the line_detail minimap draws straight polylines between stops which
zig-zags across roads. This fetches actual route relations from OpenStreetMap
Overpass and stores their geometry so the map shows real road paths.

OSM bus lines are tagged as:
    relation[type=route][route=bus][ref=<line_number>][network=<operator>]

The relation has member ways (roads) that together form the driven path.
We concatenate way geometries in order, dedupe endpoints, store as JSON
[[lat,lon],...] in a new ``line_geometries`` table.

Run:
    venv/bin/python3 data/pipelines/scrape_route_geometries.py
    venv/bin/python3 data/pipelines/scrape_route_geometries.py beograd
    venv/bin/python3 data/pipelines/scrape_route_geometries.py novi-sad nis

Cron: add to nightly_refresh.sh (runs ~30-60 min for all cities).
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path

import duckdb
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("route_geometries")

PROJECT = Path(__file__).resolve().parent.parent.parent
DB = PROJECT / "data" / "dbs" / "transit.duckdb"
# Ordered by observed latency (kumi + private.coffee ~0.5-1s, overpass-api.de 2-5s).
# No .ru mirror (SSL cert issues + slow).
OVERPASS_ENDPOINTS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

# Supported cities with their network tags + bounding boxes
# Format: city_slug -> {"network": overpass network filter, "bbox": (south, west, north, east)}
CITIES = {
    "beograd": {
        "network": ["GSP Beograd", "Beograd"],
        "bbox": (44.65, 20.20, 44.95, 20.65),
    },
    "novi-sad": {
        "network": ["JGSP Novi Sad", "Novi Sad"],
        "bbox": (45.18, 19.72, 45.32, 19.92),
    },
    "nis": {
        "network": ["JKP Naissus", "Nis", "Niš"],
        "bbox": (43.28, 21.82, 43.38, 21.98),
    },
    "kragujevac": {
        "network": ["Kragujevac"],
        "bbox": (44.00, 20.84, 44.08, 20.98),
    },
}

PAUSE_BETWEEN_CITIES = 3.0
PAUSE_BETWEEN_LINES = 0.8  # be kind to Overpass
REQUEST_TIMEOUT = 25


def ensure_table(conn: duckdb.DuckDBPyConnection) -> None:
    """Create line_geometries table if missing."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS line_geometries (
            line_id INTEGER PRIMARY KEY,
            city VARCHAR,
            coords_json VARCHAR,
            way_count INTEGER,
            node_count INTEGER,
            fetched_at TIMESTAMP
        )
        """
    )


def _overpass_fetch(query: str) -> dict | None:
    """POST a query to Overpass, try mirrors on failure. Returns parsed JSON or None."""
    last_err = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            resp = requests.post(endpoint, data={"data": query}, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (429, 504, 503):
                last_err = f"{endpoint}: HTTP {resp.status_code}"
                log.debug("  %s returned %s", endpoint.split("/")[2], resp.status_code)
                time.sleep(2)
                continue
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            last_err = f"{endpoint}: {exc}"
            log.debug("  %s failed: %s", endpoint.split("/")[2], exc)
            time.sleep(2)
    log.warning("all Overpass endpoints failed — last: %s", last_err)
    return None


def fetch_relations_for_line(city: str, cfg: dict, ref: str) -> list[dict]:
    """Fetch OSM route=bus relations for a single line number within city bbox."""
    south, west, north, east = cfg["bbox"]
    # Escape ref for OSM tag (it's user input from DB; keep it simple, ASCII-safe)
    ref_esc = ref.replace('"', '').replace('\\', '')
    # `out body;` emits the relation with its member list. `>;` recurses to the
    # member ways, then `out geom;` attaches lat/lon geometry to each way.
    # (Using `out tags;` was the bug — members=[] and we'd see 0 coords.)
    query = (
        f"[out:json][timeout:30];\n"
        f'relation[type=route][route=bus]["ref"="{ref_esc}"]({south},{west},{north},{east});\n'
        f"out body;\n"
        f">;\n"
        f"out geom;\n"
    )
    data = _overpass_fetch(query)
    if data is None:
        return []
    elements = data.get("elements", [])

    # Separate relations and ways
    relations = [e for e in elements if e.get("type") == "relation"]
    ways_by_id = {e["id"]: e for e in elements if e.get("type") == "way"}

    out: list[dict] = []
    for rel in relations:
        tags = rel.get("tags") or {}
        rel_ref = (tags.get("ref") or "").strip()
        if not rel_ref:
            continue

        # Collect way geometries IN ORDER (relation members preserve direction)
        coords: list[list[float]] = []
        way_count = 0
        for mem in rel.get("members", []):
            if mem.get("type") != "way":
                continue
            way = ways_by_id.get(mem.get("ref"))
            if not way:
                continue
            geom = way.get("geometry") or []
            if not geom:
                continue
            segment = [[p["lat"], p["lon"]] for p in geom]
            if not segment:
                continue
            # Match direction: role can be "forward"/"backward"; simpler heuristic —
            # if last appended coord ≈ first of new segment, keep; if ≈ last, reverse
            if coords:
                last = coords[-1]
                first_new = segment[0]
                last_new = segment[-1]

                def close(a, b):
                    return abs(a[0] - b[0]) < 1e-5 and abs(a[1] - b[1]) < 1e-5

                if close(last, last_new) and not close(last, first_new):
                    segment = list(reversed(segment))
                # Dedupe the join point
                if close(coords[-1], segment[0]):
                    segment = segment[1:]
            coords.extend(segment)
            way_count += 1

        if len(coords) < 2:
            continue

        out.append({
            "ref": rel_ref,
            "name": tags.get("name") or "",
            "network": tags.get("network") or "",
            "operator": tags.get("operator") or "",
            "from": tags.get("from") or "",
            "to": tags.get("to") or "",
            "coords": coords,
            "way_count": way_count,
        })
    return out


def match_to_line(conn: duckdb.DuckDBPyConnection, city: str, ref: str) -> int | None:
    """Find city_lines.id by city + number (ref in OSM)."""
    # Exact match first
    row = conn.execute(
        "SELECT id FROM city_lines WHERE city=? AND number=? LIMIT 1",
        [city, ref],
    ).fetchone()
    if row:
        return row[0]
    # Case-insensitive
    row = conn.execute(
        "SELECT id FROM city_lines WHERE city=? AND LOWER(number)=LOWER(?) LIMIT 1",
        [city, ref],
    ).fetchone()
    return row[0] if row else None


def save_geometry(
    conn: duckdb.DuckDBPyConnection,
    line_id: int,
    city: str,
    coords: list[list[float]],
    way_count: int,
) -> None:
    coords_json = json.dumps(coords, separators=(",", ":"))
    conn.execute(
        """
        INSERT OR REPLACE INTO line_geometries
          (line_id, city, coords_json, way_count, node_count, fetched_at)
        VALUES (?, ?, ?, ?, ?, NOW())
        """,
        [line_id, city, coords_json, way_count, len(coords)],
    )


def pick_best_relation(rels: list[dict]) -> dict | None:
    """Among multiple OSM relations for the same line (one per direction,
    sometimes legacy duplicates), pick the one with the longest coord list."""
    if not rels:
        return None
    return max(rels, key=lambda r: len(r.get("coords") or []))


def process_city(conn: duckdb.DuckDBPyConnection, city: str, cfg: dict) -> tuple[int, int]:
    """Iterate city_lines, fetch geometry per line. Returns (matched, total)."""
    rows = conn.execute(
        "SELECT id, number FROM city_lines WHERE city = ? ORDER BY id",
        [city],
    ).fetchall()
    log.info("%s: %d lines to process", city, len(rows))
    matched = 0
    for i, (line_id, number) in enumerate(rows, 1):
        if not number:
            continue
        try:
            rels = fetch_relations_for_line(city, cfg, number)
        except Exception as exc:
            log.warning("  [%d/%d] line %s failed: %s", i, len(rows), number, exc)
            time.sleep(PAUSE_BETWEEN_LINES)
            continue
        best = pick_best_relation(rels)
        if best:
            save_geometry(conn, line_id, city, best["coords"], best["way_count"])
            conn.commit()
            matched += 1
            log.info("  [%d/%d] %s: %d coords (via %d ways)", i, len(rows), number, len(best["coords"]), best["way_count"])
        else:
            log.info("  [%d/%d] %s: no OSM relation found", i, len(rows), number)
        time.sleep(PAUSE_BETWEEN_LINES)
    log.info("%s: %d/%d lines now have geometry", city, matched, len(rows))
    return matched, len(rows)


def main() -> int:
    if not DB.exists():
        log.error("DB not found: %s", DB)
        return 1
    cities = sys.argv[1:] or list(CITIES.keys())
    unknown = [c for c in cities if c not in CITIES]
    if unknown:
        log.error("unknown cities: %s (supported: %s)", unknown, list(CITIES.keys()))
        return 2

    conn = duckdb.connect(str(DB))
    ensure_table(conn)

    total_matched = 0
    total_seen = 0
    for i, city in enumerate(cities):
        if i:
            time.sleep(PAUSE_BETWEEN_CITIES)
        try:
            m, s = process_city(conn, city, CITIES[city])
            total_matched += m
            total_seen += s
        except requests.RequestException as exc:
            log.error("  %s failed: %s", city, exc)
        except Exception:
            log.exception("  %s unexpected error", city)

    log.info("DONE: %d routes with geometry saved (%d seen total)", total_matched, total_seen)
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

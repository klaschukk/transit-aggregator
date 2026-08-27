"""Pre-fetch road-following geometry for the /rute + /pretraga route-overview
map, via Mapbox Directions, and cache it in analytics_db.route_geometries.

The map currently draws a straight line between two city centroids (see
app/city_coords.py) — accurate for orientation, not for "does this road
actually go there". Directions gives the real driving-route polyline.

Idempotent — a pair already cached is skipped, so it's safe to re-run (e.g.
after new routes are scraped). Cache-only at request time by design, same
discipline as scripts/pregen_far_routes.py for AI itineraries: a synchronous
Directions call on every pageview would slow Googlebot and has no
request-time cost cap. This script is the ONLY place that calls Mapbox
Directions for this feature.

Run AFTER deploy, on the prod box (the cache lives in the analytics DB
there):

    ./venv/bin/python scripts/pregen_route_geometries.py [--limit N]
"""
import argparse
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckdb  # noqa: E402

from app import analytics_db, create_app  # noqa: E402
from app.city_coords import CITY_COORDS  # noqa: E402

os.environ.setdefault('DUCKDB_PATH', 'data/dbs/transit.duckdb')

DIRECTIONS_URL = (
    'https://api.mapbox.com/directions/v5/mapbox/driving/{lon1},{lat1};{lon2},{lat2}'
)
# Mapbox Directions' default free-tier limit is 300 req/min — far more
# headroom than Groq's 12/min in pregen_far_routes.py. A 0.3s gap is
# conservative, not paced to a hard ceiling like that script.
REQUEST_GAP = 0.3
MAX_ATTEMPTS = 2
RETRY_BACKOFF = 5.0


def fetch_geometry(token: str, a: tuple, b: tuple) -> dict | None:
    """One Directions call → {'coords', 'distance_m', 'duration_s'} or None."""
    url = DIRECTIONS_URL.format(lon1=a[1], lat1=a[0], lon2=b[1], lat2=b[0])
    for attempt in range(MAX_ATTEMPTS):
        try:
            resp = requests.get(url, params={
                'geometries': 'geojson', 'overview': 'simplified',
                'access_token': token,
            }, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                routes = data.get('routes') or []
                if not routes:
                    return None
                r = routes[0]
                return {
                    'coords': r['geometry']['coordinates'],
                    'distance_m': int(r.get('distance', 0)),
                    'duration_s': int(r.get('duration', 0)),
                }
        except requests.RequestException:
            pass
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(RETRY_BACKOFF)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None,
                        help='Cap the number of pairs fetched this run')
    args = parser.parse_args()

    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        analytics_db.init_schema()
        token = app.config.get('MAPBOX_TOKEN', '')
        if not token:
            print('ERROR: MAPBOX_TOKEN not set')
            return

        con = duckdb.connect(os.environ['DUCKDB_PATH'], read_only=True)
        pairs = con.execute("""
            SELECT DISTINCT from_city, to_city, from_city_slug, to_city_slug
            FROM routes WHERE type = 'intercity'
            ORDER BY from_city, to_city
        """).fetchall()

        ok = skipped = no_coords = failed = 0
        for from_city, to_city, from_slug, to_slug in pairs:
            if args.limit and ok >= args.limit:
                print(f'\nStopped at --limit {args.limit}')
                break
            pair_key = f'{from_slug}:{to_slug}'
            if analytics_db.get_route_geometry(pair_key) is not None:
                skipped += 1
                continue
            a, b = CITY_COORDS.get(from_city), CITY_COORDS.get(to_city)
            if not a or not b:
                no_coords += 1
                print(f'NO-COORDS {pair_key} ({from_city} / {to_city})')
                continue
            result = fetch_geometry(token, a, b)
            if result:
                analytics_db.upsert_route_geometry(
                    pair_key, from_city, to_city, result['coords'],
                    result['distance_m'], result['duration_s'],
                )
                ok += 1
                print(f'OK   {pair_key}')
            else:
                failed += 1
                print(f'FAIL {pair_key}')
            time.sleep(REQUEST_GAP)

        print(f'\nDone: {ok} fetched, {skipped} cached, '
              f'{no_coords} no coords, {failed} failed')


if __name__ == '__main__':
    main()

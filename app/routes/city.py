from datetime import datetime

from flask import Blueprint, render_template, abort, request, jsonify
from app.db import query, query_one, cached_query, cached_query_one, db_ready

city_bp = Blueprint('city', __name__)

_SERVICE_BY_WEEKDAY = {0: 'RD', 1: 'RD', 2: 'RD', 3: 'RD', 4: 'RD', 5: 'S', 6: 'N'}


def _today_service() -> str:
    return _SERVICE_BY_WEEKDAY[datetime.now().weekday()]


@city_bp.route('/gradski/<city>/')
def city_hub(city: str):
    if city not in ('beograd', 'novi-sad', 'nis'):
        abort(404)

    lines = cached_query("""
        SELECT cl.number, cl.name, cl.slug, cl.color, cl.type
        FROM city_lines cl
        WHERE cl.city = ?
        ORDER BY CAST(REGEXP_REPLACE(cl.number, '[^0-9]', '', 'g') || '0' AS INTEGER)
    """, [city]) if db_ready() else []

    stops_with_coords = 0
    if db_ready():
        row = cached_query_one("SELECT COUNT(*) as c FROM city_stops WHERE city = ? AND lat IS NOT NULL", [city])
        stops_with_coords = row['c'] if row else 0

    # Top stops by number of lines serving them
    top_stops = cached_query("""
        SELECT cs.slug, cs.name, COUNT(cls.line_id) as line_count
        FROM city_stops cs
        JOIN city_line_stops cls ON cls.stop_id = cs.id
        WHERE cs.city = ?
        GROUP BY cs.slug, cs.name
        ORDER BY line_count DESC
        LIMIT 5
    """, [city]) if db_ready() else []

    return render_template('city_transport.html', city=city, lines=lines,
                           stops_with_coords=stops_with_coords,
                           top_stops=top_stops)


@city_bp.route('/gradski/<city>/linija/<line_slug>/')
def line_detail(city: str, line_slug: str):
    line = query_one("""
        SELECT id, city, number, name, slug, color, code
        FROM city_lines
        WHERE city = ? AND slug = ?
    """, [city, line_slug]) if db_ready() else None

    if not line:
        abort(404)

    stops = query("""
        SELECT cs.name, cs.slug, cs.lat, cs.lon,
               cls.stop_order AS stop_sequence, NULL AS departure_time
        FROM city_line_stops cls
        JOIN city_stops cs ON cs.id = cls.stop_id
        WHERE cls.line_id = ?
        ORDER BY cls.stop_order
    """, [line['id']])

    # GTFS schedule: departure times from first stop, grouped by service day
    schedule: dict[str, list[str]] = {'RD': [], 'S': [], 'N': []}
    first_dep = None
    last_dep = None

    gtfs_count = cached_query_one(
        "SELECT COUNT(*) as c FROM gtfs_trips WHERE line_id = ?",
        [line['id']], ttl=3600
    )
    has_gtfs = (gtfs_count or {}).get('c', 0) > 0

    if has_gtfs:
        for sid in ('RD', 'S', 'N'):
            deps = cached_query("""
                SELECT DISTINCT st.departure_time
                FROM gtfs_stop_times st
                JOIN gtfs_trips gt ON gt.trip_id = st.trip_id
                WHERE gt.line_id = ? AND st.stop_sequence = 1
                  AND gt.service_id = ? AND gt.direction_id = 0
                ORDER BY st.departure_time
            """, [line['id'], sid], ttl=3600)
            schedule[sid] = [d['departure_time'][:5] for d in deps]

        # First/last service from workday schedule
        if schedule['RD']:
            first_dep = schedule['RD'][0]
            last_dep = schedule['RD'][-1]

    # Line type label
    type_labels = {
        'bus': 'Autobus', 'tram': 'Tramvaj', 'trolleybus': 'Trolejbus',
        'night': 'Noćna linija', 'e-bus': 'E-bus', 'bg-voz': 'BG Voz',
    }
    line_type_label = type_labels.get(line.get('type', ''), 'Autobus')

    return render_template('line_detail.html', city=city, line=line, stops=stops,
                           schedule=schedule, has_gtfs=has_gtfs,
                           first_dep=first_dep, last_dep=last_dep,
                           line_type_label=line_type_label)


@city_bp.route('/gradski/<city>/stajaliste/<stop_slug>/')
def stop_detail(city: str, stop_slug: str):
    stop = query_one("""
        SELECT id, city, name, slug, lat, lon, code
        FROM city_stops
        WHERE city = ? AND slug = ?
    """, [city, stop_slug]) if db_ready() else None

    if not stop:
        abort(404)

    # Lines serving this stop via city_line_stops
    lines_at_stop = query("""
        SELECT DISTINCT cl.number, cl.name, cl.slug, cl.color
        FROM city_line_stops cls
        JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cls.stop_id = ?
        ORDER BY CAST(REGEXP_REPLACE(cl.number, '[^0-9]', '', 'g') || '0' AS INTEGER)
    """, [stop['id']])

    departures = []  # No GTFS schedule data yet

    # Nearby stops by coordinates
    nearby_stops = []
    if stop.get('lat') and stop.get('lon'):
        nearby_stops = query("""
            SELECT slug, name, lat, lon
            FROM city_stops
            WHERE city = ?
              AND lat BETWEEN ? - 0.005 AND ? + 0.005
              AND lon BETWEEN ? - 0.005 AND ? + 0.005
              AND slug != ?
              AND lat IS NOT NULL
            LIMIT 5
        """, [city, stop['lat'], stop['lat'], stop['lon'], stop['lon'], stop_slug])

    return render_template('stop_detail.html', city=city, stop=stop,
                           departures=departures, lines_at_stop=lines_at_stop,
                           nearby_stops=nearby_stops)


@city_bp.route('/api/stop-arrivals')
def api_stop_arrivals():
    """Return lines at a stop with next arrivals from GTFS schedule."""
    stop_slug = request.args.get('slug', '').strip()
    if not stop_slug or not db_ready():
        return jsonify([])

    stop = query_one("SELECT id FROM city_stops WHERE slug = ?", [stop_slug])
    if not stop:
        return jsonify([])

    # Get lines serving this stop
    lines = query("""
        SELECT cl.number, cl.name, cl.slug AS line_slug, cl.color, cls.stop_order
        FROM city_line_stops cls
        JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cls.stop_id = ?
        ORDER BY CAST(REGEXP_REPLACE(cl.number, '[^0-9]', '', 'g') || '0' AS INTEGER)
        LIMIT 12
    """, [stop['id']])

    if not lines:
        return jsonify([])

    now = datetime.now()
    current_min = now.hour * 60 + now.minute
    now_time = f'{now.hour:02d}:{now.minute:02d}:00'
    service_id = _today_service()

    # Try GTFS schedule: find next 2 departures per line at this stop
    gtfs_arrivals = query("""
        SELECT cl.number,
               st.departure_time,
               gt.direction_id
        FROM gtfs_stop_times st
        JOIN gtfs_trips gt ON gt.trip_id = st.trip_id
        JOIN city_lines cl ON cl.id = gt.line_id
        WHERE st.city_stop_id = ?
          AND gt.service_id = ?
          AND st.departure_time >= ?
        ORDER BY cl.number, st.departure_time
    """, [stop['id'], service_id, now_time])

    # Group by line number: keep first 2 departures
    gtfs_by_line: dict[str, list[str]] = {}
    for row in gtfs_arrivals:
        num = row['number']
        if num not in gtfs_by_line:
            gtfs_by_line[num] = []
        if len(gtfs_by_line[num]) < 2:
            gtfs_by_line[num].append(row['departure_time'])

    result = []
    for line in lines:
        name = line['name'] or ''
        direction = name.split('—')[-1].strip() if '—' in name else name

        departures = gtfs_by_line.get(line['number'])
        if departures:
            # Real GTFS times
            mins1 = _time_to_min(departures[0]) - current_min
            if mins1 < 0:
                mins1 = 0
            mins2 = _time_to_min(departures[1]) - current_min if len(departures) > 1 else mins1 + 15
            if mins2 < mins1:
                mins2 = mins1 + 15
        else:
            # Fallback: headway estimate
            if current_min < 360 or current_min > 1380:
                headway = 30
            elif current_min < 540 or (900 < current_min < 1020):
                headway = 6
            else:
                headway = 10
            offset = (current_min + (line.get('stop_order') or 0) * 2) % headway
            mins1 = headway - offset
            if mins1 <= 0:
                mins1 = 1
            mins2 = mins1 + headway

        result.append({
            'line': line['number'],
            'direction': direction,
            'color': line.get('color') or '#0d9488',
            'slug': line['line_slug'],
            'mins': mins1,
            'mins2': mins2,
        })

    return jsonify(result)


def _time_to_min(t: str) -> int:
    """Convert HH:MM:SS to minutes since midnight. Handles 25:00:00 etc."""
    parts = t.split(':')
    return int(parts[0]) * 60 + int(parts[1])


@city_bp.route('/api/city-stops')
def api_city_stops():
    """Return stops within bounding box as JSON for map markers."""
    try:
        sw_lat = float(request.args['sw_lat'])
        sw_lon = float(request.args['sw_lon'])
        ne_lat = float(request.args['ne_lat'])
        ne_lon = float(request.args['ne_lon'])
    except (KeyError, ValueError):
        return jsonify({'error': 'Required: sw_lat, sw_lon, ne_lat, ne_lon'}), 400

    if not db_ready():
        return jsonify([])

    stops = query("""
        SELECT name, slug, lat, lon
        FROM city_stops
        WHERE lat BETWEEN ? AND ?
          AND lon BETWEEN ? AND ?
          AND lat IS NOT NULL
        LIMIT 200
    """, [sw_lat, ne_lat, sw_lon, ne_lon])

    return jsonify(stops)

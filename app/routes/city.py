import threading
from datetime import datetime

from flask import Blueprint, render_template, abort, request, jsonify, redirect, url_for
from app.db import query, query_one, cached_query, cached_query_one, db_ready
from app.extensions import limiter
from app.slug import normalize_slug

city_bp = Blueprint('city', __name__)

_SERVICE_BY_WEEKDAY = {0: 'RD', 1: 'RD', 2: 'RD', 3: 'RD', 4: 'RD', 5: 'S', 6: 'N'}


def _today_service() -> str:
    return _SERVICE_BY_WEEKDAY[datetime.now().weekday()]


@city_bp.route('/gradski/')
def city_index():
    """Landing page listing all cities with public transit."""
    cities = [
        {'slug': 'beograd', 'name': 'Beograd', 'desc': 'GSP — autobus, tramvaj, trolejbus', 'lines': 0},
    ]
    if db_ready():
        row = cached_query_one("SELECT COUNT(*) as c FROM city_lines WHERE city = 'beograd'", ttl=3600)
        cities[0]['lines'] = row['c'] if row else 0
        for slug, name in [('novi-sad', 'Novi Sad'), ('nis', 'Niš'), ('kragujevac', 'Kragujevac')]:
            row = cached_query_one("SELECT COUNT(*) as c FROM city_lines WHERE city = ?", [slug], ttl=3600)
            if row and row['c'] > 0:
                cities.append({'slug': slug, 'name': name, 'desc': f'{row["c"]} linija', 'lines': row['c']})
    return render_template('city_index.html', cities=cities)


_SUPPORTED_CITIES = ('beograd', 'novi-sad', 'nis', 'kragujevac')


@city_bp.route('/gradski/<city>/')
def city_hub(city: str):
    if city not in _SUPPORTED_CITIES:
        norm = normalize_slug(city)
        if norm in _SUPPORTED_CITIES and norm != city:
            return redirect(url_for('city.city_hub', city=norm), code=301)
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

    # Popular intercity routes departing from this city — for SEO interlinking.
    # Match against from_city name (city_slug → Title case) since routes.from_city is display name.
    city_display = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'}.get(city, city.title())
    popular_intercity = cached_query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) as min_price_rsd,
               r.from_city_slug, r.to_city_slug
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity' AND r.from_city = ?
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.from_city_slug, r.to_city_slug
        HAVING trip_count > 0
        ORDER BY trip_count DESC
        LIMIT 8
    """, [city_display], ttl=3600) if db_ready() else []

    return render_template('city_transport.html', city=city, lines=lines,
                           stops_with_coords=stops_with_coords,
                           top_stops=top_stops,
                           popular_intercity=popular_intercity,
                           city_label=city_display)


@city_bp.route('/gradski/<city>/linija/<line_slug>/')
def line_detail(city: str, line_slug: str):
    # Canonicalize both path segments before DB lookup: cyrillic/uppercase/
    # diacritic variants redirect to the ASCII canonical form.
    city_norm = city if city in _SUPPORTED_CITIES else normalize_slug(city)
    line_norm = normalize_slug(line_slug)
    if (city_norm, line_norm) != (city, line_slug) and city_norm in _SUPPORTED_CITIES and line_norm:
        return redirect(
            url_for('city.line_detail', city=city_norm, line_slug=line_norm),
            code=301,
        )

    line = query_one("""
        SELECT id, city, number, name, slug, color, code, type
        FROM city_lines
        WHERE city = ? AND slug = ?
    """, [city, line_slug]) if db_ready() else None

    if not line:
        # Non-ASCII legacy URLs → 410 Gone (Google drops permanently).
        if not line_slug.isascii() or '---' in line_slug:
            abort(410)
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

    # Road-following polyline geometry (OSM route relation) — optional,
    # falls back to straight-line-between-stops if missing. Populated by
    # data/pipelines/scrape_route_geometries.py.
    geometry = None
    try:
        geom_row = cached_query_one(
            "SELECT coords_json FROM line_geometries WHERE line_id = ?",
            [line['id']], ttl=86400,
        )
        if geom_row and geom_row.get('coords_json'):
            geometry = geom_row['coords_json']
    except Exception:
        geometry = None

    # Related lines of the same type in the same city (up to 6, excluding this line)
    related_lines = cached_query("""
        SELECT number, name, slug, color, type
        FROM city_lines
        WHERE city = ? AND type = ? AND id != ?
        ORDER BY CAST(REGEXP_REPLACE(number, '[^0-9]', '', 'g') || '0' AS INTEGER)
        LIMIT 6
    """, [city, line.get('type', 'bus'), line['id']], ttl=3600) if db_ready() else []

    return render_template('line_detail.html', city=city, line=line, stops=stops,
                           schedule=schedule, has_gtfs=has_gtfs,
                           first_dep=first_dep, last_dep=last_dep,
                           line_type_label=line_type_label,
                           geometry=geometry,
                           related_lines=related_lines)


@city_bp.route('/gradski/<city>/stajaliste/<stop_slug>/')
def stop_detail(city: str, stop_slug: str):
    city_norm = city if city in _SUPPORTED_CITIES else normalize_slug(city)
    stop_norm = normalize_slug(stop_slug)
    if (city_norm, stop_norm) != (city, stop_slug) and city_norm in _SUPPORTED_CITIES and stop_norm:
        return redirect(
            url_for('city.stop_detail', city=city_norm, stop_slug=stop_norm),
            code=301,
        )

    stop = query_one("""
        SELECT id, city, name, slug, lat, lon, code
        FROM city_stops
        WHERE city = ? AND slug = ?
    """, [city, stop_slug]) if db_ready() else None

    if not stop:
        # Legacy URLs from a prior DB state (cyrillic, triple-dash, or
        # numeric-only scraper artefacts like "/stajaliste/1/") won't come
        # back — 410 Gone tells Google to drop them permanently. Clean
        # ASCII misses stay 404 (may be typos).
        if not stop_slug.isascii() or '---' in stop_slug or stop_slug.isdigit():
            abort(410)
        abort(404)

    # Lines serving this stop via city_line_stops
    lines_at_stop = query("""
        SELECT DISTINCT cl.number, cl.name, cl.slug, cl.color, cl.type
        FROM city_line_stops cls
        JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cls.stop_id = ?
        ORDER BY CAST(REGEXP_REPLACE(cl.number, '[^0-9]', '', 'g') || '0' AS INTEGER)
    """, [stop['id']])

    departures = []

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

    # Compute stop_info for SEO content enrichment
    stop_info: dict = {}
    stop_id = stop['id']

    if lines_at_stop:
        type_labels = {
            'bus': 'autobus', 'tram': 'tramvaj', 'trolleybus': 'trolejbus',
            'night': 'noćni', 'e-bus': 'e-bus', 'bg-voz': 'BG Voz',
        }
        line_types = sorted(set(t['type'] for t in lines_at_stop if t.get('type')))
        stop_info['line_count'] = len(lines_at_stop)
        stop_info['line_types'] = [type_labels.get(t, t) for t in line_types]

    # GTFS: first/last departure and busiest lines (cached, heavy queries)
    gtfs_stats = cached_query_one("""
        SELECT MIN(st.departure_time) AS first_dep,
               MAX(st.departure_time) AS last_dep
        FROM gtfs_stop_times st
        JOIN gtfs_trips gt ON gt.trip_id = st.trip_id
        WHERE st.city_stop_id = ? AND gt.service_id = 'RD'
    """, [stop_id], ttl=600)

    if gtfs_stats and gtfs_stats.get('first_dep'):
        stop_info['has_gtfs'] = True
        fd = gtfs_stats['first_dep']
        ld = gtfs_stats['last_dep']
        stop_info['first_departure'] = fd[:5] if fd else None
        # Normalize times > 24:00 for display
        if ld and int(ld[:2]) >= 24:
            h = int(ld[:2]) - 24
            stop_info['last_departure'] = f'{h:02d}{ld[2:5]}'
        else:
            stop_info['last_departure'] = ld[:5] if ld else None

        busiest = cached_query("""
            SELECT cl.number, cl.name, COUNT(*) AS freq
            FROM gtfs_stop_times st
            JOIN gtfs_trips gt ON gt.trip_id = st.trip_id
            JOIN city_lines cl ON cl.id = gt.line_id
            WHERE st.city_stop_id = ? AND gt.service_id = 'RD'
            GROUP BY cl.number, cl.name
            ORDER BY freq DESC LIMIT 3
        """, [stop_id], ttl=600)
        stop_info['busiest_lines'] = busiest
    else:
        stop_info['has_gtfs'] = False

    # E-E-A-T prose: rules-based 150–300-word unique block per stop, cached
    # in-process for 24 h since inputs (lines/nearby/gtfs) only change when
    # the transit DB rebuilds overnight.
    from app.content.stop_prose import build_prose
    from flask import g
    lang = getattr(g, 'lang', 'sr')
    lang_prefix = getattr(g, 'lang_prefix', '')
    prose = _stop_prose_cached(
        stop_slug=stop['slug'], lang=lang, lang_prefix=lang_prefix,
        stop=stop, lines=lines_at_stop, nearby=nearby_stops,
        gtfs=stop_info if stop_info.get('has_gtfs') else None,
    )

    return render_template('stop_detail.html', city=city, stop=stop,
                           departures=departures, lines_at_stop=lines_at_stop,
                           nearby_stops=nearby_stops, stop_info=stop_info,
                           prose=prose)


# ── Stop prose cache (in-process, 24 h TTL) ─────────────────────────────
# Keyed by (slug, lang). Single worker hits ~2K unique stops × 3 langs = 6K
# entries max. Cheap to recompute but caching saves ~1 ms per request.

_STOP_PROSE_CACHE: dict[tuple[str, str], dict] = {}
_STOP_PROSE_CACHE_LOCK = threading.Lock()
_STOP_PROSE_CACHE_TTL = 24 * 3600
_STOP_PROSE_CACHE_STAMPS: dict[tuple[str, str], float] = {}


def _stop_prose_cached(*, stop_slug, lang, lang_prefix, stop, lines, nearby, gtfs):
    import time as _time
    from app.content.stop_prose import build_prose
    key = (stop_slug, lang)
    now = _time.time()
    with _STOP_PROSE_CACHE_LOCK:
        stamp = _STOP_PROSE_CACHE_STAMPS.get(key, 0)
        if key in _STOP_PROSE_CACHE and now - stamp < _STOP_PROSE_CACHE_TTL:
            return _STOP_PROSE_CACHE[key]
    prose = build_prose(stop, lines, nearby, gtfs, lang=lang, lang_prefix=lang_prefix)
    with _STOP_PROSE_CACHE_LOCK:
        _STOP_PROSE_CACHE[key] = prose
        _STOP_PROSE_CACHE_STAMPS[key] = now
    return prose


@city_bp.route('/api/stop-arrivals')
@limiter.limit("30 per minute")
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
@limiter.limit("30 per minute")
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
        LIMIT 500
    """, [sw_lat, ne_lat, sw_lon, ne_lon])

    return jsonify(stops)

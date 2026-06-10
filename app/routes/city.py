import json as _json
import threading
from datetime import datetime

from flask import Blueprint, render_template, abort, request, jsonify, redirect, url_for, current_app
from app.db import query, query_one, cached_query, cached_query_one, db_ready
from app.extensions import limiter
from app.slug import normalize_slug, slugify_serbian

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

# Slug renames after a data re-crawl — 301 so Google transfers PageRank
# to the successor and drops the old URL. Keyed by city → old_slug → new_slug.
# None means the stop/line was removed entirely → redirect to city hub.
_LINE_SLUG_REDIRECTS: dict[str, dict[str, str]] = {
    'beograd': {
        'linija-31l': 'linija-31',   # 31Л variant merged into regular 31
        'linija-6a':  'linija-6',    # 6А variant merged into regular 6
        'linija-29l': 'linija-29',   # 29Л variant merged into regular 29
        'linija-12l': 'linija-12',   # 12Л variant merged into regular 12
        'linija-28a': 'linija-28',   # 28А variant merged into regular 28
    },
}
_STOP_SLUG_REDIRECTS: dict[str, dict[str, str | None]] = {
    'novi-sad': {
        'rumenacka-dom-zdravlja':                    None,
        'sentandrejski-put-partizanska':             None,
        'bulevar-mihajla-pupina-pothodnik':          None,
        'bulevar-slobodana-jovanovica-dom-zdravlja': None,
        'rumenacki-put-gradsko-groblje':             None,
        'futoski-put-bulevar-patrijarha-pavla':      None,
        'temerinska-najlon-pijaca':                  None,
        'bulevar-evrope-cara-dusana':                None,
        'bulevar-cara-lazara-dom-zdravlja':          None,
        'uspenska-safarikova':                       None,
        'paragovo-iriski-put-2':                     None,
        'sentandrejski-put-benzinska-pumpa':         None,
        'bulevar-oslobodjenja-brace-ribnikar':       None,
        'sentandrejski-put-savska':                  None,
        'rakovac-3-raskrsnica':                      None,
        'bulevar-kralja-petra-prvog-sajam':          None,
        'kac-svetosavska-63':                        None,
        'sremski-karlovci-karlovacka-gimnazija':     None,
        'petrovaradin-zeleznicka-stanica':           None,
    },
}


def _line_geometries_available() -> bool:
    """Memoise whether line_geometries exists. Set on first call per
    process; cleared by gunicorn worker recycle. The DuckDB system
    catalog query is cheap and one round-trip beats catching an
    exception on every line_detail render."""
    cache_key = '_line_geom_seen'
    seen = getattr(_line_geometries_available, cache_key, None)
    if seen is not None:
        return seen
    try:
        row = query_one(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'line_geometries' LIMIT 1"
        ) if db_ready() else None
        seen = bool(row)
    except Exception:
        seen = False
    setattr(_line_geometries_available, cache_key, seen)
    return seen


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

    # Top stops by number of lines serving them. Lifted 5 → 12 so the
    # city hub becomes a real interchange-stop hub: stop_detail pages
    # were averaging 1 inbound link in the link-audit, this is the
    # cheapest place to seed weight to the busiest dozen.
    top_stops = cached_query("""
        SELECT cs.slug, cs.name, COUNT(cls.line_id) as line_count
        FROM city_stops cs
        JOIN city_line_stops cls ON cls.stop_id = cs.id
        WHERE cs.city = ?
        GROUP BY cs.slug, cs.name
        ORDER BY line_count DESC
        LIMIT 12
    """, [city]) if db_ready() else []

    # Popular intercity routes departing from this city — for SEO interlinking.
    # Match against from_city name (city_slug → Title case) since routes.from_city is display name.
    city_display = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'}.get(city, city.title())
    popular_intercity = cached_query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) as min_price_rsd,
               r.from_city_slug, r.to_city_slug
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity' AND r.from_city = ?
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.from_city_slug, r.to_city_slug
        HAVING trip_count > 0
        ORDER BY trip_count DESC
        LIMIT 12
    """, [city_display], ttl=3600) if db_ready() else []

    # Top operators serving intercity from this city — gives carrier
    # pages an inbound link from each city hub and lets users discover
    # carriers from a city-shaped query.
    top_operators = cached_query("""
        SELECT o.slug, o.name, COUNT(DISTINCT r.id) AS route_count
        FROM operators o
        JOIN trips t ON t.operator_id = o.id
        JOIN routes r ON r.id = t.route_id
        WHERE r.type = 'intercity' AND r.from_city = ?
        GROUP BY o.slug, o.name
        ORDER BY route_count DESC
        LIMIT 6
    """, [city_display], ttl=3600) if db_ready() else []

    # Reviews — same pattern as line_detail / stop_detail. Slug is
    # "city-<city>" so a Beograd review and a Novi Sad review don't
    # aggregate into the same bucket.
    review_slug = f'city-{city}'
    reviews_data: list = []
    reviews_aggregate = None
    try:
        from app import analytics_db
        reviews_data = analytics_db.approved_reviews(review_slug)
        reviews_aggregate = analytics_db.aggregate_rating(review_slug)
    except Exception:
        pass

    page_context_json = _json.dumps({
        'type': 'city_transport',
        'city': city_display,
        'line_count': len(lines) if lines else 0,
    }, ensure_ascii=False)
    return render_template('city_transport.html', city=city, lines=lines,
                           stops_with_coords=stops_with_coords,
                           top_stops=top_stops,
                           popular_intercity=popular_intercity,
                           top_operators=top_operators,
                           city_label=city_display,
                           review_slug=review_slug,
                           reviews=reviews_data,
                           reviews_agg=reviews_aggregate,
                           page_context_json=page_context_json)


@city_bp.route('/gradski/<city>/linija/<line_slug>/')
def line_detail(city: str, line_slug: str):
    # Static redirects for slugs renamed in a DB re-crawl (GSC 404 list).
    if line_slug in _LINE_SLUG_REDIRECTS.get(city, {}):
        new_slug = _LINE_SLUG_REDIRECTS[city][line_slug]
        return redirect(url_for('city.line_detail', city=city, line_slug=new_slug), code=301)

    # Canonicalize both path segments before DB lookup: cyrillic/uppercase/
    # diacritic variants redirect to the ASCII canonical form *only when
    # the canonical slug actually resolves to a row*. A blanket
    # transliterate-and-redirect emits 301 → 404 chains for legacy URLs
    # that no longer correspond to any line, wasting crawl budget. The
    # existence-gated path was added 2026-04-27 after GSC reported 313
    # 404s on URL-encoded Cyrillic stop/line slugs from a legacy
    # migration.
    city_norm = city if city in _SUPPORTED_CITIES else normalize_slug(city)
    line_norm = normalize_slug(line_slug)
    # Two transliteration candidates per inbound slug:
    #   normalize_slug      — conservative ASCII fold (ђ→d) used for
    #                         pipeline-side slug generation; matches
    #                         most legacy DB rows.
    #   slugify_serbian     — Serbian-standard (ђ→dj) used at request
    #                         time for inbound Cyrillic URLs whose
    #                         canonical slug contains 'dj' (oslobodjenja,
    #                         djordja-stanojevica, ilije-djuricica, …).
    # Try both; redirect to whichever resolves. Order matters only for
    # the rare case where BOTH candidates match different rows — we
    # prefer normalize_slug since pipeline-side already-stored slugs
    # are the source of truth.
    line_candidates: list[str] = []
    for cand in (line_norm, slugify_serbian(line_slug)):
        if cand and cand not in line_candidates:
            line_candidates.append(cand)
    for cand in line_candidates:
        if (city_norm, cand) == (city, line_slug):
            continue  # input already canonical, fall through to DB lookup
        if city_norm not in _SUPPORTED_CITIES:
            break
        if not (db_ready() and query_one(
            "SELECT 1 FROM city_lines WHERE city = ? AND slug = ?",
            [city_norm, cand],
        )):
            continue
        return redirect(
            url_for('city.line_detail', city=city_norm, line_slug=cand),
            code=301,
        )
    # Fall through — Cyrillic miss with no Latin counterpart → 410
    # in the same `not line` branch below.

    line = query_one("""
        SELECT id, city, number, name, slug, color, code, type
        FROM city_lines
        WHERE city = ? AND slug = ?
    """, [city, line_slug]) if db_ready() else None

    if not line:
        if not db_ready():
            abort(503)
        # Genuine miss with the DB up = the line is gone (restructured or
        # renumbered in a re-crawl), not transient → 410 for fast deindex
        # rather than lingering in GSC "Not found (404)".
        abort(410)

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
    # data/pipelines/scrape_route_geometries.py. The pipeline is opt-in
    # and the table only exists once it has been run, so we probe once
    # per process and skip the per-line query otherwise — avoids spamming
    # `DuckDB query error: Table line_geometries does not exist` in error.log
    # 600+ times on every nightly DB rebuild.
    geometry = None
    if _line_geometries_available():
        geom_row = cached_query_one(
            "SELECT coords_json FROM line_geometries WHERE line_id = ?",
            [line['id']], ttl=86400,
        )
        if geom_row and geom_row.get('coords_json'):
            geometry = geom_row['coords_json']

    # Related lines of the same type in the same city (up to 8, excluding this line)
    related_lines = cached_query("""
        SELECT number, name, slug, color, type
        FROM city_lines
        WHERE city = ? AND type = ? AND id != ?
        ORDER BY CAST(REGEXP_REPLACE(number, '[^0-9]', '', 'g') || '0' AS INTEGER)
        LIMIT 8
    """, [city, line.get('type', 'bus'), line['id']], ttl=3600) if db_ready() else []

    # Interchange stops on this line — stops that serve the most other
    # lines (excluding the terminals, which we list separately). These
    # are the high-value stop_detail pages and giving each line a
    # 4-stop interchange block redirects PageRank to them from every
    # line page that touches them. ~611 lines × 4 stops = ~2.4K extra
    # inbound edges concentrated on busy stops.
    interchange_stops = cached_query("""
        WITH this_line_stops AS (
          SELECT stop_id FROM city_line_stops WHERE line_id = ?
        )
        SELECT cs.slug, cs.name, COUNT(DISTINCT cls.line_id) AS line_count
        FROM city_stops cs
        JOIN city_line_stops cls ON cls.stop_id = cs.id
        WHERE cs.id IN (SELECT stop_id FROM this_line_stops)
        GROUP BY cs.slug, cs.name
        HAVING line_count > 1
        ORDER BY line_count DESC, cs.name
        LIMIT 4
    """, [line['id']], ttl=3600) if db_ready() else []

    # E-E-A-T prose: rules-based 150–250-word unique block per line, cached
    # on (slug, lang). Replaces the duplicate 2-paragraph boilerplate that
    # used to live in line_detail.html and made every line page register
    # as near-duplicate content in GSC.
    from flask import g as _g
    _lang = getattr(_g, 'lang', 'sr')
    _lang_prefix = getattr(_g, 'lang_prefix', '')
    prose = _line_prose_cached(
        line_slug=line_slug, lang=_lang, lang_prefix=_lang_prefix,
        line=line, stops=stops,
        schedule_rd=schedule.get('RD'), schedule_sat=schedule.get('S'),
        interchange=interchange_stops,
    )

    # Reviews — same pattern as stop_detail. Slug is "line-<city>-<slug>"
    # so a Beograd L7 review and a Niš L7 review don't aggregate into the
    # same bucket.
    review_slug = f'line-{city}-{line_slug}'
    reviews_data = []
    reviews_aggregate = None
    try:
        from app import analytics_db
        reviews_data = analytics_db.approved_reviews(review_slug)
        reviews_aggregate = analytics_db.aggregate_rating(review_slug)
    except Exception:
        pass

    og_image_url = f"{current_app.config['BASE_URL']}/og/line/{city}/{line_slug}.png"
    city_names = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'}
    page_context_json = _json.dumps({
        'type': 'line',
        'city': city_names.get(city, city),
        'line_number': line.get('number') if line else None,
        'line_name': line.get('name') if line else None,
        'stop_count': len(stops) if stops else 0,
    }, ensure_ascii=False)
    return render_template('line_detail.html', city=city, line=line, stops=stops,
                           schedule=schedule, has_gtfs=has_gtfs,
                           first_dep=first_dep, last_dep=last_dep,
                           line_type_label=line_type_label,
                           geometry=geometry,
                           related_lines=related_lines,
                           interchange_stops=interchange_stops,
                           prose=prose,
                           review_slug=review_slug,
                           reviews=reviews_data, reviews_agg=reviews_aggregate,
                           og_image_url=og_image_url,
                           page_context_json=page_context_json)


@city_bp.route('/gradski/<city>/stajaliste/<stop_slug>/')
def stop_detail(city: str, stop_slug: str):
    # Static redirects for stops renamed or removed in a DB re-crawl.
    if stop_slug in _STOP_SLUG_REDIRECTS.get(city, {}):
        new_slug = _STOP_SLUG_REDIRECTS[city][stop_slug]
        if new_slug:
            return redirect(url_for('city.stop_detail', city=city, stop_slug=new_slug), code=301)
        return redirect(url_for('city.city_hub', city=city), code=301)

    # Existence-gated cyrillic→latin redirect: only 301 to the canonical
    # ASCII slug when that slug actually resolves to a row. GSC reported
    # 313 404s on URL-encoded cyrillic stop slugs from a legacy
    # migration; ~75% transliterate to a current Latin canonical and get
    # caught here. The remaining ~25% (stops removed upstream) fall
    # through to abort(410) below so Google drops them permanently
    # instead of being chained 301→404.
    city_norm = city if city in _SUPPORTED_CITIES else normalize_slug(city)
    stop_norm = normalize_slug(stop_slug)
    # Try both transliteration candidates (see line_detail for context):
    # normalize_slug catches most rows; slugify_serbian (ђ→dj) catches
    # the ~30% of Novi Sad stops whose canonical contains 'dj'
    # (bulevar-oslobodjenja-*, ilije-djuricica, djordja-nedeljkovica,
    # …). 250+ of the GSC 404 batch are exactly this shape.
    stop_candidates: list[str] = []
    for cand in (stop_norm, slugify_serbian(stop_slug)):
        if cand and cand not in stop_candidates:
            stop_candidates.append(cand)
    for cand in stop_candidates:
        if (city_norm, cand) == (city, stop_slug):
            continue
        if city_norm not in _SUPPORTED_CITIES:
            break
        if not (db_ready() and query_one(
            "SELECT 1 FROM city_stops WHERE city = ? AND slug = ?",
            [city_norm, cand],
        )):
            continue
        return redirect(
            url_for('city.stop_detail', city=city_norm, stop_slug=cand),
            code=301,
        )

    stop = query_one("""
        SELECT id, city, name, slug, lat, lon, code
        FROM city_stops
        WHERE city = ? AND slug = ?
    """, [city, stop_slug]) if db_ready() else None

    if not stop:
        if not db_ready():
            abort(503)
        # Genuine miss with the DB up = the stop is gone, not transient. The
        # 2026 re-scrape dropped ~886 stops (3770→2884); their indexed URLs
        # (clean-ASCII slugs like banostor-1, mas-polazni-peron-broj-13) are
        # permanently dead. 410 deindexes them fast instead of leaving them
        # stuck in GSC "Not found (404)" for months; renamed stops are
        # re-found via the new slug already listed in sitemap-stops.
        abort(410)

    # Lines serving this stop via city_line_stops
    lines_at_stop = query("""
        SELECT DISTINCT cl.number, cl.name, cl.slug, cl.color, cl.type
        FROM city_line_stops cls
        JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cls.stop_id = ?
        ORDER BY CAST(REGEXP_REPLACE(cl.number, '[^0-9]', '', 'g') || '0' AS INTEGER)
    """, [stop['id']])

    # Per-line GTFS schedule window AT THIS STOP (first/last departure + count)
    # for today's service. Rendered server-side so every stop shows its
    # timetable at a glance — visible without JS and crawlable for "{stop} red
    # vožnje" queries. Static for the day → cached. Lines with no GTFS schedule
    # (e.g. tourist/charter lines absent from the feed) simply get no window;
    # we never fabricate one (same honesty rule as /api/stop-arrivals). The live
    # "za N min" countdown (JS, /api/stop-arrivals) still enhances on top.
    if lines_at_stop and db_ready():
        _svc = _today_service()
        _sched_rows = cached_query("""
            SELECT cl.number,
                   MIN(st.departure_time) AS first_dep,
                   MAX(st.departure_time) AS last_dep,
                   COUNT(*) AS freq
            FROM gtfs_stop_times st
            JOIN gtfs_trips gt ON gt.trip_id = st.trip_id
            JOIN city_lines cl ON cl.id = gt.line_id
            WHERE st.city_stop_id = ? AND gt.service_id = ?
            GROUP BY cl.number
        """, [stop['id'], _svc], ttl=600)
        _sched = {r['number']: r for r in (_sched_rows or [])}

        def _hhmm(t: str | None) -> str | None:
            # GTFS times can exceed 24:00 (after-midnight service); fold for display.
            if not t:
                return None
            h = int(t[:2])
            return f'{h - 24:02d}{t[2:5]}' if h >= 24 else t[:5]

        for _ln in lines_at_stop:
            _s = _sched.get(_ln['number'])
            if _s and _s.get('first_dep'):
                _ln['sched_first'] = _hhmm(_s['first_dep'])
                _ln['sched_last'] = _hhmm(_s['last_dep'])
                _ln['sched_freq'] = _s['freq']

    departures = []

    # Nearby stops by coordinates. Lifted 5 → 10 and widened the box
    # 0.005 → 0.008 deg (~900m) so stops in less-dense outer zones (the
    # ones that score 1-2 inbound in the link audit) actually find
    # neighbours to point at. Cap at 10 to stay under the 12-link
    # ceiling for the section.
    nearby_stops = []
    if stop.get('lat') and stop.get('lon'):
        nearby_stops = query("""
            SELECT slug, name, lat, lon
            FROM city_stops
            WHERE city = ?
              AND lat BETWEEN ? - 0.008 AND ? + 0.008
              AND lon BETWEEN ? - 0.008 AND ? + 0.008
              AND slug != ?
              AND lat IS NOT NULL
            LIMIT 10
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

    # Reviews — same source as route_detail / city_pair. Stop slug is namespaced
    # ("stop-<city>-<slug>") so it doesn't collide with intercity rute slugs.
    review_slug = f'stop-{city}-{stop_slug}'
    reviews_data = []
    reviews_aggregate = None
    try:
        from app import analytics_db
        reviews_data = analytics_db.approved_reviews(review_slug)
        reviews_aggregate = analytics_db.aggregate_rating(review_slug)
    except Exception:
        pass

    og_image_url = f"{current_app.config['BASE_URL']}/og/stop/{city}/{stop_slug}.png"
    city_names = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'}
    page_context_json = _json.dumps({
        'type': 'stop',
        'city': city_names.get(city, city),
        'stop_name': stop.get('name') if stop else None,
        'line_count': stop_info.get('line_count') if stop_info else 0,
    }, ensure_ascii=False)
    return render_template('stop_detail.html', city=city, stop=stop,
                           departures=departures, lines_at_stop=lines_at_stop,
                           nearby_stops=nearby_stops, stop_info=stop_info,
                           prose=prose,
                           review_slug=review_slug,
                           reviews=reviews_data, reviews_agg=reviews_aggregate,
                           og_image_url=og_image_url,
                           page_context_json=page_context_json)


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


# ── Line prose cache (in-process, 24 h TTL) ─────────────────────────────
# Mirrors _STOP_PROSE_CACHE. ~611 lines × 3 langs = 1833 entries; trivial.
# Cache key intentionally excludes city — slug is unique within a city
# but a single key namespace across cities still avoids collisions because
# slugs include city-specific prefixes (e.g. 'linija-2a' vs '4').

_LINE_PROSE_CACHE: dict[tuple[str, str], dict] = {}
_LINE_PROSE_CACHE_LOCK = threading.Lock()
_LINE_PROSE_CACHE_TTL = 24 * 3600
_LINE_PROSE_CACHE_STAMPS: dict[tuple[str, str], float] = {}


def _line_prose_cached(*, line_slug, lang, lang_prefix, line, stops,
                       schedule_rd, schedule_sat, interchange):
    import time as _time
    from app.content.line_prose import build_prose
    key = (line_slug, lang)
    now = _time.time()
    with _LINE_PROSE_CACHE_LOCK:
        stamp = _LINE_PROSE_CACHE_STAMPS.get(key, 0)
        if key in _LINE_PROSE_CACHE and now - stamp < _LINE_PROSE_CACHE_TTL:
            return _LINE_PROSE_CACHE[key]
    prose = build_prose(
        line, stops,
        schedule_rd=schedule_rd, schedule_sat=schedule_sat,
        interchange=interchange,
        lang=lang, lang_prefix=lang_prefix,
    )
    with _LINE_PROSE_CACHE_LOCK:
        _LINE_PROSE_CACHE[key] = prose
        _LINE_PROSE_CACHE_STAMPS[key] = now
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
        departures = gtfs_by_line.get(line['number'])
        if not departures:
            # No real GTFS arrival for this line at this stop. We do NOT fabricate
            # a headway estimate: the page promises "ETA na osnovu zvaničnog GTFS
            # reda vožnje", and a made-up countdown is actively harmful on a transit
            # site — when stop_order is flat it printed an identical "4 min" for
            # every line, which is obviously fake and can make riders miss a bus.
            # Omit the line; the client renders "—" for any line without an entry.
            continue

        name = line['name'] or ''
        direction = name.split('—')[-1].strip() if '—' in name else name

        # Real GTFS times
        mins1 = _time_to_min(departures[0]) - current_min
        if mins1 < 0:
            mins1 = 0
        mins2 = _time_to_min(departures[1]) - current_min if len(departures) > 1 else mins1 + 15
        if mins2 < mins1:
            mins2 = mins1 + 15

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

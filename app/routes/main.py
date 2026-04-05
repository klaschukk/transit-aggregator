from datetime import datetime

from flask import Blueprint, render_template, request, make_response, jsonify, Response, current_app

from app.db import query, query_one, cached_query, cached_query_one, db_ready

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage with search form."""
    popular_routes = cached_query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km, COUNT(t.id) as trip_count
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity'
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km
        ORDER BY trip_count DESC
        LIMIT 8
    """) if db_ready() else []

    cities = cached_query("""
        SELECT DISTINCT from_city as city FROM routes WHERE type = 'intercity'
        UNION
        SELECT DISTINCT to_city FROM routes WHERE type = 'intercity'
        ORDER BY city
    """) if db_ready() else []
    cities_list = [c['city'] for c in cities]

    stats = {'routes': 0, 'lines': 0, 'stops': 0, 'cities': 0}
    if db_ready():
        row = cached_query_one("""
            SELECT
                (SELECT COUNT(*) FROM routes WHERE type = 'intercity') AS routes,
                (SELECT COUNT(*) FROM city_lines) AS lines,
                (SELECT COUNT(*) FROM city_stops) AS stops,
                (SELECT COUNT(DISTINCT city) FROM city_lines) AS cities
        """)
        if row:
            stats = dict(row)

    # Per-city stats for city cards
    cities_data = cached_query("""
        SELECT cl.city,
               COUNT(DISTINCT cl.id) as line_count,
               (SELECT COUNT(*) FROM city_stops cs WHERE cs.city = cl.city) as stop_count
        FROM city_lines cl
        GROUP BY cl.city
        ORDER BY COUNT(DISTINCT cl.id) DESC
    """) if db_ready() else []

    city_labels = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš'}
    for c in cities_data:
        c['label'] = city_labels.get(c['city'], c['city'].title())

    # Popular city lines (by number of stops)
    popular_lines = cached_query("""
        SELECT cl.number, cl.name, cl.slug, cl.color,
               COUNT(cls.stop_id) as stop_count
        FROM city_lines cl
        JOIN city_line_stops cls ON cls.line_id = cl.id
        WHERE cl.city = 'beograd'
        GROUP BY cl.id, cl.number, cl.name, cl.slug, cl.color
        ORDER BY stop_count DESC
        LIMIT 4
    """) if db_ready() else []

    return render_template('index.html', popular_routes=popular_routes,
                           cities=cities_list, stats=stats,
                           cities_data=cities_data,
                           popular_lines=popular_lines)


@main_bp.route('/pretraga/')
def search():
    """Search results page."""
    from_city = request.args.get('od', '').strip()
    to_city = request.args.get('do', '').strip()
    date = request.args.get('datum', '')

    results = []
    if from_city and to_city and db_ready():
        results = query("""
            SELECT t.departure_time, t.arrival_time, t.duration_min,
                   t.price_rsd, o.name as operator, r.from_city, r.to_city
            FROM trips t
            JOIN routes r ON r.id = t.route_id
            JOIN operators o ON o.id = t.operator_id
            WHERE lower(r.from_city) = lower(?) AND lower(r.to_city) = lower(?)
            ORDER BY t.departure_time
        """, [from_city, to_city])

    # Hide past departures for today
    now_time = datetime.now().strftime('%H:%M')
    if not date or date == datetime.now().strftime('%Y-%m-%d'):
        results = [r for r in results if (r.get('departure_time') or '') >= now_time]

    # Min price for summary header
    min_price = None
    if results:
        prices = [r['price_rsd'] for r in results if r.get('price_rsd')]
        min_price = min(prices) if prices else None

    # Popular routes for search landing (when no query)
    popular_routes = []
    if not from_city and not to_city and db_ready():
        popular_routes = query("""
            SELECT r.slug, r.from_city, r.to_city, COUNT(t.id) as trip_count,
                   MIN(t.price_rsd) as min_price_rsd
            FROM routes r
            LEFT JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity'
            GROUP BY r.id, r.slug, r.from_city, r.to_city
            ORDER BY trip_count DESC
            LIMIT 6
        """)

    return render_template('search_results.html',
                           results=results, from_city=from_city,
                           to_city=to_city, datum=date,
                           min_price=min_price,
                           popular_routes=popular_routes)


@main_bp.route('/api/cities')
def api_cities():
    """Return city list for autocomplete."""
    q = request.args.get('q', '').strip().lower()
    if len(q) < 1 or not db_ready():
        return jsonify([])

    cities = query("""
        SELECT DISTINCT from_city as name FROM routes WHERE type = 'intercity' AND lower(from_city) LIKE ?
        UNION
        SELECT DISTINCT to_city FROM routes WHERE type = 'intercity' AND lower(to_city) LIKE ?
        ORDER BY name
        LIMIT 8
    """, [f'{q}%', f'{q}%'])

    return jsonify([c['name'] for c in cities])


@main_bp.route('/health')
def health():
    db_ok = db_ready()
    status = 'ok' if db_ok else 'degraded'
    return jsonify({'status': status, 'service': 'transit-serbia', 'db': db_ok})


@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate sitemap with lastmod, proper priorities, filtered stops."""
    from pathlib import Path
    base = current_app.config['BASE_URL']

    # DB lastmod: use file modification time
    db_path = Path(current_app.config['DUCKDB_PATH'])
    if db_path.exists():
        lastmod = datetime.fromtimestamp(db_path.stat().st_mtime).strftime('%Y-%m-%d')
    else:
        lastmod = datetime.now().strftime('%Y-%m-%d')

    def url(loc: str, freq: str, prio: str, mod: str = lastmod) -> str:
        return f'<url><loc>{base}{loc}</loc><lastmod>{mod}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>'

    pages = [
        url('/', 'daily', '1.0'),
        url('/rute/', 'weekly', '0.8'),
        url('/gradski/', 'weekly', '0.7'),
        url('/gradski/beograd/', 'weekly', '0.8'),
        url('/prevoznici/', 'monthly', '0.5'),
        url('/autobuske-stanice/', 'monthly', '0.5'),
        url('/o-nama/', 'monthly', '0.3'),
        url('/kontakt/', 'monthly', '0.3'),
    ]

    if db_ready():
        # Intercity routes (all have trips — verified)
        routes = cached_query("SELECT slug FROM routes WHERE type = 'intercity'", ttl=3600)
        for r in routes:
            pages.append(url(f'/rute/{r["slug"]}/', 'daily', '0.7'))

        # SEO city-pair pages
        routes2 = cached_query("SELECT from_city_slug, to_city_slug FROM routes WHERE type = 'intercity'", ttl=3600)
        for r in routes2:
            pages.append(url(f'/voznja/{r["from_city_slug"]}-do-{r["to_city_slug"]}/', 'weekly', '0.6'))

        # City lines
        lines = cached_query("SELECT city, slug FROM city_lines", ttl=3600)
        for line in lines:
            pages.append(url(f'/gradski/{line["city"]}/linija/{line["slug"]}/', 'weekly', '0.5'))

        # Stops: only those with 2+ lines (meaningful content, avoids thin pages)
        stops = cached_query("""
            SELECT cs.slug, cs.city
            FROM city_stops cs
            JOIN city_line_stops cls ON cls.stop_id = cs.id
            GROUP BY cs.slug, cs.city
            HAVING COUNT(cls.line_id) >= 2
        """, ttl=3600)
        for s in stops:
            pages.append(url(f'/gradski/{s["city"]}/stajaliste/{s["slug"]}/', 'weekly', '0.4'))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(pages)
    xml += '\n</urlset>'
    resp = make_response(xml)
    resp.headers['Content-Type'] = 'application/xml'
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp


@main_bp.route('/robots.txt')
def robots():
    base = current_app.config['BASE_URL']
    lines = [
        'User-agent: *',
        'Allow: /',
        '',
        'Disallow: /api/',
        'Disallow: /health',
        'Disallow: /pretraga/?*',
        '',
        f'Sitemap: {base}/sitemap.xml',
    ]
    resp = make_response('\n'.join(lines) + '\n')
    resp.headers['Content-Type'] = 'text/plain'
    return resp

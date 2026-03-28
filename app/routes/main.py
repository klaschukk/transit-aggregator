from flask import Blueprint, render_template, request

from app.db import query

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage with search form."""
    popular_routes = query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km, COUNT(t.id) as trip_count
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km
        ORDER BY trip_count DESC
        LIMIT 10
    """) if _db_ready() else []

    return render_template('index.html', popular_routes=popular_routes)


@main_bp.route('/pretraga/')
def search():
    """Search results page."""
    from_city = request.args.get('od', '').strip()
    to_city = request.args.get('do', '').strip()
    date = request.args.get('datum', '')

    results = []
    if from_city and to_city and _db_ready():
        results = query("""
            SELECT t.departure_time, t.arrival_time, t.duration_min,
                   t.price_rsd, o.name as operator, r.from_city, r.to_city
            FROM trips t
            JOIN routes r ON r.id = t.route_id
            JOIN operators o ON o.id = t.operator_id
            WHERE lower(r.from_city) = lower(?) AND lower(r.to_city) = lower(?)
            ORDER BY t.departure_time
        """, [from_city, to_city])

    return render_template('search_results.html',
                           results=results,
                           from_city=from_city,
                           to_city=to_city,
                           date=date)


@main_bp.route('/health')
def health():
    from flask import jsonify
    return jsonify({'status': 'ok', 'country': 'RS', 'service': 'transit-serbia'})


def _db_ready() -> bool:
    """Check if database file exists and has tables."""
    from flask import current_app
    from pathlib import Path
    return Path(current_app.config['DUCKDB_PATH']).exists()


@main_bp.route('/sitemap.xml')
def sitemap():
    from flask import Response, current_app
    from app.db import query

    pages = []
    base = 'https://benovite.com'  # replace with actual domain

    pages.append(f'<url><loc>{base}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>')
    pages.append(f'<url><loc>{base}/rute/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')

    if _db_ready():
        routes = query("SELECT slug FROM routes WHERE type = 'intercity'")
        for r in routes:
            pages.append(f'<url><loc>{base}/rute/{r["slug"]}/</loc><changefreq>daily</changefreq><priority>0.7</priority></url>')

        routes2 = query("SELECT from_city_slug, to_city_slug FROM routes WHERE type = 'intercity'")
        for r in routes2:
            pages.append(f'<url><loc>{base}/voznja/{r["from_city_slug"]}-do-{r["to_city_slug"]}/</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>')

        lines = query("SELECT city, slug FROM city_lines")
        for line in lines:
            pages.append(f'<url><loc>{base}/gradski/{line["city"]}/linija/{line["slug"]}/</loc><changefreq>weekly</changefreq><priority>0.5</priority></url>')

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(pages)
    xml += '\n</urlset>'
    return Response(xml, mimetype='application/xml')


@main_bp.route('/robots.txt')
def robots():
    from flask import Response
    txt = "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n"
    return Response(txt, mimetype='text/plain')

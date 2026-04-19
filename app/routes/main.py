from datetime import datetime

from flask import Blueprint, render_template, request, make_response, jsonify, current_app

from app.db import query, cached_query, cached_query_one, db_ready
from app.extensions import limiter

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
@limiter.limit("30 per minute")
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
    import os
    import tempfile
    db_ok = db_ready()

    logs_ok = False
    logs_dir = os.path.join(current_app.root_path, '..', 'logs')
    try:
        os.makedirs(logs_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=logs_dir, prefix='.healthcheck-', delete=True
        ) as f:
            f.write(b'ok')
        logs_ok = True
    except OSError:
        logs_ok = False

    status = 'ok' if (db_ok and logs_ok) else 'degraded'
    code = 200 if status == 'ok' else 503
    return jsonify({
        'status': status,
        'service': 'prevozni',
        'db': db_ok,
        'logs_writable': logs_ok,
    }), code


# ── Sitemap helpers ───────────────────────────────────────────────────
#
# Sitemap is split into one index + five shards (core / routes / pairs /
# lines / stops). Google reports indexation per-sitemap, so separate shards
# let us see which content type is stuck in "Discovered not indexed"
# instead of staring at one aggregate number. Each shard is also smaller
# and refetched independently when its content changes — nightly data
# refresh only bumps the lastmod on routes/pairs/stops, not core.


def _sitemap_lastmod() -> str:
    from pathlib import Path
    db_path = Path(current_app.config['DUCKDB_PATH'])
    if db_path.exists():
        return datetime.fromtimestamp(db_path.stat().st_mtime).strftime('%Y-%m-%d')
    return datetime.now().strftime('%Y-%m-%d')


def _urlset(pages: list[str]) -> "Response":  # noqa: F821
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(pages)
        + '\n</urlset>'
    )
    resp = make_response(xml)
    resp.headers['Content-Type'] = 'application/xml'
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp


def _build_url_fn(base: str, lastmod: str):
    """Return an `url(loc, freq, prio)` fn that emits one <url> per language
    with full hreflang alternates. Shared by every sitemap shard."""
    from app.i18n import SUPPORTED_LANGS, DEFAULT_LANG

    def _loc_for(lang: str, loc: str) -> str:
        if lang == DEFAULT_LANG:
            return f'{base}{loc}'
        return f'{base}/{lang}{loc}'

    def url(loc: str, freq: str, prio: str, mod: str = lastmod) -> str:
        alternates = ''.join(
            f'<xhtml:link rel="alternate" hreflang="{l}" href="{_loc_for(l, loc)}"/>'
            for l in SUPPORTED_LANGS
        )
        alternates += (
            f'<xhtml:link rel="alternate" hreflang="x-default" '
            f'href="{_loc_for(DEFAULT_LANG, loc)}"/>'
        )
        parts = []
        for l in SUPPORTED_LANGS:
            parts.append(
                f'<url><loc>{_loc_for(l, loc)}</loc>'
                f'<lastmod>{mod}</lastmod><changefreq>{freq}</changefreq>'
                f'<priority>{prio}</priority>{alternates}</url>'
            )
        return ''.join(parts)

    return url


@main_bp.route('/sitemap.xml')
def sitemap_index():
    """Sitemap-index pointing at the five content-type shards.

    Kept at the canonical /sitemap.xml location so existing GSC submissions
    and the robots.txt `Sitemap:` line keep working; Google treats an index
    here identically to a urlset.
    """
    base = current_app.config['BASE_URL']
    lastmod = _sitemap_lastmod()
    shards = ['core', 'routes', 'pairs', 'lines', 'stops']
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for shard in shards:
        xml += (
            f'<sitemap><loc>{base}/sitemap-{shard}.xml</loc>'
            f'<lastmod>{lastmod}</lastmod></sitemap>\n'
        )
    xml += '</sitemapindex>'
    resp = make_response(xml)
    resp.headers['Content-Type'] = 'application/xml'
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp


@main_bp.route('/sitemap-core.xml')
def sitemap_core():
    """Hub/landing pages — home, catalogs, city hubs, about/contact."""
    base = current_app.config['BASE_URL']
    url = _build_url_fn(base, _sitemap_lastmod())
    pages = [
        url('/', 'daily', '1.0'),
        url('/rute/', 'weekly', '0.8'),
        url('/gradski/', 'weekly', '0.7'),
        url('/gradski/beograd/', 'weekly', '0.8'),
        url('/gradski/novi-sad/', 'weekly', '0.7'),
        url('/gradski/nis/', 'weekly', '0.7'),
        url('/gradski/kragujevac/', 'weekly', '0.7'),
        url('/prevoznici/', 'monthly', '0.5'),
        url('/autobuske-stanice/', 'monthly', '0.5'),
        url('/destinacije/', 'weekly', '0.7'),
        url('/destinacije/crna-gora/', 'weekly', '0.7'),
        url('/destinacije/bosna/', 'weekly', '0.7'),
        url('/destinacije/hrvatska/', 'weekly', '0.7'),
        url('/destinacije/makedonija/', 'weekly', '0.7'),
        url('/vodici/', 'weekly', '0.6'),
        url('/vodici/kako-doci-beograd-budva/', 'monthly', '0.5'),
        url('/vodici/najjeftinije-autobus-karte-srbija/', 'monthly', '0.5'),
        url('/vodici/autobus-ili-voz-srbija/', 'monthly', '0.5'),
        url('/o-nama/', 'monthly', '0.3'),
        url('/kontakt/', 'monthly', '0.3'),
        url('/privatnost/', 'monthly', '0.2'),
    ]
    return _urlset(pages)


@main_bp.route('/sitemap-routes.xml')
def sitemap_routes():
    """Intercity route-detail pages (/rute/<slug>/) + operator-detail pages
    (/prevoznici/<slug>/). Both are hub-like catalog entries; same shard
    keeps their freshness signal aligned with the routes table."""
    base = current_app.config['BASE_URL']
    url = _build_url_fn(base, _sitemap_lastmod())
    pages: list[str] = []
    if db_ready():
        routes = cached_query("""
            SELECT r.slug FROM routes r
            WHERE r.type = 'intercity'
              AND EXISTS (SELECT 1 FROM trips t WHERE t.route_id = r.id AND t.price_rsd > 0)
        """, ttl=3600)
        for r in routes:
            pages.append(url(f'/rute/{r["slug"]}/', 'daily', '0.7'))

        operators = cached_query("""
            SELECT DISTINCT o.slug FROM operators o
            JOIN trips t ON t.operator_id = o.id
            WHERE o.slug IS NOT NULL
        """, ttl=3600)
        for op in operators:
            pages.append(url(f'/prevoznici/{op["slug"]}/', 'weekly', '0.5'))
    return _urlset(pages)


@main_bp.route('/sitemap-pairs.xml')
def sitemap_pairs():
    """SEO city-pair pages (/voznja/<from>-do-<to>/). Same trips filter."""
    base = current_app.config['BASE_URL']
    url = _build_url_fn(base, _sitemap_lastmod())
    pages: list[str] = []
    if db_ready():
        pairs = cached_query("""
            SELECT r.from_city_slug, r.to_city_slug FROM routes r
            WHERE r.type = 'intercity'
              AND EXISTS (SELECT 1 FROM trips t WHERE t.route_id = r.id AND t.price_rsd > 0)
        """, ttl=3600)
        for r in pairs:
            pages.append(
                url(f'/voznja/{r["from_city_slug"]}-do-{r["to_city_slug"]}/',
                    'weekly', '0.6')
            )
    return _urlset(pages)


@main_bp.route('/sitemap-lines.xml')
def sitemap_lines():
    """City transit line-detail pages (/gradski/<city>/linija/<slug>/)."""
    base = current_app.config['BASE_URL']
    url = _build_url_fn(base, _sitemap_lastmod())
    pages: list[str] = []
    if db_ready():
        lines = cached_query("SELECT city, slug FROM city_lines", ttl=3600)
        for line in lines:
            pages.append(
                url(f'/gradski/{line["city"]}/linija/{line["slug"]}/',
                    'weekly', '0.5')
            )
    return _urlset(pages)


@main_bp.route('/sitemap-stops.xml')
def sitemap_stops():
    """City stop-detail pages (/gradski/<city>/stajaliste/<slug>/). Only
    stops with 2+ lines AND coordinates — thin single-line stops stay out
    of the index to save crawl budget."""
    base = current_app.config['BASE_URL']
    url = _build_url_fn(base, _sitemap_lastmod())
    pages: list[str] = []
    if db_ready():
        stops = cached_query("""
            SELECT DISTINCT cs.slug, cs.city
            FROM city_stops cs
            JOIN city_line_stops cls ON cls.stop_id = cs.id
            WHERE cs.lat IS NOT NULL
            GROUP BY cs.slug, cs.city
            HAVING COUNT(DISTINCT cls.line_id) >= 2
        """, ttl=3600)
        for s in stops:
            pages.append(
                url(f'/gradski/{s["city"]}/stajaliste/{s["slug"]}/',
                    'monthly', '0.2')
            )
    return _urlset(pages)


@main_bp.route('/offline.html')
def offline_page():
    """Cached by the service worker as the offline fallback shell."""
    return render_template('offline.html')


@main_bp.route('/sw.js')
def service_worker():
    """Service worker — must be served from the site root so its scope
    covers the whole app. Flask's /static/ would scope it to /static/."""
    from pathlib import Path
    sw_path = Path(current_app.root_path) / 'static' / 'js' / 'sw.js'
    body = sw_path.read_text(encoding='utf-8')
    resp = make_response(body)
    resp.headers['Content-Type'] = 'application/javascript'
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    resp.headers['Service-Worker-Allowed'] = '/'
    return resp


@main_bp.route('/robots.txt')
def robots():
    base = current_app.config['BASE_URL']
    # Disallow AI-training crawlers. They don't send traffic back, so
    # letting them index wastes server resources and exposes original
    # content (scraped timetables, FAQ prose) to models that won't cite
    # or link back. Search-engine bots (Google/Bing/Yandex) stay allowed.
    ai_bots = (
        'GPTBot',           # OpenAI
        'ChatGPT-User',     # OpenAI on-demand browsing
        'OAI-SearchBot',    # OpenAI SearchGPT
        'ClaudeBot',        # Anthropic
        'anthropic-ai',     # legacy Anthropic name
        'Claude-Web',       # legacy Claude web crawler
        'Google-Extended',  # Google Gemini/Bard training (NOT Googlebot)
        'CCBot',            # Common Crawl (feeds most open LLMs)
        'PerplexityBot',    # Perplexity
        'Bytespider',       # ByteDance / TikTok
        'Amazonbot',        # Alexa / Amazon AI
        'cohere-ai',        # Cohere
        'FacebookBot',      # Meta AI training
        'Diffbot',          # crawl-for-resale aggregator
    )
    lines = [
        '# AI training crawlers — block (no traffic return, content reuse risk)',
    ]
    for bot in ai_bots:
        lines.append(f'User-agent: {bot}')
        lines.append('Disallow: /')
        lines.append('')

    lines += [
        '# All other crawlers (Googlebot, Bingbot, YandexBot, …)',
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

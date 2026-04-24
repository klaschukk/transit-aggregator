import re
import time
from datetime import datetime

from flask import Blueprint, render_template, request, make_response, jsonify, current_app

from app.db import query, cached_query, cached_query_one, db_ready
from app.extensions import limiter, csrf

main_bp = Blueprint('main', __name__)


# Minimal profanity list (sr / en / ru). Intentionally short — false-positive
# rate on a free-text review form is worse than letting the occasional slur
# through to the moderation queue.
_PROFANITY = (
    'kurac', 'jebi', 'jeba', 'pizda', 'picka', 'govno',
    'fuck', 'shit', 'bitch', 'asshole',
    'хуй', 'пизд', 'бляд', 'сука',
)

# Allow prevozni.com links in comments; strip all other URLs.
_URL_RE = re.compile(r'\bhttps?://\S+', re.IGNORECASE)
_EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
_SLUG_RE = re.compile(r'^[a-z0-9][a-z0-9\-]{1,199}$')


def _validate_review(form: dict) -> tuple[str | None, dict]:
    """Return (error_key, cleaned_fields). error_key is None on success."""
    # Honeypot — any content means bot.
    if (form.get('website') or '').strip():
        return 'review.error.spam', {}

    # Minimum fill time (defeats the dumbest submit-on-load bots).
    try:
        loaded_at = float(form.get('loaded_at') or '0')
    except ValueError:
        loaded_at = 0.0
    if loaded_at and time.time() - loaded_at < 3.0:
        return 'review.error.too_fast', {}

    try:
        rating = int(form.get('rating') or '0')
    except (ValueError, TypeError):
        rating = 0
    if not 1 <= rating <= 5:
        return 'review.error.rating', {}

    comment = (form.get('comment') or '').strip()
    if not 50 <= len(comment) <= 500:
        return 'review.error.comment_length', {}

    # Strip non-prevozni URLs; if stripping is needed, reject so the
    # author knows their link was dropped rather than silently mangling.
    for m in _URL_RE.finditer(comment):
        host = m.group(0).split('/', 3)[2].lower() if '/' in m.group(0)[8:] else ''
        if 'prevozni.com' not in host:
            return 'review.error.no_urls', {}

    lower = comment.lower()
    if any(w in lower for w in _PROFANITY):
        return 'review.error.profanity', {}

    name = (form.get('name') or '').strip()
    if not 2 <= len(name) <= 40:
        return 'review.error.name_length', {}

    email = (form.get('email') or '').strip()[:100]
    if email and not _EMAIL_RE.match(email):
        return 'review.error.email_invalid', {}

    return None, {
        'rating': rating, 'comment': comment, 'name': name, 'email': email,
    }


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


@main_bp.route('/api/review/<route_slug>', methods=['POST'])
@limiter.limit("3 per hour")
def api_review_submit(route_slug):
    """Submit a user review for a route. CSRF-protected (form POST, not JSON).
    Goes to moderation queue by default; trusted authors auto-approve."""
    from app import analytics_db
    from app.extensions import _client_ip
    from app.notifier import notify_admin
    from flask import g

    if not _SLUG_RE.match(route_slug or ''):
        return jsonify(error='bad_route'), 400

    error_key, cleaned = _validate_review(request.form.to_dict())
    if error_key:
        return jsonify(error=error_key), 400

    # Trusted auto-approve is opt-in — see config REVIEWS_AUTO_APPROVE_TRUSTED.
    # Default 'false' matches the 100%-manual spec for the first month.
    auto_approve = (
        current_app.config.get('REVIEWS_AUTO_APPROVE_TRUSTED')
        and analytics_db.is_trusted_author(cleaned['email'])
    )
    status = 'approved' if auto_approve else 'pending'

    review_id = analytics_db.insert_review(
        route_slug=route_slug,
        rating=cleaned['rating'],
        comment=cleaned['comment'],
        author_name=cleaned['name'],
        email=cleaned['email'],
        lang=getattr(g, 'lang', 'sr'),
        ip=_client_ip(),
        status=status,
    )
    if review_id is None:
        return jsonify(error='db_error'), 500

    if status == 'pending':
        notify_admin(
            subject='Nova recenzija čeka moderaciju',
            body=(
                f'Route: {route_slug}\nRating: {cleaned["rating"]}★\n'
                f'Author: {cleaned["name"]}\n\n'
                f'{cleaned["comment"]}\n\n'
                f'Approve: /admin/reviews/{review_id}/approve'
            ),
        )

    return jsonify(
        ok=True, status=status, review_id=review_id,
        message='review.ok.auto' if status == 'approved' else 'review.ok.pending',
    ), 202


@main_bp.route('/api/reviews/<route_slug>', methods=['GET'])
def api_reviews_list(route_slug):
    """Public JSON feed of approved reviews for a route, 5-min cached."""
    from app import analytics_db

    if not _SLUG_RE.match(route_slug or ''):
        return jsonify(error='bad_route'), 400

    items = []
    for r in analytics_db.approved_reviews(route_slug):
        items.append({
            'id': r['id'], 'rating': r['rating'],
            'comment': r['comment'], 'author_name': r['author_name'],
            'lang': r['lang'], 'ts': r['ts'].isoformat() if r.get('ts') else None,
        })
    agg = analytics_db.aggregate_rating(route_slug)
    resp = jsonify(aggregate=agg, reviews=items)
    resp.headers['Cache-Control'] = 'public, max-age=300'
    return resp


@main_bp.route('/api/review/<int:review_id>/delete-request', methods=['POST'])
@limiter.limit("5 per hour")
@csrf.exempt
def api_review_delete_request(review_id):
    """Mark a review for admin-confirmed deletion. Requester proves ownership
    by re-entering the email they submitted with. We return `ok: true` on
    mismatch too — an attacker can't enumerate review ownership."""
    from app import analytics_db
    from app.notifier import notify_admin

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    email = (data.get('email') or '').strip()
    if not _EMAIL_RE.match(email):
        return jsonify(ok=False), 400

    ok = analytics_db.request_review_deletion(review_id, email)
    if ok:
        notify_admin(
            subject='GDPR: zahtev za brisanje recenzije',
            body=f'Review id {review_id} marked deletion_requested=True.\n'
                 f'Confirm in /admin/reviews (Delete button).',
        )
    return jsonify(ok=True), 200


@main_bp.route('/api/ba-click', methods=['POST'])
@limiter.limit("60 per minute")
@csrf.exempt
def api_ba_click():
    """Log a Bookaway affiliate click for per-route CTR + later revenue
    attribution. Client POSTs a small JSON payload and opens the Bookaway
    URL itself — we never redirect here so there's no open-redirect surface."""
    from app.analytics_db import insert_ba_click
    from app.extensions import _client_ip

    data = request.get_json(silent=True) or {}

    route_slug = str(data.get('route_slug', ''))[:200]
    surface = str(data.get('surface', ''))[:40]
    operator = str(data.get('operator', ''))[:100]
    trip_time = str(data.get('trip_time', ''))[:10]

    # Surface allowlist — prevents cardinality bloat from bogus values.
    if surface and surface not in (
        'search', 'route_detail', 'city_pair', 'route_detail_global',
        'city_pair_global', 'search_global',
    ):
        surface = 'other'

    insert_ba_click(
        route_slug=route_slug,
        surface=surface,
        operator=operator,
        trip_time=trip_time,
        ip=_client_ip(),
        user_agent=request.headers.get('User-Agent', '')[:300],
        referrer=request.headers.get('Referer', '')[:500],
    )
    return '', 204


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
    """Structured health probe for cron + ops dashboards.

    Contract: always returns JSON (never raises); HTTP 200 only when every
    critical check is green, 503 otherwise. Never leaks tracebacks or paths
    outside the project root — exposed to the public internet behind
    Cloudflare but not gated.

    Checks are deliberately cheap (<50ms total): filesystem stat, a COUNT(*)
    against a cached connection, and a last-refresh marker file. Heavier
    probes belong in /admin/* dashboards, not on a cron-polled endpoint.
    """
    import json
    import os
    import shutil
    import tempfile
    from pathlib import Path

    from app import APP_START_TIME, _ASSET_VERSION

    checks: dict = {}
    critical_ok = True  # transit_db + logs — sets overall http code
    degraded = False    # analytics_db, nightly — surfaces but doesn't 503

    # ── transit_db: file present, age, route count ──────────────────────
    db_path_str = current_app.config['DUCKDB_PATH']
    db_path = Path(db_path_str)
    transit = {'ok': False, 'age_hours': None, 'routes': None}
    if db_path.exists():
        try:
            age_s = time.time() - db_path.stat().st_mtime
            transit['age_hours'] = round(age_s / 3600, 1)
        except OSError:
            pass
        try:
            row = cached_query_one(
                "SELECT COUNT(*) AS c FROM routes", ttl=60
            )
            transit['routes'] = int(row['c']) if row else None
            transit['ok'] = bool(transit['routes'])
        except Exception:  # noqa: BLE001 — /health must never raise
            transit['ok'] = False
    if not transit['ok']:
        critical_ok = False
    # Stale data warning — nightly refresh didn't run or failed silently.
    if transit['age_hours'] is not None and transit['age_hours'] > 36:
        degraded = True
    checks['transit_db'] = transit

    # ── analytics_db: writable (ba_clicks insert path) ──────────────────
    analytics = {'ok': False}
    try:
        from app import analytics_db
        rows = analytics_db.query("SELECT COUNT(*) AS c FROM ba_clicks")
        if rows:
            analytics['ok'] = True
            analytics['clicks_total'] = int(rows[0]['c'])
    except Exception:  # noqa: BLE001
        analytics['ok'] = False
    if not analytics['ok']:
        degraded = True
    checks['analytics_db'] = analytics

    # ── logs dir writable (gunicorn access/error) ───────────────────────
    logs_dir = Path(current_app.root_path).parent / 'logs'
    logs_ok = False
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=str(logs_dir), prefix='.healthcheck-', delete=True
        ) as f:
            f.write(b'ok')
        logs_ok = True
    except OSError:
        logs_ok = False
    if not logs_ok:
        critical_ok = False
    checks['logs_writable'] = logs_ok

    # ── disk free % on the partition hosting the project ────────────────
    try:
        usage = shutil.disk_usage(str(logs_dir.parent))
        free_pct = round(usage.free * 100.0 / usage.total, 1)
        checks['disk_free_pct'] = free_pct
        # <10% free means the nightly snapshot will OOM the partition soon.
        if free_pct < 10:
            degraded = True
    except OSError:
        checks['disk_free_pct'] = None

    # ── nightly refresh status (written by scripts/nightly_refresh.sh) ──
    nightly = {'last_run': None, 'status': None, 'age_hours': None}
    marker = logs_dir / 'last_refresh.json'
    try:
        if marker.exists():
            payload = json.loads(marker.read_text(encoding='utf-8'))
            nightly['last_run'] = payload.get('finished_at')
            nightly['status'] = payload.get('status')
            finished_ts = payload.get('finished_ts')
            if finished_ts:
                nightly['age_hours'] = round(
                    (time.time() - float(finished_ts)) / 3600, 1
                )
    except (OSError, ValueError, TypeError):
        pass
    if nightly['status'] == 'fail':
        degraded = True
    # Haven't heard from nightly in >30h — probably cron is broken.
    if nightly['age_hours'] is not None and nightly['age_hours'] > 30:
        degraded = True
    checks['nightly'] = nightly

    # ── derived ─────────────────────────────────────────────────────────
    uptime = int(time.time() - APP_START_TIME)
    if not critical_ok:
        status = 'down'
        code = 503
    elif degraded:
        status = 'degraded'
        code = 200  # degraded shouldn't page — only hard failures do
    else:
        status = 'ok'
        code = 200

    return jsonify({
        'status': status,
        'service': 'prevozni',
        'version': _ASSET_VERSION,
        'uptime_seconds': uptime,
        'checks': checks,
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
        url('/uslovi/', 'monthly', '0.2'),
        url('/politika-kolacica/', 'monthly', '0.2'),
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


@main_bp.route('/omiljeno/')
def favourites():
    """Client-side favourites list — content is rendered from localStorage
    by JS. Server just returns an empty shell so the URL is shareable and
    has proper meta tags."""
    return render_template('favourites.html')


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
        'Disallow: /admin/',
        'Disallow: /health',
        'Disallow: /pretraga/?*',
        '',
        f'Sitemap: {base}/sitemap.xml',
    ]
    resp = make_response('\n'.join(lines) + '\n')
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@main_bp.route('/ads.txt')
def ads_txt():
    """AdSense / IAB ads.txt — populated once AdSense approves; served as
    empty (single informational comment) so crawlers don't see 404 during
    the application review window. Replace the body once Google issues a
    publisher ID.

    Ref: https://iabtechlab.com/ads-txt/
    """
    ads_id = current_app.config.get('ADSENSE_ID', '').strip()
    if ads_id:
        # pub-1234567890 → google.com, pub-1234567890, DIRECT, f08c47fec0942fa0
        body = f'google.com, {ads_id}, DIRECT, f08c47fec0942fa0\n'
    else:
        body = '# ads.txt — AdSense pending. Will be populated once Google issues publisher ID.\n'
    resp = make_response(body)
    resp.headers['Content-Type'] = 'text/plain'
    return resp

import json as _json
import re
import time
from pathlib import Path
import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, make_response, jsonify, current_app, abort, redirect, Response, stream_with_context

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
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(t.id) as trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) as min_price_rsd
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity'
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km
        ORDER BY trip_count DESC
        LIMIT 10
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
                   t.price_rsd, o.name as operator, r.from_city, r.to_city,
                   t.bt4_line_id
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
                   MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) as min_price_rsd
            FROM routes r
            LEFT JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity'
            GROUP BY r.id, r.slug, r.from_city, r.to_city
            ORDER BY trip_count DESC
            LIMIT 6
        """)

    # Far-destination AI fallback: no local trips for this pair, but the
    # destination is somewhere Bookaway sells (Asia, Middle East, ...). Offer an
    # AI-composed itinerary (filled client-side from /api/compose-route) plus a
    # Bookaway CTA, so the user plans the trip here instead of bouncing to
    # Google. /pretraga is noindex — this is the dynamic Phase-1 surface; static
    # indexable pages for the most-searched far pairs come later (Phase 2).
    far = None
    bookaway_offer = None
    if from_city and to_city and not results:
        from app.ai_compose import far_pair_info
        far = far_pair_info(from_city, to_city)
        if far:
            from app.affiliates import resolve_offers
            offers = resolve_offers(
                far['from_slug'], far['to_slug'], from_city, to_city, 'search',
            )
            bookaway_offer = next(
                (o for o in offers if o.partner_key == 'bookaway'), None,
            )

    resp = make_response(render_template('search_results.html',
                                         results=results, from_city=from_city,
                                         to_city=to_city, datum=date,
                                         min_price=min_price,
                                         popular_routes=popular_routes,
                                         far=far, bookaway_offer=bookaway_offer))
    resp.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return resp


@main_bp.route('/api/compose-route')
@limiter.limit("12 per 5 minutes", key_func=lambda: request.remote_addr or 'anon')
def api_compose_route():
    """JSON: an AI-composed itinerary for a far pair (Beograd->Bangkok). Cached
    per pair+lang in analytics so Groq is hit at most once. Returns 400 for a
    pair that isn't a known far destination, 503 when the model is unavailable
    (the page already shows the Bookaway CTA, so the UX degrades gracefully)."""
    from flask import g
    from app import analytics_db
    from app.ai_compose import far_pair_info, compose_itinerary_via_groq

    from_city = request.args.get('od', '').strip()[:80]
    to_city = request.args.get('do', '').strip()[:80]
    # The fetch is path-prefix-less (/api/...), so g.lang defaults to sr; let the
    # page pass its language explicitly so EN/RU users get an EN/RU itinerary.
    lang = request.args.get('lang', '')
    if lang not in ('sr', 'en', 'ru'):
        lang = getattr(g, 'lang', 'sr')

    info = far_pair_info(from_city, to_city)
    if not info:
        return jsonify(error='not_far'), 400

    cached = analytics_db.get_composed_route(info['pair_key'], lang)
    if cached:
        return current_app.response_class(cached, content_type='application/json')

    api_key = current_app.config.get('GROQ_API_KEY', '')
    data = compose_itinerary_via_groq(from_city, to_city, lang, api_key)
    if not data:
        return jsonify(error='unavailable'), 503

    payload = _json.dumps(data, ensure_ascii=False)
    analytics_db.upsert_composed_route(info['pair_key'], lang, from_city, to_city, payload)
    return current_app.response_class(payload, content_type='application/json')


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
    partner = str(data.get('partner', ''))[:40]

    # Surface allowlist — prevents cardinality bloat from bogus values.
    if surface and surface not in (
        'search', 'route_detail', 'city_pair', 'route_detail_global',
        'city_pair_global', 'search_global',
    ):
        surface = 'other'

    # Partner allowlist — same anti-cardinality guard. Unknown keys bucket to
    # 'other' so the per-partner breakdown stays clean.
    if partner and partner not in ('bookaway', 'busticket4', 'flixbus'):
        partner = 'other'

    insert_ba_click(
        route_slug=route_slug,
        surface=surface,
        operator=operator,
        trip_time=trip_time,
        partner=partner,
        ip=_client_ip(),
        user_agent=request.headers.get('User-Agent', '')[:300],
        referrer=request.headers.get('Referer', '')[:500],
    )
    return '', 204


@main_bp.route('/api/ab-convert', methods=['POST'])
@limiter.limit("120 per minute")
@csrf.exempt
def api_ab_convert():
    """Record one A/B conversion event.

    Payload (JSON):
        experiment: string, must match a live experiment key
        event:      string, free-form (e.g. "click", "submit"); stored
                    as event_type='conv:<event>' so 'exposure' rows are
                    never confused with conversions.
        variant:    optional override; usually we read it from the
                    `ab_<experiment>` cookie that ab_variant() set.
        value:      optional float (default 1.0) — used when conversion
                    has a magnitude (price clicked, dwell-time, etc.).

    Always returns 204 on accepted-or-dropped — never reveals whether the
    experiment exists, so a hostile crawler can't enumerate live tests.
    """
    from app import ab as _ab
    from app import ab_config as _ab_config

    data = request.get_json(silent=True) or {}
    exp = str(data.get('experiment', ''))[:80]
    event = str(data.get('event', ''))[:60]
    variant = data.get('variant')
    if variant is not None:
        variant = str(variant)[:80]
    try:
        value = float(data.get('value', 1.0))
    except (TypeError, ValueError):
        value = 1.0

    if not exp or not event:
        return '', 204
    spec = _ab_config.get_spec(exp)
    if spec is None:
        return '', 204
    # Validate variant if caller passed one — otherwise track_conversion
    # reads the sticky cookie.
    if variant is not None and variant not in spec.variants:
        return '', 204

    _ab.track_conversion(
        experiment=exp, event=event, value=value, variant=variant,
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


@main_bp.route('/favicon.ico')
def favicon():
    """Browsers and Googlebot request /favicon.ico at the root; serve the
    static .ico so the request is a 200, not a 404."""
    return current_app.send_static_file('favicon/favicon.ico')


@main_bp.route('/site.webmanifest')
def site_webmanifest():
    """PWA manifest rendered dynamically so icon URLs carry ?v=asset_version.
    A static manifest cached its icons forever — Chrome/Android kept showing
    the old launcher icon after a rebrand. The version query busts that on
    each deploy (already-installed PWAs still need a reinstall, by design)."""
    resp = make_response(render_template('site.webmanifest'))
    resp.headers['Content-Type'] = 'application/manifest+json'
    return resp


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

    # ── transit_db: file present, age, every load-bearing table ────────
    #
    # Apr 25 incident: build_db.py unlinked the DB and recreated every
    # table EXCEPT line_geometries (populated by a separate scraper).
    # /health only checked `routes` count, so it stayed 200 while
    # /gradski/<city>/linija/<slug>/ silently 500'd for ~17h before
    # log-spam revealed the gap. Probe each load-bearing table with a
    # COUNT(*) and 503 the whole probe if any are missing/empty.
    #
    # Tables in the list MUST be pre-populated by the nightly pipeline.
    # Don't add tables that legitimately can be empty (gtfs_*, stations
    # for cities without train data, etc.) — false positives erode
    # trust in the 503 signal.
    _CRITICAL_TABLES = (
        'routes', 'trips',
        'city_lines', 'city_stops', 'city_line_stops',
        'operators',
    )
    # Populated by scrape_route_geometries.py (runs separately, 30-60 min).
    # Empty on fresh deploys — warn but don't 503.
    _WARN_TABLES = ('line_geometries',)

    db_path_str = current_app.config['DUCKDB_PATH']
    db_path = Path(db_path_str)
    transit: dict = {'ok': False, 'age_hours': None, 'routes': None,
                     'tables': {}, 'missing': []}
    if db_path.exists():
        try:
            age_s = time.time() - db_path.stat().st_mtime
            transit['age_hours'] = round(age_s / 3600, 1)
        except OSError:
            pass
        for tbl in _CRITICAL_TABLES:
            count: int | None = None
            try:
                row = cached_query_one(
                    f"SELECT COUNT(*) AS c FROM {tbl}", ttl=60
                )
                count = int(row['c']) if row else 0
            except Exception:  # noqa: BLE001 — /health must never raise
                count = None  # missing or unreadable
            transit['tables'][tbl] = count
            if not count:
                transit['missing'].append(tbl)
        # Back-compat alias for existing dashboards / cron alerts.
        transit['routes'] = transit['tables'].get('routes')
        transit['ok'] = not transit['missing']
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
    nightly: dict = {'last_run': None, 'status': None, 'age_hours': None}
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
            # Per-scraper status (added 2026-04-27 — see follow-up doc).
            # Surface the names of any scraper whose last run failed so a
            # human glancing at /health knows which source-key to mistrust.
            scrapers = payload.get('scrapers') or {}
            failed_scrapers = sorted(
                k for k, v in scrapers.items()
                if isinstance(v, str) and v.startswith('fail')
            )
            if failed_scrapers:
                nightly['failed_scrapers'] = failed_scrapers
                # A partial-failure isn't critical (data is stale, not gone),
                # but it's a degraded signal worth bumping into /health.
                degraded = True
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


# ── Per-URL lastmod (real freshness signal) ────────────────────────────
#
# Replaces the flat "all URLs share transit.duckdb mtime" signal. Each URL
# now carries the date of its underlying scraper output, so Google sees
# genuine deltas across runs and prioritises freshly-rescraped URLs in
# the crawl queue. No new DB column — derive from data/raw/*.json mtimes
# (one date per scraper) plus a small (operator-slug → source) map.
#
# Cache the per-URL lookup for 5 minutes so we don't hit the filesystem
# 3500× per crawl (each Googlebot fetch of the index → 4 shards → render).

_LASTMOD_CACHE: dict = {'ts': 0.0, 'src': {}, 'lookup': {}}
_LASTMOD_TTL_S = 300


def _file_date(path) -> str | None:
    try:
        if path.exists():
            return datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d')
    except OSError:
        pass
    return None


def _source_mtimes() -> dict[str, str]:
    """Latest data-file mtime per scraper source. Keys identify the
    scraper that owns a given table-row; values are the date that
    scraper last produced output. New scraper sources go here."""
    from pathlib import Path
    raw = Path(current_app.root_path).parent / 'data' / 'raw'
    sources = {
        'busticket4_dom':   raw / 'intercity_routes.json',
        'busticket4_intl':  raw / 'international_routes.json',
        'busticket4_pairs': raw / 'intercity' / 'routes.json',
        'lasta':            raw / 'lasta' / 'trips.json',
        'balkan':           raw / 'balkan_routes.json',
        'srbvoz':           raw / 'srbvoz_trains.json',
        'gsp_lines':        raw / 'gsp_lines.json',
        'gsp_stops':        raw / 'gsp_stops.json',
        'gspns_lines':      raw / 'novi-sad' / 'lines.json',
        'gspns_stops':      raw / 'novi-sad' / 'osm_stops.json',
        'gspns_stops_v1':   raw / 'novi_sad_osm_stops.json',
        'gspns_route_stops': raw / 'novi_sad_route_stops.json',
        'nis_lines':        raw / 'nis' / 'lines.json',
        'nis_stops':        raw / 'nis' / 'stops.json',
        'nis_route_stops':  raw / 'nis_route_stops.json',
        'kragujevac':       raw / 'kragujevac' / 'lines.json',
    }
    out = {}
    for k, p in sources.items():
        d = _file_date(p)
        if d:
            out[k] = d
    return out


# Operator slug → scraper source key. Most operators are scraped via
# busticket4_dom (the umbrella domestic-bus catalogue). Lasta + Srbija
# Voz have dedicated scrapers. Anything not in the map falls back to
# busticket4_dom so we always have *some* signal.
_OP_SOURCE = {
    'lasta':         'lasta',
    'srbija-voz':    'srbvoz',
    'srbijavoz':     'srbvoz',
    'srbija_voz':    'srbvoz',
}


def _city_line_source(city: str) -> str:
    return {
        'beograd':    'gsp_lines',
        'novi-sad':   'gspns_lines',
        'nis':        'nis_lines',
        'kragujevac': 'kragujevac',
    }.get(city, 'gsp_lines')


def _city_stop_source(city: str) -> tuple[str, str | None]:
    """Two source keys per city: the stops scrape, and the route-stops
    linkage scrape if separate. Per-stop lastmod = MAX of both."""
    return {
        'beograd':    ('gsp_stops', None),
        'novi-sad':   ('gspns_stops', 'gspns_route_stops'),
        'nis':        ('nis_stops',  'nis_route_stops'),
        'kragujevac': ('kragujevac', None),
    }.get(city, ('gsp_stops', None))


def _build_lastmod_lookup(default_mtime: str) -> dict:
    """Pre-compute every URL → date mapping in one TTL window.

    Returns nested dict: {category: {key: 'YYYY-MM-DD'}} where category
    is one of 'route', 'op', 'line', 'stop' and key is the row slug
    (for routes/ops/stops) or '<city>/<slug>' (for lines)."""
    now = time.time()
    if now - _LASTMOD_CACHE['ts'] < _LASTMOD_TTL_S and _LASTMOD_CACHE['lookup']:
        return _LASTMOD_CACHE['lookup']

    src = _source_mtimes()
    lookup = {'route': {}, 'op': {}, 'line': {}, 'stop': {}}

    if not db_ready():
        _LASTMOD_CACHE['ts'] = now
        _LASTMOD_CACHE['src'] = src
        _LASTMOD_CACHE['lookup'] = lookup
        return lookup

    # Routes — one row per route_slug, MAX over the operator-source mtimes
    # serving that route. International routes get the busticket4_intl
    # mtime as a floor; balkan routes pick up balkan mtime.
    route_rows = query("""
        SELECT r.slug, r.from_city_slug, r.to_city_slug, r.from_city, r.to_city,
               LIST(DISTINCT o.slug) AS op_slugs
        FROM routes r
        JOIN trips t ON t.route_id = r.id
        JOIN operators o ON o.id = t.operator_id
        WHERE r.type = 'intercity'
        GROUP BY r.slug, r.from_city_slug, r.to_city_slug, r.from_city, r.to_city
    """)
    intl_cities = {
        'Sarajevo','Banja Luka','Tuzla','Mostar','Trebinje','Zenica',
        'Zagreb','Split','Dubrovnik','Rijeka','Osijek','Vukovar','Pula','Zadar',
        'Skopje','Skoplje','Ohrid','Bitola','Bitolj','Kumanovo','Štip',
        'Ljubljana','Maribor','Koper','Celje',
        'Tirana','Drač','Drac','Skadar','Vlora',
        'Thessaloniki','Solun','Atina','Athens','Patras',
        'Sofia','Sofija','Plovdiv','Varna','Burgas',
        'Podgorica','Budva','Herceg Novi','Kotor','Tivat','Bar','Nikšić',
        'Ulcinj','Cetinje','Bijelo Polje',
        'Budapest','Vienna','Istanbul',
    }
    for row in route_rows:
        # Source-file mtimes only — no default_mtime in the MAX, otherwise
        # the global db rebuild date wins every comparison and flattens
        # the per-URL signal.
        candidates: list[str] = []
        if row['op_slugs']:
            for op_slug in row['op_slugs']:
                key = _OP_SOURCE.get(op_slug, 'busticket4_dom')
                if key in src:
                    candidates.append(src[key])
        if row['from_city'] in intl_cities or row['to_city'] in intl_cities:
            for k in ('busticket4_intl', 'balkan'):
                if k in src:
                    candidates.append(src[k])
        d = max(candidates) if candidates else default_mtime
        lookup['route'][row['slug']] = d
        # Pairs share the same date — same SQL row, different URL shape.
        if row['from_city_slug'] and row['to_city_slug']:
            lookup['route'][f'{row["from_city_slug"]}-do-{row["to_city_slug"]}'] = d

    # Operators — MAX over their own scraper + the routes they cover.
    # An operator scraped today on a corridor that hasn't changed since
    # last week still gets today's date because the operator-page itself
    # is the underlying signal.
    op_rows = query("""
        SELECT o.slug, MIN(r.id) AS _any
        FROM operators o
        JOIN trips t ON t.operator_id = o.id
        JOIN routes r ON r.id = t.route_id
        WHERE t.price_rsd > 0
        GROUP BY o.slug
    """)
    for row in op_rows:
        op_slug = row['slug']
        key = _OP_SOURCE.get(op_slug, 'busticket4_dom')
        lookup['op'][op_slug] = src.get(key, default_mtime)

    # Lines — by city.
    line_rows = query("SELECT city, slug FROM city_lines")
    for row in line_rows:
        key = _city_line_source(row['city'])
        lookup['line'][f'{row["city"]}/{row["slug"]}'] = src.get(key, default_mtime)

    # Stops — by city, MAX of stops-source and route-stops-linkage source.
    stop_rows = query("SELECT slug, city FROM city_stops")
    for row in stop_rows:
        s_key, link_key = _city_stop_source(row['city'])
        candidates: list[str] = []
        if s_key in src:
            candidates.append(src[s_key])
        if link_key and link_key in src:
            candidates.append(src[link_key])
        lookup['stop'][f'{row["city"]}/{row["slug"]}'] = (
            max(candidates) if candidates else default_mtime
        )

    _LASTMOD_CACHE['ts'] = now
    _LASTMOD_CACHE['src'] = src
    _LASTMOD_CACHE['lookup'] = lookup
    return lookup


def _lastmod_for(category: str, key: str, default: str) -> str:
    """Look up per-URL lastmod from the precomputed dict. Falls back to
    the global db mtime when no row-level signal is available (new
    scraper, missing source file, etc.)."""
    lookup = _build_lastmod_lookup(default)
    return lookup.get(category, {}).get(key, default)


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
    """Return an `url(loc, freq, prio)` fn that emits ONE <url> per logical
    page with hreflang alternates pointing at every locale.

    Earlier shape emitted N <url> tags (one per locale), each with the same
    alternate-set — tripling sitemap size to ~9k URLs and starving Google's
    crawl budget on a young site (GSC: 7355 "Discovered, currently not
    indexed", almost all /en/ + /ru/ variants).

    Google's localized-versions guidance treats one canonical <loc> with
    hreflang alternates as equivalent to multiple <loc>s — Googlebot follows
    the alternates and discovers the per-locale URLs anyway, just spread
    across crawl cycles instead of all submitted at once. Trade-off: slower
    discovery of /en/ + /ru/ pages, but the /sr/ canonical (90% of traffic)
    actually gets crawled.
    """
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
        return (
            f'<url><loc>{_loc_for(DEFAULT_LANG, loc)}</loc>'
            f'<lastmod>{mod}</lastmod><changefreq>{freq}</changefreq>'
            f'<priority>{prio}</priority>{alternates}</url>'
        )

    return url


@main_bp.route('/sitemap.xml')
def sitemap_index():
    """Sitemap-index pointing at the content-type shards.

    Kept at the canonical /sitemap.xml location so existing GSC submissions
    and the robots.txt `Sitemap:` line keep working; Google treats an index
    here identically to a urlset.
    """
    base = current_app.config['BASE_URL']
    lastmod = _sitemap_lastmod()
    # 'pairs' is intentionally NOT listed: every indexable /voznja/ pair
    # canonicalises onto its /rute/ owner (already in sitemap-routes), and
    # pairs with no owner are noindex — so the shard only ever held
    # non-canonical/noindex URLs (a mixed signal Google should not be fed
    # via the sitemap). /rute/ pages cover the same content. The
    # /sitemap-pairs.xml route is kept (empty urlset) for legacy submissions.
    shards = ['core', 'routes', 'lines', 'stops']
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
        url('/destinacije/slovenija/', 'weekly', '0.7'),
        url('/destinacije/albanija/', 'weekly', '0.7'),
        url('/destinacije/grcka/', 'weekly', '0.7'),
        url('/destinacije/bugarska/', 'weekly', '0.7'),
        url('/vodici/', 'weekly', '0.6'),
        url('/vodici/kako-doci-beograd-budva/', 'monthly', '0.5'),
        url('/vodici/najjeftinije-autobus-karte-srbija/', 'monthly', '0.5'),
        url('/vodici/autobus-ili-voz-srbija/', 'monthly', '0.5'),
        url('/vodici/beograd-novi-sad/', 'monthly', '0.7'),
        url('/vodici/prevoz-do-mora/', 'monthly', '0.7'),
        url('/vodici/flixbus-srbija/', 'monthly', '0.6'),
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
    keeps their freshness signal aligned with the routes table.

    Per-URL lastmod: route → MAX scraper-source mtime over operators
    serving that route. Operator → mtime of its dedicated scraper
    (lasta/srbvoz) or the busticket4 umbrella catalogue."""
    base = current_app.config['BASE_URL']
    default_mtime = _sitemap_lastmod()
    url = _build_url_fn(base, default_mtime)
    pages: list[str] = []
    if db_ready():
        routes = cached_query("""
            SELECT r.slug FROM routes r
            WHERE r.type = 'intercity'
              AND EXISTS (SELECT 1 FROM trips t WHERE t.route_id = r.id AND t.price_rsd > 0)
        """, ttl=3600)
        for r in routes:
            mod = _lastmod_for('route', r['slug'], default_mtime)
            pages.append(url(f'/rute/{r["slug"]}/', 'daily', '0.7', mod=mod))

        # Operators must have at least one PRICED trip — without a price the
        # operator_detail page renders an empty route list (the handler filters
        # routes by `t.price_rsd > 0`), producing ~660-byte soft-404 pages
        # that waste crawl budget. Audit on 2026-04-26 found 49/70 operators
        # in this state. The healthy 21 all have ≥1 priced trip.
        operators = cached_query("""
            SELECT DISTINCT o.slug FROM operators o
            JOIN trips t ON t.operator_id = o.id
            WHERE o.slug IS NOT NULL AND t.price_rsd > 0
        """, ttl=3600)
        for op in operators:
            mod = _lastmod_for('op', op['slug'], default_mtime)
            pages.append(url(f'/prevoznici/{op["slug"]}/', 'weekly', '0.5', mod=mod))
    return _urlset(pages)


@main_bp.route('/sitemap-pairs.xml')
def sitemap_pairs():
    """Deprecated shard — intentionally empty.

    /voznja/<from>-do-<to>/ city-pair pages are an alternate URL shape over
    the same route row as /rute/<slug>/. Every pair that has a backing route
    canonicalises (canonical + hreflang) onto its /rute/ owner; pairs with no
    owner are noindex. So this shard could only ever list non-canonical or
    noindex URLs — a mixed signal that contradicts the canonical we declare on
    the pages themselves. The canonical /rute/ URLs already live in
    sitemap-routes.xml, and Google discovers /voznja/ via internal links.

    The route is kept (vs. removed) so legacy GSC submissions and any cached
    sitemap-index reference resolve to a valid, empty urlset — telling Google
    the URLs are gone from the sitemap rather than 404-ing the shard. It is no
    longer referenced from /sitemap.xml.

    Far-destination guides (/voznja/<sr>-do-<far>/) do NOT belong here either —
    they have their own shard, sitemap-far.xml, which lists only pairs with a
    cached composed itinerary (i.e. actually indexable pages)."""
    return _urlset([])


@main_bp.route('/sitemap-lines.xml')
def sitemap_lines():
    """City transit line-detail pages (/gradski/<city>/linija/<slug>/).

    Per-URL lastmod: per-city scraper output mtime (gsp_lines.json,
    novi-sad/lines.json, nis/lines.json, kragujevac/lines.json)."""
    base = current_app.config['BASE_URL']
    default_mtime = _sitemap_lastmod()
    url = _build_url_fn(base, default_mtime)
    pages: list[str] = []
    if db_ready():
        lines = cached_query("SELECT city, slug FROM city_lines", ttl=3600)
        for line in lines:
            mod = _lastmod_for('line',
                               f'{line["city"]}/{line["slug"]}',
                               default_mtime)
            pages.append(
                url(f'/gradski/{line["city"]}/linija/{line["slug"]}/',
                    'weekly', '0.5', mod=mod)
            )
    return _urlset(pages)


@main_bp.route('/sitemap-stops.xml')
def sitemap_stops():
    """City stop-detail pages (/gradski/<city>/stajaliste/<slug>/). Only
    stops with 2+ lines AND coordinates — thin single-line stops stay out
    of the index to save crawl budget.

    Per-URL lastmod: MAX of (city-stops scrape mtime, route-stops
    linkage scrape mtime). Picks up the older signal when stops were
    re-scraped but their line-linkage table wasn't."""
    base = current_app.config['BASE_URL']
    default_mtime = _sitemap_lastmod()
    url = _build_url_fn(base, default_mtime)
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
            mod = _lastmod_for('stop',
                               f'{s["city"]}/{s["slug"]}',
                               default_mtime)
            pages.append(
                url(f'/gradski/{s["city"]}/stajaliste/{s["slug"]}/',
                    'monthly', '0.2', mod=mod)
            )
    return _urlset(pages)


@main_bp.route('/omiljeno/')
def favourites():
    """Client-side favourites list — content is rendered from localStorage
    by JS. Server just returns an empty shell so the URL is shareable and
    has proper meta tags."""
    return render_template('favourites.html')


# ── Open Graph card renderer ────────────────────────────────────────
# Per-page 1200×630 PNGs for share previews. The static og-image.png
# stays as the universal fallback; these dynamic variants ship a card
# with title + key facts so social referrals (Facebook, Twitter/X,
# LinkedIn, Telegram, Google Discover) get a relevant preview.

_OG_HEADERS = {
    'Content-Type': 'image/png',
    # 7 days: OG cards change only on nightly rebuild; disk cache absorbs
    # repeated social-bot hits without re-rendering via Pillow each time.
    'Cache-Control': 'public, max-age=604800, immutable',
}

_OG_CACHE_DIR = Path(__file__).parent.parent.parent / 'data' / 'cache' / 'og'
_OG_CACHE_TTL = 86400  # 24 h — regenerate if nightly data changed


def _og_cached(cache_key: str, generate) -> 'Response':
    """Return OG PNG from disk cache; generate + persist on miss."""
    _OG_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _OG_CACHE_DIR / f'{cache_key}.png'
    if cache_path.exists() and (time.time() - cache_path.stat().st_mtime) < _OG_CACHE_TTL:
        resp = make_response(cache_path.read_bytes())
        for k, v in _OG_HEADERS.items():
            resp.headers[k] = v
        return resp
    try:
        png = generate()
    except Exception:
        return _og_fallback()
    if png:
        try:
            cache_path.write_bytes(png)
        except OSError:
            pass
        return _og_response(png)
    return _og_fallback()


def _og_response(png_bytes: bytes):
    resp = make_response(png_bytes)
    for k, v in _OG_HEADERS.items():
        resp.headers[k] = v
    return resp


def _og_fallback():
    """Static fallback when DB lookup fails or slug doesn't resolve.
    Always returns 200 so social bots cache something rather than
    retry-storming a 404."""
    from app.og import static_fallback_bytes
    return _og_response(static_fallback_bytes())


@main_bp.route('/og/route/<slug>.png')
def og_route(slug: str):
    if not _SLUG_RE.match(slug):
        return _og_fallback()
    if not db_ready():
        return _og_fallback()
    row = cached_query_one("""
        SELECT r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) AS trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) AS min_price
        FROM routes r LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.slug = ? AND r.type = 'intercity'
        GROUP BY r.from_city, r.to_city, r.distance_km
    """, [slug])
    if not row:
        return _og_fallback()
    from app.og import render_card
    title = f"{row['from_city']} → {row['to_city']}"
    chips = []
    if row.get('distance_km'):
        chips.append(f"{int(row['distance_km'])} km")
    if row.get('trip_count'):
        chips.append(f"{row['trip_count']} polazaka")
    if row.get('min_price'):
        chips.append(f"od {int(row['min_price'])} RSD")
    return _og_cached(f'route-{slug}', lambda: render_card(title, subtitle='Direktni autobus', chips=chips))


@main_bp.route('/og/voznja/<from_city>-do-<to_city>.png')
def og_voznja(from_city: str, to_city: str):
    if not (_SLUG_RE.match(from_city) and _SLUG_RE.match(to_city)):
        return _og_fallback()
    if not db_ready():
        return _og_fallback()
    row = cached_query_one("""
        SELECT r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) AS trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) AS min_price
        FROM routes r LEFT JOIN trips t ON t.route_id = r.id
        WHERE lower(r.from_city_slug) = lower(?)
          AND lower(r.to_city_slug) = lower(?)
          AND r.type = 'intercity'
        GROUP BY r.from_city, r.to_city, r.distance_km
    """, [from_city, to_city])
    if not row:
        return _og_fallback()
    from app.og import render_card
    title = f"{row['from_city']} → {row['to_city']}"
    chips = []
    if row.get('distance_km'):
        chips.append(f"{int(row['distance_km'])} km")
    if row.get('trip_count'):
        chips.append(f"{row['trip_count']} polazaka")
    if row.get('min_price'):
        chips.append(f"od {int(row['min_price'])} RSD")
    return _og_cached(f'voznja-{from_city}-{to_city}', lambda: render_card(title, subtitle='Pretraga polazaka', chips=chips))


@main_bp.route('/og/line/<city>/<slug>.png')
def og_line(city: str, slug: str):
    if not (_SLUG_RE.match(city) and _SLUG_RE.match(slug)):
        return _og_fallback()
    if not db_ready():
        return _og_fallback()
    row = cached_query_one("""
        SELECT cl.number, cl.name, cl.type, cl.city,
               COUNT(cls.stop_id) AS stop_count
        FROM city_lines cl
        LEFT JOIN city_line_stops cls ON cls.line_id = cl.id
        WHERE cl.city = ? AND cl.slug = ?
        GROUP BY cl.id, cl.number, cl.name, cl.type, cl.city
    """, [city, slug])
    if not row:
        return _og_fallback()
    from app.og import render_card
    city_label = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad',
                  'nis': 'Niš', 'kragujevac': 'Kragujevac'}.get(city, city.title())
    type_label = {'tram': 'Tramvaj', 'trolleybus': 'Trolejbus',
                  'bus': 'Autobus', 'night': 'Noćna linija',
                  'e-bus': 'E-bus', 'suburban': 'Prigradska',
                  'bg-voz': 'BG:Voz'}.get(row.get('type') or '', 'Linija')
    title = f"Linija {row['number']}"
    sub = f"{city_label} · {row['name']}" if row.get('name') else city_label
    chips = [type_label]
    if row.get('stop_count'):
        chips.append(f"{row['stop_count']} stajališta")
    return _og_cached(f'line-{city}-{slug}', lambda: render_card(title, subtitle=sub, chips=chips))


@main_bp.route('/og/stop/<city>/<slug>.png')
def og_stop(city: str, slug: str):
    if not (_SLUG_RE.match(city) and _SLUG_RE.match(slug)):
        return _og_fallback()
    if not db_ready():
        return _og_fallback()
    row = cached_query_one("""
        SELECT cs.name, cs.city,
               COUNT(DISTINCT cls.line_id) AS line_count
        FROM city_stops cs
        LEFT JOIN city_line_stops cls ON cls.stop_id = cs.id
        WHERE cs.city = ? AND cs.slug = ?
        GROUP BY cs.id, cs.name, cs.city
    """, [city, slug])
    if not row:
        return _og_fallback()
    from app.og import render_card
    city_label = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad',
                  'nis': 'Niš', 'kragujevac': 'Kragujevac'}.get(city, city.title())
    title = row.get('name') or slug.replace('-', ' ').title()
    chips = [city_label]
    if row.get('line_count'):
        chips.append(f"{row['line_count']} linija")
    return _og_cached(f'stop-{city}-{slug}', lambda: render_card(title, subtitle='Stajalište', chips=chips))


@main_bp.route('/og/operator/<slug>.png')
def og_operator(slug: str):
    if not _SLUG_RE.match(slug):
        return _og_fallback()
    if not db_ready():
        return _og_fallback()
    row = cached_query_one("""
        SELECT o.name,
               COUNT(DISTINCT t.route_id) AS route_count,
               COUNT(DISTINCT r.from_city) + COUNT(DISTINCT r.to_city) AS city_count
        FROM operators o
        LEFT JOIN trips t ON t.operator_id = o.id
        LEFT JOIN routes r ON r.id = t.route_id AND r.type = 'intercity'
        WHERE o.slug = ?
        GROUP BY o.id, o.name
    """, [slug])
    if not row:
        return _og_fallback()
    from app.og import render_card
    title = row.get('name') or slug.replace('-', ' ').title()
    chips = []
    if row.get('route_count'):
        chips.append(f"{row['route_count']} ruta")
    if row.get('city_count'):
        chips.append(f"{row['city_count']} gradova")
    try:
        return _og_cached(f'operator-{slug}', lambda: render_card(title, subtitle='Prevoznik', chips=chips or ['Prevoznik']))
    except Exception:
        return _og_fallback()


@main_bp.route('/og/country/<slug>.png')
def og_country(slug: str):
    if not _SLUG_RE.match(slug):
        return _og_fallback()
    # Reuse country metadata from the country_hub handler so this stays
    # in sync if the country list grows.
    try:
        from app.routes.info import _COUNTRY_HUBS  # type: ignore[attr-defined]
    except Exception:
        return _og_fallback()
    info = _COUNTRY_HUBS.get(slug)
    if not info:
        return _og_fallback()
    name = info['name']
    chips: list[str] = ['Destinacija']
    if db_ready():
        cities = info.get('cities', [])
        if cities:
            placeholders = ', '.join(['?'] * len(cities))
            row = cached_query_one(
                f"""SELECT COUNT(DISTINCT r.id) AS n
                    FROM routes r JOIN trips t ON t.route_id = r.id
                    WHERE r.type = 'intercity' AND t.price_rsd > 0
                      AND (r.from_city IN ({placeholders})
                           OR r.to_city IN ({placeholders}))""",
                list(cities) + list(cities),
            )
            if row and row.get('n'):
                chips.append(f"{row['n']} ruta")
    from app.og import render_card
    try:
        return _og_cached(f'country-{slug}', lambda: render_card(name, subtitle='Autobusi iz Srbije', chips=chips))
    except Exception:
        return _og_fallback()


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


# IndexNow protocol — Bing/Yandex/Naver re-crawl in 5-30 minutes
# instead of the 3-14 days a young domain waits for organic
# crawl. The key file at /<key>.txt is the domain-ownership proof
# IndexNow checks before accepting our urlList POST. Key lives in
# data/secrets/indexnow.key (gitignored, mode 0600). Generate via:
#   python3 -c "import secrets; print(secrets.token_hex(16))" \
#     > data/secrets/indexnow.key
_INDEXNOW_KEY_RE = re.compile(r'^[a-f0-9]{32}$')


def _read_indexnow_key():
    from pathlib import Path
    p = Path(current_app.root_path).parent / 'data' / 'secrets' / 'indexnow.key'
    try:
        return p.read_text(encoding='utf-8').strip()
    except OSError:
        return None


@main_bp.route('/<key>.txt')
def indexnow_key_file(key: str):
    """Domain-ownership proof for IndexNow. The body is just the key
    itself; IndexNow's verifier hits the URL we name in keyLocation
    and checks the body matches the key in our urlList POST.

    Only matches 32-char hex slugs so this doesn't collide with any
    other .txt route — robots.txt + ads.txt continue to win because
    Flask matches them first in registration order.
    """
    if not _INDEXNOW_KEY_RE.match(key):
        abort(404)
    real = _read_indexnow_key()
    if not real or key != real:
        abort(404)
    resp = make_response(key)
    resp.headers['Content-Type'] = 'text/plain; charset=utf-8'
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp

@main_bp.route('/apple-touch-icon.png')
@main_bp.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    return redirect('/static/favicon/apple-touch-icon.png', code=301)


@main_bp.route('/sitemap_index.xml')
def sitemap_index_legacy():
    return redirect('/sitemap.xml', code=301)


@main_bp.route('/.well-known/traffic-advice')
def traffic_advice():
    resp = make_response('[]')
    resp.headers['Content-Type'] = 'application/trafficadvice+json'
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp


@main_bp.route('/ads.txt')
def ads_txt():
    """AdSense / IAB ads.txt — populated once AdSense approves; served as
    empty (single informational comment) so crawlers don't see 404 during
    the application review window. Replace the body once Google issues a
    publisher ID.

    Ref: https://iabtechlab.com/ads-txt/
    """
    # ads.txt uses the bare "pub-XXXX" publisher id, NOT the "ca-pub-XXXX" form
    # used by the AdSense JS client tag. Prefer ADSENSE_PUB_ID; strip a leading
    # "ca-" so it works whichever form is configured. A mismatched id (ca-pub-)
    # makes Google's ads.txt verification fail.
    ads_id = (current_app.config.get('ADSENSE_PUB_ID')
              or current_app.config.get('ADSENSE_ID') or '').strip()
    if ads_id.startswith('ca-'):
        ads_id = ads_id[3:]
    if ads_id:
        # pub-1234567890 → google.com, pub-1234567890, DIRECT, f08c47fec0942fa0
        body = f'google.com, {ads_id}, DIRECT, f08c47fec0942fa0\n'
    else:
        body = '# ads.txt — AdSense pending. Will be populated once Google issues publisher ID.\n'
    resp = make_response(body)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


# ── AI Chat widget ────────────────────────────────────────────────────────────

# Groq is fronted by Cloudflare, which 403s requests whose User-Agent looks
# like a bot (the urllib default "Python-urllib/x.y" is blocked). A plain
# product UA passes — without it every chat call fails and the widget hangs.
_CHAT_UA = 'PrevozniBot/1.0 (+https://prevozni.com)'
# 70B model: noticeably sharper answers than 8b-instant, still fast on Groq.
_CHAT_MODEL = 'llama-3.3-70b-versatile'

_CHAT_SYSTEM = """Ti si AI pomoćnik na sajtu Prevozni.com — besplatnom agregatu javnog prevoza u Srbiji (međugradski autobusi i vozovi + gradski prevoz).

Šta sajt pokriva:
- Međugradske rute autobusa i vozova širom Srbije, sa cenama karata, vremenima polazaka, prevoznicima (Lasta, Niš-Ekspres, Srbija Voz, BusTicket4.me itd.) i trajanjem putovanja.
- Gradski prevoz: Beograd, Novi Sad, Niš i Kragujevac — linije, stajališta i procene dolaska.
- Međunarodne linije ka Crnoj Gori, BiH, Hrvatskoj, Sloveniji, Makedoniji, Turskoj.

Kako da uputiš korisnika (uvek daj koristan sledeći korak — link ili putanju):
- Konkretna ruta između dva grada → /voznja/{od}-do-{do}/ (npr. /voznja/beograd-do-novi-sad/).
- Pretraga polazaka → /pretraga/?od=GRAD&do=GRAD.
- Gradski prevoz nekog grada → /gradski/{grad}/.
- Spisak svih ruta → /rute/.

Pravila:
- NAJVAŽNIJE: odgovori na ISTOM jeziku na kojem je poslednja poruka korisnika. Engleski upit → odgovor na engleskom. Ruski upit → odgovor na ruskom. Srpski upit → odgovor na srpskom. Nikada ne menjaj jezik korisnika.
- Budi kratak, ljubazan i konkretan: 1–3 rečenice + relevantan link/putanja.
- Ako u kontekstu stranice ima podataka (broj polazaka, cena, prevoznici), koristi ih; inače uputi korisnika na odgovarajuću stranicu.
- Nikad ne izmišljaj tačne cene, vremena ili polaske kojih nema u kontekstu — radije reci gde da ih proveri.
- Ne spominji konkurentske sajtove. Ostani u temi prevoza u Srbiji."""


def _chat_session_key() -> str:
    sid = request.cookies.get('chat_sid', '')
    return sid if (sid and len(sid) == 36) else 'anon'


@main_bp.route('/api/chat', methods=['POST'])
@csrf.exempt
@limiter.limit("20 per 5 minutes", key_func=_chat_session_key)
def api_chat():
    data = request.get_json(silent=True) or {}
    messages = data.get('messages', [])
    page_ctx = data.get('page_context', {})

    if not isinstance(messages, list) or not messages or len(messages) > 20:
        return jsonify(error='invalid'), 400

    safe = []
    for m in messages[-10:]:
        role = m.get('role', '')
        content = str(m.get('content', ''))[:800]
        if role in ('user', 'assistant') and content.strip():
            safe.append({'role': role, 'content': content})
    if not safe:
        return jsonify(error='invalid'), 400

    api_key = current_app.config.get('GROQ_API_KEY', '')
    if not api_key:
        return jsonify(error='unavailable'), 503

    system = _CHAT_SYSTEM
    if isinstance(page_ctx, dict) and page_ctx:
        system += '\n\nKontekst trenutne stranice:\n' + _json.dumps(page_ctx, ensure_ascii=False)

    import urllib.request as _ur
    payload = _json.dumps({
        'model': _CHAT_MODEL,
        'messages': [{'role': 'system', 'content': system}] + safe,
        'max_tokens': 350,
        'temperature': 0.6,
        'stream': True,
    }).encode()

    req = _ur.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'User-Agent': _CHAT_UA,
        },
        method='POST',
    )

    def _stream():
        try:
            with _ur.urlopen(req, timeout=15) as resp:
                for raw_line in resp:
                    line = raw_line.decode('utf-8').strip()
                    if not line.startswith('data:'):
                        continue
                    chunk = line[5:].strip()
                    if chunk == '[DONE]':
                        yield 'data: [DONE]\n\n'
                        return
                    try:
                        delta = _json.loads(chunk)['choices'][0]['delta'].get('content', '')
                        if delta:
                            yield f'data: {_json.dumps(delta, ensure_ascii=False)}\n\n'
                    except Exception:
                        continue
        except Exception:
            yield 'data: {"error":"unavailable"}\n\n'

    needs_sid = not request.cookies.get('chat_sid')
    new_sid = str(uuid.uuid4()) if needs_sid else ''

    sse = Response(
        stream_with_context(_stream()),
        content_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )
    if needs_sid:
        sse.set_cookie('chat_sid', new_sid, max_age=60 * 60 * 24 * 90, httponly=True, samesite='Lax')
    return sse

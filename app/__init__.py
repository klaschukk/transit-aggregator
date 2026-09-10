import logging
import os
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)

from flask import Flask, render_template, request, g, abort, make_response, redirect
from config import config_map
from .i18n import get_text, SUPPORTED_LANGS, DEFAULT_LANG
from .slug import transliterate_cyrillic_serbian
from . import observability


# Worker/process boot timestamp — exposed via /health as uptime_seconds so we
# can tell at a glance whether gunicorn just restarted (crashloop symptom).
APP_START_TIME = time.time()


def _compute_asset_version(root: Path) -> str:
    """Git SHA (short) at startup, fallback to app.css mtime."""
    git_bin = next(
        (p for p in ('/usr/bin/git', '/usr/local/bin/git') if Path(p).exists()),
        'git',
    )
    try:
        sha = subprocess.check_output(
            [git_bin, 'rev-parse', '--short', 'HEAD'],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            timeout=2,
        ).decode().strip()
        if sha:
            return sha
    except (subprocess.SubprocessError, OSError, FileNotFoundError):
        pass
    try:
        css = root / 'app' / 'static' / 'css' / 'app.css'
        return str(int(css.stat().st_mtime))
    except OSError:
        return 'dev'


_ASSET_VERSION = _compute_asset_version(Path(__file__).parent.parent)


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    # Defensive: a malformed unit/.env can leak the literal "FLASK_ENV=production"
    # into the value (double assignment), which crashed every gunicorn worker on
    # boot with KeyError → site-wide 5xx. Recover the real name instead of dying.
    if config_name not in config_map:
        recovered = config_name.split('=')[-1].strip()
        if recovered in config_map:
            logger.warning("Malformed FLASK_ENV %r; recovered as %r", config_name, recovered)
            config_name = recovered
        else:
            fallback = 'production' if 'production' in config_map else 'default'
            logger.error("Unknown FLASK_ENV %r; falling back to %r", config_name, fallback)
            config_name = fallback
    app.config.from_object(config_map[config_name])

    # Trust nginx's X-Forwarded-* headers so request.is_secure / request.remote_addr
    # reflect the original client request, not the loopback hop. Without this:
    # - Cookies miss the Secure flag (is_secure=False on HTTPS pages)
    # - Rate-limit keying buckets every visitor under 127.0.0.1
    # nginx is the only fronting proxy, so x_for=1, x_proto=1, x_host=1 is right.
    if config_name == 'production':
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=0,
        )

    if config_name == 'production' and not app.config.get('SECRET_KEY'):
        raise RuntimeError(
            "SECRET_KEY environment variable must be set in production"
        )

    # Sentry — no-op when SENTRY_DSN is empty (dev/tests). Must run before
    # blueprint registration so Flask error handlers below are already wired
    # with the integration's hooks.
    observability.init_sentry(
        dsn=app.config.get('SENTRY_DSN', ''),
        environment=app.config.get('SENTRY_ENV') or config_name,
        release=_ASSET_VERSION,
        traces_sample_rate=app.config.get('SENTRY_TRACES_SAMPLE_RATE', 0.1),
    )

    # ── www -> apex host redirect ──────────────────────────────────────
    # Cloudflare/nginx answer both prevozni.com and www.prevozni.com with
    # the identical origin response — no redirect, no canonical host
    # enforcement anywhere before this. Google was crawling www.* as a
    # fully separate, uncanonicalized copy of the whole site (35.7K of
    # the last 90 days' crawl requests went to the www host per GSC Crawl
    # stats, alongside 295K on the apex) — found 2026-09-10 investigating
    # slow post-outage traffic recovery. First before_request so it
    # short-circuits everything else (i18n detection, DB-ready check,
    # A/B cookie logic) for the ~10% of crawl hits that land here.
    @app.before_request
    def _redirect_www_to_apex():
        host = request.host.split(':', 1)[0]  # strip a dev-server port, if any
        if host == 'www.prevozni.com':
            target = f'https://prevozni.com{request.path}'
            if request.query_string:
                target += '?' + request.query_string.decode('utf-8')
            return redirect(target, code=301)

    # ── A/B framework: surface the per-browser ab_id on flask.g ────────
    # Cookie is only written back (in after_request) when at least one
    # experiment was actually rendered this request — keeps GDPR posture
    # clean for crawlers and one-shot static-page hits.
    @app.before_request
    def _ab_prepare_id():
        from app.ab import AB_ID_COOKIE
        existing = request.cookies.get(AB_ID_COOKIE) if request else None
        if existing:
            g.ab_id = existing

    @app.after_request
    def _ab_persist_cookies(response):
        from app.ab import response_cookies_for_variants, AB_ID_COOKIE
        to_persist = getattr(g, '_ab_to_persist', None) or []
        minted_id = getattr(g, '_ab_id_minted', False)
        if not to_persist and not minted_id:
            return response
        existing_id = request.cookies.get(AB_ID_COOKIE) if request else None
        new_id = getattr(g, 'ab_id', None) if minted_id and not existing_id else None
        for name, value, kwargs in response_cookies_for_variants(to_persist, new_id):
            response.set_cookie(name, value, **kwargs)
        return response

    # ── A/B Jinja global: ab_variant() works in every template render,
    # including error-handler renders (404/410/500) where a request-bound
    # context_processor occasionally doesn't fire. We never want a
    # template to die with `'ab_variant' is undefined`. Gracefully returns
    # the configured DEFAULT outside an app context (e.g. background-thread
    # renders) or when the experiment isn't live yet. ──
    def _ab_variant_global(key: str) -> str:
        from datetime import datetime as _dt, timezone as _tz
        from app import ab as _ab
        from app import ab_config as _ab_config
        spec = _ab_config.get_spec(key)
        default = _ab_config.DEFAULTS.get(key, '')
        if spec is None or not spec.is_live(_dt.now(_tz.utc).date().isoformat()):
            return default
        try:
            if not getattr(g, 'ab_id', None):
                import uuid as _uuid
                g.ab_id = _uuid.uuid4().hex
                g._ab_id_minted = True
            variant = _ab.assign(spec)
            if variant is None:
                return default
            queue = getattr(g, '_ab_to_persist', None)
            if queue is None:
                queue = []
                g._ab_to_persist = queue
            if not any(k == spec.key for k, _v in queue):
                queue.append((spec.key, variant))
            _ab.track_exposure(spec.key, variant, spec.surface)
            return variant
        except RuntimeError:
            return default
    app.jinja_env.globals['ab_variant'] = _ab_variant_global

    # ── Line-number badge: Cyrillic -> Latin at render time only ──────────
    # city_lines.number can carry a Cyrillic letter glued to Latin digits
    # ('105л', '25П') — a browser audit flagged badges reading "2Л"/"АДА1"
    # next to plain Latin "5"/"A1" in the same list. `number` also
    # participates in city_lines' UNIQUE (city, number) constraint, and
    # DuckDB 1.2.1 raises a spurious FK ConstraintException on ANY UPDATE
    # that touches a UNIQUE-constrained column once a child table
    # (city_line_stops) references the row — confirmed by testing that the
    # identical transliteration already applied in build_db.py to `name`
    # (not UNIQUE-constrained) works fine. Fixing it in storage would mean
    # either dropping/rebuilding the constraint mid-pipeline or moving every
    # scraper's INSERT to pre-latinise `number`, both riskier than this.
    #
    # Fixing it here instead is also strictly safer: /api/stop-arrivals
    # returns the SAME unmodified `number` from this column, and city.js
    # matches DOM elements by `data-line="{{ line.number }}"` against that
    # response. Only latinise the human-facing text (badges, titles, FAQ
    # copy) via this filter; never apply it to a `data-*` attribute — doing
    # so would desync the two and break every ETA lookup.
    app.jinja_env.filters['latin'] = transliterate_cyrillic_serbian

    # ── i18n: detect language from URL prefix ──
    @app.before_request
    def detect_language():
        # Check URL prefix: /en/... or /ru/...
        path = request.path
        g.lang = DEFAULT_LANG
        g.lang_prefix = ''
        for lang in SUPPORTED_LANGS:
            if lang != DEFAULT_LANG and (path == f'/{lang}' or path.startswith(f'/{lang}/')):
                g.lang = lang
                g.lang_prefix = f'/{lang}'
                break

    # ── DB-availability guard ──────────────────────────────────────────
    # The DuckDB file is briefly absent during the nightly rebuild
    # (db_ready() → False). Without this, the DB-backed detail handlers fall
    # through to abort(404), so Googlebot crawling that window logged live
    # pages as "Not found (404)" — the bulk of GSC's 1572. Serve 503 +
    # Retry-After for those paths instead, so crawlers come back and keep the
    # URL indexed. Static / info / robots / sitemap paths don't need the DB
    # and keep working.
    _DB_BACKED_PREFIXES = (
        '/rute', '/voznja', '/gradski', '/prevoznici',
        '/autobuske-stanice', '/pretraga',
    )

    @app.before_request
    def _serve_503_while_db_rebuilds():
        from app.db import db_ready
        if db_ready():
            return
        p = request.path
        for lp in ('/en', '/ru'):
            if p == lp or p.startswith(lp + '/'):
                p = p[len(lp):] or '/'
                break
        if p == '/' or p.startswith(_DB_BACKED_PREFIXES):
            abort(503)

    @app.context_processor
    def inject_i18n():
        lang = getattr(g, 'lang', DEFAULT_LANG)
        prefix = getattr(g, 'lang_prefix', '')

        def _(key: str) -> str:
            return get_text(key, lang)

        def lang_url(path: str, target_lang: str = '') -> str:
            """Build URL with language prefix."""
            if target_lang == DEFAULT_LANG or not target_lang:
                return path
            return f'/{target_lang}{path}'

        # Path without any language prefix — used for canonical/hreflang construction.
        path = request.path
        if prefix and (path == prefix or path.startswith(prefix + '/')):
            clean_path = path[len(prefix):] or '/'
        else:
            clean_path = path

        # Canonical/hreflang may point at a DIFFERENT path than the current
        # one: a route can set `g.canonical_path` to consolidate a duplicate
        # onto its owner (e.g. /voznja/<a>-do-<b>/ → its /rute/<slug>/ owner).
        # `clean_path` itself stays request-based so the language switcher and
        # other self-links keep pointing at the current page.
        canon_path = getattr(g, 'canonical_path', None) or clean_path

        # Per-variant canonical:
        #   sr (default) → BASE_URL + canon_path
        #   en/ru        → BASE_URL + /{lang} + canon_path
        base_url = app.config.get('BASE_URL', '')
        if lang == DEFAULT_LANG:
            canonical_url = base_url + canon_path
        else:
            canonical_url = f"{base_url}/{lang}{canon_path}"

        hreflang_urls = {}
        for l in SUPPORTED_LANGS:
            if l == DEFAULT_LANG:
                hreflang_urls[l] = base_url + canon_path
            else:
                hreflang_urls[l] = f"{base_url}/{l}{canon_path}"
        hreflang_urls['x-default'] = base_url + canon_path

        from datetime import datetime as _dt, timezone as _tz
        from app.affiliates import resolve_offers as _resolve_offers, ab_partner_order as _ab_order
        from app.affiliates import bt4_checkout_url as _bt4_checkout_url

        def affiliate_offers(from_slug, to_slug, from_city='', to_city='', utm_medium='trip-card'):
            """Template helper — resolves the ranked offer list for a pair.

            Applies the per-request A/B variant (cookie `ab_partner`, else
            deterministic from client IP) so the first offer is the one
            the user's variant wants promoted.
            """
            ab = _ab_order(
                request.cookies if request else None,
                seed=(request.remote_addr or '') if request else '',
            )
            return _resolve_offers(
                from_slug, to_slug, from_city, to_city, utm_medium, ab_choice=ab,
            )

        # Review-form anti-spam timestamp — embedded as hidden field so the
        # submit handler can check the user read the form for >3s before
        # sending. Computed once per request.
        import time as _time
        review_loaded_at = f'{_time.time():.3f}'

        # Single source of truth for the "see-also" country cross-link
        # widget (country_hub.html, carriers_index.html) — was previously
        # duplicated as two separately-hardcoded (slug, name) lists in
        # those templates, both of which silently missed every country
        # hub added after they were written (grcka/bugarska missing from
        # one, nemacka/turska/ceska/madjarska/austrija missing from both).
        from app.routes.info import _COUNTRY_HUBS as _country_hubs
        all_country_hubs = [(slug, info['name']) for slug, info in _country_hubs.items()]

        # `ab_variant` is registered as a Jinja global in create_app
        # (search for `_ab_variant_global`). Do NOT shadow it from this
        # context_processor — context-processor returns override
        # jinja_env.globals at template-resolve time, and a default-only
        # stub here would silently kill exposure tracking + cookie
        # issuance for the entire site.
        return {
            '_': _,
            'lang': lang,
            'lang_prefix': prefix,
            'lang_url': lang_url,
            'supported_langs': SUPPORTED_LANGS,
            'clean_path': clean_path,
            'canonical_url': canonical_url,
            'hreflang_urls': hreflang_urls,
            # Thin pages (route with no priced trips, pair with no route row)
            # set g.meta_robots = 'noindex, follow' to stay out of the index
            # while still passing link equity. Everything else is indexable.
            'meta_robots': getattr(g, 'meta_robots', 'index, follow, max-image-preview:large'),
            'asset_version': _ASSET_VERSION,
            'current_year': _dt.now(_tz.utc).year,
            'affiliate_offers': affiliate_offers,
            'bt4_checkout_url': _bt4_checkout_url,
            '_review_loaded_at': review_loaded_at,
            'all_country_hubs': all_country_hubs,
        }

    # Register blueprints
    from .routes.main import main_bp
    from .routes.intercity import intercity_bp
    from .routes.city import city_bp
    from .routes.info import info_bp
    from .routes.admin import admin_bp
    from .routes.subscribe import subscribe_bp

    # growth_bp owns /api/mailgun-webhook, /api/backlinks-unsubscribe and
    # /admin/backlinks. Wrapped so a missing module (mid-refactor) takes
    # only those endpoints down rather than the whole app.
    growth_bp = None
    try:
        from .routes.growth import growth_bp as _growth_bp
        growth_bp = _growth_bp
    except ImportError:
        pass

    app.register_blueprint(main_bp)
    app.register_blueprint(intercity_bp)
    app.register_blueprint(city_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(subscribe_bp)
    if growth_bp is not None:
        app.register_blueprint(growth_bp)

    # Register same blueprints under /en/ and /ru/ prefixes.
    # admin_bp stays unprefixed — dashboards don't need localisation.
    for lang in SUPPORTED_LANGS:
        if lang == DEFAULT_LANG:
            continue
        app.register_blueprint(main_bp, url_prefix=f'/{lang}', name=f'main_{lang}')
        app.register_blueprint(intercity_bp, url_prefix=f'/{lang}', name=f'intercity_{lang}')
        app.register_blueprint(city_bp, url_prefix=f'/{lang}', name=f'city_{lang}')
        app.register_blueprint(info_bp, url_prefix=f'/{lang}', name=f'info_{lang}')

    # Analytics schema init — idempotent, first request wins.
    from . import analytics_db
    with app.app_context():
        analytics_db.init_schema()
        # Seed the three baked-in newsletter drafts (welcome / weekly /
        # seasonal). Idempotent — refreshes existing rows, doesn't
        # duplicate. Skipped under testing so tests can build their
        # own fixture state without 3 drafts pre-populating the table.
        if os.environ.get('FLASK_ENV') != 'testing':
            try:
                from .newsletter import seed_drafts
                seed_drafts.seed()
            except Exception as exc:  # nosec — boot must not crash on drafts
                logger.warning('newsletter draft seed skipped: %s', exc)
                # A broken analytics-DB migration would otherwise be just one
                # WARNING while the app boots "healthy" — surface it in Sentry.
                observability.capture_exception(exc, subsystem='boot',
                                                phase='seed_drafts')
        # Drop the boot-thread connection so gunicorn's pre-fork workers
        # don't inherit a file descriptor pointing at analytics.duckdb.
        # Without this, every fork() leaves an open R/W lock owned by a
        # zombie connection in the master process, blocking any future
        # cross-process writer.
        analytics_db.close_thread_conn()

    # Close the per-thread analytics DB connection at the end of every
    # request so the R/W file lock isn't held between requests. Cross-
    # process writers (cron: adsense_fetch, price_snapshot, seed_reviews)
    # need windows when no Flask thread holds the lock; this hook gives
    # them one after every page render. _get_conn() reopens lazily on
    # the next request that needs it.
    @app.teardown_appcontext
    def _close_analytics_db(_exc):
        analytics_db.close_thread_conn()

    # Gzip compression
    from flask_compress import Compress
    Compress(app)

    # CSRF protection (flask-wtf). Runtime config WTF_CSRF_ENABLED can turn it off in tests.
    from .extensions import csrf
    csrf.init_app(app)

    # Rate limiting
    from .extensions import limiter
    limiter.init_app(app)

    from flask import jsonify
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify(error="rate_limit_exceeded", message=str(e.description)), 429

    # Cache headers. HTML uses `no-cache` (revalidate each hit) instead of
    # `no-store` — the latter blocks bfcache in all evergreen browsers and
    # Lighthouse flags it as a mobile UX regression. no-cache still forces
    # a round-trip for freshness but lets Back/Forward restore instantly.
    @app.after_request
    def add_cache_headers(response):
        path = request.path
        if path.startswith('/static/'):
            # Assets are versioned with ?v=<sha> — safe to cache 1 year
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif path.startswith('/og/'):
            # OG images keyed by slug — 7-day cache, regenerated nightly
            response.headers['Cache-Control'] = 'public, max-age=604800'
        elif 'text/html' in (response.content_type or ''):
            response.headers['Cache-Control'] = 'no-cache, must-revalidate'
        return response

    # Security headers.
    #   HSTS — forces browsers to use HTTPS for 2 years, includes subdomains,
    #     preload-eligible. Tells aggregators/scanners we're an HTTPS-only site.
    #   CSP — restrictive but practical: self + the external services we
    #     actually embed (Leaflet from unpkg, OSM tiles, Umami analytics,
    #     AdSense once enabled, Bookaway buy links). 'unsafe-inline' is
    #     required because Jinja templates still ship inline JSON-LD +
    #     inline <script> blocks (nav toggle, currency switcher, etc.) —
    #     converting those to hashed scripts is a separate refactor.
    #   Referrer-Policy + X-Content-Type-Options are belt-and-suspenders.
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault(
            'Strict-Transport-Security',
            'max-age=63072000; includeSubDomains; preload',
        )
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        # geolocation=(self): the city map's locate-me button centres the rider
        # and points out their nearest stop. An empty allowlist blocks the
        # Geolocation API for our own pages too, so the control would fail
        # silently. Third parties stay blocked — only this origin may ask, and
        # the browser still requires explicit user consent.
        response.headers.setdefault(
            'Permissions-Policy',
            'geolocation=(self), microphone=(), camera=(), payment=()',
        )
        if 'text/html' in (response.content_type or ''):
            # style-src/font-src allow fonts.googleapis.com/fonts.gstatic.com
            # for Google's own Funding Choices consent UI (CMP ID 300, footer
            # link) — it self-styles with Google Sans/Material Symbols and was
            # silently falling back to unstyled system fonts under CSP block,
            # confirmed via console: "violates ... style-src" on every page.
            response.headers.setdefault('Content-Security-Policy', (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' "
                "https://unpkg.com "
                "https://api.mapbox.com "
                "https://cloud.umami.is "
                "https://www.googletagmanager.com "
                "https://pagead2.googlesyndication.com "
                "https://*.googlesyndication.com "
                "https://adservice.google.com "
                "https://fundingchoicesmessages.google.com "
                "https://ep2.adtrafficquality.google; "
                "style-src 'self' 'unsafe-inline' "
                "https://unpkg.com https://api.mapbox.com "
                "https://fonts.googleapis.com; "
                "img-src 'self' data: blob: https:; "
                "font-src 'self' data: https://api.mapbox.com "
                "https://fonts.gstatic.com; "
                "connect-src 'self' "
                "https://cloud.umami.is "
                "https://gateway.umami.is "
                "https://api.mapbox.com "
                "https://events.mapbox.com "
                "https://*.mapbox.com "
                "https://tile.openstreetmap.org "
                "https://pagead2.googlesyndication.com "
                "https://*.googlesyndication.com "
                "https://googleads.g.doubleclick.net "
                "https://ep1.adtrafficquality.google "
                "https://fundingchoicesmessages.google.com "
                "https://csi.gstatic.com "
                "https://www.google-analytics.com "
                "https://*.google-analytics.com "
                "https://*.analytics.google.com "
                "https://stats.g.doubleclick.net; "
                "worker-src blob:; "
                "frame-src 'self' "
                "https://pagead2.googlesyndication.com "
                "https://*.googlesyndication.com "
                "https://googleads.g.doubleclick.net "
                "https://www.google.com "
                "https://fundingchoicesmessages.google.com "
                "https://ep2.adtrafficquality.google; "
                "base-uri 'self'; form-action 'self'; "
                "object-src 'none';"
            ))
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        # Without this, inject_i18n()'s context processor defaults
        # meta_robots to the indexable "index, follow" — a hard 404 has no
        # unique content to index, so it was shipping <meta name="robots"
        # content="index, follow"> on every not-found page (Google mostly
        # ignores meta robots on a true 4xx, but other crawlers/SEO
        # auditors don't, and it's simply wrong either way).
        g.meta_robots = 'noindex, follow'
        return render_template('404.html', status_code=404), 404

    @app.errorhandler(410)
    def gone(e):
        # Signal permanent removal so Google drops the URL faster than 404.
        # The template is shared with 404, so pass the code through rather
        # than let the page announce "404" over a 410 response.
        g.meta_robots = 'noindex, follow'
        return render_template('404.html', status_code=410), 410

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(503)
    def service_unavailable(e):
        # DB temporarily missing (nightly rebuild swaps the DuckDB file). Body
        # is inline on purpose — render_template would run the context
        # processor, which can touch request/DB state mid-rebuild. Retry-After
        # is the signal Google reads to come back instead of dropping the URL.
        html = (
            '<!doctype html><html lang="sr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="robots" content="noindex">'
            '<title>Trenutno nedostupno — Prevozni</title></head>'
            '<body style="font-family:system-ui,-apple-system,sans-serif;'
            'max-width:34rem;margin:4rem auto;padding:0 1rem;text-align:center;color:#0f172a">'
            '<h1 style="font-size:1.5rem">Osvežavamo podatke</h1>'
            '<p>Stranica je privremeno nedostupna. Pokušajte ponovo za koji minut.</p>'
            '</body></html>'
        )
        resp = make_response(html, 503)
        resp.headers['Retry-After'] = '120'
        return resp

    return app

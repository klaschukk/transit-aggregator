import os
import subprocess
from pathlib import Path

from flask import Flask, render_template, request, g
from config import config_map
from .i18n import get_text, SUPPORTED_LANGS, DEFAULT_LANG


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
    app.config.from_object(config_map[config_name])

    if config_name == 'production' and not app.config.get('SECRET_KEY'):
        raise RuntimeError(
            "SECRET_KEY environment variable must be set in production"
        )

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

        # Per-variant self-referencing canonical:
        #   sr (default) → BASE_URL + clean_path
        #   en/ru        → BASE_URL + /{lang} + clean_path
        base_url = app.config.get('BASE_URL', '')
        if lang == DEFAULT_LANG:
            canonical_url = base_url + clean_path
        else:
            canonical_url = f"{base_url}/{lang}{clean_path}"

        hreflang_urls = {}
        for l in SUPPORTED_LANGS:
            if l == DEFAULT_LANG:
                hreflang_urls[l] = base_url + clean_path
            else:
                hreflang_urls[l] = f"{base_url}/{l}{clean_path}"
        hreflang_urls['x-default'] = base_url + clean_path

        from datetime import datetime as _dt
        from app.affiliates import resolve_offers as _resolve_offers, ab_partner_order as _ab_order

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

        return {
            '_': _,
            'lang': lang,
            'lang_prefix': prefix,
            'lang_url': lang_url,
            'supported_langs': SUPPORTED_LANGS,
            'clean_path': clean_path,
            'canonical_url': canonical_url,
            'hreflang_urls': hreflang_urls,
            'asset_version': _ASSET_VERSION,
            'current_year': _dt.utcnow().year,
            'affiliate_offers': affiliate_offers,
            '_review_loaded_at': review_loaded_at,
        }

    # Register blueprints
    from .routes.main import main_bp
    from .routes.intercity import intercity_bp
    from .routes.city import city_bp
    from .routes.info import info_bp
    from .routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(intercity_bp)
    app.register_blueprint(city_bp)
    app.register_blueprint(info_bp)
    app.register_blueprint(admin_bp)

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

    # Cache headers
    @app.after_request
    def add_cache_headers(response):
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=86400'
        elif 'text/html' in (response.content_type or ''):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
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
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault(
            'Permissions-Policy',
            'geolocation=(), microphone=(), camera=(), payment=()',
        )
        if 'text/html' in (response.content_type or ''):
            response.headers.setdefault('Content-Security-Policy', (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' "
                "https://unpkg.com "
                "https://analytics.farmako.ro "
                "https://www.googletagmanager.com "
                "https://pagead2.googlesyndication.com "
                "https://www.bookaway.com; "
                "style-src 'self' 'unsafe-inline' https://unpkg.com; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://analytics.farmako.ro "
                "https://tile.openstreetmap.org; "
                "frame-src 'self' https://www.bookaway.com "
                "https://pagead2.googlesyndication.com "
                "https://googleads.g.doubleclick.net; "
                "base-uri 'self'; form-action 'self'; "
                "object-src 'none';"
            ))
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(410)
    def gone(e):
        # Signal permanent removal so Google drops the URL faster than 404.
        return render_template('404.html'), 410

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app

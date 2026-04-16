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
        }

    # Register blueprints
    from .routes.main import main_bp
    from .routes.intercity import intercity_bp
    from .routes.city import city_bp
    from .routes.info import info_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(intercity_bp)
    app.register_blueprint(city_bp)
    app.register_blueprint(info_bp)

    # Register same blueprints under /en/ and /ru/ prefixes
    for lang in SUPPORTED_LANGS:
        if lang == DEFAULT_LANG:
            continue
        app.register_blueprint(main_bp, url_prefix=f'/{lang}', name=f'main_{lang}')
        app.register_blueprint(intercity_bp, url_prefix=f'/{lang}', name=f'intercity_{lang}')
        app.register_blueprint(city_bp, url_prefix=f'/{lang}', name=f'city_{lang}')
        app.register_blueprint(info_bp, url_prefix=f'/{lang}', name=f'info_{lang}')

    # Gzip compression
    from flask_compress import Compress
    Compress(app)

    # CSRF protection (flask-wtf). Runtime config WTF_CSRF_ENABLED can turn it off in tests.
    from flask_wtf.csrf import CSRFProtect
    CSRFProtect(app)

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

import os
from flask import Flask, render_template, request
from config import config_map


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config_map[config_name])

    # Register blueprints
    from .routes.main import main_bp
    from .routes.intercity import intercity_bp
    from .routes.city import city_bp
    from .routes.info import info_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(intercity_bp)
    app.register_blueprint(city_bp)
    app.register_blueprint(info_bp)

    # Gzip compression
    from flask_compress import Compress
    Compress(app)

    # Static files caching
    @app.after_request
    def add_cache_headers(response):
        if 'static' in (response.headers.get('Content-Location') or '') or \
           request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=86400'
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app

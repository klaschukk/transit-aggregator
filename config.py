import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-key-do-not-use-in-prod')
    DUCKDB_PATH = os.environ.get('DUCKDB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'transit.duckdb'))
    ANALYTICS_DB_PATH = os.environ.get(
        'ANALYTICS_DB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'analytics.duckdb')
    )
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    EUR_RSD_RATE = max(1.0, float(os.environ.get('EUR_RSD_RATE', '117')))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', '')
    ADSENSE_ID = os.environ.get('ADSENSE_ID', '')
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', '')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    YANDEX_VERIFICATION = os.environ.get('YANDEX_VERIFICATION', '')

    # Analytics / monetization. IP_HASH_SALT fed into sha256 so stored hashes
    # aren't trivially reversible; rotate it to invalidate historical series.
    IP_HASH_SALT = os.environ.get('IP_HASH_SALT', '')
    # Basic auth for /admin/* dashboards. Routes 401 when unset.
    ADMIN_USER = os.environ.get('ADMIN_USER', '')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', '')


class ProductionConfig(Config):
    DEBUG = False
    BASE_URL = os.environ.get('BASE_URL', 'https://prevozni.com')
    SECRET_KEY = os.environ.get('SECRET_KEY', '')


class DevelopmentConfig(Config):
    DEBUG = True


config_map = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}

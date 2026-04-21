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

    # Reviews: gate trusted-author auto-approve behind an opt-in flag so the
    # first month of production runs 100% manual moderation (spec: quality >
    # velocity). Flip to 'true' after the review volume warrants it.
    REVIEWS_AUTO_APPROVE_TRUSTED = os.environ.get(
        'REVIEWS_AUTO_APPROVE_TRUSTED', 'false'
    ).lower() == 'true'

    # Outbound mail. Without SMTP_HOST the mailer writes to
    # logs/mail_dev.log so the double-opt-in flow stays testable until
    # Mailgun/SES lands. Port 587 → STARTTLS, 465 → implicit TLS.
    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587') or '587')
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASS = os.environ.get('SMTP_PASS', '')
    MAIL_FROM = os.environ.get('MAIL_FROM', 'no-reply@prevozni.com')


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

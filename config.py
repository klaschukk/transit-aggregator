import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-insecure-key-do-not-use-in-prod')
    DUCKDB_PATH = os.environ.get('DUCKDB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'transit.duckdb'))
    ANALYTICS_DB_PATH = os.environ.get(
        'ANALYTICS_DB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'analytics.sqlite')
    )
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    EUR_RSD_RATE = max(1.0, float(os.environ.get('EUR_RSD_RATE', '117')))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', '')
    ADSENSE_ID = os.environ.get('ADSENSE_ID', '')
    # Publisher ID for /ads.txt (`pub-XXXXXXXXX`). Same numeric body as
    # ADSENSE_ID — kept separate so /ads.txt is independent of whether
    # the site is currently rendering ads (a paused campaign still
    # needs a valid ads.txt for re-approval).
    ADSENSE_PUB_ID = os.environ.get('ADSENSE_PUB_ID', ADSENSE_ID)
    # Per-slot ad-unit IDs. Set ADSENSE_SLOT_<KEY> env vars from the
    # AdSense console; missing keys skip rendering (no house ad).
    # Keys must match the strings passed to ad_slot() in templates.
    ADSENSE_SLOTS = {
        'home_top':           os.environ.get('ADSENSE_SLOT_HOME_TOP', ''),
        'home_mid':           os.environ.get('ADSENSE_SLOT_HOME_MID', ''),
        'route_bottom':       os.environ.get('ADSENSE_SLOT_ROUTE_BOTTOM', ''),
        'city_pair_bottom':   os.environ.get('ADSENSE_SLOT_CITY_PAIR_BOTTOM', ''),
        'city_transport_mid': os.environ.get('ADSENSE_SLOT_CITY_TRANSPORT_MID', ''),
        'catalog_in_feed':    os.environ.get('ADSENSE_SLOT_CATALOG_IN_FEED', ''),
        'guide_sidebar':      os.environ.get('ADSENSE_SLOT_GUIDE_SIDEBAR', ''),
        'search_mid':         os.environ.get('ADSENSE_SLOT_SEARCH_MID', ''),
        'stop_bottom':        os.environ.get('ADSENSE_SLOT_STOP_BOTTOM', ''),
        'line_bottom':        os.environ.get('ADSENSE_SLOT_LINE_BOTTOM', ''),
        'mobile_anchor':      os.environ.get('ADSENSE_SLOT_MOBILE_ANCHOR', ''),
    }
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', '')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
    YANDEX_VERIFICATION = os.environ.get('YANDEX_VERIFICATION', '')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
    MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN', '')

    # Bookaway / TUNE (HasOffers) affiliate API — server-side only. Used by
    # the admin revenue dashboard to pull real clicks/conversions/payout.
    # Without a key the dashboard simply hides the API section.
    BOOKAWAY_API_KEY = os.environ.get('BOOKAWAY_API_KEY', '')
    BOOKAWAY_NETWORK_ID = os.environ.get('BOOKAWAY_NETWORK_ID', 'bookaway2')
    BOOKAWAY_AFF_ID = os.environ.get('BOOKAWAY_AFF_ID', '4033')
    # Comma-separated HasOffers ad-group campaign IDs to render as ad slots on
    # content pages (e.g. "386,387"). Empty = no ad slots shown. Turn on only
    # once the ad group has active creatives in the Bookaway panel, otherwise
    # the tag renders nothing.
    BOOKAWAY_AD_CAMPAIGNS = os.environ.get('BOOKAWAY_AD_CAMPAIGNS', '')

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

    # Mailgun (optional, for cold outreach only — transactional mail
    # stays on SMTP so a Mailgun outage can't break newsletter signup).
    # With MAILGUN_API_KEY + MAILGUN_DOMAIN set, scripts/backlinks_send.py
    # posts to Mailgun's v3 API and we get open/click/bounce webhooks
    # at /api/mailgun-webhook. MAILGUN_WEBHOOK_SIGNING_KEY is the HMAC
    # key used to verify those callbacks (distinct from the API key in
    # newer Mailgun setups); falls back to MAILGUN_API_KEY when unset.
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY', '')
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', '')
    MAILGUN_WEBHOOK_SIGNING_KEY = os.environ.get(
        'MAILGUN_WEBHOOK_SIGNING_KEY', '',
    )

    # CAN-SPAM compliant physical mailing address — appears in the
    # CAN-SPAM footer of every cold-outreach email. US recipients
    # require a real postal address; set this in systemd before the
    # first non-dry-run send. Read straight from env at module load
    # so app.outreach.sender stays import-clean.
    MAIL_PHYSICAL_ADDRESS = os.environ.get(
        'MAIL_PHYSICAL_ADDRESS', 'Prevozni · Belgrade, Serbia',
    )

    # Sentry error tracking. Empty DSN → sentry_sdk.init() is skipped entirely
    # so dev/tests never phone home. Traces sample rate applies to performance
    # spans; keep low — 5K events/mo free tier burns fast at 100% sampling.
    SENTRY_DSN = os.environ.get('SENTRY_DSN', '')
    SENTRY_ENV = os.environ.get('SENTRY_ENV', '')  # falls back to FLASK_ENV
    SENTRY_TRACES_SAMPLE_RATE = float(
        os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1') or '0.1'
    )


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

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DUCKDB_PATH = os.environ.get('DUCKDB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'transit.duckdb'))
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    EUR_RSD_RATE = max(1.0, float(os.environ.get('EUR_RSD_RATE', '117')))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', '')
    ADSENSE_ID = os.environ.get('ADSENSE_ID', '')


class ProductionConfig(Config):
    DEBUG = False
    BASE_URL = os.environ.get('BASE_URL', 'http://81.28.248.71')


class DevelopmentConfig(Config):
    DEBUG = True


config_map = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}

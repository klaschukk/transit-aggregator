import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DUCKDB_PATH = os.environ.get('DUCKDB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'transit.duckdb'))
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    EUR_RSD_RATE = max(1.0, float(os.environ.get('EUR_RSD_RATE', '117')))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'


class ProductionConfig(Config):
    DEBUG = False
    BASE_URL = os.environ.get('BASE_URL', 'https://transit-serbia.com')


class DevelopmentConfig(Config):
    DEBUG = True


config_map = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}

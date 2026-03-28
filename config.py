import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    COUNTRY = os.environ.get('COUNTRY', 'RS')
    DUCKDB_PATH = os.environ.get('DUCKDB_PATH', str(BASE_DIR / 'data' / 'dbs' / 'transit.duckdb'))
    CACHE_TTL = int(os.environ.get('CACHE_TTL', '300'))  # 5 min default
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'


class ProductionConfig(Config):
    DEBUG = False
    CACHE_TTL = 3600  # 1 hour in prod


class DevelopmentConfig(Config):
    DEBUG = True
    CACHE_TTL = 0  # no cache in dev


config_map = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}

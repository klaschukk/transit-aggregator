import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DB_HOST = 'localhost'
    DB_NAME = 'transitdb'
    DB_USER = 'transit'
    DB_PASS = 'transitpass123'
    REDIS_URL = 'redis://localhost:6379/0'
    COUNTRY = os.environ.get('COUNTRY', 'RS')

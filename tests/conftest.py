import pytest

from app import create_app
from app.db import query, query_one


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    application = create_app("development")
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    yield application


@pytest.fixture(scope="session")
def client(app):
    """Flask test client that reuses the same app for the whole session."""
    return app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """Provide query helpers within app context."""
    class DB:
        @staticmethod
        def q(sql, params=None):
            with app.app_context():
                return query(sql, params)
        @staticmethod
        def one(sql, params=None):
            with app.app_context():
                return query_one(sql, params)
    return DB()

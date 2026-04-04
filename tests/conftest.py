import pytest

from app import create_app


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    application = create_app("development")
    application.config["TESTING"] = True
    yield application


@pytest.fixture(scope="session")
def client(app):
    """Flask test client that reuses the same app for the whole session."""
    return app.test_client()

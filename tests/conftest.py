import pytest

from app import create_app
from app.db import query, query_one


@pytest.fixture(autouse=True)
def _isolate_flask_env(monkeypatch):
    """Keep FLASK_ENV out of the test process.

    Several CLI scripts (scripts/data_snapshot.py, scripts/audit_links.py) run
    `os.environ.setdefault("FLASK_ENV", "production")` at import time so they
    boot the production config when launched standalone from cron. pytest
    imports every module during collection, so that side effect leaks
    FLASK_ENV=production into the whole session — and then any bare
    create_app() builds the production config (with a frozen-empty SECRET_KEY),
    making unrelated tests raise RuntimeError. Reset it per test so each starts
    from the default config, exactly as the suite ran before those scripts
    landed. Tests that need production pass config_name explicitly.
    """
    monkeypatch.delenv("FLASK_ENV", raising=False)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    """Create application for testing."""
    application = create_app("development")
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    application.config["RATELIMIT_ENABLED"] = False
    # With Telegram unconfigured, logs/contact_messages.log IS the contact
    # inbox — keep the suite's fixture enquiries out of it.
    application.config["CONTACT_LOG_PATH"] = str(
        tmp_path_factory.mktemp("contact") / "contact_messages.log")
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

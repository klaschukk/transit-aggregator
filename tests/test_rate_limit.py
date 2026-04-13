"""Rate limiting on public API endpoints."""

import pytest

from app import create_app


@pytest.fixture()
def rl_client():
    app = create_app("development")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["RATELIMIT_ENABLED"] = True
    # Reset in-memory counters per test
    from app.extensions import limiter
    limiter.reset()
    return app.test_client()


def test_api_cities_rate_limited(rl_client):
    triggered = False
    for i in range(40):
        resp = rl_client.get("/api/cities?q=be")
        if resp.status_code == 429:
            triggered = True
            assert resp.is_json
            assert resp.get_json()["error"] == "rate_limit_exceeded"
            break
    assert triggered, "expected 429 within 40 requests"


def test_api_cities_ok_under_limit(rl_client):
    from app.extensions import limiter
    limiter.reset()
    for _ in range(5):
        resp = rl_client.get("/api/cities?q=be")
        assert resp.status_code == 200

"""Contact form: validation, CSRF, truncation."""

import pytest

from app import create_app


@pytest.fixture(scope="module")
def csrf_client():
    app = create_app("development")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["SECRET_KEY"] = "test-secret"
    return app.test_client()


def _good():
    return {"ime": "Ana", "email": "ana@example.com", "poruka": "Hello there"}


def test_csrf_blocks_post_without_token(csrf_client):
    resp = csrf_client.post("/kontakt/", data=_good())
    assert resp.status_code == 400


def test_post_ok_when_csrf_disabled(client):
    resp = client.post("/kontakt/", data=_good())
    assert resp.status_code == 200


def test_invalid_email_returns_400(client):
    data = _good() | {"email": "not-an-email"}
    resp = client.post("/kontakt/", data=data)
    assert resp.status_code == 400


def test_missing_fields_returns_400(client):
    resp = client.post("/kontakt/", data={"ime": "", "email": "", "poruka": ""})
    assert resp.status_code == 400


def test_name_too_long_rejected(client):
    data = _good() | {"ime": "x" * 101}
    resp = client.post("/kontakt/", data=data)
    assert resp.status_code == 400


def test_message_too_long_rejected(client):
    data = _good() | {"poruka": "y" * 501}
    resp = client.post("/kontakt/", data=data)
    assert resp.status_code == 400


def test_email_too_long_rejected(client):
    long_local = "a" * 95
    data = _good() | {"email": f"{long_local}@ex.com"}  # > 100
    resp = client.post("/kontakt/", data=data)
    assert resp.status_code == 400


def test_contact_form_renders_csrf_token(client):
    resp = client.get("/kontakt/")
    assert resp.status_code == 200
    assert b"csrf_token" in resp.data

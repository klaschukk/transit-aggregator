"""Privacy page + production SECRET_KEY guard."""

import os

import pytest


def test_privacy_page_sr(client):
    resp = client.get("/privatnost/")
    assert resp.status_code == 200
    assert b"Privatnost" in resp.data or b"privacy" in resp.data.lower()


def test_privacy_page_en(client):
    resp = client.get("/en/privatnost/")
    assert resp.status_code == 200
    assert b"Privacy Policy" in resp.data


def test_privacy_page_ru(client):
    resp = client.get("/ru/privatnost/")
    assert resp.status_code == 200


def test_privacy_in_sitemap(client):
    # /privatnost/ is a hub page → lives in the core shard after the split.
    resp = client.get("/sitemap-core.xml")
    assert b"/privatnost/" in resp.data


def test_privacy_link_in_footer(client):
    resp = client.get("/")
    assert b"/privatnost/" in resp.data


def test_production_requires_secret_key(monkeypatch):
    import config as cfg
    from app import create_app
    # ProductionConfig.SECRET_KEY is read from the env at import time, so under
    # CI (which sets SECRET_KEY=ci-test-secret) the class attr is already frozen
    # to a value — delenv alone can't undo that. Clear the frozen attr directly;
    # monkeypatch restores it afterwards.
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setattr(cfg.ProductionConfig, "SECRET_KEY", "", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_production_ok_with_secret_key(monkeypatch):
    from app import create_app
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    # Reload config module so ProductionConfig picks up the env var
    import importlib, config as cfg
    importlib.reload(cfg)
    import app as app_pkg
    importlib.reload(app_pkg)
    app = app_pkg.create_app("production")
    assert app.config["SECRET_KEY"] == "x" * 32

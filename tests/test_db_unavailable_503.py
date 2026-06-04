"""When the DuckDB file is briefly absent (nightly rebuild), DB-backed pages
must answer 503 + Retry-After, NOT 404. The old fall-through to abort(404) made
Googlebot crawling that window log live pages as "Not found (404)" — the bulk
of GSC's 1572. A 503 keeps the URL: Google retries instead of dropping it.

This was diagnosed from prod nginx logs: 52/54 URLs that 404'd during a rebuild
window were live again minutes later — transient, not removed.
"""

import pytest

DB_BACKED = [
    "/",
    "/rute/beograd-novi-sad/",
    "/en/rute/beograd-novi-sad/",
    "/ru/rute/beograd-novi-sad/",
    "/voznja/beograd-do-novi-sad/",
    "/gradski/beograd/",
    "/gradski/beograd/stajaliste/sajam/",
    "/prevoznici/",
]

DB_LESS = ["/o-nama/", "/kontakt/", "/robots.txt", "/sitemap.xml"]


def test_db_backed_paths_503_with_retry_after_when_db_missing(client, monkeypatch):
    monkeypatch.setattr("app.db.db_ready", lambda: False)
    for url in DB_BACKED:
        r = client.get(url)
        assert r.status_code == 503, f"{url} -> {r.status_code}, expected 503"
        assert r.headers.get("Retry-After") == "120", f"{url} missing Retry-After"
        assert b"noindex" in r.data, f"{url} 503 body should be noindex"


def test_db_less_paths_keep_working_when_db_missing(client, monkeypatch):
    monkeypatch.setattr("app.db.db_ready", lambda: False)
    for url in DB_LESS:
        r = client.get(url)
        assert r.status_code != 503, f"{url} should not 503 (it needs no DB), got {r.status_code}"


def test_valid_route_is_200_when_db_up(client):
    assert client.get("/rute/beograd-novi-sad/").status_code == 200


def test_genuinely_missing_slug_still_404_when_db_up(client):
    # DB is up → a real "not found" must stay 404/410 (not masked as 503).
    r = client.get("/rute/zzz-this-route-does-not-exist-xyz/")
    assert r.status_code in (404, 410), f"expected 404/410, got {r.status_code}"

"""Tests for all routes — status codes, API responses, and SEO basics."""

import json

import pytest


# ── a) Page status codes ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "url, expected_status",
    [
        ("/", 200),
        ("/rute/", 200),
        ("/rute/beograd-novi-sad/", 200),
        ("/rute/NEPOSTOJECI/", 404),
        ("/gradski/beograd/", 200),
        ("/gradski/NEPOSTOJECI/", 404),
        ("/gradski/beograd/linija/linija-2a/", 200),
        ("/gradski/beograd/stajaliste/sajam/", 200),
        ("/prevoznici/", 200),
        ("/autobuske-stanice/", 200),
        ("/o-nama/", 200),
        ("/kontakt/", 200),
        ("/health", 200),
        ("/sitemap.xml", 200),
        ("/robots.txt", 200),
        ("/NEPOSTOJECI", 404),
    ],
)
def test_page_status(client, url, expected_status):
    resp = client.get(url)
    assert resp.status_code == expected_status


# ── b) API endpoints ─────────────────────────────────────────────────


def test_api_cities_with_query(client):
    resp = client.get("/api/cities?q=beo")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert len(data) > 0


def test_api_cities_empty_query(client):
    resp = client.get("/api/cities?q=")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == []


def test_api_city_stops_with_bounds(client):
    resp = client.get(
        "/api/city-stops?sw_lat=44.7&sw_lon=20.3&ne_lat=44.9&ne_lon=20.6"
    )
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_api_city_stops_missing_params(client):
    resp = client.get("/api/city-stops")
    assert resp.status_code == 400


def test_api_stop_arrivals(client):
    resp = client.get("/api/stop-arrivals?slug=sajam")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_api_stop_arrivals_empty_slug(client):
    resp = client.get("/api/stop-arrivals?slug=")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == []


# ── c) SEO checks ────────────────────────────────────────────────────

_SEO_PAGES = [
    "/",
    "/rute/",
    "/rute/beograd-novi-sad/",
    "/gradski/beograd/",
    "/o-nama/",
    "/kontakt/",
]


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_title(client, url):
    html = client.get(url).data.decode()
    assert "<title>" in html and "</title>" in html


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_meta_description(client, url):
    html = client.get(url).data.decode()
    assert 'name="description"' in html


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_canonical(client, url):
    html = client.get(url).data.decode()
    assert 'rel="canonical"' in html
    # Canonical href must contain the page path
    canonical_tag = html.split('rel="canonical"')[1].split(">")[0]
    assert 'href="' in canonical_tag
    assert url.rstrip("/") in canonical_tag or url == "/"


def test_sitemap_has_urls(client):
    resp = client.get("/sitemap.xml")
    xml = resp.data.decode()
    url_count = xml.count("<url>")
    assert url_count > 100, f"Sitemap has only {url_count} URLs, expected >100"


def test_robots_has_sitemap(client):
    txt = client.get("/robots.txt").data.decode()
    assert "Sitemap:" in txt


# ── d) Health endpoint detail ─────────────────────────────────────────


def test_health_has_db_field(client):
    data = json.loads(client.get("/health").data)
    assert "db" in data
    assert "status" in data

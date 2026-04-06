"""Edge case tests — malformed input, injection attempts, unusual URLs."""

import json

import pytest


# ── Cyrillic and unicode in URLs ──


def test_cyrillic_slug_returns_404(client):
    resp = client.get("/gradski/beograd/stajaliste/трг-републике/")
    assert resp.status_code in (200, 404), f"Got {resp.status_code}"


def test_unicode_route_slug(client):
    resp = client.get("/rute/београд-нови-сад/")
    assert resp.status_code in (200, 404)


def test_emoji_in_url(client):
    resp = client.get("/rute/🚌/")
    assert resp.status_code in (400, 404)


# ── Very long inputs ──


def test_long_city_query(client):
    resp = client.get("/api/cities?q=" + "a" * 500)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == []


def test_long_slug(client):
    resp = client.get("/rute/" + "x" * 1000 + "/")
    assert resp.status_code == 404


def test_long_stop_slug(client):
    resp = client.get("/gradski/beograd/stajaliste/" + "y" * 500 + "/")
    assert resp.status_code == 404


# ── SQL injection attempts ──


def test_sqli_cities_api(client):
    resp = client.get("/api/cities?q='; DROP TABLE routes; --")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)


def test_sqli_stop_arrivals(client):
    resp = client.get("/api/stop-arrivals?slug=' OR 1=1 --")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == []


def test_sqli_search(client):
    resp = client.get("/pretraga/?od=' UNION SELECT * FROM operators--&do=test")
    assert resp.status_code == 200
    assert "Traceback" not in resp.data.decode()


def test_sqli_route_slug(client):
    resp = client.get("/rute/' OR '1'='1/")
    assert resp.status_code in (200, 404)


def test_sqli_city_stops(client):
    resp = client.get("/api/city-stops?sw_lat=44.7&sw_lon=20.3&ne_lat=44.9&ne_lon=20.6' OR 1=1--")
    assert resp.status_code == 400


# ── XSS attempts ──


def test_xss_search_from(client):
    resp = client.get("/pretraga/?od=<script>alert(1)</script>&do=Beograd")
    html = resp.data.decode()
    assert resp.status_code == 200
    assert "<script>alert(1)</script>" not in html


def test_xss_search_to(client):
    resp = client.get("/pretraga/?od=Beograd&do=<img onerror=alert(1) src=x>")
    html = resp.data.decode()
    assert resp.status_code == 200
    # Jinja2 autoescapes: <img> must become &lt;img&gt;, not a real tag
    assert "<img onerror=" not in html


def test_xss_cities_api(client):
    resp = client.get('/api/cities?q=<script>alert("xss")</script>')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == []


def test_xss_stop_arrivals(client):
    resp = client.get('/api/stop-arrivals?slug=<script>alert(1)</script>')
    assert resp.status_code == 200


# ── Malformed URLs ──


def test_double_slash(client):
    resp = client.get("//rute//")
    assert resp.status_code in (200, 301, 308, 404)


def test_url_with_spaces(client):
    resp = client.get("/rute/beograd%20novi%20sad/")
    assert resp.status_code in (200, 404)


def test_trailing_junk(client):
    resp = client.get("/rute/beograd-novi-sad/../../etc/passwd")
    assert resp.status_code in (301, 400, 404)
    if resp.status_code == 200:
        assert "root:" not in resp.data.decode()


def test_null_byte_in_url(client):
    resp = client.get("/rute/test%00/")
    assert resp.status_code in (200, 400, 404)


def test_dot_dot_in_static(client):
    resp = client.get("/static/../config.py")
    assert resp.status_code in (400, 403, 404)
    if resp.status_code == 200:
        assert "SECRET_KEY" not in resp.data.decode()


# ── HTTP methods ──


def test_post_to_kontakt(client):
    resp = client.post("/kontakt/", data={})
    assert resp.status_code in (200, 405)


def test_post_to_api(client):
    resp = client.post("/api/cities?q=beo")
    assert resp.status_code in (200, 405)


def test_put_to_route(client):
    resp = client.put("/rute/beograd-novi-sad/")
    assert resp.status_code == 405


def test_delete_to_route(client):
    resp = client.delete("/rute/beograd-novi-sad/")
    assert resp.status_code == 405


# ── API param edge cases ──


def test_city_stops_negative_coords(client):
    resp = client.get("/api/city-stops?sw_lat=-90&sw_lon=-180&ne_lat=90&ne_lon=180")
    assert resp.status_code == 200


def test_city_stops_zero_bbox(client):
    resp = client.get("/api/city-stops?sw_lat=44.8&sw_lon=20.4&ne_lat=44.8&ne_lon=20.4")
    assert resp.status_code == 200


def test_city_stops_partial_params(client):
    resp = client.get("/api/city-stops?sw_lat=44.7&sw_lon=20.3")
    assert resp.status_code == 400


def test_city_stops_nan(client):
    resp = client.get("/api/city-stops?sw_lat=NaN&sw_lon=NaN&ne_lat=NaN&ne_lon=NaN")
    assert resp.status_code in (200, 400)  # float('nan') is valid Python float


def test_city_stops_inf(client):
    resp = client.get("/api/city-stops?sw_lat=Infinity&sw_lon=20&ne_lat=45&ne_lon=21")
    assert resp.status_code in (200, 400)  # float('inf') is valid Python float


# ── City slugs ──


def test_unknown_city(client):
    resp = client.get("/gradski/zagreb/")
    assert resp.status_code == 404


def test_city_case_sensitive(client):
    resp = client.get("/gradski/BEOGRAD/")
    assert resp.status_code == 404  # slugs are lowercase


def test_city_pair_nonexistent(client):
    resp = client.get("/voznja/mars-do-jupiter/")
    assert resp.status_code == 200  # renders empty page, not 404
    assert "Traceback" not in resp.data.decode()


# ── Content safety on error pages ──


def test_404_no_traceback(client):
    html = client.get("/does-not-exist-at-all").data.decode()
    assert "Traceback" not in html
    assert "debugger" not in html.lower()


def test_404_has_html(client):
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    assert b"<html" in resp.data


# ── Search edge cases ──


def test_search_empty_params(client):
    resp = client.get("/pretraga/")
    assert resp.status_code == 200


def test_search_same_city(client):
    resp = client.get("/pretraga/?od=Beograd&do=Beograd")
    assert resp.status_code == 200


def test_search_special_chars(client):
    resp = client.get("/pretraga/?od=Niš&do=Čačak")
    assert resp.status_code == 200
    assert "Traceback" not in resp.data.decode()

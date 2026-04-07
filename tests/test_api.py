"""API endpoint tests — response format and content validation."""

import json

import pytest


# ── /api/cities ──


def test_cities_beograd(client):
    data = json.loads(client.get("/api/cities?q=beo").data)
    assert any("Beograd" in c for c in data), f"Beograd not in {data}"


def test_cities_novi_sad(client):
    data = json.loads(client.get("/api/cities?q=nov").data)
    assert any("Novi Sad" in c for c in data), f"Novi Sad not in {data}"


def test_cities_nis(client):
    data = json.loads(client.get("/api/cities?q=ni").data)
    names = " ".join(data)
    assert "Ni" in names, f"Nis-related city not in {data}"


def test_cities_empty_query(client):
    data = json.loads(client.get("/api/cities?q=").data)
    assert data == []


def test_cities_no_results(client):
    data = json.loads(client.get("/api/cities?q=zzzzzzz").data)
    assert data == []


def test_cities_short_query(client):
    data = json.loads(client.get("/api/cities?q=b").data)
    assert isinstance(data, list)


def test_cities_limit(client):
    data = json.loads(client.get("/api/cities?q=b").data)
    assert len(data) <= 10, "Too many results returned"


# ── /api/city-stops ──


def test_city_stops_beograd(client):
    resp = client.get("/api/city-stops?sw_lat=44.7&sw_lon=20.3&ne_lat=44.9&ne_lon=20.6")
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert len(data) > 0, "No stops in Beograd bbox"


def test_city_stops_fields(client):
    data = json.loads(client.get(
        "/api/city-stops?sw_lat=44.7&sw_lon=20.3&ne_lat=44.9&ne_lon=20.6"
    ).data)
    if data:
        item = data[0]
        assert "name" in item
        assert "slug" in item
        assert "lat" in item
        assert "lon" in item


def test_city_stops_novi_sad(client):
    data = json.loads(client.get(
        "/api/city-stops?sw_lat=45.20&sw_lon=19.75&ne_lat=45.30&ne_lon=19.90"
    ).data)
    assert isinstance(data, list)  # May be empty if coords not enriched yet


def test_city_stops_nis(client):
    data = json.loads(client.get(
        "/api/city-stops?sw_lat=43.28&sw_lon=21.85&ne_lat=43.35&ne_lon=21.96"
    ).data)
    assert isinstance(data, list)  # May be empty after DB rebuild before enrich


def test_city_stops_missing_params(client):
    assert client.get("/api/city-stops").status_code == 400


def test_city_stops_invalid_params(client):
    assert client.get("/api/city-stops?sw_lat=abc&sw_lon=20&ne_lat=45&ne_lon=21").status_code == 400


def test_city_stops_empty_bbox(client):
    data = json.loads(client.get(
        "/api/city-stops?sw_lat=0&sw_lon=0&ne_lat=0.01&ne_lon=0.01"
    ).data)
    assert data == []


# ── /api/stop-arrivals ──


def test_stop_arrivals_sajam(client):
    data = json.loads(client.get("/api/stop-arrivals?slug=sajam").data)
    assert isinstance(data, list)
    assert len(data) > 0, "No arrivals at Sajam"


def test_stop_arrivals_fields(client):
    data = json.loads(client.get("/api/stop-arrivals?slug=sajam").data)
    if data:
        item = data[0]
        assert "line" in item
        assert "mins" in item
        assert "direction" in item
        assert "color" in item
        assert "slug" in item


def test_stop_arrivals_mins_positive(client):
    data = json.loads(client.get("/api/stop-arrivals?slug=sajam").data)
    for item in data:
        assert item["mins"] >= 0, f"Negative mins: {item}"


def test_stop_arrivals_empty_slug(client):
    data = json.loads(client.get("/api/stop-arrivals?slug=").data)
    assert data == []


def test_stop_arrivals_nonexistent(client):
    data = json.loads(client.get("/api/stop-arrivals?slug=NEPOSTOJECI").data)
    assert data == []


# ── /health ──


def test_health_status(client):
    data = json.loads(client.get("/health").data)
    assert data["status"] == "ok"
    assert data["db"] is True
    assert "service" in data

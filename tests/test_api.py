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
    # Honest contract: arrivals are REAL GTFS times only — the endpoint never
    # fabricates a headway estimate (which used to print an identical "X min" for
    # every line). Sajam (Beograd) has no mapped GTFS in the test DB, so it
    # returns an empty list. The real-data path is asserted in
    # test_stop_arrivals_real_gtfs below.
    data = json.loads(client.get("/api/stop-arrivals?slug=sajam").data)
    assert isinstance(data, list)


def _live_gtfs_stop_slug():
    """Slug of a stop that has >=1 real GTFS departure from now on, else None."""
    from datetime import datetime

    from app.db import query
    from app.routes.city import _today_service

    now = f"{datetime.now().hour:02d}:{datetime.now().minute:02d}:00"
    rows = query(
        """
        SELECT cs.slug
        FROM gtfs_stop_times st
        JOIN city_stops cs ON cs.id = st.city_stop_id
        JOIN gtfs_trips gt ON gt.trip_id = st.trip_id
        WHERE gt.service_id = ? AND st.departure_time >= ?
        GROUP BY cs.slug
        ORDER BY COUNT(*) DESC
        LIMIT 1
        """,
        [_today_service(), now],
    )
    return rows[0]["slug"] if rows else None


def test_stop_arrivals_real_gtfs(client):
    """Real-data path: a stop with current GTFS departures returns arrivals with
    valid structure and genuine (non-fabricated) minute values."""
    slug = _live_gtfs_stop_slug()
    if not slug:
        pytest.skip("no GTFS departures from now in test DB (e.g. overnight run)")
    data = json.loads(client.get(f"/api/stop-arrivals?slug={slug}").data)
    assert len(data) > 0, f"expected real arrivals at {slug}"
    for item in data:
        for key in ("line", "mins", "direction", "color", "slug"):
            assert key in item, f"missing {key} in {item}"
        assert isinstance(item["mins"], int) and item["mins"] >= 0


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
    # /health returns HTTP 200 for both "ok" and "degraded" — only "down"
    # (HTTP 503) pages. Tests tolerate "degraded" because the dev box often
    # has the live gunicorn holding analytics.duckdb's write lock.
    resp = client.get("/health")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] in ("ok", "degraded")
    assert data["service"] == "prevozni"
    assert data["checks"]["transit_db"]["ok"] is True
    assert data["checks"]["logs_writable"] is True
    assert "version" in data
    assert "uptime_seconds" in data


def test_health_reports_line_geometries(client):
    """/health must surface line_geometries, the Apr 25 incident's table.

    build_db recreates the DB from scratch and does not create that table —
    only the standalone geometry scraper does, and build_db can merely
    preserve what already exists. So a rebuilt-from-nothing box loses it
    silently: line maps fall back to zig-zag straight lines between stops
    while every other check stays green. The incident write-up called for
    probing every load-bearing table, but this one was never added, and the
    loss recurred unnoticed. Reported as degraded, not critical — the maps
    lose quality, the pages still serve a timetable.
    """
    data = json.loads(client.get("/health").data)
    transit = data["checks"]["transit_db"]
    assert "line_geometries" in transit, "health must report line_geometries"
    count = transit["line_geometries"]
    assert count is None or isinstance(count, int)
    if not count:
        assert data["status"] == "degraded", (
            "missing/empty line_geometries must degrade the health status"
        )

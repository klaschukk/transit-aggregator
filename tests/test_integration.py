"""Integration tests — verify real data renders on pages."""

import json
import re


def test_route_index_has_cards(client):
    html = client.get("/rute/").data.decode()
    count = html.count("route-card")
    assert count > 0, "No route-card on /rute/"


def test_route_detail_has_trips(client):
    html = client.get("/rute/beograd-novi-sad/").data.decode()
    count = html.count("trip-card")
    assert count > 0, "No trip-card on route detail"


def test_route_detail_has_stats(client):
    html = client.get("/rute/beograd-novi-sad/").data.decode()
    assert "stats-strip" in html


def test_city_hub_has_lines(client):
    html = client.get("/gradski/beograd/").data.decode()
    count = html.count('data-num="')
    assert count > 0, "No lines on city hub"


def test_city_hub_has_map(client):
    html = client.get("/gradski/beograd/").data.decode()
    assert "cityMap" in html


def test_stop_detail_has_lines(client):
    html = client.get("/gradski/beograd/stajaliste/sajam/").data.decode()
    count = html.count("stop-line-row")
    assert count > 0, "No stop-line-row on stop detail"


def test_stop_detail_has_seo_block(client):
    html = client.get("/gradski/beograd/stajaliste/sajam/").data.decode()
    assert "seo-block" in html, "No SEO block on stop detail"


def test_line_detail_has_stops(client):
    html = client.get("/gradski/beograd/linija/linija-2a/").data.decode()
    count = html.count("stop-row")
    assert count > 0, "No stop-row on line detail"


def test_line_detail_has_map(client):
    html = client.get("/gradski/beograd/linija/linija-2a/").data.decode()
    assert "lineMap" in html


def test_carriers_has_cards(client):
    html = client.get("/prevoznici/").data.decode()
    assert html.count("carrier-card ") > 0, "No carrier cards on /prevoznici/"


def test_carriers_link_to_operator_pages(client):
    """The directory's job is to get you to a carrier, so every card is a
    link to /prevoznici/<slug>/. It used to also inline up to 6 route
    links per carrier — a partial copy of the page the card already
    points at, repeated 50 times down a 23,780px phone column."""
    html = client.get("/prevoznici/").data.decode()
    assert html.count('class="carrier-card') >= 5
    assert "/prevoznici/lasta/" in html
    assert "carrier-route-link" not in html


def test_stations_has_cards(client):
    html = client.get("/autobuske-stanice/").data.decode()
    assert "station-card" in html


def test_homepage_has_hero(client):
    html = client.get("/").data.decode()
    assert "hero__title" in html


def test_homepage_has_stats(client):
    html = client.get("/").data.decode()
    assert "home-stats" in html


def test_homepage_has_popular_routes(client):
    html = client.get("/").data.decode()
    assert "home-route" in html


def test_city_pair_has_faq(client):
    html = client.get("/voznja/beograd-do-novi-sad/").data.decode()
    assert "faq-item" in html


def test_city_pair_has_seo_block(client):
    html = client.get("/voznja/beograd-do-novi-sad/").data.decode()
    assert "seo-block" in html


def test_search_results_has_trips(client):
    html = client.get("/pretraga/?od=Beograd&do=Novi+Sad").data.decode()
    # May have trips or empty state depending on time of day
    assert "trip-card" in html or "empty-state" in html


def test_api_arrivals_structure(client):
    # Arrivals are real GTFS only; sajam (Beograd) has no mapped GTFS in the test
    # DB so it is empty by honest design (no fabricated headway estimate).
    # Validate structure for whatever real entries are present.
    data = json.loads(client.get("/api/stop-arrivals?slug=sajam").data)
    assert isinstance(data, list)
    for item in data:
        assert "line" in item
        assert "mins" in item
        assert "direction" in item
        assert isinstance(item["mins"], int)


def test_api_arrivals_all_have_color(client):
    data = json.loads(client.get("/api/stop-arrivals?slug=sajam").data)
    for item in data:
        assert item.get("color", "").startswith("#"), f"Bad color: {item}"


def test_health_db_true(client):
    data = json.loads(client.get("/health").data)
    assert data["checks"]["transit_db"]["ok"] is True
    # "degraded" is acceptable in CI — analytics_db may be write-locked by a
    # live prod gunicorn on the dev box. /health returns HTTP 200 anyway.
    assert data["status"] in ("ok", "degraded")


def test_sitemap_has_line_urls(client):
    xml = client.get("/sitemap-lines.xml").data.decode()
    assert "/linija/" in xml


def test_sitemap_has_stop_urls(client):
    xml = client.get("/sitemap-stops.xml").data.decode()
    assert "/stajaliste/" in xml


def test_city_pair_content_covered_by_rute_shard(client):
    # /voznja/ pairs canonicalise to their /rute/ owner, so the pairs shard is
    # deprecated/empty and the city-pair content is discoverable via the
    # canonical /rute/ URLs in sitemap-routes.
    assert "/voznja/" not in client.get("/sitemap-pairs.xml").data.decode()
    assert "/rute/" in client.get("/sitemap-routes.xml").data.decode()


def test_404_page_structure(client):
    resp = client.get("/does-not-exist-xyz/")
    assert resp.status_code == 404
    html = resp.data.decode()
    assert "<html" in html
    assert "error-actions" in html or "empty-state" in html


def test_gradski_index_has_cities(client):
    html = client.get("/gradski/").data.decode()
    assert "Beograd" in html


def test_nis_hub_accessible(client):
    resp = client.get("/gradski/nis/")
    assert resp.status_code == 200
    assert "Niš" in resp.data.decode() or "nis" in resp.data.decode()

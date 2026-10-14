"""Tests for all routes — status codes, API responses, SEO, and data quality."""

import json
import time
from pathlib import Path

import pytest


def _route_count() -> int:
    try:
        from app.db import query
        result = query("SELECT COUNT(*) FROM routes")
        return (result or [[0]])[0][0]
    except Exception:
        return 0


# ── a) Page status codes ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "url, expected_status",
    [
        ("/", 200),
        ("/rute/", 200),
        ("/rute/beograd-novi-sad/", 200),
        # Single-token /rute/<x>/ is the retired city-hub scheme → 410 Gone.
        ("/rute/NEPOSTOJECI/", 410),
        ("/gradski/", 200),
        ("/gradski/beograd/", 200),
        ("/gradski/novi-sad/", 200),
        ("/gradski/nis/", 200),
        ("/gradski/NEPOSTOJECI/", 404),
        ("/gradski/beograd/linija/linija-2a/", 200),
        # A missing line/stop with the DB up is a removed programmatic page
        # (re-scrape dropped ~886 stops) → 410 Gone so Google deindexes fast,
        # not 404 which lingers in GSC "Not found" for months.
        ("/gradski/beograd/linija/NEPOSTOJECI/", 410),
        ("/gradski/beograd/linija/nepostojeci/", 410),
        ("/gradski/beograd/stajaliste/sajam/", 200),
        ("/gradski/beograd/stajaliste/NEPOSTOJECI/", 410),
        ("/gradski/beograd/stajaliste/nepostojeci/", 410),
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


def test_rute_with_do_redirects_to_clean_slug(client):
    # Users sometimes type /rute/X-do-Y/ confusing it with the /voznja/X-do-Y/
    # pattern. If /rute/X-Y/ exists, 301 to it instead of 404.
    resp = client.get("/rute/beograd-do-novi-sad/")
    assert resp.status_code == 301
    assert resp.headers["Location"].endswith("/rute/beograd-novi-sad/")


def test_rute_with_do_410s_when_target_missing(client):
    # Don't blanket-redirect — only 301 when the cleaned slug exists. If neither
    # /rute/X-do-Y/ nor /rute/X-Y/ exists, it's a removed route → 410 Gone.
    resp = client.get("/rute/nepostojeci-do-takode-nepostojeci/")
    assert resp.status_code == 410


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


def test_api_cities_no_results(client):
    resp = client.get("/api/cities?q=zzzzzzz")
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
    "/gradski/novi-sad/",
    "/prevoznici/",
    "/o-nama/",
    "/kontakt/",
]


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_title(client, url):
    html = client.get(url).data.decode()
    assert "<title>" in html and "</title>" in html
    title = html.split("<title>")[1].split("</title>")[0]
    assert len(title) > 10, f"Title too short: {title}"
    assert "None" not in title


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_meta_description(client, url):
    html = client.get(url).data.decode()
    assert 'name="description"' in html


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_canonical(client, url):
    html = client.get(url).data.decode()
    assert 'rel="canonical"' in html
    canonical = html.split('rel="canonical"')[1].split(">")[0]
    assert 'href="' in canonical


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_has_og_tags(client, url):
    html = client.get(url).data.decode()
    assert 'property="og:title"' in html
    assert 'property="og:description"' in html


@pytest.mark.parametrize("url", _SEO_PAGES)
def test_no_none_in_html(client, url):
    html = client.get(url).data.decode()
    assert ">None<" not in html
    assert '"None"' not in html.replace('fill="None"', '').replace("fill='None'", '')
    assert "None km" not in html
    assert "None pol" not in html


def test_sitemap_has_urls(client, app):
    # /sitemap.xml is now an index of shards; real <url> entries live in
    # the shards. Pick the largest one (routes) and assert a floor.
    with app.app_context():
        if _route_count() < 50:
            pytest.skip("seed DB too small for sitemap floor check")
    resp = client.get("/sitemap-routes.xml")
    xml = resp.data.decode()
    url_count = xml.count("<url>")
    assert url_count > 100, f"sitemap-routes.xml has only {url_count} URLs"


def test_robots_has_sitemap(client):
    txt = client.get("/robots.txt").data.decode()
    assert "Sitemap:" in txt
    assert "Disallow: /api/" in txt


# ── d) Data quality ──────────────────────────────────────────────────


def test_rute_has_routes(client, app):
    with app.app_context():
        if _route_count() < 50:
            pytest.skip("seed DB too small for route floor check")
    html = client.get("/rute/").data.decode()
    assert html.count("route-card") >= 50, "Expected at least 50 routes"


def test_prevoznici_has_operators(client):
    html = client.get("/prevoznici/").data.decode()
    assert html.count("carrier-card ") >= 5, "Expected at least 5 operators"


def test_gradski_beograd_has_lines(client, app):
    with app.app_context():
        if _route_count() < 50:
            pytest.skip("seed DB too small for line floor check")
    html = client.get("/gradski/beograd/").data.decode()
    assert html.count("data-num") >= 100, "Expected at least 100 lines"


def test_gradski_novi_sad_has_lines(client, app):
    with app.app_context():
        if _route_count() < 50:
            pytest.skip("seed DB too small for line floor check")
    html = client.get("/gradski/novi-sad/").data.decode()
    assert html.count("data-num") >= 10, "Expected at least 10 Novi Sad lines"


def test_route_detail_has_trips(client):
    html = client.get("/rute/beograd-novi-sad/").data.decode()
    assert "trip-card" in html, "Route detail should have trip cards"


def test_stop_detail_has_lines(client):
    html = client.get("/gradski/beograd/stajaliste/sajam/").data.decode()
    assert "stop-line-row" in html or "arrival-row" in html


# ── e) Health endpoint ───────────────────────────────────────────────


def test_health_has_db_field(client):
    data = json.loads(client.get("/health").data)
    assert data["checks"]["transit_db"]["ok"] is True
    assert data["status"] in ("ok", "degraded")


def test_health_surfaces_failed_scrapers(client, tmp_path, monkeypatch, app):
    """When last_refresh.json reports a per-scraper failure, /health
    surfaces the failed names under nightly.failed_scrapers and flips
    status to 'degraded'."""
    import json as _json
    logs_dir = Path(app.root_path).parent / 'logs'
    marker = logs_dir / 'last_refresh.json'
    backup = marker.read_text(encoding='utf-8') if marker.exists() else None
    try:
        marker.write_text(_json.dumps({
            'status': 'ok',
            'finished_at': '2026-04-27T01:00:00Z',
            'finished_ts': time.time() - 3600,
            'duration_s': 60,
            'health_http': '200',
            'scrapers': {
                'scrape_lasta': 'fail:1',
                'scrape_intercity': 'ok',
                'scrape_srbvoz': 'ok',
            },
        }))
        data = _json.loads(client.get('/health').data)
        assert data['checks']['nightly']['failed_scrapers'] == ['scrape_lasta']
        assert data['status'] == 'degraded'
    finally:
        if backup is not None:
            marker.write_text(backup, encoding='utf-8')
        else:
            marker.unlink(missing_ok=True)


# ── f) JSON-LD validation ───────────────────────────────────────────


@pytest.mark.parametrize("url", ["/", "/rute/beograd-novi-sad/", "/o-nama/", "/kontakt/"])
def test_json_ld_valid(client, url):
    html = client.get(url).data.decode()
    import re
    schemas = re.findall(r'application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for s in schemas:
        parsed = json.loads(s)
        assert "@context" in parsed


# ── g) "Departures left today" honest urgency signal ──────────────────


def test_departures_left_today_counts_only_upcoming():
    """Pure helper: counts real departures still ahead of now (HH:MM compare),
    ignoring blanks. No invented scarcity."""
    from app.routes.intercity import _departures_left_today
    trips = [{'departure_time': '06:00'}, {'departure_time': '12:30:00'},
             {'departure_time': '21:00'}, {'departure_time': ''}, {}]
    assert _departures_left_today(trips, '10:00') == 2   # 12:30 + 21:00
    assert _departures_left_today(trips, '23:00') == 0   # all gone
    assert _departures_left_today(trips, '00:00') == 3   # all ahead, blanks skipped


def test_next_departure_is_the_first_trip_after_now():
    from app.routes.intercity import _next_departure
    trips = [{'departure_time': '06:00'}, {'departure_time': ''}, {'departure_time': '12:30:00'},
             {'departure_time': '21:00'}]
    assert _next_departure(trips, '10:00') == (trips[2], 150)
    assert _next_departure(trips, '21:00') == (None, None)    # 21:00 itself has left


def test_route_detail_puts_the_next_departure_first(client, monkeypatch):
    from app.routes import intercity
    monkeypatch.setattr(intercity, '_belgrade_now_hhmm', lambda: '00:01')
    r = client.get('/en/rute/beograd-novi-sad/')
    if r.status_code != 200:
        pytest.skip('route page unavailable (no transit.duckdb in this env)')
    page = r.data.decode()
    assert 'Next departure' in page and 'data-surface="route_next"' in page
    assert page.index('class="next-dep') < page.index('id="tripList"')
    monkeypatch.setattr(intercity, '_belgrade_now_hhmm', lambda: '23:59')
    late = client.get('/en/rute/beograd-novi-sad/').data.decode()
    assert 'No more departures today.' in late and 'route_next' not in late
    assert 'class="next-dep' not in client.get('/en/rute/beograd-novi-sad/?dan=1').data.decode()


def test_route_detail_shows_departures_left_today(client, monkeypatch):
    """The today tab shows an honest "Left today" count; switching to tomorrow
    hides it (the signal is today-only)."""
    from app.routes import intercity
    monkeypatch.setattr(intercity, '_belgrade_now_hhmm', lambda: '00:01')
    r = client.get('/en/rute/beograd-novi-sad/')
    if r.status_code != 200:
        pytest.skip('route page unavailable (no transit.duckdb in this env)')
    assert 'Left today' in r.data.decode()
    tomorrow = client.get('/en/rute/beograd-novi-sad/?dan=1').data.decode()
    assert 'Left today' not in tomorrow


def test_route_detail_hides_departures_left_when_day_over(client, monkeypatch):
    """Late at night (after the last bus) the chip disappears — never a stale
    "0 left" or a past departure time."""
    from app.routes import intercity
    monkeypatch.setattr(intercity, '_belgrade_now_hhmm', lambda: '23:59')
    r = client.get('/en/rute/beograd-novi-sad/')
    if r.status_code != 200:
        pytest.skip('route page unavailable (no transit.duckdb in this env)')
    assert 'Left today' not in r.data.decode()

"""Performance regression gates — bundle size limits.

Rationale: the site is read-mostly, delivered over Cloudflare + gzip. HTML
transfer weight is the dominant Core Web Vitals lever. These tests lock in
the post-optimisation byte budget so a careless template change can't silently
triple the homepage payload.

Budgets are gzipped bytes (what the client downloads). Raw HTML is larger but
immaterial — nginx and flask-compress always serve gzip to mobile browsers.
Add +30% headroom vs current measurements so normal content growth doesn't
fail CI; tighten when a page materially regresses in Lighthouse.
"""

import gzip

import pytest


BUDGETS_GZIPPED = {
    "/": 15000,
    "/rute/": 70000,
    "/rute/beograd-novi-sad/": 20000,
    "/voznja/beograd-do-budva/": 18000,
    "/gradski/beograd/": 45000,
    "/gradski/beograd/stajaliste/sajam/": 20000,
}

CSS_BUDGET_GZIPPED = 18000  # app.css currently ~12KB gzipped; +50% headroom


@pytest.mark.parametrize("url,budget", list(BUDGETS_GZIPPED.items()))
def test_bundle_size_limits(client, url, budget):
    resp = client.get(url, headers={"Accept-Encoding": "gzip"})
    assert resp.status_code == 200, f"{url} returned {resp.status_code}"
    body = resp.data
    # Flask test client may decompress automatically; compress raw bytes
    # ourselves so we measure against the same yardstick as production.
    if resp.headers.get("Content-Encoding") != "gzip":
        body = gzip.compress(body)
    size = len(body)
    assert size <= budget, (
        f"{url}: gzipped size {size} exceeds budget {budget} "
        f"(diff +{size - budget}). Investigate template bloat before raising budget."
    )


def test_app_css_size_limit(client):
    resp = client.get("/static/css/app.css", headers={"Accept-Encoding": "gzip"})
    assert resp.status_code == 200
    body = resp.data
    if resp.headers.get("Content-Encoding") != "gzip":
        body = gzip.compress(body)
    size = len(body)
    assert size <= CSS_BUDGET_GZIPPED, (
        f"app.css gzipped size {size} exceeds budget {CSS_BUDGET_GZIPPED}"
    )


def test_no_eager_leaflet_on_map_pages(client):
    """Guard: map templates must not regress back to render-blocking Leaflet.
    Lazy pattern loads via dynamic <script> injection; eager pattern uses a
    static <script src="https://unpkg.com/leaflet..."> tag which would undo
    the 40KB/200ms savings documented in docs/06_tech/perf-baseline.md."""
    for url in ("/gradski/beograd/", "/gradski/beograd/linija/linija-2a/"):
        html = client.get(url).data.decode()
        # Inline JS string references are fine — actual static tag is not.
        assert '<script src="https://unpkg.com/leaflet' not in html, (
            f"{url} regressed to eager Leaflet <script> tag; use lazy loader"
        )

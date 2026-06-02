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
    "/": 19500,                                # raised: chat widget HTML + streaming JS
    "/rute/": 70000,
    "/rute/beograd-novi-sad/": 23000,          # raised: chat widget JS
    "/voznja/beograd-do-budva/": 21500,        # raised: hero tabs JS
    "/gradski/beograd/": 46000,
    "/gradski/beograd/stajaliste/sajam/": 23000,  # raised: chat widget JS
}

# raised: chat widget CSS + visual polish
CSS_BUDGET_GZIPPED = 26000


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


def test_no_eager_map_script_on_map_pages(client):
    """Guard: map templates must not use render-blocking static script tags.
    Both Leaflet (old) and Mapbox GL (current) must be loaded via dynamic
    <script> injection so the library parse stays off the critical path."""
    for url in ("/gradski/beograd/", "/gradski/beograd/linija/linija-2a/"):
        html = client.get(url).data.decode()
        assert '<script src="https://unpkg.com/leaflet' not in html, (
            f"{url} regressed to eager Leaflet <script> tag"
        )
        assert '<script src="https://api.mapbox.com' not in html, (
            f"{url} has eager static Mapbox GL tag; must use dynamic injection"
        )


# ── Mobile regression gates ────────────────────────────────────────────────
# Lock in the mobile-pass fixes from docs/06_tech/perf-baseline-mobile.md.
# Each test protects a common regression that the byte-size budget would not
# catch but that would still break real mobile UX.

MOBILE_16PX_SELECTORS = (
    ".journey-form__date",
    ".search-bar__input",
    ".review-form textarea",
    ".review-form input[type=\"text\"]",
    ".review-form input[type=\"email\"]",
)


def test_mobile_inputs_avoid_ios_zoom(client):
    """iOS auto-zooms any focused input with computed font-size < 16px. We
    remap sub-16px inputs to --text-base inside the <640px breakpoint.
    This test asserts the rule survives future edits; if a new input is
    legitimately below 16px, add it to the mobile block explicitly."""
    css = client.get("/static/css/app.css").data.decode()
    anchor = css.find("@media (max-width: 639px)")
    assert anchor != -1, "mobile breakpoint block went missing"
    block = css[anchor:anchor + 5000]
    for selector in MOBILE_16PX_SELECTORS:
        assert selector in block, (
            f"{selector} must be remapped to 16px inside <640px block "
            "to prevent iOS zoom-on-focus"
        )


def test_form_inputs_have_mobile_keyboard_hints(client):
    """Email inputs must surface the email keyboard + autocomplete. Search
    inputs must surface enterkeyhint. A <input type="text"> regression
    would force the user to hunt for @ on their virtual keyboard."""
    html = client.get("/").data.decode()
    assert 'inputmode="email"' in html, "newsletter email input lost inputmode"
    assert 'autocomplete="email"' in html
    assert ('enterkeyhint="search"' in html) or ('enterkeyhint="next"' in html)


def test_map_containers_reserve_height(client):
    """CLS guard: Leaflet containers must not collapse to 0 before JS runs.
    If someone swaps the explicit height/aspect-ratio for a content-driven
    layout, the hero pops in and blows CLS."""
    css = client.get("/static/css/app.css").data.decode()
    assert "aspect-ratio" in css, (
        "map wrap lost its CLS-reserving aspect-ratio rule"
    )
    hero_anchor = css.find(".stop-hero__map")
    assert hero_anchor != -1
    hero_decl = css[hero_anchor:hero_anchor + 400]
    assert "height:" in hero_decl and "180px" in hero_decl, (
        "stop-hero__map must keep its explicit 180px height (LCP candidate)"
    )


def test_ios_safe_area_insets_in_layout(client):
    """iPhone X+ notch / home indicator need env(safe-area-inset-*) on
    pinned chrome (header, footer, cookie + install banners). Regression
    here leaves content under the notch or behind the home bar."""
    css = client.get("/static/css/app.css").data.decode()
    assert "safe-area-inset-top" in css
    assert "safe-area-inset-bottom" in css
    assert "safe-area-inset-left" in css
    assert "safe-area-inset-right" in css


def test_autocomplete_js_has_early_return(client):
    """The city-autocomplete block ships from base.html on every page even
    when no search form exists. The early-return keeps per-page TBT ~0ms
    on ~4000 non-form pages."""
    html = client.get("/o-nama/").data.decode()
    assert ".js-city-input" in html
    assert "_cityInputs.length" in html  # guarded NodeList length check

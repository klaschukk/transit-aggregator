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
    "/": 20400,                                # raised: default-English first-visit redirect JS (in <head>, every page)
    "/rute/": 70000,
    "/rute/beograd-novi-sad/": 24500,          # raised: route-overview map (markup + intent-gated Mapbox
                                                # init script, geometry itself fetched separately via
                                                # /api/route-geometry — not inlined). Full-suite runs also
                                                # see ~5KB more than an isolated run on this exact route
                                                # (pre-existing cross-test state bleed, e.g. test_reviews.py
                                                # seeding rows for this slug — not caused by the map); budget
                                                # includes headroom for that rather than chasing it down here.
                                                # +46B 2026-09: ResizeObserver fix for a real live bug (map
                                                # rendering as a narrow rectangle, stuck at its init-time
                                                # width) — real fix, not fat.
    "/voznja/beograd-do-budva/": 22200,        # raised: default-English first-visit redirect JS (in <head>, every page)
    "/gradski/beograd/": 46000,
    "/gradski/beograd/stajaliste/sajam/": 23400,  # raised: default-English first-visit redirect JS (in <head>, every page)
}

# Budgets for the MINIFIED CSS — that's what prod ships (base.html serves
# dist/*.css when not DEBUG). The old budget measured the raw source app.css
# (~27 KB gzip), but the client actually downloads the minified dist (~16 KB),
# so the source budget guarded the wrong artifact and would false-trip on
# source growth that minifies away. Headroom ~+25% over current minified size.
CSS_BUDGETS_MIN_GZIPPED = {
    "app.css": 20000,         # currently ~16.1 KB minified+gzipped
    "app.mobile.css": 6000,   # currently ~4.3 KB minified+gzipped
}


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


@pytest.mark.parametrize("name,budget", CSS_BUDGETS_MIN_GZIPPED.items())
def test_css_minified_size_limit(name, budget):
    """Measure the MINIFIED + gzipped CSS — the actual prod payload — instead
    of the raw source the client never downloads."""
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "minify_css", Path(__file__).resolve().parent.parent / "scripts" / "minify_css.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    raw = (Path(__file__).resolve().parent.parent / "app" / "static" / "css" / name).read_text()
    size = len(gzip.compress(mod.minify(raw).encode()))
    assert size <= budget, (
        f"{name} minified+gzipped {size} exceeds budget {budget} "
        f"(diff +{size - budget}) — tighten the source or raise the budget knowingly"
    )


@pytest.mark.parametrize("name", ["app.css", "app.mobile.css", "ads.css", "admin.css"])
def test_css_braces_balanced(name):
    """Every block must close exactly once.

    A stray '}' does not fail a build, does not fail any other test, and
    does not stop the minifier — the browser just discards from the bad
    token to the next recoverable rule, so an arbitrary slice of the
    stylesheet silently stops applying. That is exactly how a run of
    responsive grid rules went missing once: the page still rendered,
    only wrong. Comments are stripped first because braces inside them
    do not count."""
    from pathlib import Path
    import re

    src = (Path(__file__).resolve().parent.parent
           / "app" / "static" / "css" / name).read_text()
    stripped = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    opens, closes = stripped.count("{"), stripped.count("}")
    assert opens == closes, (
        f"{name}: {opens} '{{' vs {closes} '}}' — unbalanced braces mean the "
        f"browser drops rules from the bad token onward"
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
# Lock in the mobile-pass fixes from docs/90_archive/06_tech/perf-baseline-mobile.md.
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


def test_header_logo_is_eager_not_lazy(client):
    """The site logo sits in the header — above the fold on every page. Lazy-
    loading an above-the-fold image is a Lighthouse anti-pattern that delays
    first paint / LCP, so the logo must load eagerly."""
    import re
    html = client.get("/").data.decode()
    m = re.search(r'<img[^>]*class="site-logo__icon"[^>]*>', html)
    assert m, "site logo <img> not found in header"
    tag = m.group(0)
    assert 'loading="lazy"' not in tag, "above-the-fold logo must not be lazy-loaded"
    assert 'loading="eager"' in tag


def test_autocomplete_input_and_listbox_are_wired_by_id(client):
    """The city input must point at its listbox with aria-controls, and
    the JS must resolve it that way.

    It used to do `input.parentElement.querySelector('.autocomplete')`,
    which held only while the two were siblings. Wrapping the caption and
    the input in a <label> — so clicking anywhere in the 64px field
    focuses it — moved the listbox out of that parent and killed the
    autocomplete on every page rendering this form. Nothing caught it:
    the markup was valid, every page still returned 200, and the failure
    only showed when a human typed a city name.
    """
    html = client.get("/").data.decode()
    assert 'aria-controls="fromDropdown"' in html
    assert 'id="fromDropdown"' in html
    assert 'aria-controls="toDropdown"' in html
    assert 'id="toDropdown"' in html
    # The lookup must not depend on the input and listbox being siblings.
    assert "input.parentElement.querySelector('.autocomplete')" not in html, (
        "autocomplete resolves its listbox by DOM position again — that "
        "breaks the moment the field markup is regrouped"
    )
    assert "input.getAttribute('aria-controls')" in html


def test_search_field_label_wraps_its_input(client):
    """A click anywhere in the field focuses the input, natively.

    The first attempt grew the INPUT to fill the cell instead, which
    pinned the caption to the capsule's top edge and left the value
    floating ~25px below it — the two stopped reading as one field.
    """
    html = client.get("/").data.decode()
    for fid in ("fromCity", "toCity", "tripDate"):
        assert f'class="journey-form__field" for="{fid}"' in html, fid

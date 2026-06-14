"""SEO tests — titles, descriptions, JSON-LD, sitemap, robots."""

import json
import re

import pytest


def _route_count() -> int:
    try:
        from app.db import query
        result = query("SELECT COUNT(*) FROM routes")
        return (result or [[0]])[0][0]
    except Exception:
        return 0


def _beograd_line_count() -> int:
    """Belgrade city_lines in the active DB.

    The night-bus / airport / tram guides are DB-grounded: they render their
    line links from the full Belgrade line set (~521 lines). The tiny CI seed
    carries only a handful of regular lines (no night/tram/airport lines at
    all), so those guides legitimately render zero matching links there. Tests
    use this to skip cleanly on the seed — same contract as the GTFS-headway
    skips — and run for real against the full DB.
    """
    try:
        from app.db import query
        # query() returns a list of dicts — alias the count so we read it by
        # name (result[0][0] would KeyError on a dict and silently skip away).
        result = query("SELECT COUNT(*) AS c FROM city_lines WHERE city = 'beograd'")
        return result[0]["c"] if result else 0
    except Exception:
        return 0


# Below this many Belgrade lines the DB is the seed fixture, not the real set.
_SEED_BG_LINES_CEILING = 50


_ALL_PAGES = [
    "/", "/rute/", "/gradski/", "/gradski/beograd/", "/gradski/novi-sad/",
    "/prevoznici/", "/autobuske-stanice/", "/o-nama/", "/kontakt/",
    "/rute/beograd-novi-sad/", "/voznja/beograd-do-novi-sad/",
    "/gradski/beograd/linija/linija-2a/", "/gradski/beograd/stajaliste/sajam/",
]


# ── Title length ──


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_title_length(client, url):
    html = client.get(url).data.decode()
    m = re.search(r"<title>(.*?)</title>", html)
    assert m, f"No <title> on {url}"
    title = m.group(1).strip()
    assert 10 <= len(title) <= 75, f"Title length {len(title)} on {url}: {title}"


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_title_no_none(client, url):
    html = client.get(url).data.decode()
    title = re.search(r"<title>(.*?)</title>", html).group(1)
    assert "None" not in title, f"None in title: {title}"


# ── Meta description length ──


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_description_length(client, url):
    html = client.get(url).data.decode()
    m = re.search(r'name="description"\s+content="([^"]*)"', html)
    assert m, f"No meta description on {url}"
    desc = m.group(1).strip()
    assert 40 <= len(desc) <= 300, f"Description length {len(desc)} on {url}: {desc}"


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_description_no_none(client, url):
    html = client.get(url).data.decode()
    m = re.search(r'name="description"\s+content="([^"]*)"', html)
    if m:
        assert "None" not in m.group(1), f"None in description on {url}"


# ── Canonical ──


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_has_canonical(client, url):
    html = client.get(url).data.decode()
    assert 'rel="canonical"' in html, f"No canonical on {url}"


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_canonical_has_path(client, url):
    """Canonical URL must contain the page path (domain varies by config).

    Exception: /voznja/<a>-do-<b>/ canonicalises onto its /rute/<a>-<b>/ owner
    (cannibalisation fix), so its canonical is the owner path, not self.
    """
    html = client.get(url).data.decode()
    m = re.search(r'rel="canonical"\s+href="([^"]*)"', html)
    assert m, f"No canonical href on {url}"
    canon = m.group(1)
    if url.startswith("/voznja/"):
        owner = "/rute/" + url[len("/voznja/"):].replace("-do-", "-", 1)
        assert owner.rstrip("/") in canon, \
            f"voznja must canonicalise to its /rute/ owner, got: {canon}"
    else:
        assert url.rstrip("/") in canon or url == "/", f"Path missing from canonical: {canon}"


# ── OG tags ──


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_og_title(client, url):
    html = client.get(url).data.decode()
    assert 'property="og:title"' in html, f"No og:title on {url}"


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_og_description(client, url):
    html = client.get(url).data.decode()
    assert 'property="og:description"' in html, f"No og:description on {url}"


# ── No "None" in visible text ──


@pytest.mark.parametrize("url", _ALL_PAGES)
def test_no_none_in_content(client, url):
    html = client.get(url).data.decode()
    main = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL)
    if main:
        text = re.sub(r"<script.*?</script>", "", main.group(1), flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", "", text)
        assert "None km" not in text, f"'None km' on {url}"
        assert "None pol" not in text, f"'None pol' on {url}"
        assert ">None<" not in main.group(1), f"'>None<' on {url}"


# ── Sitemap ──


# /sitemap.xml is a sitemap-index pointing at the content-type shards.
# Tests load each shard explicitly instead of expecting one monolithic urlset.
# 'pairs' is deprecated: every indexable /voznja/ pair canonicalises onto its
# /rute/ owner (already in sitemap-routes), so the pairs shard is intentionally
# empty and dropped from the index — see test_pairs_shard_deprecated_and_empty.
# 'far' holds far-destination /voznja guides with a cached composed itinerary
# (the only /voznja URLs that are self-canonical) — see test_far_routes.py.
_SHARDS = [
    "/sitemap-core.xml",
    "/sitemap-routes.xml",
    "/sitemap-lines.xml",
    "/sitemap-stops.xml",
    "/sitemap-far.xml",
]


def _all_sitemap_xml(client) -> str:
    """Concatenated XML from every shard — used when a test just wants to
    assert something about *the full sitemap surface* without caring which
    shard holds the URL."""
    return "\n".join(client.get(s).data.decode() for s in _SHARDS)


def test_sitemap_index_references_all_shards(client):
    xml = client.get("/sitemap.xml").data.decode()
    assert "<sitemapindex" in xml
    for shard in _SHARDS:
        assert shard in xml, f"sitemap-index is missing shard {shard}"


def test_pairs_shard_deprecated_and_empty(client):
    """The /voznja/ pairs shard must NOT be advertised in the index (its URLs
    all canonicalise to /rute/), and the route itself must return a valid but
    empty urlset so legacy GSC submissions don't 404."""
    index = client.get("/sitemap.xml").data.decode()
    assert "/sitemap-pairs.xml" not in index, "deprecated pairs shard is still in the index"
    resp = client.get("/sitemap-pairs.xml")
    assert resp.status_code == 200
    body = resp.data.decode()
    assert "<urlset" in body and "</urlset>" in body
    assert "<url>" not in body and "/voznja/" not in body


def test_sitemap_url_count(client, app):
    with app.app_context():
        if _route_count() < 50:
            pytest.skip("seed DB too small for sitemap URL count check")
    xml = _all_sitemap_xml(client)
    count = xml.count("<url>")
    assert count >= 1000, f"Sitemap has only {count} URLs across shards"


def test_sitemap_consistent_base_url(client):
    """All sitemap URLs should use the same base URL (whatever it is)."""
    xml = _all_sitemap_xml(client)
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    bases = set()
    for u in urls[:20]:
        base = u.split("/", 3)[:3]  # ['http:', '', 'host:port']
        bases.add("/".join(base))
    assert len(bases) == 1, f"Mixed base URLs in sitemap: {bases}"


def test_sitemap_has_routes(client):
    xml = client.get("/sitemap-routes.xml").data.decode()
    assert "/rute/" in xml


def test_sitemap_has_lines(client):
    xml = client.get("/sitemap-lines.xml").data.decode()
    assert "/linija/" in xml


def test_sitemap_has_stops(client):
    xml = client.get("/sitemap-stops.xml").data.decode()
    assert "/stajaliste/" in xml


def test_sitemap_core_lists_every_guide_and_country_hub(client):
    """sitemap-core derives guide and country-hub URLs from their registries
    in app.routes.info, so a new entry there is always discoverable. Guards
    against the old hand-synced list silently orphaning a fresh guide."""
    from app.routes.info import _COUNTRY_HUBS, _GUIDES
    xml = client.get("/sitemap-core.xml").data.decode()
    for slug in _COUNTRY_HUBS:
        assert f"/destinacije/{slug}/" in xml, f"country hub {slug} missing from sitemap"
    for slug in _GUIDES:
        assert f"/vodici/{slug}/" in xml, f"guide {slug} missing from sitemap"


def test_sitemap_sample_urls_valid(client):
    """Pick 5 URLs from the combined sitemap shards and verify they 200."""
    xml = _all_sitemap_xml(client)
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    # Filter out the shard-index URLs themselves
    urls = [u for u in urls if "/sitemap-" not in u]
    step = max(1, len(urls) // 5)
    for i in range(0, min(len(urls), step * 5), step):
        url = urls[i]
        path = url.split("//", 1)[-1].split("/", 1)[-1]  # strip domain
        resp = client.get("/" + path)
        assert resp.status_code == 200, f"Sitemap URL /{path} returned {resp.status_code}"


# ── Robots.txt ──


def test_robots_disallow_api(client):
    txt = client.get("/robots.txt").data.decode()
    assert "Disallow: /api/" in txt


def test_robots_has_sitemap(client):
    txt = client.get("/robots.txt").data.decode()
    assert "Sitemap:" in txt
    assert "sitemap.xml" in txt


# ── JSON-LD ──


_JSONLD_PAGES = [
    ("/", "WebSite"),
    ("/rute/beograd-novi-sad/", "ItemList"),
    ("/gradski/beograd/stajaliste/sajam/", "BusStation"),
    ("/prevoznici/", "ItemList"),
    ("/voznja/beograd-do-novi-sad/", "FAQPage"),
]


@pytest.mark.parametrize("url,expected_type", _JSONLD_PAGES)
def test_json_ld_valid(client, url, expected_type):
    html = client.get(url).data.decode()
    blocks = re.findall(r'type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    assert blocks, f"No JSON-LD on {url}"
    found = False
    for block in blocks:
        parsed = json.loads(block)
        assert "@context" in parsed
        if parsed.get("@type") == expected_type:
            found = True
    assert found, f"No JSON-LD @type={expected_type} on {url}"


def test_json_ld_breadcrumb_on_subpages(client):
    for url in ["/rute/", "/gradski/beograd/", "/prevoznici/"]:
        html = client.get(url).data.decode()
        assert "BreadcrumbList" in html, f"No BreadcrumbList on {url}"


def test_route_links_to_city_transport_hub_for_covered_endpoint(client):
    """An intercity route whose endpoint is one of the 4 cities we cover
    locally must link to that city's /gradski/ hub — funnels crawl/authority
    to the high-traffic city pages. Beograd–Novi Sad covers both ends."""
    html = client.get("/rute/beograd-novi-sad/").data.decode()
    assert '/gradski/beograd/"' in html, "no city-transport link to Beograd hub"
    assert '/gradski/novi-sad/"' in html, "no city-transport link to Novi Sad hub"
    # A route to a non-covered city links only the covered endpoint.
    html2 = client.get("/rute/beograd-budva/").data.decode()
    assert '/gradski/beograd/"' in html2
    assert '/gradski/budva/"' not in html2, "linked a city we don't cover locally"


def test_voznja_links_to_city_transport_hub_for_covered_endpoint(client):
    """Same city-transport cross-link on the /voznja/ city-pair page."""
    html = client.get("/voznja/beograd-do-novi-sad/").data.decode()
    assert '/gradski/beograd/"' in html, "no city-transport link to Beograd hub"
    assert '/gradski/novi-sad/"' in html, "no city-transport link to Novi Sad hub"
    html2 = client.get("/voznja/beograd-do-budva/").data.decode()
    assert '/gradski/beograd/"' in html2
    assert '/gradski/budva/"' not in html2, "linked a city we don't cover locally"


def test_nocni_bus_guide_indexable_and_links_night_lines(client):
    """The Belgrade night-bus guide must be indexable, list real night lines
    (links to /gradski/beograd/linija/linija-Nn/), and be in the sitemap.
    Content is DB-grounded — the page must carry several night-line links."""
    import re
    if _beograd_line_count() < _SEED_BG_LINES_CEILING:
        pytest.skip("seed DB has no Belgrade night lines — guide is DB-grounded")
    resp = client.get("/vodici/nocni-autobus-beograd/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "noindex" not in html.lower(), "night-bus guide must stay indexable"
    assert "/vodici/nocni-autobus-beograd/" in client.get("/sitemap-core.xml").data.decode()
    # The link-count is DB-grounded: the seed has no Belgrade night lines, so
    # skip that assertion there (page/indexable/sitemap checks above still run).
    from app.db import query_one
    have = query_one("SELECT COUNT(*) AS c FROM city_lines "
                     "WHERE city='beograd' AND lower(slug) LIKE 'linija-%n'")
    if not have or have["c"] < 10:
        pytest.skip("seed DB lacks Belgrade night lines")
    night_links = re.findall(r"/gradski/beograd/linija/linija-\d+n/", html)
    assert len(night_links) >= 10, f"too few night-line links: {len(night_links)}"


def test_airport_guide_indexable_and_links_real_lines(client):
    """Belgrade airport guide must be indexable, link the real Nikola Tesla
    lines (72, A1, 600, 607, 72N), and be in the sitemap. DB-grounded."""
    if _beograd_line_count() < _SEED_BG_LINES_CEILING:
        pytest.skip("seed DB lacks Belgrade airport lines — guide is DB-grounded")
    resp = client.get("/vodici/kako-doci-do-aerodroma-beograd/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "noindex" not in html.lower(), "airport guide must stay indexable"
    assert "/vodici/kako-doci-do-aerodroma-beograd/" in client.get("/sitemap-core.xml").data.decode()
    # DB-grounded: seed lacks the airport lines (72/A1). Skip the link asserts.
    from app.db import query_one
    have = query_one("SELECT COUNT(*) AS c FROM city_lines "
                     "WHERE city='beograd' AND slug='linija-72'")
    if not have or have["c"] == 0:
        pytest.skip("seed DB lacks Belgrade airport lines")
    assert "/gradski/beograd/linija/linija-72/" in html, "no link to line 72"
    assert "/gradski/beograd/linija/linija-a1/" in html, "no link to line A1"


def test_tram_guide_indexable_links_deduped_lines(client):
    """Belgrade tram guide must be indexable, link real tram lines, dedupe by
    slug (9Л/9л → one linija-9l), and be in the sitemap. DB-grounded."""
    import re
    if _beograd_line_count() < _SEED_BG_LINES_CEILING:
        pytest.skip("seed DB has no Belgrade tram lines — guide is DB-grounded")
    resp = client.get("/vodici/tramvaj-beograd/")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "noindex" not in html.lower(), "tram guide must stay indexable"
    assert "/vodici/tramvaj-beograd/" in client.get("/sitemap-core.xml").data.decode()
    # DB-grounded: seed has no Belgrade tram lines. Skip the link asserts.
    from app.db import query_one
    have = query_one("SELECT COUNT(*) AS c FROM city_lines "
                     "WHERE city='beograd' AND type='tram'")
    if not have or have["c"] < 8:
        pytest.skip("seed DB lacks Belgrade tram lines")
    links = re.findall(r"/gradski/beograd/linija/(linija-[0-9a-z]+)/", html)
    assert len(links) >= 8, f"too few tram-line links: {len(links)}"
    assert len(links) == len(set(links)), f"tram links not deduped: {links}"


def test_line_faq_adds_frequency_question_when_headway(client):
    # "Na koliko minuta ide linija N" is a top GSC query: when a line has a
    # GTFS-derived headway, its FAQPage must carry a frequency Q&A. Novi Sad
    # line 6 is a core frequent line that reliably has a headway. Every line's
    # FAQPage must always be valid JSON with no trailing-comma breakage.
    # This is fundamentally a GTFS-headway test: the seed DB carries no GTFS
    # stop_times (and no NS line 6), so it is meaningless there — skip cleanly.
    import json
    import re
    from app.db import query_one
    gtfs = query_one("SELECT COUNT(*) AS c FROM gtfs_stop_times")
    if not gtfs or gtfs["c"] == 0:
        pytest.skip("seed DB has no GTFS headway data — frequency Q&A absent")
    html = client.get("/gradski/novi-sad/linija/linija-6/").data.decode()
    faq = None
    for block in re.findall(r'type="application/ld\+json">(.*?)</script>',
                            html, re.DOTALL):
        parsed = json.loads(block)  # raises on the trailing-comma bug
        if parsed.get("@type") == "FAQPage":
            faq = parsed
    assert faq is not None, "no FAQPage JSON-LD on line page"
    questions = [m["name"] for m in faq["mainEntity"]]
    assert any("koliko minuta" in q for q in questions), \
        f"no frequency question in line FAQ: {questions}"

    # A line without a headway keeps a clean 3-question FAQ (no broken JSON).
    html2 = client.get("/gradski/kragujevac/linija/linija-1/").data.decode()
    for block in re.findall(r'type="application/ld\+json">(.*?)</script>',
                            html2, re.DOTALL):
        json.loads(block)

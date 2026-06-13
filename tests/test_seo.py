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

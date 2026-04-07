"""SEO tests — titles, descriptions, JSON-LD, sitemap, robots."""

import json
import re

import pytest


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
    """Canonical URL must contain the page path (domain varies by config)."""
    html = client.get(url).data.decode()
    m = re.search(r'rel="canonical"\s+href="([^"]*)"', html)
    assert m, f"No canonical href on {url}"
    canon = m.group(1)
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


def test_sitemap_url_count(client):
    xml = client.get("/sitemap.xml").data.decode()
    count = xml.count("<url>")
    assert count >= 1000, f"Sitemap has only {count} URLs"


def test_sitemap_consistent_base_url(client):
    """All sitemap URLs should use the same base URL (whatever it is)."""
    xml = client.get("/sitemap.xml").data.decode()
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    bases = set()
    for u in urls[:20]:
        base = u.split("/", 3)[:3]  # ['http:', '', 'host:port']
        bases.add("/".join(base))
    assert len(bases) == 1, f"Mixed base URLs in sitemap: {bases}"


def test_sitemap_has_routes(client):
    xml = client.get("/sitemap.xml").data.decode()
    assert "/rute/" in xml


def test_sitemap_has_lines(client):
    xml = client.get("/sitemap.xml").data.decode()
    assert "/linija/" in xml


def test_sitemap_has_stops(client):
    xml = client.get("/sitemap.xml").data.decode()
    assert "/stajaliste/" in xml


def test_sitemap_sample_urls_valid(client):
    """Pick 5 URLs from sitemap and verify they return 200."""
    xml = client.get("/sitemap.xml").data.decode()
    urls = re.findall(r"<loc>([^<]+)</loc>", xml)
    # Pick evenly spaced samples
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
    ("/gradski/beograd/stajaliste/sajam/", "BusStop"),
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

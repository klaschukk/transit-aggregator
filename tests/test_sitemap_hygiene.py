"""Sitemap hygiene guard. The shards themselves (200-only URLs, priced-trip
filters, per-URL lastmod) are exercised by test_seo; the noindex↔sitemap
alignment is exercised by test_thin_noindex (a route with no priced trips is
both noindex AND excluded from sitemap-routes by the same condition).

This adds the one piece neither covers: the index lastmod must be a real data
date (YYYY-MM-DD from the DB / scraper mtimes), never a build constant or
timestamp. Scoped to /sitemap.xml (5 lines) so it stays fast.
"""

import re

import pytest

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_sitemap_index_lastmod_is_a_real_date(client):
    xml = client.get("/sitemap.xml").data.decode()
    mods = re.findall(r"<lastmod>([^<]+)</lastmod>", xml)
    assert mods, "sitemap index has no <lastmod>"
    for lm in mods:
        assert DATE.match(lm), f"lastmod is not a YYYY-MM-DD data date: {lm!r}"


def test_stopless_lines_are_noindex_and_absent_from_sitemap(client, db):
    """A line with no stops has nothing to show — keep it out of the index.

    The page rendered an empty ItemList (numberOfItems: 0) and an FAQ
    answering "linija 21 ima 0 stajališta", yet shipped index,follow and sat
    in sitemap-lines: 41 such lines (39 in Niš) after a stop scrape failed.
    They stay reachable and crawlable (noindex, follow) and re-enter the
    sitemap by themselves once the stops come back.
    """
    row = db.one("""
        SELECT cl.city, cl.slug FROM city_lines cl
        WHERE NOT EXISTS (SELECT 1 FROM city_line_stops cls
                          WHERE cls.line_id = cl.id)
        LIMIT 1
    """)
    if not row:
        pytest.skip("no stopless lines in this DB")
    path = f"/gradski/{row['city']}/linija/{row['slug']}/"
    html = client.get(path).data.decode()
    robots = re.search(r'<meta name="robots" content="([^"]*)"', html)
    assert robots and "noindex" in robots.group(1), (
        f"{path} must not be indexable without stops"
    )
    sitemap = client.get("/sitemap-lines.xml").data.decode()
    assert path not in sitemap, f"{path} is noindex but listed in sitemap"


def test_lines_with_stops_stay_indexable(client, db):
    """The thin-content guard must only hit genuinely empty lines."""
    row = db.one("""
        SELECT cl.city, cl.slug FROM city_lines cl
        WHERE EXISTS (SELECT 1 FROM city_line_stops cls
                      WHERE cls.line_id = cl.id)
        LIMIT 1
    """)
    if not row:
        pytest.skip("no populated lines in this DB")
    path = f"/gradski/{row['city']}/linija/{row['slug']}/"
    html = client.get(path).data.decode()
    # Match the meta tag, not the whole page: a template comment mentions
    # "noindex" and a substring check reads that as the page being noindex.
    robots = re.search(r'<meta name="robots" content="([^"]*)"', html)
    assert robots and "noindex" not in robots.group(1), (
        f"{path} has stops and must stay indexable"
    )
    assert path in client.get("/sitemap-lines.xml").data.decode()


def test_sitemap_urls_do_not_redirect(client):
    """Every URL we submit must be the final one, not a 301 hop.

    The static slug-redirect maps take priority over the DB, so a stop that a
    later scrape brings back kept redirecting to the city hub while also being
    listed in the sitemap — 9 Novi Sad stops after the OSM stop import.
    """
    import random
    xml = client.get("/sitemap-stops.xml").data.decode()
    locs = re.findall(r"<loc>(.*?)</loc>", xml)
    paths = [re.sub(r"^https?://[^/]+", "", l) for l in locs]
    if not paths:
        pytest.skip("empty stop sitemap")
    random.seed(17)
    for p in random.sample(paths, min(40, len(paths))):
        code = client.get(p).status_code
        assert code == 200, f"{p} in sitemap returns {code}, not 200"


def test_returned_stop_beats_stale_redirect(client, db):
    """A stop present in the DB must render, even if the redirect map lists it."""
    from app.routes.city import _STOP_SLUG_REDIRECTS
    for city, mapping in _STOP_SLUG_REDIRECTS.items():
        for old in mapping:
            if db.one("SELECT 1 AS ok FROM city_stops WHERE city = ? AND slug = ?",
                      [city, old]):
                path = f"/gradski/{city}/stajaliste/{old}/"
                assert client.get(path).status_code == 200, (
                    f"{path} exists in the DB but the redirect map hides it"
                )
                return
    pytest.skip("no redirect-mapped stop is currently live")

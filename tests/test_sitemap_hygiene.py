"""Sitemap hygiene guard. The shards themselves (200-only URLs, priced-trip
filters, per-URL lastmod) are exercised by test_seo; the noindex↔sitemap
alignment is exercised by test_thin_noindex (a route with no priced trips is
both noindex AND excluded from sitemap-routes by the same condition).

This adds the one piece neither covers: the index lastmod must be a real data
date (YYYY-MM-DD from the DB / scraper mtimes), never a build constant or
timestamp. Scoped to /sitemap.xml (5 lines) so it stays fast.
"""

import re

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

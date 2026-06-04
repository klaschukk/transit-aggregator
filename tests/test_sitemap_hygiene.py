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

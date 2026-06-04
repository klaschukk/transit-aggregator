"""Removed programmatic pages return 410 (Gone), not 404, so Google deindexes
them fast instead of leaving them in GSC "Not found (404)" for months.

Background: a 2026 re-scrape dropped ~886 city stops (3770→2884) and retired the
single-token /rute/<city>/ hub scheme. Those indexed URLs are permanently dead.
Renamed stops are re-found via their new slug in sitemap-stops; the old URL is
correctly 410.
"""

import pytest


def test_missing_stop_is_410(client):
    assert client.get("/gradski/novi-sad/stajaliste/this-stop-was-removed-xyz/").status_code == 410
    # a real GSC-404 example (removed in the re-scrape)
    assert client.get("/gradski/novi-sad/stajaliste/banostor-1/").status_code == 410


def test_missing_line_is_410(client):
    assert client.get("/gradski/beograd/linija/linija-removed-xyz/").status_code == 410
    assert client.get("/gradski/beograd/linija/linija-604/").status_code == 410


def test_single_token_route_is_410(client):
    # Retired /rute/<city>/ hub scheme — a live route slug is always from-to.
    for slug in ("budimpesta", "jagodina", "pancevo", "kotor"):
        assert client.get(f"/rute/{slug}/").status_code == 410, slug


def test_hyphenated_missing_route_stays_404(client):
    # Looks like a from-to slug → could be a typo or not-yet-scraped route.
    # Keep 404 (retryable), don't over-claim 410.
    assert client.get("/rute/beograd-thiscitydoesnotexistxyz/").status_code == 404


def test_valid_pages_still_200(client, db):
    assert client.get("/rute/beograd-novi-sad/").status_code == 200
    row = db.one("SELECT city, slug FROM city_stops LIMIT 1")
    if row:
        city = row["city"] if isinstance(row, dict) else row[0]
        slug = row["slug"] if isinstance(row, dict) else row[1]
        assert client.get(f"/gradski/{city}/stajaliste/{slug}/").status_code == 200

"""Thin pages ("crawled, currently not indexed") must noindex so Google stops
re-fetching them, while staying reachable (follow). Targets: intercity routes
with no priced trips, /voznja/ pairs with no route row, operators with no
priced routes. Healthy pages stay indexable.

Examples are looked up at runtime so the test holds on both the full DB and the
trimmed CI seed.
"""

import re

import pytest


def _robots(client, url):
    html = client.get(url).data.decode()
    m = re.search(r'name="robots" content="([^"]+)"', html)
    return m.group(1) if m else None


def _slug(row):
    if row is None:
        return None
    return row["slug"] if isinstance(row, dict) else row[0]


def test_route_without_priced_trips_is_noindex(client, db):
    slug = _slug(db.one(
        "SELECT r.slug FROM routes r WHERE r.type='intercity' "
        "AND NOT EXISTS (SELECT 1 FROM trips t WHERE t.route_id=r.id AND t.price_rsd>0) "
        "LIMIT 1"
    ))
    if not slug:
        pytest.skip("no trip-less route in this DB")
    assert _robots(client, f"/rute/{slug}/").startswith("noindex")


def test_route_with_priced_trips_is_indexable(client, db):
    slug = _slug(db.one(
        "SELECT r.slug FROM routes r WHERE r.type='intercity' "
        "AND EXISTS (SELECT 1 FROM trips t WHERE t.route_id=r.id AND t.price_rsd>0) "
        "LIMIT 1"
    ))
    assert slug, "expected at least one priced route"
    assert _robots(client, f"/rute/{slug}/").startswith("index")


def test_operator_without_priced_routes_is_noindex(client, db):
    slug = _slug(db.one(
        "SELECT o.slug FROM operators o WHERE NOT EXISTS ("
        "  SELECT 1 FROM trips t JOIN routes r ON r.id=t.route_id "
        "  WHERE t.operator_id=o.id AND r.type='intercity' AND t.price_rsd>0) "
        "LIMIT 1"
    ))
    if not slug:
        pytest.skip("no priced-route-less operator in this DB")
    assert _robots(client, f"/prevoznici/{slug}/").startswith("noindex")


def test_empty_pair_is_noindex(client):
    assert _robots(client, "/voznja/nonexistentcity-do-nowhereville/").startswith("noindex")


def test_healthy_pages_stay_indexable(client):
    for url in ["/", "/rute/", "/gradski/beograd/"]:
        assert _robots(client, url).startswith("index"), url

"""A route with a real timetable but no scraped fare must RENDER its schedule
and appear in the sitemap — the "X red vožnje" intent the site ranks for.
Regression guard for the schedule query switching from `price>0` to
`departure_time IS NOT NULL`, plus the matching sitemap filter.

Routes are looked up at runtime, so it holds on the full DB and the CI seed
(seed fixture `cacak-kragujevac` is schedule-only, no price).
"""
import re

import pytest


def _slug(row):
    if row is None:
        return None
    return row["slug"] if isinstance(row, dict) else row[0]


def _schedule_no_price_route(db):
    return _slug(db.one(
        "SELECT r.slug FROM routes r WHERE r.type='intercity' "
        "AND NOT EXISTS (SELECT 1 FROM trips t WHERE t.route_id=r.id AND t.price_rsd>0) "
        "AND EXISTS (SELECT 1 FROM trips t WHERE t.route_id=r.id "
        "            AND t.departure_time IS NOT NULL AND t.departure_time<>'') "
        "LIMIT 1"
    ))


def test_schedule_no_price_route_renders_times(client, db):
    slug = _schedule_no_price_route(db)
    if not slug:
        pytest.skip("no schedule-without-price route in this DB")
    html = client.get(f"/rute/{slug}/").data.decode()
    # The timetable is actually visible: several HH:MM departure times present.
    times = re.findall(r"\b[0-2]\d:[0-5]\d\b", html)
    assert len(times) >= 2, f"expected a visible schedule on /rute/{slug}/"


def test_schedule_no_price_route_in_sitemap(client, db):
    slug = _schedule_no_price_route(db)
    if not slug:
        pytest.skip("no schedule-without-price route in this DB")
    # Sitemap must agree with the page's indexability.
    assert f"/rute/{slug}/" in client.get("/sitemap-routes.xml").data.decode()


def test_priced_route_keeps_buy_cta(client, db):
    # Regression: priced routes keep their schedule and buy CTA.
    slug = _slug(db.one(
        "SELECT r.slug FROM routes r WHERE r.type='intercity' "
        "AND EXISTS (SELECT 1 FROM trips t WHERE t.route_id=r.id AND t.price_rsd>0) "
        "LIMIT 1"
    ))
    assert slug, "expected at least one priced route"
    html = client.get(f"/rute/{slug}/").data.decode()
    assert "data-partner" in html  # buy button intact
    assert len(re.findall(r"\b[0-2]\d:[0-5]\d\b", html)) >= 1  # schedule intact

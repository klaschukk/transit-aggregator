"""Deterministic coverage for /pretraga past-departure filtering.

The search route hides trips whose departure_time < now() when the date is
today/empty (main.py). This feeds the BusTicket4 checkout date, so a regression
(timezone, '24:00' string-compare) would silently show or hide trips. The seed
has beograd→novi-sad departures at 06:00 and 08:00, so a frozen 07:00 'now'
pins the boundary.
"""
from datetime import datetime as _real_dt

import pytest


class _FrozenDT(_real_dt):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 6, 14, 7, 0)  # 07:00 — between the seed's 06:00 / 08:00


def _cards(resp):
    return resp.data.decode().count('class="trip-card"')


@pytest.fixture
def _seed_only(app):
    # These assertions assume the seed's exact two beograd→novi-sad departures.
    from app.db import query
    rows = query(
        "SELECT t.departure_time FROM trips t JOIN routes r ON r.id=t.route_id "
        "WHERE r.slug='beograd-novi-sad'"
    )
    times = sorted(r["departure_time"] for r in rows)
    if times != ["06:00", "08:00"]:
        pytest.skip(f"needs the seed's 06:00/08:00 fixture, got {times}")


def test_past_departures_hidden_for_today(client, monkeypatch, _seed_only):
    import app.routes.main as main_mod
    monkeypatch.setattr(main_mod, "datetime", _FrozenDT)
    resp = client.get("/pretraga/?od=Beograd&do=Novi%20Sad")
    assert resp.status_code == 200
    # 06:00 is in the past at 07:00 → only 08:00 remains.
    assert _cards(resp) == 1, "past 06:00 departure should be filtered out today"


def test_future_date_keeps_all_departures(client, monkeypatch, _seed_only):
    import app.routes.main as main_mod
    monkeypatch.setattr(main_mod, "datetime", _FrozenDT)
    resp = client.get("/pretraga/?od=Beograd&do=Novi%20Sad&datum=2026-12-31")
    assert resp.status_code == 200
    # A future date must not apply the now() filter — both departures show.
    assert _cards(resp) == 2, "future date should keep all departures"

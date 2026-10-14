"""Per-departure BusTicket4 checkout links (bt4_departures.json)."""
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from flask import render_template_string

from app.affiliates import partners
from data.pipelines.refresh_bt4_lineids import _departures_by_time

BG = ZoneInfo('Europe/Belgrade')


@pytest.fixture
def at_noon(monkeypatch):
    now = datetime.now(BG).replace(hour=12, minute=0, second=0, microsecond=0)
    monkeypatch.setattr(partners, '_now_belgrade', lambda: now)
    monkeypatch.setattr(partners, '_BT4_DEPARTURES', {'budva-kotor': {'06:30': 5183, '14:00': 777}})
    return now


def _ddmmyyyy(d):
    return d.strftime('%d-%m-%Y')


def test_line_for_exact_time_only(at_noon):
    assert partners.bt4_line_for('budva', 'kotor', '14:00:00') == 777
    assert partners.bt4_line_for('budva', 'kotor', '14:05') is None
    assert partners.bt4_line_for('kotor', 'budva', '14:00') is None
    assert partners.bt4_line_for('budva', 'kotor', '') is None


def test_checkout_date_today_until_departure(at_noon):
    later = partners.bt4_checkout_url('budva', 'kotor', 777, None, '14:00')
    gone = partners.bt4_checkout_url('budva', 'kotor', 5183, None, '06:30')
    assert f'departureDate={_ddmmyyyy(at_noon.date())}' in later
    assert f'departureDate={_ddmmyyyy(at_noon.date() + timedelta(days=1))}' in gone


def test_checkout_keeps_chosen_future_day(at_noon):
    day2 = (at_noon.date() + timedelta(days=2)).isoformat()
    url = partners.bt4_checkout_url('budva', 'kotor', 5183, day2, '06:30')
    assert f'departureDate={_ddmmyyyy(at_noon.date() + timedelta(days=2))}' in url


def test_checkout_without_time_unchanged(at_noon):
    """Pair-level callers pass no time: still tomorrow, as before."""
    url = partners.bt4_checkout_url('budva', 'kotor', 148)
    assert f'departureDate={_ddmmyyyy(datetime.now().date() + timedelta(days=1))}' in url


def test_trip_cards_open_their_own_departure(app, at_noon):
    tpl = ("{% from '_partials/_trip_card.html' import trip_card with context %}"
           "{% for t in trips %}{{ trip_card(t, from_slug='budva', to_slug='kotor', route_slug='budva-kotor',"
           " surface='route_detail', bt4_fallback_line_id=148) }}{% endfor %}")
    trips = [{'departure_time': '06:30', 'arrival_time': '07:00', 'price_rsd': 409, 'operator': 'X', 'bt4_line_id': None},
             {'departure_time': '14:00', 'arrival_time': '14:30', 'price_rsd': 409, 'operator': 'X', 'bt4_line_id': None},
             {'departure_time': '15:10', 'arrival_time': '15:40', 'price_rsd': 409, 'operator': 'X', 'bt4_line_id': None}]
    with app.test_request_context('/rute/budva-kotor/'):
        html = render_template_string(tpl, trips=trips)
    ids = re.findall(r'lineId=(\d+)', html)
    assert ids == ['5183', '777', '148']   # exact, exact, pair fallback for an unknown time


def test_pipeline_keeps_only_unambiguous_purchasable():
    res = [
        {'departure_time': '06:30:00', 'route_id': '5183', 'purchase_allowed': 'true'},
        {'departure_time': '08:00', 'route_id': '458', 'purchase_allowed': 'false'},
        {'departure_time': '09:00', 'route_id': '1', 'purchase_allowed': 'true'},
        {'departure_time': '09:00', 'route_id': '2', 'purchase_allowed': 'true'},
        {'departure_time': '10:00', 'route_id': '3', 'purchase_allowed': 'true'},
        {'departure_time': '10:00', 'route_id': '3', 'purchase_allowed': 'true'},
    ]
    assert _departures_by_time(res) == {'06:30': 5183, '10:00': 3}


def test_route_page_uses_day_tab_date(client):
    """Every exact-departure link opens the day tab's date. (Times BT4 does not
    sell keep the partner resolver's pair link — unchanged, A/B-ranked.)"""
    html = client.get('/rute/budva-kotor/?dan=2').get_data(as_text=True)
    day2 = _ddmmyyyy(datetime.now(BG).date() + timedelta(days=2))
    # minus the pair-level id: the resolver's fallback link reuses it (tomorrow)
    exact = set(partners._BT4_DEPARTURES.get('budva-kotor', {}).values()) - {
        partners._BT4_PAIR_LINEID.get('budva-kotor')}
    links = re.findall(r'class="trip-card__buy[^"]*"\s+href="[^"]*departureDate=([\d-]+)[^"]*lineId=(\d+)', html)
    dated = {d for d, lid in links if int(lid) in exact}
    if exact:
        assert dated == {day2}

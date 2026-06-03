"""Bookaway affiliate API client: graceful degradation + parsing."""
from unittest.mock import patch

from app import create_app
from app.affiliates import bookaway_api


def _app(**cfg):
    app = create_app()
    app.config.update(cfg)
    return app


def test_disabled_without_key():
    """No API key → dashboard is None and is_enabled() is False, never raises."""
    app = _app(BOOKAWAY_API_KEY='')
    with app.app_context():
        assert bookaway_api.is_enabled() is False
        assert bookaway_api.get_dashboard(30) is None


def test_network_error_degrades_to_zero(monkeypatch):
    """A failing API call must not raise — summary degrades to zeros."""
    app = _app(BOOKAWAY_API_KEY='x', BOOKAWAY_NETWORK_ID='bookaway2')
    bookaway_api._cache.clear()
    with app.app_context():
        with patch.object(bookaway_api, '_call', return_value=None):
            d = bookaway_api.get_dashboard(30)
        assert d is not None
        assert d['summary'] == {'clicks': 0, 'conversions': 0, 'payout': 0.0,
                                'cr': 0.0, 'epc': 0.0}
        assert d['offers'] == []
        assert d['daily'] == []


def test_summary_parses_and_derives_metrics():
    """getStats totals → clicks/conversions/payout plus derived CR and EPC."""
    app = _app(BOOKAWAY_API_KEY='x')
    bookaway_api._cache.clear()
    fake = {'totals': {'Stat': {'clicks': '200', 'conversions': '4', 'payout': '50'}}}
    with app.app_context():
        with patch.object(bookaway_api, '_call', return_value=fake):
            s = bookaway_api.get_summary('2026-05-01', '2026-05-31')
        assert s['clicks'] == 200
        assert s['conversions'] == 4
        assert s['payout'] == 50.0
        assert s['cr'] == 2.0          # 4/200 * 100
        assert s['epc'] == 0.25        # 50/200


def test_revenue_page_renders_without_key():
    """Admin revenue page must render even with the API disabled."""
    import base64
    app = _app(BOOKAWAY_API_KEY='', ADMIN_USER='t', ADMIN_PASS='t')
    client = app.test_client()
    auth = base64.b64encode(b't:t').decode()
    r = client.get('/admin/revenue', headers={'Authorization': f'Basic {auth}'})
    assert r.status_code == 200
    assert b'API key not configured' in r.data

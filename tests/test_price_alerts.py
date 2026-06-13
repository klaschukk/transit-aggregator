"""Tests for the price-alert delivery pipeline.

Covers the four moving parts:
  * evaluate_snapshots — threshold + baseline-short edge cases
  * analytics_db helpers — upsert idempotency, cooldown, confirmed filter
  * /api/subscribe route_slug acceptance + rejection
  * price_alert_scan end-to-end (with mailer in dev-log mode)

No real SMTP is used — mailer.send_mail falls back to logs/mail_dev.log
when SMTP_HOST is empty, which the test fixtures enforce.
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from app import create_app
from app.price_alerts import (
    COOLDOWN_DAYS,
    DROP_THRESHOLD,
    MIN_BASELINE_DAYS,
    build_price_alert_email,
    evaluate_snapshots,
)


# ── fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def alerts_app(tmp_path):
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['ANALYTICS_DB_PATH'] = str(tmp_path / 'ana.duckdb')
    app.config['IP_HASH_SALT'] = 'test-salt'
    app.config['SMTP_HOST'] = ''  # force dev-log fallback
    app.config['BASE_URL'] = 'https://prevozni.com'
    app.config['ADMIN_USER'] = 'admin'
    app.config['ADMIN_PASS'] = 'secret'
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()
    yield app


@pytest.fixture
def client(alerts_app):
    return alerts_app.test_client()


@pytest.fixture
def ana(alerts_app):
    from app import analytics_db
    return analytics_db


def _mk_snapshots(slug: str, prices_by_day: dict[int, int]) -> list[dict]:
    """Build a snapshot list shaped like the DB rows.

    `prices_by_day` is {days_ago: min_price}. Newest-first expected by
    evaluate_snapshots; we reverse-sort here.
    """
    today = date.today()
    rows = []
    for days_ago, price in sorted(prices_by_day.items()):
        rows.append({
            'route_slug': slug,
            'date': today - timedelta(days=days_ago),
            'min_price': price,
            'max_price': price + 200,
            'avg_price': price + 50,
            'trip_count': 5,
        })
    return sorted(rows, key=lambda r: r['date'], reverse=True)


# ── evaluate_snapshots ────────────────────────────────────────────────

def test_drop_threshold_fires_at_ten_percent():
    # Baseline 1000 RSD, today 899 → 10.1% drop — above threshold.
    snaps = _mk_snapshots('x', {i: 1000 for i in range(1, 8)} | {0: 899})
    ev = evaluate_snapshots(snaps, date.today())
    assert ev.qualifies is True
    assert ev.drop_pct == 10
    assert ev.today_min == 899
    assert ev.baseline_min == 1000


def test_drop_threshold_rejects_at_nine_percent():
    snaps = _mk_snapshots('x', {i: 1000 for i in range(1, 8)} | {0: 910})
    ev = evaluate_snapshots(snaps, date.today())
    assert ev.qualifies is False
    assert ev.drop_pct is None


def test_baseline_too_short_rejects():
    # Only 3 days of prior data — below MIN_BASELINE_DAYS (7)
    snaps = _mk_snapshots('x', {1: 1000, 2: 1000, 3: 1000, 0: 500})
    ev = evaluate_snapshots(snaps, date.today())
    assert ev.qualifies is False
    assert 'baseline too short' in ev.reason


def test_no_today_snapshot_rejects():
    snaps = _mk_snapshots('x', {i: 1000 for i in range(1, 10)})
    ev = evaluate_snapshots(snaps, date.today())
    assert ev.qualifies is False
    assert 'no snapshot for today' in ev.reason


def test_baseline_uses_minimum_not_average():
    # Prior days: 900, 900, 900, 900, 900, 900, 500 (one cheap day)
    # Today: 450 → drop vs baseline 500 is 10% exactly → NOT strict <
    prices = {i: 900 for i in range(1, 7)} | {7: 500, 0: 450}
    snaps = _mk_snapshots('x', prices)
    ev = evaluate_snapshots(snaps, date.today())
    # 450 < 500 × 0.9 (= 450)? strictly less = False → shouldn't fire
    assert ev.qualifies is False


def test_price_bounce_back_does_not_fire():
    # Yesterday it was cheap (500), today back to 1000 — NOT a drop event.
    prices = {i: 1000 for i in range(2, 9)} | {1: 500, 0: 1000}
    snaps = _mk_snapshots('x', prices)
    ev = evaluate_snapshots(snaps, date.today())
    assert ev.qualifies is False


# ── analytics_db snapshots / alerts ledger ────────────────────────────

def test_snapshot_upsert_idempotent(alerts_app, ana):
    slug = 'beograd-nis'
    today = date.today()
    with alerts_app.app_context():
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=900, max_price=1200, avg_price=1050.0, trip_count=6,
        )
        # Rerun with different numbers — must overwrite, not duplicate.
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=800, max_price=1100, avg_price=950.0, trip_count=7,
        )
        rows = ana.query(
            "SELECT min_price, max_price FROM price_snapshots "
            "WHERE route_slug = ? AND date = ?",
            [slug, today],
        )
    assert len(rows) == 1
    assert rows[0]['min_price'] == 800


def test_snapshot_history_window(alerts_app, ana):
    slug = 'beograd-subotica'
    today = date.today()
    with alerts_app.app_context():
        for d in range(10):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000 - d * 10, max_price=1200,
                avg_price=1100.0, trip_count=5,
            )
        rows = ana.price_snapshots_for_route(slug, days=7)
    # We inserted 10 days; window should return only those within 7 days.
    assert 7 <= len(rows) <= 8  # inclusive-today edge
    dates = [r['date'] for r in rows]
    # Newest first
    assert dates == sorted(dates, reverse=True)


def test_subscribers_for_route_respects_status(alerts_app, ana):
    slug = 'kragujevac-kraljevo'
    with alerts_app.app_context():
        # confirmed + price_alert — IN
        row_ok = ana.insert_or_refresh_subscriber(
            email='ok@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.1', route_slug=slug,
        )
        ana.confirm_subscriber(row_ok['confirm_token'])

        # pending — OUT
        ana.insert_or_refresh_subscriber(
            email='pending@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.2', route_slug=slug,
        )

        # confirmed then unsubscribed — OUT
        row_un = ana.insert_or_refresh_subscriber(
            email='unsub@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.3', route_slug=slug,
        )
        ana.confirm_subscriber(row_un['confirm_token'])
        refreshed = ana.subscriber_by_email('unsub@example.com')
        ana.unsubscribe_subscriber(refreshed['unsubscribe_token'])

        # generic newsletter (route_slug None) — OUT
        ana.insert_or_refresh_subscriber(
            email='generic@example.com', lang='sr', source='footer',
            referrer='', ip='1.1.1.4', route_slug=None,
        )

        out = ana.subscribers_for_route_alerts(slug)
    emails = {s['email'] for s in out}
    assert emails == {'ok@example.com'}


def test_cooldown_dedup_prevents_repeat_send(alerts_app, ana):
    slug = 'beograd-sarajevo'
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='cool@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.5', route_slug=slug,
        )
        ana.confirm_subscriber(row['confirm_token'])
        sub = ana.subscriber_by_email('cool@example.com')

        assert ana.price_alert_recently_sent(sub['id'], slug) is False
        ana.record_price_alert_sent(
            subscriber_id=sub['id'], route_slug=slug,
            old_price=1200, new_price=1000, drop_pct=17, delivered_ok=True,
        )
        assert ana.price_alert_recently_sent(sub['id'], slug) is True
        # Different route — no cooldown applies
        assert ana.price_alert_recently_sent(sub['id'], 'other-route') is False


def test_route_update_on_resubscribe(alerts_app, ana):
    """A confirmed subscriber signing up for a second route switches the
    binding without needing a fresh confirm click."""
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='switcher@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.6', route_slug='beograd-novi-sad',
        )
        ana.confirm_subscriber(row['confirm_token'])

        # Second signup on a different route
        refreshed = ana.insert_or_refresh_subscriber(
            email='switcher@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.6', route_slug='beograd-nis',
        )
    assert refreshed['_action'] == 'route_updated'
    assert refreshed['route_slug'] == 'beograd-nis'


# ── /api/subscribe route_slug handling ────────────────────────────────

def test_api_subscribe_accepts_route_slug(client, ana, alerts_app):
    r = client.post('/api/subscribe', data={
        'email': 'alice@example.com',
        'source': 'price_alert',
        'route_slug': 'beograd-novi-sad',
        'consent': '1',
    })
    assert r.status_code == 202
    with alerts_app.app_context():
        row = ana.subscriber_by_email('alice@example.com')
    assert row is not None
    assert row['route_slug'] == 'beograd-novi-sad'
    assert row['source'] == 'price_alert'


def test_api_subscribe_requires_route_when_price_alert(client):
    r = client.post('/api/subscribe', data={
        'email': 'bob@example.com',
        'source': 'price_alert',
        'consent': '1',
    })
    assert r.status_code == 400
    assert 'route_required' in r.get_data(as_text=True)


def test_api_subscribe_rejects_bad_slug(client):
    # Uppercase / spaces / dots all fail the ^[a-z0-9-]+$ check
    r = client.post('/api/subscribe', data={
        'email': 'bob@example.com',
        'source': 'price_alert',
        'route_slug': 'Beograd Novi Sad!',
        'consent': '1',
    })
    assert r.status_code == 400


def test_api_subscribe_ignores_slug_for_footer_source(client, ana, alerts_app):
    r = client.post('/api/subscribe', data={
        'email': 'carol@example.com',
        'source': 'footer',
        'route_slug': 'ignored-slug',  # should be discarded silently
        'consent': '1',
    })
    assert r.status_code == 202
    with alerts_app.app_context():
        row = ana.subscriber_by_email('carol@example.com')
    assert row['route_slug'] is None


# ── email rendering ───────────────────────────────────────────────────

def test_email_render_contains_prices_and_unsub(alerts_app):
    with alerts_app.app_context():
        subject, text, html = build_price_alert_email(
            route_slug='beograd-novi-sad',
            from_city='Beograd', to_city='Novi Sad',
            old_price=1000, new_price=750, drop_pct=25,
            lang='sr',
            unsubscribe_token='UNSUB-ABC',
        )
    assert 'Beograd → Novi Sad' in subject
    assert '750' in text and '1000' in text
    assert '25%' in text
    assert '/api/unsubscribe/UNSUB-ABC' in text
    assert 'utm_medium=price-alert' in text
    assert 'prevozni.com' in html


def test_email_render_localises_all_three_langs(alerts_app):
    with alerts_app.app_context():
        for lang, marker in (('sr', 'Cena je pala'),
                             ('en', 'Price drop'),
                             ('ru', 'Цена упала')):
            subject, _text, _html = build_price_alert_email(
                route_slug='x-y',
                from_city='X', to_city='Y',
                old_price=900, new_price=800, drop_pct=11,
                lang=lang, unsubscribe_token='T',
            )
            assert marker in subject, (lang, subject)


# ── end-to-end scan ───────────────────────────────────────────────────

def _seed_monkeypatched_transit_route(monkeypatch, slug, from_city, to_city):
    """Stub the transit-db lookup in the scanner so tests don't need a
    real DuckDB route table."""
    from scripts import price_alert_scan as scanner
    monkeypatch.setattr(
        scanner, '_route_labels',
        lambda _path, slugs: {slug: (from_city, to_city)},
    )


def test_scan_skips_routes_with_insufficient_history(alerts_app, ana, monkeypatch):
    slug = 'new-route-pair'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='watch@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.7', route_slug=slug,
        )
        ana.confirm_subscriber(row['confirm_token'])
        # Only 3 prior snapshots — below MIN_BASELINE_DAYS (7)
        for d in range(1, 4):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=500, max_price=1200, avg_price=800.0, trip_count=5,
        )
    monkeypatch.setattr(
        price_alert_scan, 'create_app', lambda: alerts_app,
    )
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=False)
    assert stats['emails_sent'] == 0
    assert stats['routes_qualified'] == 0


def test_scan_email_carries_list_unsubscribe(alerts_app, ana, monkeypatch):
    """Price-alert mail is bulk marketing — it must hand the mailer a one-click
    List-Unsubscribe URL (Gmail/Yahoo bulk rules; without it the return channel
    risks the spam folder)."""
    slug = 'unsub-route'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='alerthdr@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.21', route_slug=slug,
        )
        ana.confirm_subscriber(row['confirm_token'])
        for d in range(1, 8):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=700, max_price=1200, avg_price=900.0, trip_count=5,
        )
    captured = []
    monkeypatch.setattr(price_alert_scan, 'send_mail',
                        lambda **kw: captured.append(kw) or True)
    monkeypatch.setattr(price_alert_scan, 'create_app', lambda: alerts_app)
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=False)
    assert stats['emails_sent'] == 1
    assert captured, 'no email was sent'
    assert captured[-1].get('list_unsubscribe'), 'price alert missing List-Unsubscribe'
    assert '/api/unsubscribe/' in captured[-1]['list_unsubscribe']


def test_scan_fires_single_email_on_qualifying_drop(alerts_app, ana, monkeypatch):
    slug = 'drop-route'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='drop@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.8', route_slug=slug,
        )
        ana.confirm_subscriber(row['confirm_token'])
        # 7 days at 1000 RSD + today at 700 (30% drop)
        for d in range(1, 8):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=700, max_price=1200, avg_price=900.0, trip_count=5,
        )

    monkeypatch.setattr(price_alert_scan, 'create_app', lambda: alerts_app)
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=False)

    assert stats['routes_qualified'] == 1
    assert stats['emails_sent'] == 1
    with alerts_app.app_context():
        sent = ana.query(
            "SELECT drop_pct, new_price, old_price FROM price_alerts_sent"
        )
    assert len(sent) == 1
    assert sent[0]['new_price'] == 700
    assert sent[0]['old_price'] == 1000
    assert sent[0]['drop_pct'] == 30


def test_scan_skips_unconfirmed_and_unsubscribed(alerts_app, ana, monkeypatch):
    slug = 'only-confirmed'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        # Pending confirmation — should be skipped
        ana.insert_or_refresh_subscriber(
            email='pending@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.9', route_slug=slug,
        )
        # Unsubscribed — should be skipped
        row_un = ana.insert_or_refresh_subscriber(
            email='unsub@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.10', route_slug=slug,
        )
        ana.confirm_subscriber(row_un['confirm_token'])
        refreshed = ana.subscriber_by_email('unsub@example.com')
        ana.unsubscribe_subscriber(refreshed['unsubscribe_token'])

        # seed a qualifying drop — but there are 0 valid subscribers
        for d in range(1, 8):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=500, max_price=1200, avg_price=800.0, trip_count=5,
        )

    monkeypatch.setattr(price_alert_scan, 'create_app', lambda: alerts_app)
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=False)
    # No confirmed non-unsubbed subscribers for this route — the route is
    # never even listed in routes_seen.
    assert stats['emails_sent'] == 0


def test_scan_respects_cooldown(alerts_app, ana, monkeypatch):
    slug = 'cooldown-route'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='cd@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.11', route_slug=slug,
        )
        ana.confirm_subscriber(row['confirm_token'])
        sub = ana.subscriber_by_email('cd@example.com')
        # Pretend we sent an alert 2 days ago — cooldown window is 7.
        ana.record_price_alert_sent(
            subscriber_id=sub['id'], route_slug=slug,
            old_price=1000, new_price=800, drop_pct=20, delivered_ok=True,
        )
        for d in range(1, 8):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=500, max_price=1200, avg_price=800.0, trip_count=5,
        )

    monkeypatch.setattr(price_alert_scan, 'create_app', lambda: alerts_app)
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=False)
    # Only one row should exist in price_alerts_sent (the seeded one) —
    # no new send because of cooldown.
    with alerts_app.app_context():
        count = ana.query("SELECT COUNT(*) AS c FROM price_alerts_sent")
    assert count[0]['c'] == 1
    assert stats['skipped_cooldown'] >= 1


def test_scan_caps_at_max_emails(alerts_app, ana, monkeypatch):
    slug = 'capped-route'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        for i in range(5):
            row = ana.insert_or_refresh_subscriber(
                email=f'u{i}@example.com', lang='sr', source='price_alert',
                referrer='', ip=f'1.1.1.{100 + i}', route_slug=slug,
            )
            ana.confirm_subscriber(row['confirm_token'])
        for d in range(1, 8):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=500, max_price=1200, avg_price=800.0, trip_count=5,
        )

    monkeypatch.setattr(price_alert_scan, 'create_app', lambda: alerts_app)
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=False, max_emails=2)
    assert stats['emails_sent'] == 2
    assert stats['skipped_capped'] >= 1


def test_scan_dry_run_logs_but_sends_nothing(alerts_app, ana, monkeypatch):
    slug = 'dry-route'
    from scripts import price_alert_scan
    today = date.today()
    with alerts_app.app_context():
        row = ana.insert_or_refresh_subscriber(
            email='dry@example.com', lang='sr', source='price_alert',
            referrer='', ip='1.1.1.200', route_slug=slug,
        )
        ana.confirm_subscriber(row['confirm_token'])
        for d in range(1, 8):
            ana.insert_or_refresh_price_snapshot(
                slug, snapshot_date=today - timedelta(days=d),
                min_price=1000, max_price=1200, avg_price=1100.0, trip_count=5,
            )
        ana.insert_or_refresh_price_snapshot(
            slug, snapshot_date=today,
            min_price=700, max_price=1200, avg_price=900.0, trip_count=5,
        )

    monkeypatch.setattr(price_alert_scan, 'create_app', lambda: alerts_app)
    _seed_monkeypatched_transit_route(monkeypatch, slug, 'A', 'B')
    stats = price_alert_scan.scan(today=today, dry_run=True)
    assert stats['emails_sent'] == 0
    assert stats['routes_qualified'] == 1
    with alerts_app.app_context():
        count = ana.query("SELECT COUNT(*) AS c FROM price_alerts_sent")
    # Dry-run must not record anything either
    assert count[0]['c'] == 0


# ── admin views ───────────────────────────────────────────────────────

def test_admin_subscribers_requires_auth(client):
    r = client.get('/admin/subscribers')
    assert r.status_code == 401


def test_admin_subscribers_returns_200_with_auth(client):
    token = base64.b64encode(b'admin:secret').decode()
    r = client.get('/admin/subscribers',
                   headers={'Authorization': f'Basic {token}'})
    assert r.status_code == 200


def test_admin_price_alerts_returns_200_with_auth(client):
    token = base64.b64encode(b'admin:secret').decode()
    r = client.get('/admin/price-alerts',
                   headers={'Authorization': f'Basic {token}'})
    assert r.status_code == 200


def test_admin_subscribers_filter_by_source(client, ana, alerts_app):
    with alerts_app.app_context():
        ana.insert_or_refresh_subscriber(
            email='f@example.com', lang='sr', source='price_alert',
            referrer='', ip='x', route_slug='r',
        )
        ana.insert_or_refresh_subscriber(
            email='g@example.com', lang='sr', source='footer',
            referrer='', ip='y', route_slug=None,
        )
    token = base64.b64encode(b'admin:secret').decode()
    r = client.get('/admin/subscribers?source=price_alert',
                   headers={'Authorization': f'Basic {token}'})
    body = r.get_data(as_text=True)
    assert 'f@example' in body or 'f@' in body
    # Footer signup should be filtered out
    assert 'g@example' not in body

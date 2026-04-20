"""Tests for /api/ba-click and /admin/revenue analytics stack."""

import base64

import pytest

from app import create_app


@pytest.fixture(scope='module')
def analytics_app(tmp_path_factory):
    """App with a throwaway analytics DB so we don't pollute dev data.

    Config.ANALYTICS_DB_PATH is resolved at class-import time, so env-var
    patching alone is too late. We set `app.config` directly, then re-run
    init_schema on the fresh path before the first request hits the DB."""
    tmp = tmp_path_factory.mktemp('ana')
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['ANALYTICS_DB_PATH'] = str(tmp / 'analytics.duckdb')
    app.config['IP_HASH_SALT'] = 'test-salt'
    app.config['ADMIN_USER'] = 'admin'
    app.config['ADMIN_PASS'] = 'secret'
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()
    yield app


@pytest.fixture
def ana_client(analytics_app):
    return analytics_app.test_client()


# ── /api/ba-click ──


def test_ba_click_accepts_valid_payload(ana_client):
    r = ana_client.post(
        '/api/ba-click',
        json={
            'route_slug': 'beograd-budva',
            'surface': 'route_detail',
            'operator': 'Lasta',
            'trip_time': '07:30',
        },
    )
    assert r.status_code == 204


def test_ba_click_handles_empty_body(ana_client):
    """Should not 500 on missing JSON — treat as unknown click."""
    r = ana_client.post('/api/ba-click', data='')
    assert r.status_code == 204


def test_ba_click_clamps_surface_to_allowlist(ana_client, analytics_app):
    r = ana_client.post(
        '/api/ba-click',
        json={'route_slug': 'x', 'surface': 'attacker-injected-value'},
    )
    assert r.status_code == 204
    with analytics_app.app_context():
        from app import analytics_db
        rows = analytics_db.query(
            "SELECT surface FROM ba_clicks WHERE route_slug = 'x' ORDER BY ts DESC LIMIT 1"
        )
    assert rows and rows[0]['surface'] == 'other'


def test_ba_click_writes_to_db(ana_client, analytics_app):
    ana_client.post('/api/ba-click', json={'route_slug': 'nis-skopje', 'surface': 'search'})
    with analytics_app.app_context():
        from app import analytics_db
        rows = analytics_db.query(
            "SELECT route_slug, surface FROM ba_clicks WHERE route_slug = 'nis-skopje'"
        )
    assert rows and rows[0]['surface'] == 'search'


def test_ba_click_ip_is_hashed_not_raw(ana_client, analytics_app):
    """Raw IPs must never land in ba_clicks — only sha256 prefixes."""
    ana_client.post(
        '/api/ba-click',
        json={'route_slug': 'leak-check', 'surface': 'route_detail'},
        headers={'X-Forwarded-For': '203.0.113.42'},
    )
    with analytics_app.app_context():
        from app import analytics_db
        rows = analytics_db.query(
            "SELECT ip_hash FROM ba_clicks WHERE route_slug = 'leak-check' LIMIT 1"
        )
    assert rows
    ip_hash = rows[0]['ip_hash']
    assert '203.0.113.42' not in ip_hash
    assert len(ip_hash) == 32  # sha256 hex truncated in analytics_db.hash_ip


# ── /admin/revenue ──


def test_admin_requires_basic_auth(ana_client):
    r = ana_client.get('/admin/revenue')
    assert r.status_code == 401
    assert r.headers.get('WWW-Authenticate', '').startswith('Basic')


def test_admin_rejects_bad_creds(ana_client):
    bad = base64.b64encode(b'admin:wrong').decode()
    r = ana_client.get('/admin/revenue', headers={'Authorization': 'Basic ' + bad})
    assert r.status_code == 401


def test_admin_renders_with_good_creds(ana_client):
    good = base64.b64encode(b'admin:secret').decode()
    r = ana_client.get('/admin/revenue', headers={'Authorization': 'Basic ' + good})
    assert r.status_code == 200
    body = r.data.decode()
    assert 'Bookaway affiliate' in body
    assert 'revenue dashboard' in body


def test_admin_sets_noindex(ana_client):
    good = base64.b64encode(b'admin:secret').decode()
    r = ana_client.get('/admin/revenue', headers={'Authorization': 'Basic ' + good})
    assert 'noindex' in r.headers.get('X-Robots-Tag', '')


def test_admin_disabled_when_creds_missing(tmp_path, monkeypatch):
    """Without creds provisioned, admin endpoints must 503, not run open."""
    monkeypatch.setenv('ANALYTICS_DB_PATH', str(tmp_path / 'a.duckdb'))
    monkeypatch.setenv('IP_HASH_SALT', 'test')
    monkeypatch.delenv('ADMIN_USER', raising=False)
    monkeypatch.delenv('ADMIN_PASS', raising=False)
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['ADMIN_USER'] = ''
    app.config['ADMIN_PASS'] = ''
    with app.test_client() as c:
        r = c.get('/admin/revenue')
    assert r.status_code == 503


# ── robots.txt + privacy ──


def test_robots_disallows_admin(client):
    txt = client.get('/robots.txt').data.decode()
    assert 'Disallow: /admin/' in txt


def test_privacy_mentions_affiliate_tracking(client):
    body = client.get('/privatnost/').data.decode()
    # Any of the three language variants should mention ba_click tracking.
    assert 'ba_click' in body or 'Bookaway' in body
    assert 'sha256' in body or 'hash' in body.lower()

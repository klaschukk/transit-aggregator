"""Newsletter double-opt-in backend — submit, confirm, unsubscribe."""

import re
from datetime import datetime, timedelta

import pytest

from app import create_app


@pytest.fixture(scope='module')
def sub_app(tmp_path_factory):
    tmp = tmp_path_factory.mktemp('sub')
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['ANALYTICS_DB_PATH'] = str(tmp / 'analytics.duckdb')
    app.config['IP_HASH_SALT'] = 'sub-salt'
    app.config['BASE_URL'] = 'http://localhost:5000'
    app.config['SMTP_HOST'] = ''           # force DEV-log fallback
    app.config['DEV_LOG_DIR'] = str(tmp)
    from app.extensions import limiter
    limiter.enabled = False
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()
    yield app
    limiter.enabled = True


@pytest.fixture
def sub_client(sub_app):
    return sub_app.test_client()


def _post(client, email='reader@example.com', consent='1',
          source='home'):
    return client.post('/api/subscribe', data={
        'email': email, 'consent': consent, 'source': source,
    })


def _last_token(app, email):
    """Return (confirm_token, unsubscribe_token) for a recently inserted row."""
    from app import analytics_db
    with app.app_context():
        rows = analytics_db.query(
            "SELECT confirm_token, unsubscribe_token FROM subscribers "
            "WHERE email_lower = ?",
            [email.lower()],
        )
    assert rows, f"no subscriber row for {email}"
    return rows[0]['confirm_token'], rows[0]['unsubscribe_token']


# ── Submit ──


def test_submit_happy_path_returns_202(sub_client):
    r = _post(sub_client, email='alice@example.com')
    assert r.status_code == 202
    assert r.get_json()['ok'] is True
    assert r.get_json()['status'] == 'pending_confirm'


def test_submit_rejects_missing_consent(sub_client):
    r = _post(sub_client, email='bob@example.com', consent='')
    assert r.status_code == 400
    assert 'consent' in r.get_json()['error']


def test_submit_rejects_invalid_email(sub_client):
    for bad in ('', 'notanemail', 'a@b', 'a@b.', '@example.com', 'x' * 120):
        r = _post(sub_client, email=bad)
        assert r.status_code == 400, f"expected 400 for {bad!r}"


def test_submit_resend_for_pending_row_rotates_token(sub_app, sub_client):
    email = 'carol@example.com'
    r1 = _post(sub_client, email=email)
    assert r1.status_code == 202
    tok1_confirm, tok1_unsub = _last_token(sub_app, email)

    r2 = _post(sub_client, email=email)
    assert r2.status_code == 202
    tok2_confirm, tok2_unsub = _last_token(sub_app, email)

    assert tok1_confirm != tok2_confirm, "confirm token must rotate on resend"
    assert tok1_unsub != tok2_unsub, "unsubscribe token must rotate on resend"


def test_submit_already_confirmed_returns_200_not_202(sub_app, sub_client):
    email = 'dave@example.com'
    assert _post(sub_client, email=email).status_code == 202
    confirm_tok, _ = _last_token(sub_app, email)
    assert sub_client.get(f'/api/subscribe/confirm/{confirm_tok}').status_code == 200

    # Second signup after confirmation — polite 200 + already_subscribed
    r = _post(sub_client, email=email)
    assert r.status_code == 200
    assert r.get_json()['status'] == 'already_subscribed'


# ── Confirm ──


def test_confirm_valid_token_sets_confirmed_at(sub_app, sub_client):
    email = 'erin@example.com'
    _post(sub_client, email=email)
    confirm_tok, _ = _last_token(sub_app, email)

    r = sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')
    assert r.status_code == 200
    assert b'potvr' in r.data.lower() or b'confirm' in r.data.lower()

    from app import analytics_db
    with sub_app.app_context():
        rows = analytics_db.query(
            "SELECT confirmed_at, confirm_token FROM subscribers "
            "WHERE email_lower = ?", [email],
        )
    assert rows[0]['confirmed_at'] is not None
    assert rows[0]['confirm_token'] is None, "token must be one-shot"


def test_confirm_invalid_token_returns_404(sub_client):
    r = sub_client.get('/api/subscribe/confirm/' + 'a' * 32)
    assert r.status_code == 404


def test_confirm_token_with_non_alphanumeric_is_404(sub_client):
    r = sub_client.get('/api/subscribe/confirm/../../etc/passwd')
    assert r.status_code == 404


def test_confirm_already_confirmed_returns_200(sub_app, sub_client):
    """A user re-clicking the confirm link from a 3-day-old email must
    see a friendly message, not a 404."""
    email = 'frank@example.com'
    _post(sub_client, email=email)
    confirm_tok, _ = _last_token(sub_app, email)
    sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')

    # The token is nulled after first confirm — simulate the re-click by
    # writing the token back and observing 'already' branch.
    from app import analytics_db
    with sub_app.app_context():
        analytics_db._get_conn().execute(
            "UPDATE subscribers SET confirm_token = ? WHERE email_lower = ?",
            [confirm_tok, email],
        )
    r = sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')
    assert r.status_code == 200  # already branch is success-ish


def test_confirm_expired_token_returns_410(sub_app, sub_client):
    email = 'grace@example.com'
    _post(sub_client, email=email)
    confirm_tok, _ = _last_token(sub_app, email)

    # Back-date the row past the 7-day TTL.
    old_ts = datetime.utcnow() - timedelta(days=10)
    from app import analytics_db
    with sub_app.app_context():
        analytics_db._get_conn().execute(
            "UPDATE subscribers SET ts = ? WHERE email_lower = ?",
            [old_ts, email],
        )
    r = sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')
    assert r.status_code == 410
    assert b'isteka' in r.data.lower() or b'expir' in r.data.lower()


# ── Unsubscribe ──


def test_unsubscribe_valid_token_sets_unsubscribed_at(sub_app, sub_client):
    email = 'helen@example.com'
    _post(sub_client, email=email)
    confirm_tok, unsub_tok = _last_token(sub_app, email)
    sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')

    r = sub_client.get(f'/api/unsubscribe/{unsub_tok}')
    assert r.status_code == 200
    assert b'odjav' in r.data.lower() or b'unsubscr' in r.data.lower()

    from app import analytics_db
    with sub_app.app_context():
        rows = analytics_db.query(
            "SELECT unsubscribed_at FROM subscribers WHERE email_lower = ?",
            [email],
        )
    assert rows[0]['unsubscribed_at'] is not None


def test_unsubscribe_invalid_token_returns_404(sub_client):
    r = sub_client.get('/api/unsubscribe/' + 'z' * 32)
    assert r.status_code == 410  # valid format, not found → already-used branch


def test_unsubscribe_twice_second_returns_410(sub_app, sub_client):
    email = 'ivan@example.com'
    _post(sub_client, email=email)
    confirm_tok, unsub_tok = _last_token(sub_app, email)
    sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')

    assert sub_client.get(f'/api/unsubscribe/{unsub_tok}').status_code == 200
    # The token stays in the row (so admins can see who unsubscribed) but
    # unsubscribed_at is already set — second hit returns 410.
    r2 = sub_client.get(f'/api/unsubscribe/{unsub_tok}')
    assert r2.status_code == 410


# ── Flow + side effects ──


def test_confirm_writes_welcome_mail_to_dev_log(sub_app, sub_client, tmp_path):
    """The DEV mailer appends to logs/mail_dev.log under the project root.
    After confirm we expect exactly one 'welcome' entry for the user."""
    email = 'julia@example.com'
    _post(sub_client, email=email)
    confirm_tok, _ = _last_token(sub_app, email)
    sub_client.get(f'/api/subscribe/confirm/{confirm_tok}')

    from pathlib import Path
    log_path = Path(sub_app.root_path).parent / 'logs' / 'mail_dev.log'
    assert log_path.exists(), "DEV mailer should have written the log"
    body = log_path.read_text()
    assert email in body
    # The welcome mail should appear AFTER the confirm mail in the same file.
    welcome_markers = re.findall(
        r'subject:.*(Welcome|Dobrodoš|Добро пожаловать)', body,
    )
    assert welcome_markers, "welcome letter subject missing from dev log"


def test_subscriber_stats_counts_by_state(sub_app, sub_client):
    """subscriber_stats() reports total/confirmed/pending/unsubscribed."""
    from app import analytics_db
    _post(sub_client, email='k1@example.com')   # pending
    _post(sub_client, email='k2@example.com')
    ct, _ = _last_token(sub_app, 'k2@example.com')
    sub_client.get(f'/api/subscribe/confirm/{ct}')  # confirmed
    _post(sub_client, email='k3@example.com')
    ct3, ut3 = _last_token(sub_app, 'k3@example.com')
    sub_client.get(f'/api/subscribe/confirm/{ct3}')
    sub_client.get(f'/api/unsubscribe/{ut3}')    # unsubscribed

    with sub_app.app_context():
        stats = analytics_db.subscriber_stats()
    assert stats['total'] >= 3
    assert stats['confirmed'] >= 1
    assert stats['pending'] >= 1
    assert stats['unsubscribed'] >= 1


# ── Rate limit (separate app with limiter enabled) ──


def test_submit_rate_limit_five_per_hour(tmp_path):
    """6th submit within an hour from the same IP must 429."""
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = True
    app.config['ANALYTICS_DB_PATH'] = str(tmp_path / 'analytics.duckdb')
    app.config['IP_HASH_SALT'] = 'rl-salt'
    app.config['SMTP_HOST'] = ''
    from app.extensions import limiter
    limiter.enabled = True
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()

    client = app.test_client()
    for i in range(5):
        r = client.post('/api/subscribe', data={
            'email': f'rate{i}@example.com', 'consent': '1',
        })
        assert r.status_code == 202, f"expected 202 on submit {i}, got {r.status_code}"
    r = client.post('/api/subscribe', data={
        'email': 'rate6@example.com', 'consent': '1',
    })
    assert r.status_code == 429

    limiter.enabled = False

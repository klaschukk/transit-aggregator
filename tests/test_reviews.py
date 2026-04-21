"""Tests for UGC review submission, moderation, GDPR deletion, and schema.org."""

import base64
import re
import time

import pytest

from app import create_app


@pytest.fixture(scope='module')
def rv_app(tmp_path_factory):
    tmp = tmp_path_factory.mktemp('rv')
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['ANALYTICS_DB_PATH'] = str(tmp / 'analytics.duckdb')
    app.config['IP_HASH_SALT'] = 'rv-salt'
    app.config['ADMIN_USER'] = 'admin'
    app.config['ADMIN_PASS'] = 'secret'
    # Flask-Limiter grabs settings at init_app; runtime override needed for tests.
    from app.extensions import limiter
    limiter.enabled = False
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()
    yield app
    limiter.enabled = True


@pytest.fixture
def rv_client(rv_app):
    return rv_app.test_client()


def _ok_payload(**overrides):
    base = {
        'rating': '5',
        'comment': 'Putovanje je bilo odlično, autobus čist i tačan, vozač ljubazan. Preporučujem ovu liniju.',
        'name': 'Marko',
        'email': 'marko@example.com',
        'website': '',
        'loaded_at': str(time.time() - 5),  # > 3s rule
    }
    base.update(overrides)
    return base


# ── Submit happy path ──


def test_review_submit_returns_202_pending(rv_client):
    r = rv_client.post('/api/review/beograd-novi-sad', data=_ok_payload())
    assert r.status_code == 202
    j = r.get_json()
    assert j['ok'] and j['status'] == 'pending'


def test_review_submit_writes_to_db(rv_client, rv_app):
    rv_client.post(
        '/api/review/nis-skopje',
        data=_ok_payload(name='TestAuthor', comment='Odlična linija, sve je bilo u redu, samo tako nastaviti.'),
    )
    with rv_app.app_context():
        from app import analytics_db
        rows = analytics_db.query(
            "SELECT route_slug, rating, status FROM reviews WHERE route_slug = 'nis-skopje'"
        )
    assert rows and rows[0]['status'] == 'pending'


# ── Anti-spam ──


def test_review_honeypot_rejects(rv_client):
    r = rv_client.post('/api/review/beograd-budva', data=_ok_payload(website='http://spam.example'))
    assert r.status_code == 400
    assert r.get_json()['error'] == 'review.error.spam'


def test_review_too_fast_rejects(rv_client):
    r = rv_client.post(
        '/api/review/beograd-budva',
        data=_ok_payload(loaded_at=str(time.time() - 1)),  # 1s < 3s rule
    )
    assert r.status_code == 400
    assert r.get_json()['error'] == 'review.error.too_fast'


def test_review_profanity_rejects(rv_client):
    r = rv_client.post(
        '/api/review/beograd-budva',
        data=_ok_payload(comment='Ova linija je stvarno kurac, nemojte je koristiti nikada u životu molim vas.'),
    )
    assert r.status_code == 400
    assert r.get_json()['error'] == 'review.error.profanity'


def test_review_external_url_rejects(rv_client):
    r = rv_client.post(
        '/api/review/beograd-budva',
        data=_ok_payload(comment='Odlična ruta, više detalja na https://spam.example/ jako preporučujem svim.'),
    )
    assert r.status_code == 400
    assert r.get_json()['error'] == 'review.error.no_urls'


def test_review_prevozni_url_allowed(rv_client):
    """Our own domain is on the allowlist."""
    r = rv_client.post(
        '/api/review/beograd-budva',
        data=_ok_payload(comment='Pogledajte red vožnje na https://prevozni.com/rute/beograd-budva/ jako koristan sajt.'),
    )
    assert r.status_code == 202


def test_review_short_comment_rejects(rv_client):
    r = rv_client.post('/api/review/beograd-budva', data=_ok_payload(comment='prekratko'))
    assert r.status_code == 400
    assert r.get_json()['error'] == 'review.error.comment_length'


def test_review_bad_rating_rejects(rv_client):
    r = rv_client.post('/api/review/beograd-budva', data=_ok_payload(rating='7'))
    assert r.status_code == 400


def test_review_rejects_bad_slug_format(rv_client):
    # Reject path-traversal-ish slugs before they reach the DB.
    r = rv_client.post('/api/review/../etc/passwd', data=_ok_payload())
    assert r.status_code in (400, 404)


# ── Trusted author auto-approve ──


def test_trusted_author_auto_approves_after_three(rv_app):
    from app import analytics_db
    with rv_app.app_context():
        email = 'trusted@example.com'
        for _ in range(3):
            rid = analytics_db.insert_review(
                route_slug='novi-sad-subotica', rating=5,
                comment='Odlično, bez komentara, brzo i udobno, svakako preporučujem putovanje.',
                author_name='Trust',
                email=email, lang='sr', ip='1.2.3.4', status='approved',
            )
            assert rid
        assert analytics_db.is_trusted_author(email) is True
        assert analytics_db.is_trusted_author('somebody-else@example.com') is False


# ── GET /api/reviews/<slug> ──


def test_reviews_api_returns_approved_only(rv_client, rv_app):
    with rv_app.app_context():
        from app import analytics_db
        analytics_db.insert_review(
            route_slug='beograd-kragujevac', rating=5,
            comment='Bez problema, autobus je bio čist i udobno sam putovao celom rutom.',
            author_name='Ana', email='a@ex.com', lang='sr', ip='1.1.1.1',
            status='approved',
        )
        analytics_db.insert_review(
            route_slug='beograd-kragujevac', rating=2,
            comment='Nije mi se svidelo nista, ali nisam siguran zašto — osećaj nepovoljan.',
            author_name='Bob', email='b@ex.com', lang='sr', ip='2.2.2.2',
            status='pending',
        )
    r = rv_client.get('/api/reviews/beograd-kragujevac')
    assert r.status_code == 200
    j = r.get_json()
    # Only approved leaks out.
    assert all(rv['author_name'] == 'Ana' for rv in j['reviews'])
    assert j['aggregate']['n'] >= 1


# ── Admin moderation ──


def test_admin_reviews_requires_auth(rv_client):
    r = rv_client.get('/admin/reviews')
    assert r.status_code == 401


def test_admin_can_approve_review(rv_client, rv_app):
    with rv_app.app_context():
        from app import analytics_db
        rid = analytics_db.insert_review(
            route_slug='beograd-podgorica', rating=4,
            comment='U redu putovanje, prosek vremena po rasporedu, par stajanja bila su predugačka.',
            author_name='Pero', email='p@ex.com', lang='sr', ip='3.3.3.3',
        )
    good = base64.b64encode(b'admin:secret').decode()
    r = rv_client.post(
        f'/admin/reviews/{rid}/approve',
        headers={'Authorization': 'Basic ' + good},
    )
    assert r.status_code in (302, 303)
    with rv_app.app_context():
        from app import analytics_db
        row = analytics_db.query("SELECT status FROM reviews WHERE id = ?", [rid])
    assert row[0]['status'] == 'approved'


def test_admin_delete_wipes_pii(rv_client, rv_app):
    with rv_app.app_context():
        from app import analytics_db
        rid = analytics_db.insert_review(
            route_slug='beograd-tirana', rating=3,
            comment='Prosečno iskustvo bez ikakvih iznenađenja, sve je proteklo uglavnom po planu.',
            author_name='Zorica', email='z@ex.com', lang='sr', ip='4.4.4.4',
            status='approved',
        )
    good = base64.b64encode(b'admin:secret').decode()
    rv_client.post(
        f'/admin/reviews/{rid}/delete',
        headers={'Authorization': 'Basic ' + good},
    )
    with rv_app.app_context():
        from app import analytics_db
        row = analytics_db.query(
            "SELECT status, author_name, comment, email_hash FROM reviews WHERE id = ?",
            [rid],
        )
    assert row[0]['status'] == 'deleted'
    assert row[0]['author_name'] == '[deleted]'
    assert row[0]['email_hash'] is None


# ── GDPR deletion request ──


def test_deletion_request_requires_matching_email(rv_client, rv_app):
    with rv_app.app_context():
        from app import analytics_db
        rid = analytics_db.insert_review(
            route_slug='beograd-ljubljana', rating=5,
            comment='Linija je bila bez problema i osoblje vrlo prijatno tokom celog putovanja.',
            author_name='Mila', email='mila@example.com', lang='sr', ip='5.5.5.5',
            status='approved',
        )

    # Wrong email — silent 200 (don't leak ownership), nothing flagged.
    r = rv_client.post(
        f'/api/review/{rid}/delete-request',
        json={'email': 'attacker@example.com'},
    )
    assert r.status_code == 200
    with rv_app.app_context():
        from app import analytics_db
        row = analytics_db.query(
            "SELECT deletion_requested FROM reviews WHERE id = ?", [rid]
        )
    assert row[0]['deletion_requested'] is False

    # Correct email — still 200, but deletion_requested flips.
    r = rv_client.post(
        f'/api/review/{rid}/delete-request',
        json={'email': 'mila@example.com'},
    )
    assert r.status_code == 200
    with rv_app.app_context():
        from app import analytics_db
        row = analytics_db.query(
            "SELECT deletion_requested FROM reviews WHERE id = ?", [rid]
        )
    assert row[0]['deletion_requested'] is True


# ── Page-level schema.org ──


def test_route_detail_renders_aggregate_rating(rv_client, rv_app):
    """When approved reviews exist, page emits Product + AggregateRating JSON-LD."""
    with rv_app.app_context():
        from app import analytics_db
        for i in range(3):
            analytics_db.insert_review(
                route_slug='beograd-novi-sad', rating=5,
                comment=f'Bilo je dobro putovanje broj {i}, autobus udoban, stigli smo na vreme uvek.',
                author_name=f'User{i}', email=f'u{i}@ex.com', lang='sr',
                ip='6.6.6.6', status='approved',
            )
    r = rv_client.get('/rute/beograd-novi-sad/')
    body = r.data.decode()
    assert '"@type": "AggregateRating"' in body or '"@type":"AggregateRating"' in body
    assert '"reviewCount"' in body


def test_review_partial_renders_in_route_detail(rv_client):
    r = rv_client.get('/rute/beograd-novi-sad/')
    body = r.data.decode()
    assert 'reviewsHeading' in body
    assert 'rating-widget' in body
    assert 'review-form' in body


def test_privacy_mentions_reviews(rv_client):
    body = rv_client.get('/privatnost/').data.decode()
    assert 'recenziju' in body.lower() or 'review' in body.lower()

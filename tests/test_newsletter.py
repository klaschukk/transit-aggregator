"""Newsletter sub-system tests — campaigns CRUD, audience, validator,
render, dispatch, Mailgun webhook, GDPR export.

Each test uses a private analytics DB path so the prod-seeded drafts
don't pollute fixtures. The dispatch tests inject a stub send_fn so
nothing actually leaves the box.
"""
from __future__ import annotations

import hmac
import hashlib
import json

import pytest

from app import create_app


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope='module')
def nl_app(tmp_path_factory):
    tmp = tmp_path_factory.mktemp('nl')
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['RATELIMIT_ENABLED'] = False
    app.config['ANALYTICS_DB_PATH'] = str(tmp / 'analytics.duckdb')
    app.config['BASE_URL'] = 'http://localhost:5000'
    app.config['SMTP_HOST'] = ''
    app.config['ADMIN_USER'] = 'admin'
    app.config['ADMIN_PASS'] = 'pw'
    app.config['ADMIN_EMAIL'] = 'admin@example.com'
    app.config['MAILGUN_WEBHOOK_SIGNING_KEY'] = 'mg-test-key'
    from app.extensions import limiter
    limiter.enabled = False
    from app import analytics_db
    with app.app_context():
        analytics_db.init_schema()
    yield app
    limiter.enabled = True


@pytest.fixture
def nl_client(nl_app):
    return nl_app.test_client()


def _admin_headers():
    import base64
    creds = base64.b64encode(b'admin:pw').decode()
    return {'Authorization': f'Basic {creds}'}


def _make_subscriber(nl_app, *, email, lang='sr', source='footer',
                     confirmed=True, route_slug=None):
    from app import analytics_db
    with nl_app.app_context():
        conn = analytics_db._get_conn()
        conn.execute(
            "INSERT INTO subscribers (email, email_lower, lang, source, "
            "confirm_token, unsubscribe_token, confirmed_at, route_slug) "
            "VALUES (?, ?, ?, ?, ?, ?, "
            f"{'CURRENT_TIMESTAMP' if confirmed else 'NULL'}, ?)",
            [email, email.lower(), lang, source,
             f'tk-{email}', f'unsub-{email}', route_slug],
        )
        rows = analytics_db.query(
            "SELECT id FROM subscribers WHERE email_lower = ?", [email.lower()],
        )
        return int(rows[0]['id'])


# ── 1. Campaigns CRUD ───────────────────────────────────────────────

def test_upsert_campaign_creates_then_updates(nl_app):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-1', subjects={'sr': 'Привет'},
            bodies={'sr': 'Body'},
            audience_filter={'lang': 'sr'},
        )
        assert cid > 0
        again = cmp_mod.upsert_campaign(
            slug='t-1', subjects={'sr': 'Updated'},
            bodies={'sr': 'New body'},
            audience_filter={'lang': 'en'},
        )
        assert again == cid  # same row
        c = cmp_mod.get_campaign_by_slug('t-1')
        assert c['subject_sr'] == 'Updated'
        assert json.loads(c['audience_filter'])['lang'] == 'en'


def test_upsert_rejects_unknown_status(nl_app):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        with pytest.raises(ValueError):
            cmp_mod.upsert_campaign(slug='t-bad', status='nuked')


def test_list_campaigns_filter_by_status(nl_app):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        cmp_mod.upsert_campaign(slug='t-list-d', subjects={'sr': 'd'},
                                bodies={'sr': 'd'}, status='draft')
        cmp_mod.upsert_campaign(slug='t-list-s', subjects={'sr': 's'},
                                bodies={'sr': 's'}, status='sent')
        drafts = cmp_mod.list_campaigns(status='draft')
        slugs = [c['slug'] for c in drafts]
        assert 't-list-d' in slugs
        assert 't-list-s' not in slugs


def test_parse_audience_handles_malformed_json(nl_app):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        # Bypass upsert validation — write malformed JSON directly.
        from app import analytics_db
        analytics_db._get_conn().execute(
            "INSERT INTO campaigns (slug, audience_filter, status) "
            "VALUES ('t-bad-json', '{not json', 'draft')"
        )
        c = cmp_mod.get_campaign_by_slug('t-bad-json')
        assert cmp_mod.parse_audience(c) == {}


# ── 2. Suppressions ────────────────────────────────────────────────

def test_suppress_email_idempotent(nl_app):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        cmp_mod.suppress_email('Hard@Bounce.Com', 'bounce', 'first')
        cmp_mod.suppress_email('hard@bounce.com', 'bounce', 'second')
        assert cmp_mod.is_suppressed('HARD@bounce.com')
        # First reason wins (ON CONFLICT DO NOTHING).
        rows = cmp_mod.list_suppressions(limit=10)
        target = [r for r in rows if r['email_lower'] == 'hard@bounce.com']
        assert target and target[0]['note'] == 'first'


def test_suppress_email_rejects_unknown_reason(nl_app):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        with pytest.raises(ValueError):
            cmp_mod.suppress_email('x@y.com', 'aliens', None)


# ── 3. Audience resolution ─────────────────────────────────────────

def test_audience_lang_filter(nl_app):
    from app.newsletter import audience as aud
    _make_subscriber(nl_app, email='sr1@x.com', lang='sr')
    _make_subscriber(nl_app, email='en1@x.com', lang='en')
    with nl_app.app_context():
        sr = aud.resolve({'lang': 'sr'})
        assert any(s['email'] == 'sr1@x.com' for s in sr)
        assert not any(s['email'] == 'en1@x.com' for s in sr)


def test_audience_source_filter(nl_app):
    from app.newsletter import audience as aud
    _make_subscriber(nl_app, email='home@x.com', source='home')
    _make_subscriber(nl_app, email='footer@x.com', source='footer')
    with nl_app.app_context():
        rows = aud.resolve({'source': 'home'})
        emails = [r['email'] for r in rows]
        assert 'home@x.com' in emails
        assert 'footer@x.com' not in emails


def test_audience_excludes_unconfirmed(nl_app):
    from app.newsletter import audience as aud
    _make_subscriber(nl_app, email='unconfirmed@x.com',
                     confirmed=False, source='confirm-test')
    _make_subscriber(nl_app, email='confirmed@x.com',
                     confirmed=True, source='confirm-test')
    with nl_app.app_context():
        rows = aud.resolve({'source': 'confirm-test'})
        emails = [r['email'] for r in rows]
        assert 'confirmed@x.com' in emails
        assert 'unconfirmed@x.com' not in emails


def test_audience_excludes_suppressed(nl_app):
    from app.newsletter import audience as aud
    from app.newsletter import campaigns as cmp_mod
    _make_subscriber(nl_app, email='supp@x.com', source='supp-test')
    _make_subscriber(nl_app, email='clean@x.com', source='supp-test')
    with nl_app.app_context():
        cmp_mod.suppress_email('supp@x.com', 'bounce')
        rows = aud.resolve({'source': 'supp-test'})
        emails = [r['email'] for r in rows]
        assert 'clean@x.com' in emails
        assert 'supp@x.com' not in emails


def test_audience_route_slug_null_excludes_alerts(nl_app):
    from app.newsletter import audience as aud
    _make_subscriber(nl_app, email='gen@x.com', route_slug=None,
                     source='route-test')
    _make_subscriber(nl_app, email='alert@x.com',
                     route_slug='beograd-novi-sad', source='route-test')
    with nl_app.app_context():
        rows = aud.resolve({'source': 'route-test', 'route_slug': None})
        emails = [r['email'] for r in rows]
        assert 'gen@x.com' in emails
        assert 'alert@x.com' not in emails


def test_audience_unsubscribed_excluded(nl_app):
    from app.newsletter import audience as aud
    from app import analytics_db
    _make_subscriber(nl_app, email='unsubbed@x.com', source='unsub-test')
    with nl_app.app_context():
        analytics_db._get_conn().execute(
            "UPDATE subscribers SET unsubscribed_at = CURRENT_TIMESTAMP "
            "WHERE email_lower = 'unsubbed@x.com'"
        )
        rows = aud.resolve({'source': 'unsub-test'})
        assert not any(r['email'] == 'unsubbed@x.com' for r in rows)


# ── 4. Spam-score validator ────────────────────────────────────────

def test_validator_clean_subject_passes():
    from app.newsletter import validator as val
    score, reasons, _ = val.validate(
        subject='Welcome to Prevozni',
        preheader='Five most popular routes inside.',
        body_md='# Hello\n\nThis is a normal welcome email with two paragraphs.\n\n'
                'It is a bit longer than the eighty-word minimum for the body so '
                'the validator does not flag it as too short. Adding more words to '
                'pad it out: Beograd, Novi Sad, Niš, Kragujevac, Sarajevo, Budva.',
    )
    assert score >= val.PASSING_SCORE
    assert not any(r.severity == 'fail' for r in reasons)


def test_validator_all_caps_subject_fails():
    from app.newsletter import validator as val
    score, reasons, _ = val.validate(
        subject='ACT NOW LIMITED OFFER!!!',
        preheader='', body_md='Body.' * 80,
    )
    assert score < val.PASSING_SCORE
    severities = [r.severity for r in reasons]
    assert 'fail' in severities


def test_validator_spam_keywords_fail():
    from app.newsletter import validator as val
    score, reasons, _ = val.validate(
        subject='New routes',
        preheader='hi',
        body_md='Click here for free money guaranteed risk-free! ' * 30,
    )
    assert any(r.severity == 'fail' and 'spam-keyword' in r.message
               for r in reasons)
    assert score < val.PASSING_SCORE


def test_validator_empty_body_fails():
    from app.newsletter import validator as val
    score, reasons, _ = val.validate(
        subject='Hello world', preheader='', body_md='',
    )
    assert score < val.PASSING_SCORE
    assert any('empty' in r.message for r in reasons)


def test_validator_strips_markdown_for_keyword_scan():
    """A spam-keyword inside a `[link text](url)` block where the URL
    happens to contain the word 'guarantee' must not trigger the scanner —
    the URL is stripped before scanning."""
    from app.newsletter import validator as val
    body = '# Welcome\n\n' + 'Normal travel content. ' * 40
    body += '\n[Read more](https://example.com/policy/guarantee/)'
    score, reasons, _ = val.validate(
        subject='Three lines about Belgrade',
        preheader='Six word preheader text here.',
        body_md=body,
    )
    assert not any('spam-keyword' in r.message for r in reasons)


# ── 5. Renderer ────────────────────────────────────────────────────

def test_render_email_includes_unsub_link():
    from app.newsletter import render
    _, html, text = render.render_email(
        subject='Hi', preheader='', body_md='hello',
        lang='sr', unsub_url='https://prevozni.com/api/unsubscribe/abc',
    )
    assert 'https://prevozni.com/api/unsubscribe/abc' in html
    assert 'https://prevozni.com/api/unsubscribe/abc' in text


def test_render_escapes_html_in_body():
    from app.newsletter import render
    _, html, _ = render.render_email(
        subject='Hi', preheader='', body_md='<script>alert(1)</script>',
        lang='sr', unsub_url='https://x/u/t',
    )
    assert '<script>alert(1)</script>' not in html
    assert '&lt;script&gt;' in html


def test_render_link_with_text_in_html():
    from app.newsletter import render
    _, html, text = render.render_email(
        subject='Hi', preheader='', body_md='[Beograd](https://prevozni.com/)',
        lang='sr', unsub_url='https://x/u/t',
    )
    assert 'href="https://prevozni.com/"' in html
    assert 'Beograd (https://prevozni.com/)' in text


def test_substitute_replaces_known_placeholders():
    from app.newsletter import render
    out = render.substitute(
        'Click {{unsub_url}} to unsubscribe — sent by {{sender_name}}.',
        {'unsub_url': 'https://x/u/t', 'sender_name': 'Prevozni'},
    )
    assert out == 'Click https://x/u/t to unsubscribe — sent by Prevozni.'


def test_substitute_unknown_placeholder_returns_empty():
    from app.newsletter import render
    out = render.substitute('Hi {{nope}} there', {})
    assert out == 'Hi  there'


# ── 6. Dispatch ────────────────────────────────────────────────────

class _StubSender:
    def __init__(self):
        self.calls = []
    def __call__(self, *, to, subject, text, html, list_unsubscribe=None):
        self.calls.append({
            'to': to, 'subject': subject,
            'has_text': bool(text), 'has_html': bool(html),
            'list_unsubscribe': list_unsubscribe,
        })
        return True


def test_dispatch_dry_run_sends_nothing(nl_app):
    from app.newsletter import campaigns as cmp_mod
    from app.newsletter import dispatch as disp
    sender = _StubSender()
    _make_subscriber(nl_app, email='dry1@x.com', lang='sr', source='dry-run')
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-dry', subjects={'sr': 'X'}, bodies={'sr': 'Body ' * 50},
            audience_filter={'source': 'dry-run'},
        )
        summary = disp.send_campaign(
            cid, send_fn=sender, unsub_base_url='http://x',
            dry_run=True, min_delay_s=0,
        )
        assert summary['sent'] == 0
        assert summary['rows_dry_run']
        assert sender.calls == []


def test_dispatch_actually_sends_and_records(nl_app):
    from app.newsletter import campaigns as cmp_mod
    from app.newsletter import dispatch as disp
    sender = _StubSender()
    sub_id = _make_subscriber(nl_app, email='act1@x.com', lang='sr',
                              source='dispatch-test')
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-actual', subjects={'sr': 'X'}, bodies={'sr': 'Body ' * 50},
            audience_filter={'source': 'dispatch-test'},
        )
        summary = disp.send_campaign(
            cid, send_fn=sender, unsub_base_url='http://x',
            min_delay_s=0,
        )
        assert summary['sent'] >= 1
        assert sender.calls
        # Status moved → sent
        c = cmp_mod.get_campaign(cid)
        assert c['status'] == 'sent'
        # campaign_sends row exists
        assert sub_id in cmp_mod.already_sent_subscriber_ids(cid)


def test_dispatch_resume_skips_already_sent(nl_app):
    from app.newsletter import campaigns as cmp_mod
    from app.newsletter import dispatch as disp
    sender = _StubSender()
    _make_subscriber(nl_app, email='rs1@x.com', lang='sr', source='resume-test')
    _make_subscriber(nl_app, email='rs2@x.com', lang='sr', source='resume-test')
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-resume', subjects={'sr': 'X'}, bodies={'sr': 'Body ' * 50},
            audience_filter={'source': 'resume-test'},
        )
        # First run.
        summary1 = disp.send_campaign(cid, send_fn=sender,
                                      unsub_base_url='http://x', min_delay_s=0)
        # Second run: status is 'sent', refuse without dry_run.
        with pytest.raises(RuntimeError):
            disp.send_campaign(cid, send_fn=sender,
                               unsub_base_url='http://x', min_delay_s=0)
        # But dry-run on a sent campaign is fine — used by the preview.
        summary2 = disp.send_campaign(cid, send_fn=sender,
                                      unsub_base_url='http://x',
                                      dry_run=True, min_delay_s=0)
        assert summary1['sent'] >= 2


def test_dispatch_lang_fallback_when_body_missing(nl_app):
    from app.newsletter import campaigns as cmp_mod
    from app.newsletter import dispatch as disp
    sender = _StubSender()
    _make_subscriber(nl_app, email='ru-only@x.com', lang='ru',
                     source='lang-fallback')
    with nl_app.app_context():
        # Campaign has only sr body — ru subscriber should still receive it.
        cid = cmp_mod.upsert_campaign(
            slug='t-fallback',
            subjects={'sr': 'Привет'}, bodies={'sr': 'Body ' * 50},
            audience_filter={'source': 'lang-fallback'},
        )
        summary = disp.send_campaign(cid, send_fn=sender,
                                     unsub_base_url='http://x', min_delay_s=0)
        assert summary['sent'] == 1
        assert summary['skipped_no_body'] == 0


def test_dispatch_test_mode_bypasses_audience(nl_app):
    from app.newsletter import campaigns as cmp_mod
    from app.newsletter import dispatch as disp
    sender = _StubSender()
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-test', subjects={'sr': 'X'}, bodies={'sr': 'Body ' * 50},
            audience_filter={'source': 'no-such-source'},  # 0 matches
        )
        result = disp.send_campaign(
            cid, send_fn=sender, unsub_base_url='http://x',
            test_email='admin@example.com', min_delay_s=0,
        )
        assert result.get('ok')
        assert sender.calls and sender.calls[0]['to'] == 'admin@example.com'


# ── 7. Mailgun webhook ─────────────────────────────────────────────

def _mg_signed_payload(signing_key: str, event: str,
                       recipient: str) -> dict:
    token = 'tk-1234'
    ts = '1700000000'
    sig = hmac.new(signing_key.encode(), (ts + token).encode(),
                   hashlib.sha256).hexdigest()
    return {
        'signature': {'token': token, 'timestamp': ts, 'signature': sig},
        'event-data': {
            'event': event, 'recipient': recipient,
            'message': {'headers': {'message-id': 'm@x'}},
        },
    }


def test_mailgun_webhook_rejects_bad_signature(nl_client):
    payload = {
        'signature': {'token': 'a', 'timestamp': '1', 'signature': 'BAD'},
        'event-data': {'event': 'delivered', 'recipient': 'x@x.com'},
    }
    resp = nl_client.post(
        '/admin/api/mailgun-webhook', json=payload,
    )
    assert resp.status_code == 403


def test_mailgun_webhook_marks_delivered(nl_app, nl_client):
    from app.newsletter import campaigns as cmp_mod
    from app import analytics_db
    sub_id = _make_subscriber(nl_app, email='mg-d@x.com', lang='sr',
                              source='mg-test')
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-mg-d', subjects={'sr': 'X'}, bodies={'sr': 'B' * 200},
        )
        cmp_mod.record_send(cid, sub_id)
    payload = _mg_signed_payload('mg-test-key', 'delivered', 'mg-d@x.com')
    resp = nl_client.post('/admin/api/mailgun-webhook', json=payload)
    assert resp.status_code == 200
    with nl_app.app_context():
        rows = analytics_db.query(
            "SELECT delivered_at FROM campaign_sends "
            "WHERE campaign_id = ? AND subscriber_id = ?",
            [cid, sub_id],
        )
        assert rows and rows[0]['delivered_at'] is not None


def test_mailgun_webhook_hard_bounce_suppresses(nl_app, nl_client):
    from app.newsletter import campaigns as cmp_mod
    sub_id = _make_subscriber(nl_app, email='mg-b@x.com', lang='sr',
                              source='mg-bounce')
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-mg-b', subjects={'sr': 'X'}, bodies={'sr': 'B' * 200},
        )
        cmp_mod.record_send(cid, sub_id)
    payload = _mg_signed_payload('mg-test-key', 'failed', 'mg-b@x.com')
    resp = nl_client.post('/admin/api/mailgun-webhook', json=payload)
    assert resp.status_code == 200
    with nl_app.app_context():
        from app.newsletter import campaigns as cmp_mod
        assert cmp_mod.is_suppressed('mg-b@x.com')


# ── 8. GDPR data export ────────────────────────────────────────────

def test_gdpr_export_returns_subscriber_data(nl_app, nl_client):
    _make_subscriber(nl_app, email='gdpr@x.com', source='gdpr-test')
    resp = nl_client.get('/admin/api/subscriber-data?token=unsub-gdpr@x.com')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['subscriber']['email'] == 'gdpr@x.com'
    assert body['subscriber']['source'] == 'gdpr-test'


def test_gdpr_export_404_on_unknown_token(nl_client):
    resp = nl_client.get('/admin/api/subscriber-data?token=does-not-exist')
    assert resp.status_code == 404


def test_gdpr_export_400_when_token_missing(nl_client):
    resp = nl_client.get('/admin/api/subscriber-data')
    assert resp.status_code == 400


# ── 9. Admin UI auth ───────────────────────────────────────────────

def test_admin_newsletter_requires_basic_auth(nl_client):
    resp = nl_client.get('/admin/newsletter')
    assert resp.status_code == 401
    assert 'WWW-Authenticate' in resp.headers


def test_admin_newsletter_renders_campaign_list(nl_app, nl_client):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        cmp_mod.upsert_campaign(slug='t-ui-list', subjects={'sr': 'X'},
                                bodies={'sr': 'B' * 100})
    resp = nl_client.get('/admin/newsletter', headers=_admin_headers())
    assert resp.status_code == 200
    assert b't-ui-list' in resp.data


def test_admin_compose_validate_returns_score(nl_app, nl_client):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-ui-val', subjects={'sr': 'Hi'}, bodies={'sr': 'B' * 200},
        )
    resp = nl_client.post(
        f'/admin/newsletter/{cid}',
        data={
            'op': 'validate',
            'subject_sr': 'Welcome to Prevozni',
            'preheader_sr': 'Five most popular routes',
            'body_md_sr': 'Hello world. ' * 60,
            'subject_en': '', 'preheader_en': '', 'body_md_en': '',
            'subject_ru': '', 'preheader_ru': '', 'body_md_ru': '',
            'audience_filter_json': '{}',
        },
        headers=_admin_headers(),
    )
    assert resp.status_code == 200
    j = resp.get_json()
    assert 'per_language' in j
    assert 'sr' in j['per_language']
    assert j['per_language']['sr']['score'] >= 50


def test_admin_preview_renders_html(nl_app, nl_client):
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        cid = cmp_mod.upsert_campaign(
            slug='t-ui-prev', subjects={'sr': 'Pre'},
            bodies={'sr': '# Header\n\nParagraph.'},
        )
    resp = nl_client.get(
        f'/admin/newsletter/{cid}/preview/sr', headers=_admin_headers(),
    )
    assert resp.status_code == 200
    body = resp.data.decode()
    assert '<h1' in body
    assert 'Header' in body
    assert 'Paragraph' in body


# ── 10. Seed drafts ────────────────────────────────────────────────

def test_seed_creates_three_drafts(nl_app):
    from app.newsletter import seed_drafts
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        ids = seed_drafts.seed()
        assert len(ids) == 3
        slugs = {cmp_mod.get_campaign(i)['slug'] for i in ids}
        assert slugs == {'welcome-confirmed', 'weekly-digest-template',
                         'seasonal-summer'}


def test_seed_is_idempotent(nl_app):
    from app.newsletter import seed_drafts
    from app.newsletter import campaigns as cmp_mod
    with nl_app.app_context():
        seed_drafts.seed()
        seed_drafts.seed()
        ids = seed_drafts.seed()
        rows = cmp_mod.list_campaigns(limit=200)
        slugs = [r['slug'] for r in rows
                 if r['slug'] in ('welcome-confirmed',
                                  'weekly-digest-template',
                                  'seasonal-summer')]
        assert len(slugs) == 3  # not 9


def test_seed_drafts_pass_validator(nl_app):
    """Every shipped draft must pass the spam-score gate in every language —
    otherwise the operator can't actually send them without the
    'I know what I'm doing' override, which defeats the purpose."""
    from app.newsletter import validator as val
    from app.newsletter.seed_drafts import _DRAFTS
    for draft in _DRAFTS:
        for lang in ('sr', 'en', 'ru'):
            score, reasons, _ = val.validate(
                draft['subjects'].get(lang, ''),
                draft['preheaders'].get(lang, ''),
                draft['bodies'].get(lang, ''),
            )
            assert score >= val.PASSING_SCORE, (
                f"draft {draft['slug']!r} lang={lang} fails: "
                f"score={score} reasons="
                f"{[(r.severity, r.message) for r in reasons]}"
            )

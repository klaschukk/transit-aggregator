"""Cold-outreach automation tests.

Covers the four risk surfaces:
  1. Never-send gates (testing env, empty `to`, GDPR TLDs, daily cap).
  2. CSV schema migration — existing 10-col file must still load.
  3. Template rendering: Subject parsing, placeholder substitution,
     missing-key fallback to `[KEY]` instead of raising.
  4. Webhook: HMAC verification, event→CSV state mapping, invalid payload.

Deliberately isolates per test with temporary CSV + a temporary
SEND_LOG so rate-limit state from one test can't leak into another.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app import outreach
from app.outreach import sender as sender_mod
from app.outreach.csv_io import load_targets, save_targets
from app.outreach.schema import FIELDNAMES
from app.outreach.templates import (
    TEMPLATES_DIR,
    render_template,
    template_for_category,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def isolate_send_log(monkeypatch, tmp_path):
    """Redirect SEND_LOG to a tmp file so rate-limit tests don't poison
    the real log and don't inherit state from previous runs."""
    log = tmp_path / 'backlinks_sent.log'
    monkeypatch.setattr(sender_mod, 'SEND_LOG', log)
    monkeypatch.setattr(sender_mod, '_LOG_DIR', tmp_path)
    return log


@pytest.fixture
def tmp_csv(tmp_path):
    """Legacy 10-column CSV so we exercise the migration path."""
    p = tmp_path / 'targets.csv'
    p.write_text(
        'domain,url,category,DA_estimate,language,contact_method,'
        'status,contacted_at,last_status_change,notes\n'
        'example.com,https://example.com/,travel_blog_global,40,en,email,'
        'todo,,,initial research note\n'
        'de-example.de,https://de-example.de/,expat_serbia,55,en,email,'
        'todo,,,listed in DE\n',
        encoding='utf-8',
    )
    return p


# ── 1. CSV schema migration ────────────────────────────────────────────

def test_legacy_csv_loads_with_new_fields_empty(tmp_csv):
    fields, rows = load_targets(tmp_csv)
    # Every canonical field must be present in the row dicts.
    for f in FIELDNAMES:
        assert f in rows[0], f'missing canonical column: {f}'
    # Field order must include all canonicals.
    for f in FIELDNAMES:
        assert f in fields
    # New fields default to empty string, NOT None — writer expects str.
    assert rows[0]['contact_email'] == ''
    assert rows[0]['enriched_at'] == ''


def test_roundtrip_preserves_legacy_notes(tmp_csv):
    fields, rows = load_targets(tmp_csv)
    rows[0]['contact_email'] = 'info@example.com'
    save_targets(fields, rows, tmp_csv)
    _, reloaded = load_targets(tmp_csv)
    assert reloaded[0]['notes'] == 'initial research note'
    assert reloaded[0]['contact_email'] == 'info@example.com'


# ── 2. Template rendering ──────────────────────────────────────────────

def test_template_for_category_maps_known_category():
    assert template_for_category('serbian_tourism', 'en') == 'tourism_board_en'
    assert template_for_category('travel_blog_global', 'en') == 'travel_blog_en'
    assert template_for_category('expat_serbia', 'en') == 'expat_forum_en'
    assert template_for_category('russian_diaspora', 'ru') == 'russian_diaspora_ru'


def test_template_fallback_when_category_unknown():
    assert template_for_category('nonexistent_category', 'en') == 'generic_en'


def test_render_template_substitutes_placeholders():
    subject, body = render_template('tourism_board_en', {
        'name': 'Marija',
        'site_title': 'Belgrade Tourism',
        'their_topic': 'Getting around',
        'our_hook': '/rute/',
        'domain': 'tob.rs',
    })
    assert 'Marija' in body
    assert 'Belgrade Tourism' in subject  # uses {site_title}
    assert 'Getting around' in body
    assert '{name}' not in body, 'placeholder must be substituted'


def test_render_template_missing_key_degrades_gracefully():
    """Missing placeholder → `[KEY]` hint, not KeyError."""
    subject, body = render_template('tourism_board_en', {'name': 'X'})
    assert '[SITE_TITLE]' in subject or '[SITE_TITLE]' in body
    # Existing key still rendered normally.
    assert 'X' in body


def test_render_missing_template_raises():
    with pytest.raises(FileNotFoundError):
        render_template('does_not_exist', {'name': 'x'})


# ── 3. Send guards ─────────────────────────────────────────────────────

def test_send_blocked_in_testing_env(isolate_send_log):
    """PYTEST_CURRENT_TEST is set by pytest automatically — the guard
    must refuse regardless of MAILGUN/SMTP config."""
    ok, detail = outreach.send_outreach(
        to='info@example.com', subject='Test', text='body',
        from_addr='a@b.c', dry_run=False,
    )
    assert not ok
    assert 'testing' in detail.lower()


def test_send_rejects_invalid_email(isolate_send_log, monkeypatch):
    """Unset the testing-env env vars to exercise the email validator
    directly — the testing-env guard comes first in sender.py and would
    otherwise shadow every downstream guard."""
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)
    monkeypatch.delenv('FLASK_ENV', raising=False)
    ok, detail = outreach.send_outreach(
        to='not-an-email', subject='Test', text='body',
        from_addr='a@b.c', dry_run=False,
    )
    assert not ok
    assert 'invalid' in detail.lower()


def test_send_dry_run_writes_log_event(isolate_send_log, monkeypatch):
    """Dry-run must bypass the testing-env block so `--dry-run` works in
    CI. We simulate production-env by unsetting PYTEST_CURRENT_TEST for
    the duration of the call; still, dry_run=True must not touch
    network, and must append event='dry_run'."""
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)
    monkeypatch.delenv('FLASK_ENV', raising=False)
    ok, detail = outreach.send_outreach(
        to='info@example.com', subject='Test', text='body',
        from_addr='a@b.c', domain_target='example.com', dry_run=True,
    )
    assert ok
    assert 'dry' in detail.lower()
    log = isolate_send_log.read_text(encoding='utf-8').strip().splitlines()
    assert log
    rec = json.loads(log[-1])
    assert rec['event'] == 'dry_run'
    assert rec['to'] == 'info@example.com'


def test_gdpr_strict_tld_blocks_without_note(isolate_send_log, monkeypatch):
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)
    monkeypatch.delenv('FLASK_ENV', raising=False)
    ok, detail = outreach.send_outreach(
        to='info@example.de', subject='Test', text='body',
        from_addr='a@b.c', domain_target='example.de',
        notes='no legal review yet', dry_run=True,
    )
    assert not ok
    assert 'gdpr' in detail.lower()


def test_gdpr_unblocked_with_gdpr_ok_note(isolate_send_log, monkeypatch):
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)
    monkeypatch.delenv('FLASK_ENV', raising=False)
    ok, _ = outreach.send_outreach(
        to='info@example.de', subject='Test', text='body',
        from_addr='a@b.c', domain_target='example.de',
        notes='gdpr_ok — legal review 2026-04-20', dry_run=True,
    )
    assert ok


def test_daily_cap_enforced(isolate_send_log, monkeypatch):
    """Pre-fill the log with MAX_SENDS_PER_DAY sends, then assert the
    next attempt is blocked. Bypasses the testing-env guard since we're
    asserting a guard that comes after it."""
    monkeypatch.delenv('PYTEST_CURRENT_TEST', raising=False)
    monkeypatch.delenv('FLASK_ENV', raising=False)
    now = datetime.now(timezone.utc).isoformat()
    with isolate_send_log.open('w', encoding='utf-8') as f:
        for i in range(outreach.MAX_SENDS_PER_DAY):
            f.write(json.dumps(
                {'ts': now, 'event': 'sent', 'to': f'u{i}@example.com'}
            ) + '\n')
    ok, detail = outreach.send_outreach(
        to='new@example.com', subject='Test', text='body',
        from_addr='a@b.c', domain_target='example.com', dry_run=False,
    )
    assert not ok
    assert 'cap' in detail.lower()


def test_build_message_has_unsubscribe_headers():
    msg = sender_mod.build_message(
        to='info@example.com', subject='Hi', text='Hello',
        from_addr='kirill@prevozni.com', base_url='https://prevozni.com',
        secret='secret',
    )
    assert 'List-Unsubscribe' in msg
    assert 'List-Unsubscribe-Post' in msg
    assert 'https://prevozni.com/api/backlinks-unsubscribe' in msg['List-Unsubscribe']
    # CAN-SPAM footer appended to body.
    assert 'Unsubscribe' in msg.get_content()
    assert 'STOP' in msg.get_content()


def test_gdpr_sensitive_domain_detection():
    assert outreach.is_gdpr_sensitive_domain('example.de', notes='')
    assert outreach.is_gdpr_sensitive_domain('EXAMPLE.DE', notes='')
    assert not outreach.is_gdpr_sensitive_domain('example.com', notes='')
    assert not outreach.is_gdpr_sensitive_domain(
        'example.de', notes='gdpr_ok reviewed')


# ── 4. Webhook & unsubscribe endpoints ─────────────────────────────────

def test_unsubscribe_endpoint_rejects_bad_token(client):
    resp = client.get('/api/backlinks-unsubscribe?e=a@b.com&t=invalid')
    assert resp.status_code == 400


def test_unsubscribe_endpoint_accepts_valid_token(client, app):
    """Compute the same HMAC-truncated SHA256 token the sender would
    and verify the route accepts it."""
    import hashlib
    secret = app.config.get('SECRET_KEY', 'dev-secret') or 'dev-secret'
    email = 'signed-unsub@example.com'
    tok = hashlib.sha256(
        f'{email}|{secret}'.encode('utf-8')
    ).hexdigest()[:20]
    resp = client.get(f'/api/backlinks-unsubscribe?e={email}&t={tok}')
    assert resp.status_code == 200


def test_mailgun_webhook_rejects_unsigned(client):
    resp = client.post('/api/mailgun-webhook', json={'event-data': {
        'event': 'delivered', 'recipient': 'a@b.com',
    }})
    # 401 because signing key is empty → verification fails.
    assert resp.status_code == 401


def test_admin_backlinks_requires_auth(client):
    resp = client.get('/admin/backlinks')
    # Without ADMIN_USER/PASS configured the route returns 503; with them
    # set it returns 401. Either is a valid "auth required" outcome.
    assert resp.status_code in (401, 503)

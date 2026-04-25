"""Thin send layer on top of app.mailer.

Adds the pieces specific to cold outreach that don't belong in the
transactional mailer:

 - CAN-SPAM compliant footer (physical address + one-click opt-out).
 - `List-Unsubscribe` headers (RFC 2369 + RFC 8058 POST variant).
 - Domain-level rate limit (20/day per FROM).
 - GDPR-sensitive TLD guard (DE/FR default to blocked).
 - Mailgun API backend when MAILGUN_API_KEY is set — the stdlib SMTP
   mailer can't ask for per-message event tracking.
 - Append-only send log at logs/backlinks_sent.log for rate limiting,
   audit, and after-the-fact digest building.

The CLI (scripts/backlinks_send.py) never calls SMTP directly — it goes
through `send_outreach()` so every guard fires uniformly whether you're
sending one email interactively or twenty via cron.
"""
from __future__ import annotations

import email.utils
import hashlib
import json
import logging
import os
import re
import urllib.parse


from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

logger = logging.getLogger(__name__)

# Hard cap on outbound per rolling 24h window. Raised only by editing
# this constant — deliberately not an env var so a misconfigured cron
# can't blast the inbox.
MAX_SENDS_PER_DAY = 20

# Append-only log — one JSON-per-line record per send attempt. Used for
# the daily rate-limit check AND the /admin/backlinks dashboard history.
_LOG_DIR = Path(__file__).resolve().parent.parent.parent / 'logs'
SEND_LOG = _LOG_DIR / 'backlinks_sent.log'

# GDPR-strict jurisdictions where B2B cold email needs more care.
# Target rows listed in these TLDs require `notes` to contain the
# token `gdpr_ok` (human-verified legal basis) before we send.
_GDPR_STRICT_TLDS = ('.de', '.fr', '.at', '.ch', '.nl')


# ── physical address — required for CAN-SPAM compliance.
# Read from env (`MAIL_PHYSICAL_ADDRESS`) so solo dev sets it once in
# the systemd unit, no code edit. Falls back to a Belgrade placeholder
# that's truthy enough for staging but should be replaced before the
# first non-dry-run send to a US audience.
PHYSICAL_ADDRESS = os.environ.get(
    'MAIL_PHYSICAL_ADDRESS', 'Prevozni · Belgrade, Serbia',
)


def is_gdpr_sensitive_domain(domain: str, notes: str = '') -> bool:
    """True when we should block sending because the target is in a
    GDPR-strict jurisdiction and the row hasn't been legally reviewed.

    The row unblocks itself by adding the literal string `gdpr_ok` to
    the `notes` column (added via manual review). This forces a pause
    for DE/FR/etc domains without forbidding them outright.
    """
    d = (domain or '').lower().strip()
    if not any(d.endswith(tld) for tld in _GDPR_STRICT_TLDS):
        return False
    return 'gdpr_ok' not in (notes or '').lower()


def _sent_within(hours: int) -> int:
    """Count lines in SEND_LOG with status=sent within the last N hours."""
    if not SEND_LOG.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    count = 0
    try:
        with SEND_LOG.open(encoding='utf-8') as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except ValueError:
                    continue
                if rec.get('event') != 'sent':
                    continue
                ts = rec.get('ts', '')
                try:
                    when = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except ValueError:
                    continue
                if when >= cutoff:
                    count += 1
    except OSError:
        return 0
    return count


def daily_send_cap_ok() -> tuple[bool, int]:
    """Return (can_send_more, sent_in_last_24h)."""
    n = _sent_within(24)
    return n < MAX_SENDS_PER_DAY, n


def _unsubscribe_token(to: str, secret: str) -> str:
    """HMAC-ish token so /unsubscribe-backlinks/<token> links can't be
    guessed from just the email address."""
    msg = f'{to}|{secret or "dev-secret"}'.encode('utf-8')
    return hashlib.sha256(msg).hexdigest()[:20]


def _unsubscribe_url(to: str, secret: str, base_url: str) -> str:
    tok = _unsubscribe_token(to, secret)
    q = urllib.parse.urlencode({'e': to, 't': tok})
    return f'{base_url.rstrip("/")}/api/backlinks-unsubscribe?{q}'


def build_message(
    *,
    to: str,
    subject: str,
    text: str,
    from_addr: str,
    base_url: str = 'https://prevozni.com',
    secret: str = '',
) -> EmailMessage:
    """Compose the outbound EmailMessage with unsubscribe headers and a
    CAN-SPAM footer appended to the body. Separated from send for tests
    — call build_message() in tests without touching SMTP."""
    unsub = _unsubscribe_url(to, secret, base_url)

    footer = (
        '\n\n---\n'
        f'{PHYSICAL_ADDRESS}\n'
        f'Unsubscribe (one click): {unsub}\n'
        'Reply "STOP" to this email and we will never contact you again.\n'
    )
    full_text = text.rstrip() + footer

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Message-ID'] = email.utils.make_msgid(domain='prevozni.com')
    # RFC 2369 + RFC 8058: inbox providers show an "Unsubscribe" button
    # when both headers are present. The POST form lets Gmail/Yahoo
    # process the unsubscribe without opening the browser.
    msg['List-Unsubscribe'] = f'<{unsub}>, <mailto:{from_addr}?subject=unsubscribe>'
    msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    msg.set_content(full_text)
    return msg


def _append_log(record: dict) -> None:
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        with SEND_LOG.open('a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    except OSError as exc:
        logger.warning('backlinks send-log write failed: %s', exc)


def record_event(
    *,
    email_to: str,
    event: str,
    domain: str = '',
    url: str = '',
    extra: dict | None = None,
) -> None:
    """Append a single event line to the send log. Called by:
      - send_outreach() on each send attempt (event='sent' or 'error')
      - /api/mailgun-webhook on delivery/open/click/reply/bounce
      - follow-up scripts on status transitions
    """
    rec = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'event': event,
        'to': email_to,
        'domain': domain,
        'url': url,
    }
    if extra:
        rec.update(extra)
    _append_log(rec)


# Pytest runs with FLASK_ENV=testing or PYTEST_CURRENT_TEST in env. Those
# environments MUST never reach SMTP — one stray `pytest -k send` then
# wipes the sender's reputation. This guard is re-checked on every send.
def _testing_env() -> bool:
    if os.environ.get('PYTEST_CURRENT_TEST'):
        return True
    if os.environ.get('FLASK_ENV', '').lower() == 'testing':
        return True
    return False


def _send_via_mailgun(
    *,
    msg: EmailMessage,
    api_key: str,
    domain: str,
) -> tuple[bool, str]:
    """Send the assembled EmailMessage via Mailgun's v3 Messages API.

    Returns (ok, provider_id_or_error). Keeping this here and not in
    app/mailer.py because mailer.py is shared with transactional sends
    (newsletter confirm, price alerts) — those stay on SMTP so a
    Mailgun outage can't break signup.
    """
    try:
        import requests
    except ImportError:
        return False, 'requests module required for Mailgun sender'

    data = {
        'from': msg['From'],
        'to': msg['To'],
        'subject': msg['Subject'],
        'text': msg.get_content(),
        'h:List-Unsubscribe': msg.get('List-Unsubscribe', ''),
        'h:List-Unsubscribe-Post': msg.get('List-Unsubscribe-Post', ''),
        'o:tracking': 'yes',
        'o:tracking-opens': 'yes',
        'o:tracking-clicks': 'htmlonly',
    }
    try:
        resp = requests.post(
            f'https://api.mailgun.net/v3/{domain}/messages',
            auth=('api', api_key),
            data=data,
            timeout=15,
        )
        if resp.status_code == 200:
            body = resp.json() if resp.content else {}
            return True, str(body.get('id', ''))
        return False, f'HTTP {resp.status_code}: {resp.text[:200]}'
    except Exception as exc:  # noqa: BLE001  — log everything, never raise
        return False, str(exc)


def send_outreach(
    *,
    to: str,
    subject: str,
    text: str,
    from_addr: str,
    domain_target: str = '',
    url_target: str = '',
    base_url: str = 'https://prevozni.com',
    secret: str = '',
    mailgun_api_key: str = '',
    mailgun_domain: str = '',
    notes: str = '',
    dry_run: bool = True,
) -> tuple[bool, str]:
    """Top-level send. Returns (ok, detail).

    Guards (in order):
      1. testing env          → refuse
      2. empty `to`           → refuse
      3. GDPR-strict TLD unresolved → refuse
      4. daily cap            → refuse
      5. dry_run              → log event='dry_run', return True
      6. Mailgun if configured, else SMTP via app.mailer.send_mail
    """
    if _testing_env():
        record_event(email_to=to, event='blocked_testing',
                     domain=domain_target, url=url_target)
        return False, 'blocked: testing environment'
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', (to or '').strip()):
        return False, 'invalid email address'
    if is_gdpr_sensitive_domain(domain_target, notes):
        record_event(email_to=to, event='blocked_gdpr',
                     domain=domain_target, url=url_target)
        return False, (
            f'blocked: {domain_target} is GDPR-strict; add `gdpr_ok` to '
            f'notes after legal review to unblock'
        )
    ok_cap, sent_24h = daily_send_cap_ok()
    if not ok_cap:
        record_event(email_to=to, event='blocked_cap',
                     domain=domain_target, url=url_target,
                     extra={'sent_24h': sent_24h})
        return False, f'blocked: daily cap ({sent_24h}/{MAX_SENDS_PER_DAY})'

    msg = build_message(
        to=to, subject=subject, text=text, from_addr=from_addr,
        base_url=base_url, secret=secret,
    )

    if dry_run:
        record_event(email_to=to, event='dry_run',
                     domain=domain_target, url=url_target,
                     extra={'subject': subject})
        return True, 'dry-run — no email sent'

    if mailgun_api_key and mailgun_domain:
        ok, detail = _send_via_mailgun(
            msg=msg, api_key=mailgun_api_key, domain=mailgun_domain,
        )
        record_event(
            email_to=to, event='sent' if ok else 'error',
            domain=domain_target, url=url_target,
            extra={'provider': 'mailgun', 'detail': detail,
                   'subject': subject},
        )
        return ok, detail

    # SMTP fallback — goes through the shared transactional mailer so
    # the dev-log fallback kicks in when SMTP_HOST isn't set.
    try:
        from flask import current_app  # imported lazily
        from app.mailer import send_mail
        ok = send_mail(
            to=to, subject=subject,
            text=msg.get_content(),
        )
        record_event(
            email_to=to, event='sent' if ok else 'error',
            domain=domain_target, url=url_target,
            extra={'provider': 'smtp',
                   'host': current_app.config.get('SMTP_HOST', '') or 'dev-log',
                   'subject': subject},
        )
        return ok, 'sent via SMTP' if ok else 'SMTP send failed'
    except RuntimeError as exc:
        # No app context — the CLI forgot to wrap in `with app.app_context()`.
        record_event(email_to=to, event='error',
                     domain=domain_target, url=url_target,
                     extra={'detail': f'no app context: {exc}'})
        return False, f'no app context: {exc}'

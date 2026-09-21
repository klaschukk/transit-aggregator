"""SMTP sender with a DEV-mode log fallback.

When SMTP_HOST is configured we send through stdlib smtplib (STARTTLS
when port 587, implicit TLS when 465). Without SMTP_HOST the message is
appended to logs/mail_dev.log and the caller gets True — the double-opt-in
flow keeps working locally and in CI without any real mailbox.

Kept tiny on purpose: one function, one fallback, one log file. When
Mailgun/SES lands, swap `_send_smtp()` for a provider-specific client
and leave send_mail()'s signature + log line intact.
"""
from __future__ import annotations

import logging
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from flask import current_app

from . import observability

logger = logging.getLogger(__name__)

_DEV_LOG_FILENAME = 'mail_dev.log'


def send_mail(
    *,
    to: str,
    subject: str,
    text: str,
    html: str | None = None,
    list_unsubscribe: str | None = None,
) -> bool:
    """Deliver or log. Returns True on success (including DEV-log success),
    False only when both SMTP and the fallback file write failed.

    list_unsubscribe: when set, attaches the RFC 8058 / RFC 2369 headers
    Gmail and Yahoo use to render their one-click unsubscribe button.
    Pass the per-recipient unsubscribe URL — the wrapping in
    `<https://...>` and the List-Unsubscribe-Post line are added here."""
    to = (to or '').strip()
    if not to:
        logger.warning("send_mail called with empty recipient")
        return False

    host = current_app.config.get('SMTP_HOST', '')
    if not host:
        return _append_dev_log(to, subject, text, html, list_unsubscribe)

    return _send_smtp(to=to, subject=subject, text=text, html=html,
                      list_unsubscribe=list_unsubscribe)


def _send_smtp(*, to: str, subject: str, text: str,
               html: str | None,
               list_unsubscribe: str | None = None) -> bool:
    cfg = current_app.config
    host = cfg.get('SMTP_HOST', '')
    port = int(cfg.get('SMTP_PORT', 587))
    user = cfg.get('SMTP_USER', '')
    password = cfg.get('SMTP_PASS', '')
    sender = (cfg.get('MAIL_FROM')
              or cfg.get('CONTACT_EMAIL')
              or 'no-reply@prevozni.com')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    if list_unsubscribe:
        # Gmail's one-click POST + the legacy mailto/URL list. Both are
        # required: the POST header alone produces the dashboard button,
        # but Outlook 2019 and older Apple Mail still need the URL form.
        msg['List-Unsubscribe'] = f'<{list_unsubscribe}>'
        msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype='html')

    try:
        if port == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, timeout=15,
                                  context=ctx) as s:
                if user:
                    s.login(user, password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as s:
                s.ehlo()
                if port == 587:
                    s.starttls(context=ssl.create_default_context())
                    s.ehlo()
                if user:
                    s.login(user, password)
                s.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("SMTP send failed to %s: %s", to, exc)
        observability.capture_exception(
            exc, subsystem='smtp', host=host, port=port,
        )
        # Still write to dev log so the flow stays observable when SMTP
        # is temporarily broken — the user can replay from the log if needed.
        _append_dev_log(to, subject, text, html)
        return False


def _append_dev_log(to: str, subject: str, text: str,
                    html: str | None,
                    list_unsubscribe: str | None = None) -> bool:
    try:
        # MAIL_DEV_LOG_PATH lets the test suite keep its fixture mails out of
        # the real logs/mail_dev.log (it had grown to 8 MB of localhost:5000 noise).
        override = os.environ.get('MAIL_DEV_LOG_PATH')
        log_path = (Path(override) if override
                    else Path(current_app.root_path).parent / 'logs' / _DEV_LOG_FILENAME)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        with log_path.open('a', encoding='utf-8') as f:
            f.write(
                f"\n{'=' * 60}\n"
                f"{datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z  to={to}\n"
                f"subject: {subject}\n"
            )
            if list_unsubscribe:
                f.write(f"List-Unsubscribe: <{list_unsubscribe}>\n")
                f.write("List-Unsubscribe-Post: List-Unsubscribe=One-Click\n")
            f.write(f"\n{text}\n")
            if html:
                f.write(f"\n-- HTML --\n{html}\n")
        return True
    except OSError as exc:
        logger.error("mail dev-log write failed: %s", exc)
        return False

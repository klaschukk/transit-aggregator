"""Tiny cross-cutting notifier: Telegram if configured, log file otherwise.

Used by the reviews flow (moderation queue notifications + author
'approved' notices). Email-capable infra is deliberately out of scope —
when Mailgun/SMTP lands, add a sender here and keep callers unchanged.
"""
import logging
from pathlib import Path

from flask import current_app

logger = logging.getLogger(__name__)

_DEV_LOG_FILENAME = 'review_notifications.log'


def notify_admin(subject: str, body: str) -> None:
    """Notify operators about moderation events (new review, deletion request).
    Telegram if TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID are set, else append
    to logs/review_notifications.log so devs can tail it."""
    token = current_app.config.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID', '')
    msg = f"[Prevozni mod] {subject}\n\n{body}"
    if token and chat_id:
        try:
            import requests as req  # imported lazily — keeps test boot fast
            req.post(
                f'https://api.telegram.org/bot{token}/sendMessage',
                json={'chat_id': chat_id, 'text': msg[:3900]},
                timeout=5,
            )
            return
        except Exception as exc:  # network blip shouldn't break the request
            logger.warning("telegram notify failed: %s", exc)
    _append_dev_log('ADMIN', subject, body)


def notify_author(email: str, subject: str, body: str) -> None:
    """Placeholder for 'your review was approved' emails. No SMTP infra yet:
    in dev we log to review_notifications.log so you can verify the flow;
    in prod the log line goes to the same place and operators can reply
    manually from their inbox until Mailgun/SES is wired in."""
    _append_dev_log('AUTHOR:' + (email or '<no-email>'), subject, body)


def _append_dev_log(recipient: str, subject: str, body: str) -> None:
    try:
        root = Path(current_app.root_path).parent
        log_dir = root / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime, timezone
        with (log_dir / _DEV_LOG_FILENAME).open('a', encoding='utf-8') as f:
            f.write(
                f"\n{'=' * 60}\n"
                f"{datetime.now(timezone.utc).replace(tzinfo=None).isoformat()}Z  to={recipient}\n"
                f"subject: {subject}\n"
                f"{body}\n"
            )
    except OSError as exc:
        logger.warning("dev-log write failed: %s", exc)

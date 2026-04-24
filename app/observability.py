"""Thin Sentry wrapper — safe to import even when sentry_sdk isn't installed
or SENTRY_DSN is empty. All capture helpers turn into no-ops, so callers in
db.py / mailer.py / analytics_db.py don't need their own guards.

Why wrap instead of calling sentry_sdk directly:
  1. Dev/tests run without the DSN set; they shouldn't phone home or crash
     if the package is missing from a minimal venv.
  2. We apply one beforesend filter (bots, rate-limit noise) in a single
     place instead of scattering User-Agent checks around every capture
     site — the 5K/mo free-tier quota burns fast on bot traffic.
"""
from __future__ import annotations

import logging
import os
import re

logger = logging.getLogger(__name__)

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    _SDK_AVAILABLE = True
except ImportError:
    sentry_sdk = None  # type: ignore[assignment]
    FlaskIntegration = None  # type: ignore[assignment]
    LoggingIntegration = None  # type: ignore[assignment]
    _SDK_AVAILABLE = False

_initialised = False

# Matches the common User-Agent tokens major crawlers advertise. Errors
# triggered by bot traffic usually reflect weird query strings or stale
# URLs in their indexes — not real user-facing regressions — so we drop
# them before they eat the 5K/mo event quota.
_BOT_UA_RE = re.compile(
    r'bot|crawler|spider|slurp|bingpreview|facebookexternalhit|'
    r'pingdom|uptimerobot|googlebot|yandexbot|ahrefsbot|semrushbot',
    re.IGNORECASE,
)

# Exception/message fragments we never want in Sentry:
#   - flask-limiter's RateLimitExceeded is expected behaviour for abusive
#     clients, not a server error.
#   - DuckDB "database is locked" during the 2-second nightly restart window
#     is expected and non-actionable.
_IGNORED_MESSAGE_FRAGMENTS = (
    'Rate limit exceeded',
    'ratelimit_handler',
)


def _before_send(event, hint):
    """Sentry beforesend hook — returns None to drop the event."""
    exc_info = hint.get('exc_info') if hint else None
    if exc_info:
        exc_type, exc_val, _tb = exc_info
        exc_name = getattr(exc_type, '__name__', '') or ''
        if exc_name in ('RateLimitExceeded', 'TooManyRequests'):
            return None
        msg = str(exc_val) if exc_val else ''
        for frag in _IGNORED_MESSAGE_FRAGMENTS:
            if frag in msg:
                return None

    try:
        headers = (event.get('request') or {}).get('headers') or {}
        ua = headers.get('User-Agent') or headers.get('user-agent') or ''
    except (AttributeError, TypeError):
        ua = ''
    if ua and _BOT_UA_RE.search(ua):
        return None

    return event


def init_sentry(
    *,
    dsn: str,
    environment: str,
    release: str,
    traces_sample_rate: float = 0.1,
    flask: bool = True,
) -> bool:
    """Initialise the SDK once per process. Safe to call with empty DSN
    (no-op) or without sentry_sdk installed (logs a warning). Returns True
    if Sentry is now active."""
    global _initialised
    if _initialised:
        return True
    if not dsn:
        return False
    if not _SDK_AVAILABLE:
        logger.warning(
            "SENTRY_DSN is set but sentry_sdk isn't installed — skipping init."
        )
        return False

    integrations = []
    if flask and FlaskIntegration is not None:
        integrations.append(FlaskIntegration())
    if LoggingIntegration is not None:
        # Capture logger.error / logger.exception as Sentry events; info/debug
        # stay as breadcrumbs only.
        integrations.append(LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR,
        ))

    sentry_sdk.init(
        dsn=dsn,
        integrations=integrations,
        traces_sample_rate=traces_sample_rate,
        send_default_pii=False,  # GDPR — don't send IPs, cookies, form data
        release=release,
        environment=environment,
        before_send=_before_send,
        max_breadcrumbs=50,
    )
    _initialised = True
    logger.info(
        "Sentry initialised (env=%s release=%s traces=%.2f)",
        environment, release, traces_sample_rate,
    )
    return True


def init_from_env() -> bool:
    """Bootstrap Sentry for CLI scripts (nightly_refresh etc.) using env
    vars only — no Flask app context required."""
    dsn = os.environ.get('SENTRY_DSN', '').strip()
    if not dsn:
        return False
    return init_sentry(
        dsn=dsn,
        environment=os.environ.get('SENTRY_ENV') or 'production',
        release=os.environ.get('SENTRY_RELEASE') or 'script',
        traces_sample_rate=0.0,  # scripts don't need perf spans
        flask=False,
    )


def capture_exception(exc: BaseException | None = None, **tags) -> None:
    """No-op when SDK is missing or uninitialised."""
    if not _initialised or sentry_sdk is None:
        return
    with sentry_sdk.push_scope() as scope:
        for k, v in tags.items():
            scope.set_tag(k, str(v))
        sentry_sdk.capture_exception(exc)


def capture_message(message: str, level: str = 'error', **tags) -> None:
    if not _initialised or sentry_sdk is None:
        return
    with sentry_sdk.push_scope() as scope:
        for k, v in tags.items():
            scope.set_tag(k, str(v))
        sentry_sdk.capture_message(message, level=level)


def flush(timeout: float = 2.0) -> None:
    """Flush pending events — call before short-lived CLI scripts exit."""
    if not _initialised or sentry_sdk is None:
        return
    try:
        sentry_sdk.flush(timeout=timeout)
    except Exception:  # noqa: BLE001 — flush must never raise
        pass

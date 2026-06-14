"""Shared HTTP helper for scrapers — retry transient upstream failures.

Every scraper makes long sequences of calls to flaky third-party APIs
(busticket4, Overpass, gspns, srbvoz, polazak.rs). The call sites already
pass a ``timeout`` so a single hung request can't stall the whole run, but
none of them *retried*: one transient blip — connection reset, read timeout,
a 502/503 from an overloaded upstream — silently dropped whatever that call
was fetching (a city pair, a line, a batch of stops). Over 500+ sequential
requests that adds up to real, invisible data loss; a weekday intercity run
that loses 1% of pairs to network noise quietly starves BT4 checkout coverage.

``request_with_retry`` is the one place scrapers reach for when talking to an
upstream that might flake: it retries connection errors, timeouts and 429/5xx
responses with exponential backoff, while letting genuine client errors (4xx
other than 429) fail fast so a real bug isn't hidden behind pointless retries.
"""
import logging
import time

import requests

log = logging.getLogger(__name__)

# Transient server-side conditions worth retrying: rate-limit + 5xx.
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})

# Network-level failures that are routinely transient. ConnectionError covers
# resets/DNS hiccups, Timeout covers connect+read timeouts, ChunkedEncoding
# covers a truncated streamed body.
RETRYABLE_EXC = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.ChunkedEncodingError,
)


def request_with_retry(
    session,
    method,
    url,
    *,
    retries=3,
    backoff=1.0,
    backoff_factor=2.0,
    max_backoff=30.0,
    timeout=30,
    raise_for_status=True,
    sleep=time.sleep,
    **kwargs,
):
    """Issue ``session.request(method, url, ...)`` retrying transient failures.

    Retries on connection errors, timeouts and 429/5xx responses, sleeping
    ``min(backoff * backoff_factor**attempt, max_backoff)`` seconds between
    tries (exponential backoff). Non-retryable 4xx responses raise immediately
    via ``raise_for_status`` so real client bugs surface fast.

    Returns the final :class:`requests.Response` (``raise_for_status`` already
    called unless disabled), or re-raises the last network exception after
    exhausting ``retries`` extra attempts.

    ``sleep`` is injectable so tests don't actually wait.

    Args:
        session: a ``requests.Session`` (reused connections + cookies).
        method: HTTP verb, e.g. ``'GET'`` / ``'POST'``.
        retries: number of *extra* attempts after the first (3 → up to 4 calls).
        backoff: base delay in seconds before the first retry.
        backoff_factor: multiplier applied per subsequent retry.
        max_backoff: ceiling on a single sleep.
        timeout: per-request timeout passed straight to requests.
        raise_for_status: call ``resp.raise_for_status()`` before returning.
        **kwargs: forwarded to ``session.request`` (params, json, data, …).
    """
    last_exc = None
    for attempt in range(retries + 1):
        try:
            resp = session.request(method, url, timeout=timeout, **kwargs)
        except RETRYABLE_EXC as exc:
            last_exc = exc
            if attempt >= retries:
                log.error('%s %s failed after %d tries: %s',
                          method, url, attempt + 1, exc)
                raise
            delay = min(backoff * (backoff_factor ** attempt), max_backoff)
            log.warning('%s %s %s — retry %d/%d in %.1fs',
                        method, url, type(exc).__name__,
                        attempt + 1, retries, delay)
            sleep(delay)
            continue

        if resp.status_code in RETRY_STATUS and attempt < retries:
            delay = min(backoff * (backoff_factor ** attempt), max_backoff)
            log.warning('%s %s -> HTTP %d — retry %d/%d in %.1fs',
                        method, url, resp.status_code,
                        attempt + 1, retries, delay)
            sleep(delay)
            continue

        if raise_for_status:
            resp.raise_for_status()
        return resp

    # The loop always returns or raises; this guards a logic regression only.
    raise last_exc  # pragma: no cover


def get_with_retry(session, url, **kwargs):
    """``request_with_retry`` shorthand for GET."""
    return request_with_retry(session, 'GET', url, **kwargs)


def post_with_retry(session, url, **kwargs):
    """``request_with_retry`` shorthand for POST."""
    return request_with_retry(session, 'POST', url, **kwargs)

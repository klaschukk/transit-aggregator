"""Unit tests for the shared scraper retry helper (data/pipelines/http_util).

No real network: a fake session replays a queued script of responses /
exceptions, and sleep is stubbed so backoff is asserted, never waited on.
"""
import pytest
import requests

from data.pipelines import http_util
from data.pipelines.http_util import request_with_retry


class FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f'HTTP {self.status_code}')


class FakeSession:
    """Replays a queued script: FakeResponse is returned, an Exception is raised."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def sleeps():
    """Collect backoff delays instead of sleeping."""
    recorded = []
    return recorded


def _sleep_into(recorded):
    def _sleep(delay):
        recorded.append(delay)
    return _sleep


def test_success_first_try_no_sleep(sleeps):
    sess = FakeSession([FakeResponse(200)])
    resp = request_with_retry(sess, 'GET', 'http://x', sleep=_sleep_into(sleeps))
    assert resp.status_code == 200
    assert len(sess.calls) == 1
    assert sleeps == []  # no retry → no backoff


def test_retry_after_connection_error_then_success(sleeps):
    sess = FakeSession([
        requests.exceptions.ConnectionError('reset'),
        FakeResponse(200),
    ])
    resp = request_with_retry(sess, 'GET', 'http://x', sleep=_sleep_into(sleeps))
    assert resp.status_code == 200
    assert len(sess.calls) == 2
    assert sleeps == [1.0]  # one backoff at base delay


def test_retry_on_timeout(sleeps):
    sess = FakeSession([
        requests.exceptions.Timeout('read timed out'),
        FakeResponse(200),
    ])
    resp = request_with_retry(sess, 'POST', 'http://x', sleep=_sleep_into(sleeps))
    assert resp.status_code == 200
    assert len(sess.calls) == 2


def test_exhaust_retries_reraises_last_exception(sleeps):
    sess = FakeSession([requests.exceptions.ConnectionError('reset')] * 4)
    with pytest.raises(requests.exceptions.ConnectionError):
        request_with_retry(sess, 'GET', 'http://x', retries=3,
                           sleep=_sleep_into(sleeps))
    assert len(sess.calls) == 4          # 1 initial + 3 retries
    assert len(sleeps) == 3              # slept before each retry, not after the last


def test_retryable_status_then_success(sleeps):
    sess = FakeSession([FakeResponse(503), FakeResponse(200)])
    resp = request_with_retry(sess, 'GET', 'http://x', sleep=_sleep_into(sleeps))
    assert resp.status_code == 200
    assert len(sess.calls) == 2
    assert sleeps == [1.0]


def test_retryable_status_exhausted_raises_http_error(sleeps):
    sess = FakeSession([FakeResponse(502)] * 4)
    with pytest.raises(requests.exceptions.HTTPError):
        request_with_retry(sess, 'GET', 'http://x', retries=3,
                           sleep=_sleep_into(sleeps))
    assert len(sess.calls) == 4
    assert len(sleeps) == 3


def test_client_error_4xx_fails_fast_no_retry(sleeps):
    sess = FakeSession([FakeResponse(404)])
    with pytest.raises(requests.exceptions.HTTPError):
        request_with_retry(sess, 'GET', 'http://x', sleep=_sleep_into(sleeps))
    assert len(sess.calls) == 1   # 404 is not retryable
    assert sleeps == []


def test_429_is_retried(sleeps):
    sess = FakeSession([FakeResponse(429), FakeResponse(200)])
    resp = request_with_retry(sess, 'GET', 'http://x', sleep=_sleep_into(sleeps))
    assert resp.status_code == 200
    assert len(sess.calls) == 2


def test_exponential_backoff_schedule_and_cap(sleeps):
    sess = FakeSession([requests.exceptions.ConnectionError('x')] * 6)
    with pytest.raises(requests.exceptions.ConnectionError):
        request_with_retry(sess, 'GET', 'http://x', retries=5,
                           backoff=1.0, backoff_factor=2.0, max_backoff=10.0,
                           sleep=_sleep_into(sleeps))
    # 1, 2, 4, 8, then capped at 10 (would be 16)
    assert sleeps == [1.0, 2.0, 4.0, 8.0, 10.0]


def test_raise_for_status_false_returns_bad_response(sleeps):
    sess = FakeSession([FakeResponse(404)])
    resp = request_with_retry(sess, 'GET', 'http://x', raise_for_status=False,
                              sleep=_sleep_into(sleeps))
    assert resp.status_code == 404
    assert len(sess.calls) == 1


def test_kwargs_and_timeout_forwarded(sleeps):
    sess = FakeSession([FakeResponse(200)])
    request_with_retry(sess, 'POST', 'http://x', json={'a': 1}, timeout=15,
                       headers={'X': 'y'}, sleep=_sleep_into(sleeps))
    method, url, kwargs = sess.calls[0]
    assert method == 'POST'
    assert kwargs['json'] == {'a': 1}
    assert kwargs['timeout'] == 15
    assert kwargs['headers'] == {'X': 'y'}


def test_get_and_post_shortcuts(sleeps):
    sess = FakeSession([FakeResponse(200), FakeResponse(200)])
    http_util.get_with_retry(sess, 'http://x', sleep=_sleep_into(sleeps))
    http_util.post_with_retry(sess, 'http://x', sleep=_sleep_into(sleeps))
    assert sess.calls[0][0] == 'GET'
    assert sess.calls[1][0] == 'POST'

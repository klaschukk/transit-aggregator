"""Unit tests for scripts/bt4_sales_fetch.py — the BusTicket4 sales mirror.

No real network: a fake requests.Session feeds canned responses so we can
exercise the report parser, empty-report handling, and the retry/backoff
logic the hourly cron relies on (the docstring promises retries — these
tests make sure they exist)."""
import pytest
import requests

from scripts import bt4_sales_fetch as bsf


class FakeResp:
    """Minimal stand-in for requests.Response."""

    def __init__(self, *, json_data=None, status_code=200, url='', text=''):
        self._json = json_data
        self.status_code = status_code
        self.url = url
        self.text = text

    def json(self):
        if isinstance(self._json, Exception):
            raise self._json
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'{self.status_code} error', response=self)


class FakeSession:
    """Serves a fixed response (or raises) per .request() call, counting hits.

    Pass `sequence` to vary the response across calls (for retry tests)."""

    def __init__(self, resp=None, *, raises=None, sequence=None):
        self.resp = resp
        self.raises = raises
        self.sequence = list(sequence) if sequence else None
        self.calls = 0
        self.headers = {}

    def request(self, method, url, **kw):
        self.calls += 1
        if self.sequence is not None:
            item = self.sequence.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        if self.raises is not None:
            raise self.raises
        return self.resp


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Never actually sleep during retry backoff — keeps the suite fast."""
    monkeypatch.setattr(bsf.time, 'sleep', lambda *_a, **_k: None)


def _series(days, tickets, values):
    return [
        {'name': 'Dani', 'data': days},
        {'name': 'Broj karata', 'data': tickets},
        {'name': 'Vrijednost', 'data': values},
    ]


# ── _to_ymd parser ──────────────────────────────────────────────────


@pytest.mark.parametrize('raw,expected', [
    (13, '2026-06-13'),
    ('13', '2026-06-13'),
    ('13.06', '2026-06-13'),
    ('13.06.2026', '2026-06-13'),
    ('2026-06-13', '2026-06-13'),
    ('2026-06-13T00:00:00', '2026-06-13'),
])
def test_to_ymd_accepts_known_formats(raw, expected):
    assert bsf._to_ymd(raw, 2026, 6) == expected


@pytest.mark.parametrize('raw', ['', '   ', 'garbage', 0, 99])
def test_to_ymd_rejects_junk(raw):
    assert bsf._to_ymd(raw, 2026, 6) is None


# ── _fetch_month report parsing ─────────────────────────────────────


def test_fetch_month_parses_rows():
    resp = FakeResp(json_data=_series(
        ['01.06.2026', '02.06.2026'], [2, 5], [1600.0, 4000.0]))
    rows = bsf._fetch_month(FakeSession(resp), '735', 2026, 6)
    assert rows == [
        {'ymd': '2026-06-01', 'tickets': 2, 'value': 1600.0},
        {'ymd': '2026-06-02', 'tickets': 5, 'value': 4000.0},
    ]


def test_fetch_month_empty_report_returns_no_rows():
    # The panel emits the 3 series but omits "data" keys when there are no sales.
    resp = FakeResp(json_data=[{'name': 'Dani'}, {'name': 'Broj karata'},
                               {'name': 'Vrijednost'}])
    assert bsf._fetch_month(FakeSession(resp), '735', 2026, 6) == []


@pytest.mark.parametrize('payload', [None, [], [{'name': 'Dani'}], {'x': 1}])
def test_fetch_month_malformed_payload_returns_no_rows(payload):
    resp = FakeResp(json_data=payload)
    assert bsf._fetch_month(FakeSession(resp), '735', 2026, 6) == []


def test_fetch_month_tolerates_short_value_series():
    # tickets/values shorter than days -> missing entries default to 0.
    resp = FakeResp(json_data=_series(['01.06.2026', '02.06.2026'], [3], []))
    rows = bsf._fetch_month(FakeSession(resp), '735', 2026, 6)
    assert rows[0] == {'ymd': '2026-06-01', 'tickets': 3, 'value': 0.0}
    assert rows[1] == {'ymd': '2026-06-02', 'tickets': 0, 'value': 0.0}


# ── _request retry / backoff ────────────────────────────────────────


def test_request_retries_then_succeeds():
    ok = FakeResp(status_code=200, url='ok')
    sess = FakeSession(sequence=[requests.ConnectionError('boom'),
                                 requests.ConnectionError('boom2'), ok])
    assert bsf._request(sess, 'GET', 'http://x', timeout=1) is ok
    assert sess.calls == 3


def test_request_gives_up_after_attempts():
    sess = FakeSession(raises=requests.ConnectionError('always'))
    with pytest.raises(requests.ConnectionError):
        bsf._request(sess, 'GET', 'http://x', timeout=1)
    assert sess.calls == bsf.RETRY_ATTEMPTS


def test_request_retries_on_5xx_then_returns_200():
    sess = FakeSession(sequence=[FakeResp(status_code=503),
                                 FakeResp(status_code=200, url='ok')])
    resp = bsf._request(sess, 'GET', 'http://x', timeout=1)
    assert resp.status_code == 200
    assert sess.calls == 2


def test_request_does_not_retry_4xx():
    four = FakeResp(status_code=404)
    sess = FakeSession(four)
    assert bsf._request(sess, 'GET', 'http://x', timeout=1) is four
    assert sess.calls == 1


# ── _login success / failure detection ──────────────────────────────


def test_login_success_detected():
    ok = FakeResp(status_code=200,
                  url='https://busticket4.me/bus/pocetna-p.php?pred=735x')
    assert bsf._login(FakeSession(ok), 'u', 'p') is True


def test_login_failure_detected():
    bad = FakeResp(status_code=200,
                   url='https://busticket4.me/bus/pocetna.php', text='wrong')
    assert bsf._login(FakeSession(bad), 'u', 'p') is False

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


def _row(tx, ticket, price, pct, dt):
    """Build one affiliate-sales transaction row matching the live panel."""
    n = abs(hash((tx, ticket))) % 10**8
    return (
        f'<tr id="tr_{n}"> '
        f'<td id="id_{n}">{n}</td> '
        f'<td id="broj_tansakcije_{n}">{tx}</td> '
        f'<td id="broj_{n}">{ticket}</td> '
        f'<td id="cijena_{n}">{price}</td> '
        f'<td id="valuta_id_naziv_{n}">Dinar</td> '
        f'<td id="affiliate_procenat_{n}">{pct}</td> '
        f'<td id="dazur_{n}">{dt}</td> </tr>'
    )


def _report(*rows):
    return '<table>' + ''.join(rows) + '</table>'


# ── _to_float parser ────────────────────────────────────────────────


@pytest.mark.parametrize('raw,expected', [
    ('1000.00', 1000.0),
    ('1.000,00', 1000.0),    # European thousands + decimal comma
    ('1000,00', 1000.0),
    ('2.00', 2.0),
    ('  500.50  ', 500.5),
    ('garbage', 0.0),
    ('', 0.0),
])
def test_to_float(raw, expected):
    assert bsf._to_float(raw) == expected


# ── _fetch_period report parsing ────────────────────────────────────


def test_fetch_period_aggregates_by_day_and_commission():
    html = _report(
        _row('TX1', '111', '1000.00', '2.00', '16.06.2026 09:47:58'),
        _row('TX2', '222', '1500.00', '2.00', '16.06.2026 14:00:00'),
        _row('TX3', '333', '800.00', '2.00', '17.06.2026 08:00:00'),
    )
    rows, commission = bsf._fetch_period(
        FakeSession(FakeResp(text=html)), '735', '01.06.2026', '30.06.2026')
    by_day = {r['ymd']: r for r in rows}
    assert by_day['2026-06-16'] == {'ymd': '2026-06-16', 'tickets': 2, 'value': 2500.0}
    assert by_day['2026-06-17'] == {'ymd': '2026-06-17', 'tickets': 1, 'value': 800.0}
    assert commission == pytest.approx((1000 + 1500 + 800) * 0.02)


def test_fetch_period_empty_report_returns_no_rows():
    rows, commission = bsf._fetch_period(
        FakeSession(FakeResp(text='<table></table>')), '735',
        '01.06.2026', '30.06.2026')
    assert rows == [] and commission == 0.0


def test_fetch_period_skips_malformed_rows():
    # A row missing its price or date must be skipped, not crash the run.
    bad = '<tr id="tr_9"><td id="broj_9">x</td></tr>'
    html = _report(bad, _row('TX', '1', '600.00', '2.00', '10.06.2026 10:00:00'))
    rows, _ = bsf._fetch_period(
        FakeSession(FakeResp(text=html)), '735', '01.06.2026', '30.06.2026')
    assert rows == [{'ymd': '2026-06-10', 'tickets': 1, 'value': 600.0}]


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

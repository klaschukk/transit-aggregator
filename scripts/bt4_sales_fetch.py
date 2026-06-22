"""Mirror BusTicket4 affiliate SALES into our analytics DB (bt4_sales table).

BusTicket4's own affiliate panel (busticket4.me/bus) is flaky, so we pull the
daily sales report for our affiliate (735 / prevozni.com) and store it locally,
where /admin/revenue can show it cleanly. Designed for an HOURLY cron — sales
change rarely, and logging into their panel 24×/day is already plenty (every
5 min would be 288 logins/day and risks their server flagging the account).

Login + report endpoints were reverse-engineered from the panel:
    POST  /bus/pocetna.php           username, password, submit
    POST  /bus/karte/prod_karata_period_affiliate.php
          data: affiliate=735, datum_od=DD.MM.YYYY, datum_do=DD.MM.YYYY
          -> HTML table, one <tr id="tr_NNN"> per sold ticket, with
             cijena_NNN (price), affiliate_procenat_NNN (%), dazur_NNN (datetime).

NOTE (2026-06-22): the old endpoint izvjestaji/podaci_o_kartama.php (a daily
chart) returned EMPTY even when sales existed — the real per-affiliate sales
report is karte/prod_karata_period_affiliate.php. That bug is why the mirror
showed 0 while the panel had a confirmed sale (16.06.2026, 1000 RSD, 20 RSD
commission). This script now reads the correct report.

Env:
    BT4_PANEL_USER, BT4_PANEL_PASS  — panel login (no default; required).
    ANALYTICS_DB_PATH               — sqlite path (from app config).
    BT4_AFFILIATE_ID                — defaults to 735.

Exit codes:
    0  success (rows upserted, possibly zero)
    2  credentials missing -> cron-safe skip
    3  login / fetch / parse error after retries
"""
from __future__ import annotations

import logging
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger('bt4_sales_fetch')

BASE = 'https://busticket4.me/bus'
LOGIN_URL = f'{BASE}/pocetna.php'
SALES_URL = f'{BASE}/karte/prod_karata_period_affiliate.php'

# One transaction row in the affiliate sales table; we pull price, % and date.
_ROW_RE = re.compile(r'<tr[^>]*id="tr_\d+".*?</tr>', re.S)
_CIJENA_RE = re.compile(r'id="cijena_\d+"[^>]*>\s*([\d.,]+)', re.S)
_PCT_RE = re.compile(r'id="affiliate_procenat_\d+"[^>]*>\s*([\d.,]+)', re.S)
_DATE_RE = re.compile(r'id="dazur_\d+"[^>]*>\s*(\d{2})\.(\d{2})\.(\d{4})', re.S)


def _to_float(raw: str) -> float:
    """Parse a price/percent that may be plain (1000.00) or European
    (1.000,00). Returns 0.0 on garbage rather than raising."""
    s = raw.strip()
    if ',' in s and '.' in s:          # 1.000,00 -> 1000.00
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:                     # 1000,00 -> 1000.00
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Prevozni-Affiliate/1.0'

# Their panel is flaky, so every HTTP hit gets a few backoff retries before we
# give up and bail (exit 3) — a transient blip shouldn't lose an hourly run.
RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 2.0  # seconds; exponential: 2s, 4s, ...


def _request(session: requests.Session, method: str, url: str, **kw):
    """One HTTP call with exponential-backoff retries on transient failures.

    Retries network errors (timeouts, connection resets) and 5xx server
    responses; a 4xx is returned as-is so the caller decides (our request is
    wrong, retrying won't help). Re-raises the last RequestException once all
    attempts are spent so main() can map it to exit code 3."""
    last_exc: Exception | None = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            resp = session.request(method, url, **kw)
            if resp.status_code >= 500:
                raise requests.HTTPError(
                    f'{resp.status_code} server error', response=resp)
            return resp
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < RETRY_ATTEMPTS:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                log.warning('%s %s failed (attempt %d/%d): %s — retry in %.0fs',
                            method, url, attempt, RETRY_ATTEMPTS, exc, delay)
                time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def _login(session: requests.Session, user: str, pw: str) -> bool:
    """Authenticate the session. Returns True if the affiliate landing loaded."""
    session.headers['User-Agent'] = UA
    _request(session, 'GET', f'{BASE}/index.php?s=2', timeout=30)  # seed PHPSESSID
    resp = _request(
        session, 'POST', LOGIN_URL,
        data={'username': user, 'password': pw, 'submit': 'Prijavi se'},
        headers={'Referer': f'{BASE}/index.php?s=2'},
        timeout=30,
    )
    # On success the panel redirects to pocetna-p.php?pred=735x<affiliate-domain>.
    ok = 'pocetna-p.php' in resp.url or 'Odjavi' in resp.text
    if not ok:
        log.error('login failed (landed on %s)', resp.url)
    return ok


def _fetch_period(session: requests.Session, aff_id: str,
                  datum_od: str, datum_do: str) -> tuple[list[dict], float]:
    """POST the affiliate sales report for a date range and aggregate the
    per-ticket rows by day. Returns ([{ymd, tickets, value}], total_commission).
    Empty list when there were no sales (that's a valid result, not an error)."""
    r = _request(session, 'POST', SALES_URL,
                 data={'affiliate': aff_id, 'datum_od': datum_od, 'datum_do': datum_do},
                 headers={'Referer': SALES_URL}, timeout=60)
    r.raise_for_status()
    html = r.text
    by_day: dict[str, dict] = {}
    total_commission = 0.0
    for tr in _ROW_RE.findall(html):
        m_price = _CIJENA_RE.search(tr)
        m_date = _DATE_RE.search(tr)
        if not m_price or not m_date:
            continue
        price = _to_float(m_price.group(1))
        pct = _to_float(m_pct.group(1)) if (m_pct := _PCT_RE.search(tr)) else 0.0
        dd, mm, yyyy = m_date.groups()
        ymd = f'{yyyy}-{mm}-{dd}'
        slot = by_day.setdefault(ymd, {'ymd': ymd, 'tickets': 0, 'value': 0.0})
        slot['tickets'] += 1
        slot['value'] += price
        total_commission += price * pct / 100.0
    return list(by_day.values()), total_commission


def main() -> int:
    user = os.environ.get('BT4_PANEL_USER', '').strip()
    pw = os.environ.get('BT4_PANEL_PASS', '').strip()
    aff_id = os.environ.get('BT4_AFFILIATE_ID', '735').strip()
    if not user or not pw:
        log.warning('BT4_PANEL_USER/BT4_PANEL_PASS not set — skipping (cron-safe).')
        return 2

    # Cover this month + the previous one (first day of last month → today), so
    # a sale near a month boundary is never missed. The panel wants DD.MM.YYYY.
    today = date.today()
    first_of_this = today.replace(day=1)
    last_month = 12 if first_of_this.month == 1 else first_of_this.month - 1
    last_year = first_of_this.year - 1 if first_of_this.month == 1 else first_of_this.year
    datum_od = f'01.{last_month:02d}.{last_year}'
    datum_do = today.strftime('%d.%m.%Y')

    session = requests.Session()
    try:
        if not _login(session, user, pw):
            return 3
        rows, commission = _fetch_period(session, aff_id, datum_od, datum_do)
    except (requests.RequestException, ValueError) as exc:
        log.error('fetch failed: %s', exc)
        return 3

    from app import create_app
    from app import analytics_db
    app = create_app()
    with app.app_context():
        analytics_db.init_schema()
        n = analytics_db.upsert_bt4_sales(rows)
    total_t = sum(r['tickets'] for r in rows)
    total_v = sum(r['value'] for r in rows)
    log.info('bt4_sales: %d day-rows upserted | %d tickets, %.2f value, '
             '%.2f commission (%s..%s)',
             n, total_t, total_v, commission, datum_od, datum_do)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

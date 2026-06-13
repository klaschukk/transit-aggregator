"""Mirror BusTicket4 affiliate SALES into our analytics DB (bt4_sales table).

BusTicket4's own affiliate panel (busticket4.me/bus) is flaky, so we pull the
daily sales report for our affiliate (735 / prevozni.com) and store it locally,
where /admin/revenue can show it cleanly. Designed for an HOURLY cron — sales
change rarely, and logging into their panel 24×/day is already plenty (every
5 min would be 288 logins/day and risks their server flagging the account).

Login + report endpoints were reverse-engineered from the panel:
    POST  /bus/pocetna.php           username, password, submit
    GET   /bus/izvjestaji/podaci_o_kartama.php?preduzece=735&godina=Y&mjesec=M
          -> JSON [{name:Dani,data:[...]},{name:Broj karata,data:[...]},
                   {name:Vrijednost,data:[...]}]  (no "data" keys when empty)

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
DATA_URL = f'{BASE}/izvjestaji/podaci_o_kartama.php'
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


def _fetch_month(session: requests.Session, aff_id: str, year: int, month: int) -> list[dict]:
    """Return [{ymd, tickets, value}] for one month (empty if no sales)."""
    params = {
        'preduzece': aff_id, 'prevoznik': '', 'linija': '', 'vrstakarte': '',
        'datumpretrage': '', 'preduzeceProdaje': '', 'godina': year,
        'mjesec': month, 'valutaProdaje': '',
    }
    r = _request(session, 'GET', DATA_URL, params=params,
                 headers={'Referer': f'{BASE}/izvjestaji/prodaja_karata_po_danima.php'},
                 timeout=30)
    r.raise_for_status()
    series = r.json()
    if not isinstance(series, list) or len(series) < 3:
        return []
    days = series[0].get('data') or []
    tickets = series[1].get('data') or []
    values = series[2].get('data') or []
    rows: list[dict] = []
    for i, raw_day in enumerate(days):
        ymd = _to_ymd(raw_day, year, month)
        if not ymd:
            continue
        rows.append({
            'ymd': ymd,
            'tickets': int(tickets[i]) if i < len(tickets) and tickets[i] is not None else 0,
            'value': float(values[i]) if i < len(values) and values[i] is not None else 0.0,
        })
    return rows


def _to_ymd(raw_day, year: int, month: int) -> str | None:
    """Normalise a 'Dani' label to 'YYYY-MM-DD'. Accepts a day number, a
    'DD.MM.YYYY'/'DD.MM' string, or an ISO date — whatever the panel emits."""
    s = str(raw_day).strip()
    if not s:
        return None
    if '-' in s and len(s) >= 8:          # already ISO-ish
        return s[:10]
    if '.' in s:                          # DD.MM(.YYYY)
        parts = [p for p in s.replace(' ', '').split('.') if p]
        try:
            d = int(parts[0]); m = int(parts[1]) if len(parts) > 1 else month
            y = int(parts[2]) if len(parts) > 2 and len(parts[2]) == 4 else year
            return f'{y:04d}-{m:02d}-{d:02d}'
        except (ValueError, IndexError):
            return None
    try:                                  # bare day-of-month
        d = int(float(s))
        if 1 <= d <= 31:
            return f'{year:04d}-{month:02d}-{d:02d}'
    except ValueError:
        pass
    return None


def main() -> int:
    user = os.environ.get('BT4_PANEL_USER', '').strip()
    pw = os.environ.get('BT4_PANEL_PASS', '').strip()
    aff_id = os.environ.get('BT4_AFFILIATE_ID', '735').strip()
    if not user or not pw:
        log.warning('BT4_PANEL_USER/BT4_PANEL_PASS not set — skipping (cron-safe).')
        return 2

    today = date.today()
    months = {(today.year, today.month)}
    # Also refresh the previous month for the first days of a new month.
    prev = (today.replace(day=1))
    prev_month = 12 if prev.month == 1 else prev.month - 1
    prev_year = prev.year - 1 if prev.month == 1 else prev.year
    months.add((prev_year, prev_month))

    session = requests.Session()
    try:
        if not _login(session, user, pw):
            return 3
        rows: list[dict] = []
        for y, m in sorted(months):
            rows.extend(_fetch_month(session, aff_id, y, m))
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
    log.info('bt4_sales: upserted %d day-rows, %d tickets total across %d month(s)',
             n, total_t, len(months))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

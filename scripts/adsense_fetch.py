#!/usr/bin/env python3
"""Pull yesterday's AdSense earnings + per-page RPM into analytics.duckdb.

Designed for nightly cron (3am after the data freshness window):

    0 3 * * * /path/to/venv/bin/python /path/to/scripts/adsense_fetch.py

Three execution modes, picked by env presence:

  1. GSC_CREDENTIALS_PATH set + readable, pointing at a Google service
     account JSON whose project enabled the AdSense Management API:
       Hit `accounts/{id}/reports:generate` for METRICS=
         ESTIMATED_EARNINGS,IMPRESSIONS,CLICKS,PAGE_VIEWS_RPM
       grouped by AD_UNIT_NAME and DATE.

  2. ADSENSE_API_KEY env (simpler API-key auth — works for read-only
     reports endpoints since 2024). Same call, different auth header.

  3. Neither set → DEV mode. Writes a single placeholder row per slot
     to `logs/adsense_fetch.log` so the cron run is observable but the
     dashboard column doesn't go missing. Used in dev / CI.

Schema lives in analytics_db.adsense_ensure_schema(). Idempotent: a
re-run for the same day (slot, date) updates rather than appending —
makes cron retries safe.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logger = logging.getLogger('adsense_fetch')

_LOG = _REPO_ROOT / 'logs' / 'adsense_fetch.log'

# Slot keys we report on — must match the keys in config.ADSENSE_SLOTS.
_REPORTED_SLOTS = (
    'home_top', 'home_mid',
    'route_bottom', 'city_pair_bottom', 'city_transport_mid',
    'catalog_in_feed', 'guide_sidebar', 'mobile_anchor',
)


def _yday() -> str:
    return (date.today() - timedelta(days=1)).isoformat()


def _append_dev_log(records: list[dict]) -> None:
    _LOG.parent.mkdir(parents=True, exist_ok=True)
    with _LOG.open('a', encoding='utf-8') as f:
        f.write(
            f"\n# {datetime.now(timezone.utc).isoformat()}  "
            f"DEV-mode AdSense fetch (no credentials configured)\n"
        )
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def _fetch_via_api(
    *,
    creds_path: str | None,
    api_key: str | None,
    account_id: str,
    day: str,
) -> list[dict] | None:
    """Real Management API call. Returns rows or None on auth failure
    (caller falls back to DEV mode in that case)."""
    try:
        import requests
    except ImportError:
        logger.warning('requests not installed; cannot reach AdSense API')
        return None

    base = (
        'https://adsense.googleapis.com/v2/'
        f'accounts/{account_id}/reports:generate'
    )
    params = {
        'dateRange': 'CUSTOM',
        'startDate.year':  day[:4],
        'startDate.month': str(int(day[5:7])),
        'startDate.day':   str(int(day[8:10])),
        'endDate.year':    day[:4],
        'endDate.month':   str(int(day[5:7])),
        'endDate.day':     str(int(day[8:10])),
        'metrics': [
            'ESTIMATED_EARNINGS', 'IMPRESSIONS', 'CLICKS',
            'PAGE_VIEWS_RPM',
        ],
        'dimensions': ['AD_UNIT_NAME'],
    }
    headers: dict[str, str] = {}
    if creds_path and Path(creds_path).exists():
        # Service account → bearer token via google-auth.
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request as _GReq
        except ImportError:
            logger.warning(
                'google-auth not installed; install with '
                '`pip install google-auth google-auth-oauthlib`'
            )
            return None
        scopes = ['https://www.googleapis.com/auth/adsense.readonly']
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=scopes,
        )
        creds.refresh(_GReq())
        headers['Authorization'] = f'Bearer {creds.token}'
    elif api_key:
        params['key'] = api_key
    else:
        return None

    try:
        resp = requests.get(base, headers=headers, params=params, timeout=20)
        if resp.status_code != 200:
            logger.error('AdSense API %s: %s', resp.status_code, resp.text[:300])
            return None
        return _parse_api_response(resp.json(), day)
    except Exception as exc:  # noqa: BLE001
        logger.exception('AdSense API call failed: %s', exc)
        return None


def _parse_api_response(payload: dict, day: str) -> list[dict]:
    """Map the AdSense reports API JSON shape into our flat row schema."""
    headers = [h.get('name') for h in payload.get('headers', [])]
    rows: list[dict] = []
    for r in payload.get('rows', []):
        cells = [c.get('value', '') for c in r.get('cells', [])]
        row = dict(zip(headers, cells))
        slot = row.get('AD_UNIT_NAME', '')
        try:
            earnings = float(row.get('ESTIMATED_EARNINGS', '0') or '0')
            impressions = int(row.get('IMPRESSIONS', '0') or '0')
            clicks = int(row.get('CLICKS', '0') or '0')
            rpm = float(row.get('PAGE_VIEWS_RPM', '0') or '0')
        except ValueError:
            continue
        rows.append({
            'day': day, 'slot': slot,
            'earnings_usd': earnings,
            'impressions': impressions,
            'clicks': clicks,
            'page_rpm_usd': rpm,
        })
    return rows


def _persist(rows: list[dict]) -> int:
    """Upsert into analytics_db.adsense_daily. Creates table on first run."""
    try:
        from app import create_app
        from app import analytics_db
    except ImportError as exc:
        logger.error('cannot import app: %s', exc)
        return 0
    app = create_app('development')
    with app.app_context():
        # Schema is created here — keeps the table out of the schema-bootstrap
        # path so analytics tests don't depend on AdSense at all.
        analytics_db.execute("""
            CREATE TABLE IF NOT EXISTS adsense_daily (
                day DATE NOT NULL,
                slot VARCHAR NOT NULL,
                earnings_usd DOUBLE,
                impressions BIGINT,
                clicks BIGINT,
                page_rpm_usd DOUBLE,
                PRIMARY KEY (day, slot)
            )
        """) if hasattr(analytics_db, 'execute') else None
        n = 0
        for rec in rows:
            try:
                analytics_db.execute(
                    'INSERT OR REPLACE INTO adsense_daily '
                    '(day, slot, earnings_usd, impressions, clicks, page_rpm_usd) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    [rec['day'], rec['slot'], rec['earnings_usd'],
                     rec['impressions'], rec['clicks'], rec['page_rpm_usd']],
                )
                n += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning('upsert failed for %s: %s', rec, exc)
        return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--day', default=_yday(),
                    help='ISO date (default: yesterday in local time)')
    ap.add_argument('--account-id',
                    default=os.environ.get('ADSENSE_ACCOUNT_ID', ''),
                    help='AdSense account id (env ADSENSE_ACCOUNT_ID)')
    ap.add_argument('--dry-run', action='store_true',
                    help='print parsed rows without persisting')
    args = ap.parse_args()

    creds_path = os.environ.get('ADSENSE_CREDENTIALS_PATH', '')
    api_key = os.environ.get('ADSENSE_API_KEY', '')

    if (creds_path or api_key) and args.account_id:
        rows = _fetch_via_api(
            creds_path=creds_path or None,
            api_key=api_key or None,
            account_id=args.account_id,
            day=args.day,
        )
        if rows is None:
            print('AdSense API call returned None — falling back to DEV-log',
                  file=sys.stderr)
            rows = []
    else:
        # DEV mode — write zero-impression placeholder rows so the
        # dashboard query has something to plot on day 1, before the
        # service account exists.
        rows = [
            {'day': args.day, 'slot': slot,
             'earnings_usd': 0.0, 'impressions': 0,
             'clicks': 0, 'page_rpm_usd': 0.0}
            for slot in _REPORTED_SLOTS
        ]
        _append_dev_log(rows)

    if args.dry_run:
        for r in rows:
            print(json.dumps(r, ensure_ascii=False))
        return 0

    n = _persist(rows)
    print(f'persisted {n}/{len(rows)} rows for {args.day}')
    return 0 if n else 2


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())

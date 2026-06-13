"""Bookaway / TUNE (HasOffers) affiliate API client.

Read-only wrapper over the affiliate-side Apiv3 endpoint. Used by the admin
revenue dashboard to show real clicks, conversions and payout next to our own
click logging (the `ba_clicks` table only knows about clicks that left our
site — it can't see whether the user actually bought).

Design notes:
- Server-side only. The API key is a secret; it never reaches a template or
  the browser. Config pulls it from the BOOKAWAY_API_KEY env var.
- Every public function degrades gracefully: on a missing key, network error,
  timeout or non-1 API status it returns an empty/zero structure and never
  raises, so a flaky affiliate API can't take down the admin page.
- Responses are cached in-process for CACHE_TTL seconds. The dashboard is
  low-traffic but the API is rate-limited, so we avoid a live call on every
  page refresh.
"""
from __future__ import annotations

import json as _json
import time
import urllib.parse
import urllib.request

from flask import current_app

CACHE_TTL = 900  # 15 min — affiliate stats update slowly; spare the rate limit.
_TIMEOUT = 20

# Module-level cache: {cache_key: (expires_at, value)}. Per gunicorn worker,
# which is fine — at most a handful of stale-by-15-min reads per worker.
_cache: dict[str, tuple[float, object]] = {}


def _cfg() -> tuple[str, str]:
    return (
        current_app.config.get('BOOKAWAY_API_KEY', ''),
        current_app.config.get('BOOKAWAY_NETWORK_ID', 'bookaway2'),
    )


def is_enabled() -> bool:
    """True when an API key is configured — gates the whole dashboard section."""
    return bool(current_app.config.get('BOOKAWAY_API_KEY', ''))


def _call(target: str, method: str, **params) -> dict | None:
    """One Apiv3 GET. Returns the parsed `response.data` on success, else None."""
    key, net = _cfg()
    if not key:
        return None
    q = {'NetworkId': net, 'Target': target, 'Method': method, 'api_key': key}
    q.update(params)
    url = f'https://{net}.api.hasoffers.com/Apiv3/json?' + urllib.parse.urlencode(q, doseq=True)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'PrevozniAdmin/1.0'})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            body = _json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None
    response = body.get('response') or {}
    if response.get('status') != 1:
        return None
    return response.get('data') or {}


def _cached(cache_key: str, producer):
    now = time.time()
    hit = _cache.get(cache_key)
    if hit and hit[0] > now:
        return hit[1]
    value = producer()
    _cache[cache_key] = (now + CACHE_TTL, value)
    return value


def _to_float(v) -> float:
    try:
        return round(float(v), 2)
    except (TypeError, ValueError):
        return 0.0


def _to_int(v) -> int:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def get_offers() -> list[dict]:
    """Offers available to this affiliate (id, name, payout, status)."""
    def _p():
        data = _call('Affiliate_Offer', 'findAll', limit=50)
        rows = (data or {}).get('data') if isinstance(data, dict) else None
        out = []
        if isinstance(rows, dict):
            for entry in rows.values():
                o = entry.get('Offer', entry) if isinstance(entry, dict) else {}
                out.append({
                    'id': o.get('id'),
                    'name': o.get('name', ''),
                    'payout': o.get('default_payout', ''),
                    'payout_type': o.get('payout_type', ''),
                    'status': o.get('status', ''),
                })
        return out
    return _cached('offers', _p)


def get_summary(start: str, end: str) -> dict:
    """Totals for the window: clicks, conversions, payout, derived CR/EPC."""
    def _p():
        data = _call(
            'Affiliate_Report', 'getStats',
            **{'fields[]': ['Stat.clicks', 'Stat.conversions', 'Stat.payout'],
               'data_start': start, 'data_end': end, 'totals': '1'},
        )
        stat = ((data or {}).get('totals') or {}).get('Stat') or {}
        clicks = _to_int(stat.get('clicks'))
        conversions = _to_int(stat.get('conversions'))
        payout = _to_float(stat.get('payout'))
        return {
            'clicks': clicks,
            'conversions': conversions,
            'payout': payout,
            'cr': round(100 * conversions / clicks, 2) if clicks else 0.0,
            'epc': round(payout / clicks, 4) if clicks else 0.0,
        }
    return _cached(f'summary:{start}:{end}', _p)


def get_daily(start: str, end: str) -> list[dict]:
    """Per-day clicks/conversions/payout, ascending by date."""
    def _p():
        data = _call(
            'Affiliate_Report', 'getStats',
            **{'fields[]': ['Stat.date', 'Stat.clicks', 'Stat.conversions', 'Stat.payout'],
               'groups[]': ['Stat.date'], 'sort[Stat.date]': 'asc',
               'data_start': start, 'data_end': end, 'limit': '500'},
        )
        rows = (data or {}).get('data') if isinstance(data, dict) else None
        out = []
        if isinstance(rows, list):
            for entry in rows:
                stat = (entry or {}).get('Stat') or {}
                out.append({
                    'day': stat.get('date', ''),
                    'clicks': _to_int(stat.get('clicks')),
                    'conversions': _to_int(stat.get('conversions')),
                    'payout': _to_float(stat.get('payout')),
                })
        return out
    return _cached(f'daily:{start}:{end}', _p)


def get_dashboard(days: int = 30) -> dict | None:
    """Everything the admin revenue page needs, or None when disabled/unreachable."""
    if not is_enabled():
        return None
    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=days)
    s, e = start.isoformat(), end.isoformat()
    summary = get_summary(s, e)
    daily = get_daily(s, e)
    max_payout = max((d['payout'] for d in daily), default=0) or 0
    max_clicks = max((d['clicks'] for d in daily), default=1) or 1
    for d in daily:
        d['payout_pct'] = int((d['payout'] / max_payout) * 100) if max_payout else 0
        d['clicks_pct'] = int((d['clicks'] / max_clicks) * 100)
    return {
        'summary': summary,
        'daily': daily,
        'offers': get_offers(),
        'window_days': days,
        'start': s,
        'end': e,
    }

"""
Google Search Console data fetcher.

Pulls the last 7 and 28 days of search analytics for prevozni.com
and writes a single JSON snapshot into data/gsc/YYYY-MM-DD.json.

Runs weekly (see scripts/weekly_seo.sh). Safe to run manually.

Env:
    GSC_CREDENTIALS_PATH   path to service account JSON (default
                           /home/klaschuk/.gsc-credentials.json)
    GSC_SITE_URL           target property (default sc-domain:prevozni.com)

Exit codes:
    0 — success (JSON written)
    2 — credentials missing / unreadable (non-fatal for cron: skipped)
    3 — API error that did not recover after retries
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

log = logging.getLogger("gsc_fetch")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "gsc"
DEFAULT_CREDS = "/home/klaschuk/.gsc-credentials.json"
DEFAULT_SITE = "sc-domain:prevozni.com"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

ROW_LIMIT = 50
BACKOFF_SECS = (2, 5, 15)


def _date_range(end: date, days: int) -> tuple[str, str]:
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


def _call_with_backoff(request_fn, label: str):
    """Retry wrapper for transient GSC API errors (429 / 5xx)."""
    from googleapiclient.errors import HttpError
    last_exc: Exception | None = None
    for attempt, delay in enumerate((0, *BACKOFF_SECS)):
        if delay:
            log.warning("retry %s in %ss (%s)", label, delay, last_exc)
            time.sleep(delay)
        try:
            return request_fn()
        except HttpError as exc:
            status = getattr(exc, "status_code", None) or exc.resp.status
            if status in (429, 500, 502, 503, 504):
                last_exc = exc
                continue
            raise
    raise RuntimeError(f"{label} exhausted retries: {last_exc}")


def _query(service, site_url: str, start: str, end: str,
           dimensions: list[str], limit: int = ROW_LIMIT) -> list[dict]:
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": dimensions,
        "rowLimit": limit,
        "startRow": 0,
    }
    resp = _call_with_backoff(
        lambda: service.searchanalytics().query(
            siteUrl=site_url, body=body
        ).execute(),
        f"query dims={dimensions}",
    )
    return resp.get("rows", []) or []


def _normalize_rows(rows: list[dict], key_dims: list[str]) -> list[dict]:
    """Flatten GSC rows into plain dicts keyed by the requested dimensions."""
    out = []
    for row in rows:
        keys = row.get("keys", [])
        entry = {dim: (keys[i] if i < len(keys) else None)
                 for i, dim in enumerate(key_dims)}
        entry.update({
            "clicks": int(row.get("clicks", 0)),
            "impressions": int(row.get("impressions", 0)),
            "ctr": float(row.get("ctr", 0.0)),
            "position": float(row.get("position", 0.0)),
        })
        out.append(entry)
    return out


def fetch_all(service, site_url: str, as_of: date) -> dict:
    """Collect all GSC slices into one in-memory payload."""
    s7, e7 = _date_range(as_of, 7)
    s28, e28 = _date_range(as_of, 28)

    payload = {
        "fetched_at": as_of.isoformat(),
        "site_url": site_url,
        "window_7d": {"start": s7, "end": e7},
        "window_28d": {"start": s28, "end": e28},
        "queries_7d": _normalize_rows(
            _query(service, site_url, s7, e7, ["query"]), ["query"]),
        "queries_28d": _normalize_rows(
            _query(service, site_url, s28, e28, ["query"]), ["query"]),
        "pages_7d": _normalize_rows(
            _query(service, site_url, s7, e7, ["page"]), ["page"]),
        "countries_7d": _normalize_rows(
            _query(service, site_url, s7, e7, ["country"], limit=25),
            ["country"]),
        "devices_7d": _normalize_rows(
            _query(service, site_url, s7, e7, ["device"], limit=10),
            ["device"]),
    }

    # "Indexation" approximation via search analytics: unique pages that
    # received impressions in each window. The real Coverage API is not
    # bulk-accessible, so we treat "impressions > 0" as "indexed + visible".
    pages_seen_7d = len({p["page"] for p in _normalize_rows(
        _query(service, site_url, s7, e7, ["page"], limit=25000),
        ["page"])})
    pages_seen_28d = len({p["page"] for p in _normalize_rows(
        _query(service, site_url, s28, e28, ["page"], limit=25000),
        ["page"])})
    payload["indexation"] = {
        "pages_with_impressions_7d": pages_seen_7d,
        "pages_with_impressions_28d": pages_seen_28d,
        "note": "approximation: unique pages receiving impressions",
    }

    totals_7d = _aggregate_totals(payload["queries_7d"])
    totals_28d = _aggregate_totals(payload["queries_28d"])
    payload["totals_7d"] = totals_7d
    payload["totals_28d"] = totals_28d
    return payload


def _aggregate_totals(rows: list[dict]) -> dict:
    if not rows:
        return {"clicks": 0, "impressions": 0, "ctr": 0.0, "position": 0.0}
    clicks = sum(r["clicks"] for r in rows)
    impressions = sum(r["impressions"] for r in rows)
    ctr = (clicks / impressions) if impressions else 0.0
    pos = sum(r["position"] * r["impressions"] for r in rows)
    pos = (pos / impressions) if impressions else 0.0
    return {"clicks": clicks, "impressions": impressions,
            "ctr": ctr, "position": pos}


def _build_service(creds_path: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds,
                 cache_discovery=False)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=date.today().isoformat(),
                        help="End date (YYYY-MM-DD), default=today")
    parser.add_argument("--creds", default=os.environ.get(
        "GSC_CREDENTIALS_PATH", DEFAULT_CREDS))
    parser.add_argument("--site", default=os.environ.get(
        "GSC_SITE_URL", DEFAULT_SITE))
    parser.add_argument("--out-dir", default=str(DATA_DIR))
    args = parser.parse_args(argv)

    creds_path = Path(args.creds)
    if not creds_path.is_file():
        log.warning("credentials missing at %s — skipping (cron-safe exit)",
                    creds_path)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        service = _build_service(str(creds_path))
    except Exception:
        log.exception("failed to build GSC service")
        return 3

    as_of = date.fromisoformat(args.as_of)
    try:
        payload = fetch_all(service, args.site, as_of)
    except Exception:
        log.exception("GSC fetch failed")
        return 3

    out_path = out_dir / f"{as_of.isoformat()}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    log.info("wrote %s (%d queries_7d, %d pages_7d)",
             out_path, len(payload["queries_7d"]), len(payload["pages_7d"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

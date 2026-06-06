"""Resolve a campaign's `audience_filter` JSON to a list of subscribers.

The filter dict is open-ended — new keys land without a schema change.
Currently understood keys (all optional, AND'd together):

    {
      "lang":          "sr"  | "en" | "ru" | ["sr", "en"],
      "source":        "footer" | "home" | "price_alert" | [...],
      "route_slug":    "beograd-novi-sad",      # null → exclude price-alerts
      "min_days_old":  3,                       # confirmed_at older than N days
      "max_days_old":  60,                      # confirmed within last N days
      "exclude_unsubscribed": true,             # default true
      "exclude_suppressed":   true,             # default true
    }

The output rows always carry id/email/lang/unsubscribe_token so the
dispatch worker can render the per-recipient body without an extra
query per send.
"""
from __future__ import annotations

from typing import Any

from app import analytics_db


def _coerce_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v else []
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v if x]
    return []


def resolve(filter_: dict[str, Any] | None) -> list[dict]:
    """Return [{id, email, lang, unsubscribe_token, source, route_slug}, …]."""
    f = dict(filter_ or {})
    where: list[str] = ["s.confirmed_at IS NOT NULL"]
    params: list[Any] = []

    if f.get('exclude_unsubscribed', True):
        where.append("s.unsubscribed_at IS NULL")

    langs = _coerce_list(f.get('lang'))
    if langs:
        where.append("s.lang IN (" + ", ".join("?" * len(langs)) + ")")
        params.extend(langs)

    sources = _coerce_list(f.get('source'))
    if sources:
        where.append("s.source IN (" + ", ".join("?" * len(sources)) + ")")
        params.extend(sources)

    if 'route_slug' in f:
        rs = f['route_slug']
        if rs is None:
            # Generic newsletter audience — exclude per-route price alerts.
            where.append("s.route_slug IS NULL")
        else:
            where.append("s.route_slug = ?")
            params.append(rs)

    if isinstance(f.get('min_days_old'), int) and f['min_days_old'] > 0:
        where.append(
            "datetime(s.confirmed_at) <= datetime('now', "
            f"'-{int(f['min_days_old'])} days')"
        )
    if isinstance(f.get('max_days_old'), int) and f['max_days_old'] > 0:
        where.append(
            "datetime(s.confirmed_at) >= datetime('now', "
            f"'-{int(f['max_days_old'])} days')"
        )

    if f.get('exclude_suppressed', True):
        where.append(
            "NOT EXISTS (SELECT 1 FROM email_suppressions sup "
            "WHERE sup.email_lower = s.email_lower)"
        )

    sql = (
        "SELECT s.id, s.email, s.lang, s.source, s.route_slug, "
        "       s.unsubscribe_token, s.confirmed_at "
        "FROM subscribers s "
        "WHERE " + " AND ".join(where) + " "
        "ORDER BY s.id"
    )
    return analytics_db.query(sql, params)


def estimate_count(filter_: dict[str, Any] | None) -> int:
    """Cheap COUNT(*) for the pre-flight check on the compose page."""
    return len(resolve(filter_))

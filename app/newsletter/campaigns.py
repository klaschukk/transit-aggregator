"""Campaign + campaign_sends + email_suppressions CRUD.

Thin wrappers around analytics_db so callers don't open the connection
themselves. Every query goes through duckdb's parameterised binding;
the only string-formatted part is the pre-vetted ORDER BY in
`list_campaigns`.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from app import analytics_db

logger = logging.getLogger(__name__)

# Status state machine. Anything not in this set is a config bug.
STATUSES = ('draft', 'scheduled', 'sending', 'sent', 'cancelled', 'failed')
TEMPLATE_KINDS = ('welcome', 'weekly', 'seasonal', 'oneoff', 'reengagement')


def list_campaigns(status: str | None = None, limit: int = 100) -> list[dict]:
    """Most-recent-first listing for the admin dashboard."""
    if status and status in STATUSES:
        return analytics_db.query(
            "SELECT * FROM campaigns WHERE status = ? "
            "ORDER BY COALESCE(scheduled_at, created_at) DESC LIMIT ?",
            [status, int(limit)],
        )
    return analytics_db.query(
        "SELECT * FROM campaigns "
        "ORDER BY COALESCE(scheduled_at, created_at) DESC LIMIT ?",
        [int(limit)],
    )


def get_campaign(campaign_id: int) -> dict | None:
    rows = analytics_db.query(
        "SELECT * FROM campaigns WHERE id = ?", [int(campaign_id)],
    )
    return rows[0] if rows else None


def get_campaign_by_slug(slug: str) -> dict | None:
    rows = analytics_db.query(
        "SELECT * FROM campaigns WHERE slug = ?", [slug],
    )
    return rows[0] if rows else None


def upsert_campaign(
    *,
    slug: str,
    template_kind: str = 'oneoff',
    subjects: dict[str, str] | None = None,
    preheaders: dict[str, str] | None = None,
    bodies: dict[str, str] | None = None,
    audience_filter: dict[str, Any] | None = None,
    status: str = 'draft',
    scheduled_at: str | None = None,
) -> int:
    """Create-or-replace a campaign row by slug. Returns the campaign id.

    `slug` is the stable identifier callers use to refer to a templated
    campaign (welcome, weekly-2026-W17, seasonal-summer-2026). The seeder
    uses it to refresh templates without losing the row's id (which the
    sends + analytics already point at).
    """
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r}")
    if template_kind not in TEMPLATE_KINDS:
        raise ValueError(f"unknown template_kind {template_kind!r}")

    subjects = subjects or {}
    preheaders = preheaders or {}
    bodies = bodies or {}
    audience_json = json.dumps(audience_filter or {}, ensure_ascii=False)

    existing = get_campaign_by_slug(slug)
    conn = analytics_db._get_conn()
    if existing:
        conn.execute(
            "UPDATE campaigns SET "
            "  subject_sr = ?, subject_en = ?, subject_ru = ?, "
            "  preheader_sr = ?, preheader_en = ?, preheader_ru = ?, "
            "  body_md_sr = ?, body_md_en = ?, body_md_ru = ?, "
            "  audience_filter = ?, status = ?, "
            "  template_kind = ?, scheduled_at = ? "
            "WHERE slug = ?",
            [
                subjects.get('sr'), subjects.get('en'), subjects.get('ru'),
                preheaders.get('sr'), preheaders.get('en'), preheaders.get('ru'),
                bodies.get('sr'), bodies.get('en'), bodies.get('ru'),
                audience_json, status, template_kind, scheduled_at, slug,
            ],
        )
        return int(existing['id'])

    conn.execute(
        "INSERT INTO campaigns ("
        "  slug, subject_sr, subject_en, subject_ru, "
        "  preheader_sr, preheader_en, preheader_ru, "
        "  body_md_sr, body_md_en, body_md_ru, "
        "  audience_filter, status, template_kind, scheduled_at"
        ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            slug,
            subjects.get('sr'), subjects.get('en'), subjects.get('ru'),
            preheaders.get('sr'), preheaders.get('en'), preheaders.get('ru'),
            bodies.get('sr'), bodies.get('en'), bodies.get('ru'),
            audience_json, status, template_kind, scheduled_at,
        ],
    )
    rows = analytics_db.query("SELECT id FROM campaigns WHERE slug = ?", [slug])
    return int(rows[0]['id'])


def update_status(campaign_id: int, status: str,
                  *, sent_at_now: bool = False) -> None:
    if status not in STATUSES:
        raise ValueError(f"unknown status {status!r}")
    conn = analytics_db._get_conn()
    if sent_at_now:
        conn.execute(
            "UPDATE campaigns SET status = ?, sent_at = CURRENT_TIMESTAMP "
            "WHERE id = ?",
            [status, int(campaign_id)],
        )
    else:
        conn.execute(
            "UPDATE campaigns SET status = ? WHERE id = ?",
            [status, int(campaign_id)],
        )


def parse_audience(campaign: dict) -> dict[str, Any]:
    """Robust JSON parse — returns {} on missing/empty/malformed."""
    raw = (campaign or {}).get('audience_filter') or ''
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except (ValueError, TypeError) as exc:
        logger.warning("malformed audience_filter on campaign %s: %s",
                       campaign.get('slug'), exc)
        return {}


# ── campaign_sends ────────────────────────────────────────────────────────

def already_sent_subscriber_ids(campaign_id: int) -> set[int]:
    """Used by the resume path to skip recipients we already attempted."""
    rows = analytics_db.query(
        "SELECT subscriber_id FROM campaign_sends WHERE campaign_id = ?",
        [int(campaign_id)],
    )
    return {int(r['subscriber_id']) for r in rows}


def record_send(campaign_id: int, subscriber_id: int,
                error: str | None = None) -> None:
    """Idempotent insert. DuckDB's ON CONFLICT DO UPDATE rejects
    `CURRENT_TIMESTAMP` in the SET list (parses it as a column ref),
    so we model the upsert as delete-then-insert. The unique index
    keeps both branches safe under retry."""
    conn = analytics_db._get_conn()
    conn.execute(
        "DELETE FROM campaign_sends "
        "WHERE campaign_id = ? AND subscriber_id = ?",
        [int(campaign_id), int(subscriber_id)],
    )
    conn.execute(
        "INSERT INTO campaign_sends (campaign_id, subscriber_id, error) "
        "VALUES (?, ?, ?)",
        [int(campaign_id), int(subscriber_id), error],
    )


def increment_counter(campaign_id: int, column: str, by: int = 1) -> None:
    """Bump one of recipients/delivered/opened/clicked/bounced/unsub_count.
    Column name is allowlisted to keep the SQL templated-but-safe."""
    allowed = {
        'recipients_count', 'delivered_count', 'opened_count',
        'clicked_count', 'bounced_count', 'unsub_count',
    }
    if column not in allowed:
        raise ValueError(f"refusing unknown counter column {column!r}")
    conn = analytics_db._get_conn()
    conn.execute(
        f"UPDATE campaigns SET {column} = {column} + ? WHERE id = ?",
        [int(by), int(campaign_id)],
    )


def stats(campaign_id: int) -> dict:
    """Aggregate analytics for the dashboard. Pulls from campaign_sends so
    Mailgun-event timestamps drive the percentages, not the in-row counters
    (which can drift if a webhook is replayed or arrives after the fact)."""
    rows = analytics_db.query(
        "SELECT "
        "  COUNT(*)                                AS recipients, "
        "  COUNT(delivered_at)                     AS delivered, "
        "  COUNT(opened_at)                        AS opened, "
        "  COUNT(clicked_at)                       AS clicked, "
        "  COUNT(bounced_at)                       AS bounced, "
        "  COUNT(unsubscribed_at)                  AS unsubscribed, "
        "  COUNT(error)                            AS errored "
        "FROM campaign_sends WHERE campaign_id = ?",
        [int(campaign_id)],
    )
    return rows[0] if rows else {
        'recipients': 0, 'delivered': 0, 'opened': 0, 'clicked': 0,
        'bounced': 0, 'unsubscribed': 0, 'errored': 0,
    }


# ── email_suppressions ────────────────────────────────────────────────────

def is_suppressed(email_lower: str) -> bool:
    rows = analytics_db.query(
        "SELECT 1 FROM email_suppressions WHERE email_lower = ?",
        [email_lower.lower().strip()],
    )
    return bool(rows)


def suppress_email(email_lower: str, reason: str,
                   note: str | None = None) -> None:
    """ON CONFLICT DO NOTHING — first reason wins, so a manual entry beats
    a later auto-bounce when it's already in the table for a clear cause."""
    if reason not in ('bounce', 'complaint', 'manual', 'unsubscribed'):
        raise ValueError(f"refusing unknown suppression reason {reason!r}")
    conn = analytics_db._get_conn()
    conn.execute(
        "INSERT INTO email_suppressions (email_lower, reason, note) "
        "VALUES (?, ?, ?) ON CONFLICT (email_lower) DO NOTHING",
        [email_lower.lower().strip(), reason, note],
    )


def list_suppressions(limit: int = 200) -> list[dict]:
    return analytics_db.query(
        "SELECT email_lower, reason, added_at, note FROM email_suppressions "
        "ORDER BY added_at DESC LIMIT ?",
        [int(limit)],
    )

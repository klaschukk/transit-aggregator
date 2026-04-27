"""Analytics DuckDB connection — read/write, separate file from the main
read-only transit DB so concurrent writes don't conflict with the scraper
refresh of data/dbs/transit.duckdb.

Schema is created idempotently on app boot via init_schema().

Concurrency model
-----------------
DuckDB allows many R/W connections inside a single process, but ANY
cross-process access to a file currently held R/W fails immediately
with "Conflicting lock is held in /usr/bin/python3.12". With 2 gunicorn
workers + nightly cron writers (adsense_fetch, price_snapshot,
seed_reviews) this used to spam journalctl with lock errors whenever
the cron's window overlapped a worker holding the lock.

Smallest fix: close the per-thread connection at the end of every
Flask request via app.teardown_appcontext (wired in app/__init__.py),
and retry-on-lock when opening. Flask therefore holds the lock only
during a request, leaving windows (~ms-scale) for cron writers to slip
in. Cron writers use the same _get_conn(), so they pick up the retry
behaviour for free.
"""
import hashlib
import logging
import os
import threading
import time
from pathlib import Path

import duckdb
from flask import current_app

from . import observability

logger = logging.getLogger(__name__)

_local = threading.local()


def _path() -> str:
    return current_app.config['ANALYTICS_DB_PATH']


# Retry schedule for cross-process lock contention. Worst-case wait is
# 100 + 200 + 400 + 800 = 1500 ms, after which we surface the IOException
# to the caller. The Flask write paths catch IOException and log it as a
# soft failure so /api/ba-click etc. still return 204 even on a worst-day
# collision.
_LOCK_RETRY_DELAYS = (0.1, 0.2, 0.4, 0.8)


def _open_with_retry(target: str) -> duckdb.DuckDBPyConnection:
    last_exc = None
    for delay in (0.0, *_LOCK_RETRY_DELAYS):
        if delay:
            time.sleep(delay)
        try:
            return duckdb.connect(target, read_only=False)
        except duckdb.IOException as exc:
            last_exc = exc
            if 'Conflicting lock' not in str(exc):
                raise
    # Out of retries — propagate so the caller decides (insert_* helpers
    # log + Sentry-capture; reads return [] / None).
    assert last_exc is not None
    raise last_exc


def _get_conn() -> duckdb.DuckDBPyConnection:
    """Return a per-thread R/W connection. Reconnects automatically when the
    configured path changes (matters for tests that swap DBs between apps).

    Inside a Flask request, the connection is closed by the
    teardown_appcontext hook so the file lock doesn't persist across
    requests. Outside Flask (cron scripts), close_thread_conn() should
    be called when the script exits its main work loop."""
    target = _path()
    conn = getattr(_local, 'conn', None)
    bound_path = getattr(_local, 'path', None)
    if conn is None or bound_path != target:
        if conn is not None:
            try: conn.close()
            except duckdb.Error: pass
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        conn = _open_with_retry(target)
        _local.conn = conn
        _local.path = target
    return conn


def close_thread_conn() -> None:
    """Close the per-thread DuckDB connection if any. Safe to call when no
    connection exists. Wired into Flask's teardown_appcontext so each
    request releases the file lock — keeps cross-process writers (cron)
    from starving."""
    conn = getattr(_local, 'conn', None)
    if conn is None:
        return
    try:
        conn.close()
    except duckdb.Error:
        pass
    _local.conn = None
    _local.path = None


_SCHEMA_SQL = """
CREATE SEQUENCE IF NOT EXISTS ba_clicks_id_seq;
CREATE TABLE IF NOT EXISTS ba_clicks (
    id          BIGINT PRIMARY KEY DEFAULT nextval('ba_clicks_id_seq'),
    route_slug  VARCHAR,
    surface     VARCHAR,
    operator    VARCHAR,
    trip_time   VARCHAR,
    ip_hash     VARCHAR,
    user_agent  VARCHAR,
    referrer    VARCHAR,
    ts          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ba_clicks_ts_idx ON ba_clicks(ts);
CREATE INDEX IF NOT EXISTS ba_clicks_slug_idx ON ba_clicks(route_slug);

CREATE SEQUENCE IF NOT EXISTS reviews_id_seq;
CREATE TABLE IF NOT EXISTS reviews (
    id             BIGINT PRIMARY KEY DEFAULT nextval('reviews_id_seq'),
    route_slug     VARCHAR NOT NULL,
    rating         INTEGER NOT NULL,
    comment        VARCHAR NOT NULL,
    author_name    VARCHAR NOT NULL,
    email_hash     VARCHAR,
    lang           VARCHAR,
    ts             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status         VARCHAR DEFAULT 'pending',
    moderated_at   TIMESTAMP,
    moderator_note VARCHAR,
    deletion_requested BOOLEAN DEFAULT FALSE,
    ip_hash        VARCHAR
);
CREATE INDEX IF NOT EXISTS reviews_route_idx ON reviews(route_slug, status);
CREATE INDEX IF NOT EXISTS reviews_email_idx ON reviews(email_hash);
CREATE INDEX IF NOT EXISTS reviews_status_idx ON reviews(status, ts);

CREATE SEQUENCE IF NOT EXISTS subscribers_id_seq;
CREATE TABLE IF NOT EXISTS subscribers (
    id                BIGINT PRIMARY KEY DEFAULT nextval('subscribers_id_seq'),
    email             VARCHAR NOT NULL,
    email_lower       VARCHAR NOT NULL,
    lang              VARCHAR,
    source            VARCHAR,
    referrer          VARCHAR,
    ip_hash           VARCHAR,
    ts                TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confirm_token     VARCHAR,
    confirmed_at      TIMESTAMP,
    unsubscribe_token VARCHAR,
    unsubscribed_at   TIMESTAMP
);
CREATE UNIQUE INDEX IF NOT EXISTS subscribers_email_uq ON subscribers(email_lower);
CREATE INDEX IF NOT EXISTS subscribers_confirm_idx ON subscribers(confirm_token);
CREATE INDEX IF NOT EXISTS subscribers_unsub_idx ON subscribers(unsubscribe_token);

-- Price-alert backbone. route_slug links a subscriber row to a specific
-- /rute/{slug}/ page; NULL keeps generic-newsletter rows backwards-compatible.
ALTER TABLE subscribers ADD COLUMN IF NOT EXISTS route_slug VARCHAR;
CREATE INDEX IF NOT EXISTS subscribers_route_idx ON subscribers(route_slug);

-- One row per route per day. UNIQUE(route_slug, date) makes the nightly
-- snapshot script idempotent — re-running never duplicates history.
CREATE TABLE IF NOT EXISTS price_snapshots (
    route_slug  VARCHAR NOT NULL,
    date        DATE    NOT NULL,
    min_price   INTEGER,
    max_price   INTEGER,
    avg_price   DOUBLE,
    trip_count  INTEGER,
    snapshot_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (route_slug, date)
);
CREATE INDEX IF NOT EXISTS price_snapshots_route_idx ON price_snapshots(route_slug, date);

-- Dedup ledger for alert dispatch. Join with subscribers.id + cooldown
-- window to guarantee at most one email per (subscriber, route) per week.
CREATE SEQUENCE IF NOT EXISTS price_alerts_sent_id_seq;
CREATE TABLE IF NOT EXISTS price_alerts_sent (
    id             BIGINT PRIMARY KEY DEFAULT nextval('price_alerts_sent_id_seq'),
    subscriber_id  BIGINT NOT NULL,
    route_slug     VARCHAR NOT NULL,
    old_price      INTEGER,
    new_price      INTEGER,
    drop_pct       INTEGER,
    sent_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_ok   BOOLEAN
);
CREATE INDEX IF NOT EXISTS price_alerts_sent_sub_idx ON price_alerts_sent(subscriber_id, route_slug, sent_at);
CREATE INDEX IF NOT EXISTS price_alerts_sent_route_idx ON price_alerts_sent(route_slug, sent_at);

-- Newsletter campaigns. One row per campaign (across all 3 languages —
-- we localise body/subject in-row rather than 3×row to keep the audience
-- match logic single-statement). status transitions: draft → sending →
-- sent (or → cancelled on operator abort). audience_filter is JSON so
-- new filter primitives (lang, source, route_slug, days_since_signup,
-- min_engagement) can land without a schema bump.
CREATE SEQUENCE IF NOT EXISTS campaigns_id_seq;
CREATE TABLE IF NOT EXISTS campaigns (
    id                BIGINT PRIMARY KEY DEFAULT nextval('campaigns_id_seq'),
    slug              VARCHAR NOT NULL,
    subject_sr        VARCHAR,
    subject_en        VARCHAR,
    subject_ru        VARCHAR,
    preheader_sr      VARCHAR,
    preheader_en      VARCHAR,
    preheader_ru      VARCHAR,
    body_md_sr        VARCHAR,
    body_md_en        VARCHAR,
    body_md_ru        VARCHAR,
    audience_filter   VARCHAR,          -- JSON
    status            VARCHAR NOT NULL DEFAULT 'draft',
    template_kind     VARCHAR,          -- welcome / weekly / seasonal / oneoff
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scheduled_at      TIMESTAMP,
    sent_at           TIMESTAMP,
    recipients_count  INTEGER DEFAULT 0,
    delivered_count   INTEGER DEFAULT 0,
    opened_count      INTEGER DEFAULT 0,
    clicked_count     INTEGER DEFAULT 0,
    bounced_count     INTEGER DEFAULT 0,
    unsub_count       INTEGER DEFAULT 0
);
CREATE UNIQUE INDEX IF NOT EXISTS campaigns_slug_uq ON campaigns(slug);
CREATE INDEX IF NOT EXISTS campaigns_status_idx ON campaigns(status, scheduled_at);

-- One row per (campaign, subscriber) attempt. Resume support reads the
-- last sent_at for a campaign and continues from there. delivered/opened/
-- clicked are populated by the Mailgun webhook (or stay NULL when SMTP
-- only — we still track sent_at so re-runs don't duplicate).
CREATE SEQUENCE IF NOT EXISTS campaign_sends_id_seq;
CREATE TABLE IF NOT EXISTS campaign_sends (
    id              BIGINT PRIMARY KEY DEFAULT nextval('campaign_sends_id_seq'),
    campaign_id     BIGINT NOT NULL,
    subscriber_id   BIGINT NOT NULL,
    sent_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at    TIMESTAMP,
    opened_at       TIMESTAMP,
    clicked_at      TIMESTAMP,
    bounced_at      TIMESTAMP,
    unsubscribed_at TIMESTAMP,
    error           VARCHAR
);
CREATE UNIQUE INDEX IF NOT EXISTS campaign_sends_uq
    ON campaign_sends(campaign_id, subscriber_id);
CREATE INDEX IF NOT EXISTS campaign_sends_campaign_idx
    ON campaign_sends(campaign_id, sent_at);

-- Hard-bounce + complaint suppression. Once an address is here we never
-- send to it again — protects sender reputation and bills (Mailgun
-- charges per attempted send, not per delivered).
CREATE TABLE IF NOT EXISTS email_suppressions (
    email_lower  VARCHAR PRIMARY KEY,
    reason       VARCHAR,           -- 'bounce' / 'complaint' / 'manual'
    added_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note         VARCHAR
);

-- A/B experiment events. event_type is either 'exposure' or 'conv:<event>'.
-- Stored denormalised (variant + experiment as plain strings) so adding a
-- new experiment is a config edit, no DDL. user_seed is the ab_id (UUID),
-- never raw IP.
CREATE SEQUENCE IF NOT EXISTS ab_events_id_seq;
CREATE TABLE IF NOT EXISTS ab_events (
    id           BIGINT PRIMARY KEY DEFAULT nextval('ab_events_id_seq'),
    experiment   VARCHAR NOT NULL,
    variant      VARCHAR NOT NULL,
    event_type   VARCHAR NOT NULL,
    surface      VARCHAR,
    user_seed    VARCHAR,
    value        DOUBLE  DEFAULT 1.0,
    ts           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ts_date      DATE      DEFAULT CURRENT_DATE
);
CREATE INDEX IF NOT EXISTS ab_events_exp_idx
    ON ab_events(experiment, event_type, ts_date);
CREATE INDEX IF NOT EXISTS ab_events_exp_variant_idx
    ON ab_events(experiment, variant, event_type);

-- Daily count snapshots — written by scripts/data_snapshot.py after the
-- nightly DB rebuild. Long-and-skinny shape so we can mix entity kinds
-- (operator, route, line, stop) without DDL per kind. The diff between
-- consecutive snapshot_dates surfaces "data changed today" deltas that
-- file-mtime alone misses (e.g. operator added 3 trips but JSON file
-- mtime stayed the same because the scraper rewrites unconditionally).
CREATE TABLE IF NOT EXISTS data_snapshots (
    snapshot_date DATE NOT NULL,
    kind          VARCHAR NOT NULL,
    key           VARCHAR NOT NULL,
    value         BIGINT  NOT NULL,
    PRIMARY KEY (snapshot_date, kind, key)
);
CREATE INDEX IF NOT EXISTS data_snapshots_kind_idx
    ON data_snapshots(kind, snapshot_date);
"""


def init_schema() -> None:
    """Idempotent schema creation. Runs every app boot (CREATE ... IF NOT
    EXISTS is cheap) so tests that swap ANALYTICS_DB_PATH still get a valid
    schema on the new file."""
    try:
        _get_conn().execute(_SCHEMA_SQL)
        logger.info("analytics_db schema ready at %s", _path())
    except duckdb.Error as exc:
        logger.error("analytics_db init failed: %s", exc)
        observability.capture_exception(exc, subsystem='analytics_db',
                                        op='init_schema')


def hash_ip(ip: str) -> str:
    """sha256(salt + ip) — not pseudonymising; just reducing re-identifiability.
    Salt comes from config so rotating it invalidates history for fresh audits."""
    salt = current_app.config.get('IP_HASH_SALT', '')
    if not salt:
        # Missing salt in production is a config error, but we still return
        # something stable so /api/ba-click doesn't 500 — rotation is a ops task.
        salt = 'dev-only-rotate-me'
    return hashlib.sha256((salt + '|' + (ip or '')).encode('utf-8')).hexdigest()[:32]


def insert_ba_click(
    route_slug: str,
    surface: str,
    operator: str,
    trip_time: str,
    ip: str,
    user_agent: str,
    referrer: str,
) -> None:
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO ba_clicks (route_slug, surface, operator, trip_time, ip_hash, user_agent, referrer) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (route_slug or '')[:200],
                (surface or '')[:40],
                (operator or '')[:100],
                (trip_time or '')[:10],
                hash_ip(ip),
                (user_agent or '')[:300],
                (referrer or '')[:500],
            ],
        )
    except duckdb.Error as exc:
        logger.error("insert_ba_click failed: %s", exc)
        observability.capture_exception(
            exc, subsystem='analytics_db', op='insert_ba_click',
            route_slug=route_slug, surface=surface,
        )
        _local.conn = None  # reset stale connection


def insert_ab_event(
    experiment: str,
    variant: str,
    event_type: str,
    surface: str = '',
    user_seed: str = '',
    value: float = 1.0,
) -> None:
    """Append a row to ab_events. Best-effort — DB errors are logged
    + Sentry-captured but never raised, since A/B telemetry must not
    take down a page render."""
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO ab_events (experiment, variant, event_type, surface, user_seed, value) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                (experiment or '')[:80],
                (variant or '')[:80],
                (event_type or '')[:60],
                (surface or '')[:60],
                (user_seed or '')[:64],
                float(value),
            ],
        )
    except duckdb.Error as exc:
        logger.error("insert_ab_event failed: %s", exc)
        observability.capture_exception(
            exc, subsystem='analytics_db', op='insert_ab_event',
            experiment=experiment, variant=variant,
        )
        _local.conn = None


def ab_event_summary(experiment: str) -> list[dict]:
    """Aggregate counts per (variant, event_type) for one experiment."""
    return query(
        """
        SELECT variant, event_type,
               COUNT(*) AS count,
               COUNT(DISTINCT user_seed) AS unique_users
        FROM ab_events
        WHERE experiment = ?
        GROUP BY variant, event_type
        ORDER BY variant, event_type
        """,
        [experiment],
    )


def ab_daily_exposures(experiment: str, days: int = 14) -> list[dict]:
    """Per-variant daily exposure counts, recent N days."""
    return query(
        """
        SELECT ts_date, variant, COUNT(*) AS exposures
        FROM ab_events
        WHERE experiment = ?
          AND event_type = 'exposure'
          AND ts_date >= CURRENT_DATE - ?
        GROUP BY ts_date, variant
        ORDER BY ts_date DESC, variant
        """,
        [experiment, days],
    )


def ab_export_rows(experiment: str | None = None) -> list[dict]:
    """Flat raw export for /admin/ab CSV download."""
    if experiment:
        return query(
            "SELECT experiment, variant, event_type, surface, user_seed, value, ts "
            "FROM ab_events WHERE experiment = ? ORDER BY ts",
            [experiment],
        )
    return query(
        "SELECT experiment, variant, event_type, surface, user_seed, value, ts "
        "FROM ab_events ORDER BY ts",
        [],
    )


def query(sql: str, params: list | None = None) -> list[dict]:
    """Read query helper for the admin dashboard."""
    try:
        conn = _get_conn()
        res = conn.execute(sql, params or [])
        cols = [d[0] for d in res.description]
        return [dict(zip(cols, row)) for row in res.fetchall()]
    except duckdb.Error as exc:
        logger.error("analytics_db query failed: %s | %s", exc, sql)
        _local.conn = None
        return []


# ── reviews helpers ─────────────────────────────────────────────────────


def hash_email(email: str) -> str:
    """sha256 over a stable lowercased email, salted the same way as IPs.
    Keeps plaintext out of the DB entirely while supporting GDPR match-by-email
    (user re-enters their address at deletion time)."""
    salt = current_app.config.get('IP_HASH_SALT', '') or 'dev-only-rotate-me'
    normalized = (email or '').strip().lower()
    return hashlib.sha256((salt + '|email|' + normalized).encode('utf-8')).hexdigest()


def insert_review(
    *,
    route_slug: str,
    rating: int,
    comment: str,
    author_name: str,
    email: str,
    lang: str,
    ip: str,
    status: str = 'pending',
) -> int | None:
    try:
        conn = _get_conn()
        res = conn.execute(
            "INSERT INTO reviews (route_slug, rating, comment, author_name, "
            "email_hash, lang, status, ip_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING id",
            [
                (route_slug or '')[:200],
                max(1, min(5, int(rating))),
                (comment or '').strip()[:500],
                (author_name or '').strip()[:40],
                hash_email(email) if email else None,
                (lang or 'sr')[:5],
                status if status in ('pending', 'approved') else 'pending',
                hash_ip(ip),
            ],
        )
        row = res.fetchone()
        return int(row[0]) if row else None
    except duckdb.Error as exc:
        logger.error("insert_review failed: %s", exc)
        _local.conn = None
        return None


def is_trusted_author(email: str) -> bool:
    """True after the author already has 3+ approved reviews. Callers should
    still run anti-spam checks — this only decides default status."""
    if not email:
        return False
    try:
        conn = _get_conn()
        row = conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE email_hash = ? AND status = 'approved'",
            [hash_email(email)],
        ).fetchone()
        return bool(row and row[0] >= 3)
    except duckdb.Error as exc:
        logger.error("is_trusted_author failed: %s", exc)
        return False


def approved_reviews(route_slug: str, limit: int = 50) -> list[dict]:
    return query(
        "SELECT id, rating, comment, author_name, lang, ts "
        "FROM reviews WHERE route_slug = ? AND status = 'approved' "
        "ORDER BY ts DESC LIMIT ?",
        [route_slug, limit],
    )


def aggregate_rating(route_slug: str) -> dict:
    rows = query(
        "SELECT COUNT(*) AS n, AVG(rating) AS avg_rating "
        "FROM reviews WHERE route_slug = ? AND status = 'approved'",
        [route_slug],
    )
    if not rows or not rows[0]['n']:
        return {'n': 0, 'avg': None}
    return {'n': int(rows[0]['n']), 'avg': round(float(rows[0]['avg_rating']), 1)}


def pending_reviews(limit: int = 100) -> list[dict]:
    return query(
        "SELECT id, route_slug, rating, comment, author_name, lang, ts, "
        "       deletion_requested, email_hash "
        "FROM reviews WHERE status = 'pending' OR deletion_requested = TRUE "
        "ORDER BY deletion_requested DESC, ts ASC LIMIT ?",
        [limit],
    )


def set_review_status(review_id: int, status: str, note: str = '') -> bool:
    if status not in ('approved', 'rejected', 'deleted'):
        return False
    try:
        conn = _get_conn()
        if status == 'deleted':
            # Soft delete: wipe PII so the row stays for audit but can't
            # identify the author anymore.
            conn.execute(
                "UPDATE reviews SET status='deleted', moderated_at=CURRENT_TIMESTAMP, "
                "moderator_note=?, author_name='[deleted]', comment='[deleted]', "
                "email_hash=NULL, deletion_requested=FALSE "
                "WHERE id = ?",
                [note[:200], review_id],
            )
        else:
            conn.execute(
                "UPDATE reviews SET status=?, moderated_at=CURRENT_TIMESTAMP, "
                "moderator_note=? WHERE id = ?",
                [status, note[:200], review_id],
            )
        return True
    except duckdb.Error as exc:
        logger.error("set_review_status failed: %s", exc)
        _local.conn = None
        return False


# ── subscribers helpers ─────────────────────────────────────────────────


_CONFIRM_TTL_DAYS = 7


def _new_token() -> str:
    import uuid
    return uuid.uuid4().hex


def subscriber_by_email(email: str) -> dict | None:
    if not email:
        return None
    rows = query(
        "SELECT id, email, lang, source, route_slug, confirm_token, confirmed_at, "
        "       unsubscribe_token, unsubscribed_at, ts "
        "FROM subscribers WHERE email_lower = ?",
        [email.strip().lower()],
    )
    return rows[0] if rows else None


def insert_or_refresh_subscriber(
    *,
    email: str,
    lang: str,
    source: str,
    referrer: str,
    ip: str,
    route_slug: str | None = None,
) -> dict | None:
    """Create a pending subscriber, or re-issue a confirm token for an
    existing pending/unsubscribed record. Returns the stored row including
    the fresh tokens. Idempotent for already-confirmed rows (returns
    existing with action='already_confirmed').

    `route_slug` binds a price-alert signup to one /rute/{slug}/ page. Pass
    None for generic newsletter signups. An existing confirmed subscriber
    re-subscribing with a different route_slug has their row updated so
    they can track a new route without re-confirming.
    """
    email = (email or '').strip()
    if not email:
        return None
    email_lower = email.lower()
    existing = subscriber_by_email(email_lower)
    route_slug = (route_slug or None) and route_slug[:200]

    try:
        conn = _get_conn()
        if existing is None:
            confirm_t = _new_token()
            unsub_t = _new_token()
            conn.execute(
                "INSERT INTO subscribers (email, email_lower, lang, source, "
                "referrer, ip_hash, confirm_token, unsubscribe_token, route_slug) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    email[:200], email_lower[:200],
                    (lang or 'sr')[:5],
                    (source or 'unknown')[:40],
                    (referrer or '')[:500],
                    hash_ip(ip),
                    confirm_t, unsub_t,
                    route_slug,
                ],
            )
            row = subscriber_by_email(email_lower) or {}
            row['_action'] = 'created'
            return row

        if existing.get('confirmed_at') and not existing.get('unsubscribed_at'):
            # Already confirmed. If they're signing up for a different
            # route, update the binding silently — don't make them re-confirm
            # to track a new route.
            if route_slug and existing.get('route_slug') != route_slug:
                conn.execute(
                    "UPDATE subscribers SET route_slug = ? WHERE id = ?",
                    [route_slug, existing['id']],
                )
                existing['_action'] = 'route_updated'
                existing['route_slug'] = route_slug
                return existing
            existing['_action'] = 'already_confirmed'
            return existing

        # Pending or previously unsubscribed — rotate tokens + clear the
        # unsubscribed state so the user opts back in fresh.
        confirm_t = _new_token()
        unsub_t = _new_token()
        conn.execute(
            "UPDATE subscribers SET confirm_token = ?, unsubscribe_token = ?, "
            "ts = CURRENT_TIMESTAMP, lang = ?, source = ?, referrer = ?, "
            "ip_hash = ?, unsubscribed_at = NULL, route_slug = ? "
            "WHERE id = ?",
            [
                confirm_t, unsub_t,
                (lang or 'sr')[:5],
                (source or 'unknown')[:40],
                (referrer or '')[:500],
                hash_ip(ip),
                route_slug,
                existing['id'],
            ],
        )
        fresh = subscriber_by_email(email_lower) or {}
        fresh['_action'] = 'resent'
        return fresh
    except duckdb.Error as exc:
        logger.error("insert_or_refresh_subscriber failed: %s", exc)
        _local.conn = None
        return None


def confirm_subscriber(token: str) -> tuple[str, dict | None]:
    """Exchange a confirm_token for a confirmed row.

    Returns (status, row) where status is:
    'ok'       — freshly confirmed; row has email/lang/unsubscribe_token
                 so the caller can send the welcome letter.
    'already'  — row was already confirmed before (row returned too).
    'expired'  — token older than _CONFIRM_TTL_DAYS (row returned).
    'invalid'  — token not found; row is None.
    """
    if not token:
        return 'invalid', None
    try:
        conn = _get_conn()
        rows = conn.execute(
            "SELECT id, email, lang, unsubscribe_token, confirmed_at, ts "
            "FROM subscribers WHERE confirm_token = ?",
            [token],
        ).fetchall()
        if not rows:
            return 'invalid', None
        sub_id, email, lang, unsub_token, confirmed_at, created_at = rows[0]
        row = {
            'id': sub_id, 'email': email, 'lang': lang,
            'unsubscribe_token': unsub_token,
        }
        if confirmed_at is not None:
            return 'already', row
        from datetime import datetime, timedelta
        if created_at is not None:
            age = datetime.utcnow() - created_at
            if age > timedelta(days=_CONFIRM_TTL_DAYS):
                return 'expired', row
        conn.execute(
            "UPDATE subscribers SET confirmed_at = CURRENT_TIMESTAMP, "
            "confirm_token = NULL WHERE id = ?",
            [sub_id],
        )
        return 'ok', row
    except duckdb.Error as exc:
        logger.error("confirm_subscriber failed: %s", exc)
        _local.conn = None
        return 'invalid', None


def unsubscribe_subscriber(token: str) -> bool:
    if not token:
        return False
    try:
        conn = _get_conn()
        res = conn.execute(
            "UPDATE subscribers SET unsubscribed_at = CURRENT_TIMESTAMP "
            "WHERE unsubscribe_token = ? AND unsubscribed_at IS NULL "
            "RETURNING id",
            [token],
        ).fetchone()
        return res is not None
    except duckdb.Error as exc:
        logger.error("unsubscribe_subscriber failed: %s", exc)
        return False


def subscriber_stats() -> dict:
    rows = query(
        "SELECT "
        "  COUNT(*) AS total, "
        "  COUNT(*) FILTER (WHERE confirmed_at IS NOT NULL "
        "                   AND unsubscribed_at IS NULL) AS confirmed, "
        "  COUNT(*) FILTER (WHERE confirmed_at IS NULL "
        "                   AND unsubscribed_at IS NULL) AS pending, "
        "  COUNT(*) FILTER (WHERE unsubscribed_at IS NOT NULL) AS unsubscribed "
        "FROM subscribers"
    )
    if not rows:
        return {'total': 0, 'confirmed': 0, 'pending': 0, 'unsubscribed': 0}
    return {k: int(v or 0) for k, v in rows[0].items()}


# ── price alerts helpers ────────────────────────────────────────────────


def insert_or_refresh_price_snapshot(
    route_slug: str,
    *,
    snapshot_date,
    min_price: int | None,
    max_price: int | None,
    avg_price: float | None,
    trip_count: int,
) -> bool:
    """Upsert one row per (route_slug, snapshot_date). Idempotent — rerunning
    the nightly snapshot on the same day simply refreshes the numbers.

    DuckDB's ON CONFLICT DO UPDATE had trouble mixing `excluded.*` + a
    literal CURRENT_TIMESTAMP in the same SET, so we do delete-then-insert
    atomically inside a transaction instead. Same net effect, same PK
    guarantee."""
    conn = None
    try:
        conn = _get_conn()
        conn.execute("BEGIN TRANSACTION")
        conn.execute(
            "DELETE FROM price_snapshots WHERE route_slug = ? AND date = ?",
            [route_slug, snapshot_date],
        )
        conn.execute(
            "INSERT INTO price_snapshots "
            "(route_slug, date, min_price, max_price, avg_price, trip_count) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [route_slug, snapshot_date, min_price, max_price, avg_price, trip_count],
        )
        conn.execute("COMMIT")
        return True
    except duckdb.Error as exc:
        if conn is not None:
            try:
                conn.execute("ROLLBACK")
            except duckdb.Error:
                pass
        logger.error("insert_or_refresh_price_snapshot failed: %s", exc)
        _local.conn = None
        return False


def price_snapshots_for_route(route_slug: str, days: int = 7) -> list[dict]:
    """Last `days` snapshots for one route, newest first.

    DuckDB doesn't accept parameter binding inside INTERVAL literals, so
    the day count is interpolated directly. Safe because `days` is coerced
    to int before use.
    """
    days_i = max(0, int(days))
    return query(
        "SELECT date, min_price, max_price, avg_price, trip_count "
        "FROM price_snapshots "
        f"WHERE route_slug = ? AND date >= CURRENT_DATE - INTERVAL '{days_i}' DAY "
        "ORDER BY date DESC",
        [route_slug],
    )


def subscribers_for_route_alerts(route_slug: str) -> list[dict]:
    """Every confirmed, non-unsubscribed subscriber watching this route.
    Generic-newsletter rows (route_slug IS NULL) are excluded."""
    return query(
        "SELECT id, email, lang, unsubscribe_token "
        "FROM subscribers "
        "WHERE route_slug = ? "
        "  AND confirmed_at IS NOT NULL "
        "  AND unsubscribed_at IS NULL",
        [route_slug],
    )


def price_alert_recently_sent(
    subscriber_id: int, route_slug: str, within_days: int = 7,
) -> bool:
    """True iff we already sent this (subscriber, route) an alert in the
    cooldown window. Guards against spamming the same user every night when
    a route sits cheap for a week."""
    days_i = max(0, int(within_days))
    rows = query(
        "SELECT 1 FROM price_alerts_sent "
        "WHERE subscriber_id = ? AND route_slug = ? "
        f"  AND sent_at >= CURRENT_TIMESTAMP - INTERVAL '{days_i}' DAY "
        "LIMIT 1",
        [subscriber_id, route_slug],
    )
    return bool(rows)


def record_price_alert_sent(
    *,
    subscriber_id: int,
    route_slug: str,
    old_price: int,
    new_price: int,
    drop_pct: int,
    delivered_ok: bool,
) -> None:
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT INTO price_alerts_sent "
            "(subscriber_id, route_slug, old_price, new_price, drop_pct, delivered_ok) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [subscriber_id, route_slug, old_price, new_price, drop_pct, delivered_ok],
        )
    except duckdb.Error as exc:
        logger.error("record_price_alert_sent failed: %s", exc)
        _local.conn = None


def request_review_deletion(review_id: int, email: str) -> bool:
    """Mark a review for admin-confirmed deletion, if the email hash matches.
    Prevents Alice-deleting-Bob's-review by requiring the requester prove
    ownership via the email they originally submitted with."""
    if not email:
        return False
    try:
        conn = _get_conn()
        res = conn.execute(
            "UPDATE reviews SET deletion_requested = TRUE "
            "WHERE id = ? AND email_hash = ? AND status != 'deleted' "
            "RETURNING id",
            [review_id, hash_email(email)],
        ).fetchone()
        return res is not None
    except duckdb.Error as exc:
        logger.error("request_review_deletion failed: %s", exc)
        return False

# ── data snapshots (added 2026-04-27) ────────────────────────────────
# Captures upstream scrape drift the file-mtime signal misses.

def record_snapshot(snapshot_date: str, kind: str, key: str, value: int) -> None:
    """UPSERT a single (snapshot_date, kind, key) row.

    Idempotent: re-running the same snapshot script the same day overwrites
    rather than dup-keying. Cron writes ~1500 rows per night (operators +
    routes + lines + stops), single transaction.
    """
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO data_snapshots "
            "(snapshot_date, kind, key, value) VALUES (?, ?, ?, ?)",
            [snapshot_date, kind, key, value],
        )
    except duckdb.Error as exc:
        logger.error("record_snapshot failed: %s", exc)
        _local.conn = None


def diff_snapshots(kind: str,
                   date_a: str | None = None,
                   date_b: str | None = None) -> list[dict]:
    """Compare snapshots between two dates. Defaults: latest two dates seen
    for `kind`. Returns rows where value changed.

    Each result: {key, value_a, value_b, delta}. Sorted by absolute delta
    desc so the biggest drift bubbles to the top.
    """
    try:
        conn = _get_conn()
        if not date_a or not date_b:
            dates = conn.execute(
                "SELECT DISTINCT snapshot_date FROM data_snapshots "
                "WHERE kind = ? ORDER BY snapshot_date DESC LIMIT 2",
                [kind],
            ).fetchall()
            if len(dates) < 2:
                return []
            date_b, date_a = str(dates[0][0]), str(dates[1][0])
        rows = conn.execute(
            "SELECT COALESCE(a.key, b.key) AS key, "
            "       COALESCE(a.value, 0) AS value_a, "
            "       COALESCE(b.value, 0) AS value_b "
            "FROM (SELECT key, value FROM data_snapshots "
            "      WHERE kind = ? AND snapshot_date = ?) a "
            "FULL OUTER JOIN "
            "     (SELECT key, value FROM data_snapshots "
            "      WHERE kind = ? AND snapshot_date = ?) b "
            "USING (key) "
            "WHERE COALESCE(a.value, 0) != COALESCE(b.value, 0)",
            [kind, date_a, kind, date_b],
        ).fetchall()
        results = [
            {'key': r[0], 'value_a': r[1], 'value_b': r[2], 'delta': r[2] - r[1]}
            for r in rows
        ]
        results.sort(key=lambda r: abs(r['delta']), reverse=True)
        return results
    except duckdb.Error as exc:
        logger.error("diff_snapshots failed: %s", exc)
        return []

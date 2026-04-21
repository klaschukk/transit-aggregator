"""Analytics DuckDB connection — read/write, separate file from the main
read-only transit DB so concurrent writes don't conflict with the scraper
refresh of data/dbs/transit.duckdb.

Schema is created idempotently on app boot via init_schema().
"""
import hashlib
import logging
import os
import threading
from pathlib import Path

import duckdb
from flask import current_app

logger = logging.getLogger(__name__)

_local = threading.local()


def _path() -> str:
    return current_app.config['ANALYTICS_DB_PATH']


def _get_conn() -> duckdb.DuckDBPyConnection:
    """Return a per-thread R/W connection. Reconnects automatically when the
    configured path changes (matters for tests that swap DBs between apps)."""
    target = _path()
    conn = getattr(_local, 'conn', None)
    bound_path = getattr(_local, 'path', None)
    if conn is None or bound_path != target:
        if conn is not None:
            try: conn.close()
            except duckdb.Error: pass
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect(target, read_only=False)
        _local.conn = conn
        _local.path = target
    return conn


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
        _local.conn = None  # reset stale connection


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
        "SELECT id, email, lang, source, confirm_token, confirmed_at, "
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
) -> dict | None:
    """Create a pending subscriber, or re-issue a confirm token for an
    existing pending/unsubscribed record. Returns the stored row including
    the fresh tokens. Idempotent for already-confirmed rows (returns
    existing with action='already_confirmed')."""
    email = (email or '').strip()
    if not email:
        return None
    email_lower = email.lower()
    existing = subscriber_by_email(email_lower)

    try:
        conn = _get_conn()
        if existing is None:
            confirm_t = _new_token()
            unsub_t = _new_token()
            conn.execute(
                "INSERT INTO subscribers (email, email_lower, lang, source, "
                "referrer, ip_hash, confirm_token, unsubscribe_token) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    email[:200], email_lower[:200],
                    (lang or 'sr')[:5],
                    (source or 'unknown')[:40],
                    (referrer or '')[:500],
                    hash_ip(ip),
                    confirm_t, unsub_t,
                ],
            )
            row = subscriber_by_email(email_lower) or {}
            row['_action'] = 'created'
            return row

        if existing.get('confirmed_at') and not existing.get('unsubscribed_at'):
            existing['_action'] = 'already_confirmed'
            return existing

        # Pending or previously unsubscribed — rotate tokens + clear the
        # unsubscribed state so the user opts back in fresh.
        confirm_t = _new_token()
        unsub_t = _new_token()
        conn.execute(
            "UPDATE subscribers SET confirm_token = ?, unsubscribe_token = ?, "
            "ts = CURRENT_TIMESTAMP, lang = ?, source = ?, referrer = ?, "
            "ip_hash = ?, unsubscribed_at = NULL "
            "WHERE id = ?",
            [
                confirm_t, unsub_t,
                (lang or 'sr')[:5],
                (source or 'unknown')[:40],
                (referrer or '')[:500],
                hash_ip(ip),
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

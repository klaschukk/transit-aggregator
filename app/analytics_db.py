"""Analytics SQLite connection — read/write, separate file from the main
read-only transit DB.

Concurrency model
-----------------
SQLite WAL mode allows unlimited concurrent readers and one writer at a
time. Writers queue (busy_timeout=10s) instead of raising a lock error,
so the retry logic that was required for DuckDB is gone entirely. Each
gunicorn worker process uses thread-local connections; the file lock is
acquired per-write and released immediately — no request-long file locks.
"""
import hashlib
import logging
import sqlite3
import threading
from datetime import date as _date, datetime as _datetime
from pathlib import Path

# Register adapters so Python date/datetime objects are stored as ISO strings,
# and converters so they come back as datetime objects (template-compatible).
sqlite3.register_adapter(_date, lambda d: d.isoformat())
sqlite3.register_adapter(_datetime, lambda dt: dt.isoformat())


def _parse_ts(val: bytes) -> _datetime | str:
    s = val.decode('utf-8') if isinstance(val, bytes) else val
    for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ'):
        try:
            return _datetime.strptime(s.replace('+00:00', ''), fmt)
        except ValueError:
            continue
    return s


sqlite3.register_converter('TIMESTAMP', _parse_ts)

from flask import current_app

from . import observability

logger = logging.getLogger(__name__)

_local = threading.local()


def _path() -> str:
    return current_app.config['ANALYTICS_DB_PATH']


def _get_conn() -> sqlite3.Connection:
    """Return a per-thread SQLite connection. Opens in WAL mode on first
    use. Reconnects when the configured path changes (tests swap DBs)."""
    target = _path()
    conn: sqlite3.Connection | None = getattr(_local, 'conn', None)
    if conn is None or getattr(_local, 'path', None) != target:
        if conn is not None:
            try:
                conn.close()
            except sqlite3.Error:
                pass
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            target,
            timeout=10,
            check_same_thread=False,
            isolation_level=None,  # autocommit; explicit BEGIN where needed
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA foreign_keys=ON')
        _local.conn = conn
        _local.path = target
    return conn


def close_thread_conn() -> None:
    """Close the per-thread connection if any. Wired into Flask's
    teardown_appcontext so tests that swap ANALYTICS_DB_PATH get a clean
    slate. In production the overhead is negligible."""
    conn = getattr(_local, 'conn', None)
    if conn is None:
        return
    try:
        conn.close()
    except sqlite3.Error:
        pass
    _local.conn = None
    _local.path = None


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS ba_clicks (
    id          INTEGER PRIMARY KEY,
    route_slug  TEXT,
    surface     TEXT,
    operator    TEXT,
    trip_time   TEXT,
    partner     TEXT,
    ip_hash     TEXT,
    user_agent  TEXT,
    referrer    TEXT,
    ts          TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
CREATE INDEX IF NOT EXISTS ba_clicks_ts_idx   ON ba_clicks(ts);
CREATE INDEX IF NOT EXISTS ba_clicks_slug_idx ON ba_clicks(route_slug);

CREATE TABLE IF NOT EXISTS reviews (
    id                 INTEGER PRIMARY KEY,
    route_slug         TEXT NOT NULL,
    rating             INTEGER NOT NULL,
    comment            TEXT NOT NULL,
    author_name        TEXT NOT NULL,
    email_hash         TEXT,
    lang               TEXT,
    ts                 TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    status             TEXT DEFAULT 'pending',
    moderated_at       TEXT,
    moderator_note     TEXT,
    deletion_requested INTEGER DEFAULT 0,
    ip_hash            TEXT
);
CREATE INDEX IF NOT EXISTS reviews_route_idx  ON reviews(route_slug, status);
CREATE INDEX IF NOT EXISTS reviews_email_idx  ON reviews(email_hash);
CREATE INDEX IF NOT EXISTS reviews_status_idx ON reviews(status, ts);

CREATE TABLE IF NOT EXISTS subscribers (
    id                INTEGER PRIMARY KEY,
    email             TEXT NOT NULL,
    email_lower       TEXT NOT NULL,
    lang              TEXT,
    source            TEXT,
    referrer          TEXT,
    ip_hash           TEXT,
    ts                TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    confirm_token     TEXT,
    confirmed_at      TEXT,
    unsubscribe_token TEXT,
    unsubscribed_at   TEXT,
    route_slug        TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS subscribers_email_uq   ON subscribers(email_lower);
CREATE INDEX        IF NOT EXISTS subscribers_confirm_idx ON subscribers(confirm_token);
CREATE INDEX        IF NOT EXISTS subscribers_unsub_idx   ON subscribers(unsubscribe_token);
CREATE INDEX        IF NOT EXISTS subscribers_route_idx   ON subscribers(route_slug);

CREATE TABLE IF NOT EXISTS price_snapshots (
    route_slug  TEXT    NOT NULL,
    date        TEXT    NOT NULL,
    min_price   INTEGER,
    max_price   INTEGER,
    avg_price   REAL,
    trip_count  INTEGER,
    snapshot_ts TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    PRIMARY KEY (route_slug, date)
);
CREATE INDEX IF NOT EXISTS price_snapshots_route_idx ON price_snapshots(route_slug, date);

CREATE TABLE IF NOT EXISTS price_alerts_sent (
    id            INTEGER PRIMARY KEY,
    subscriber_id INTEGER NOT NULL,
    route_slug    TEXT    NOT NULL,
    old_price     INTEGER,
    new_price     INTEGER,
    drop_pct      INTEGER,
    sent_at       TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    delivered_ok  INTEGER
);
CREATE INDEX IF NOT EXISTS price_alerts_sent_sub_idx
    ON price_alerts_sent(subscriber_id, route_slug, sent_at);
CREATE INDEX IF NOT EXISTS price_alerts_sent_route_idx
    ON price_alerts_sent(route_slug, sent_at);

CREATE TABLE IF NOT EXISTS campaigns (
    id               INTEGER PRIMARY KEY,
    slug             TEXT NOT NULL,
    subject_sr       TEXT, subject_en TEXT, subject_ru TEXT,
    preheader_sr     TEXT, preheader_en TEXT, preheader_ru TEXT,
    body_md_sr       TEXT, body_md_en TEXT, body_md_ru TEXT,
    audience_filter  TEXT,
    status           TEXT NOT NULL DEFAULT 'draft',
    template_kind    TEXT,
    created_at       TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    scheduled_at     TEXT,
    sent_at          TEXT,
    recipients_count INTEGER DEFAULT 0,
    delivered_count  INTEGER DEFAULT 0,
    opened_count     INTEGER DEFAULT 0,
    clicked_count    INTEGER DEFAULT 0,
    bounced_count    INTEGER DEFAULT 0,
    unsub_count      INTEGER DEFAULT 0
);
CREATE UNIQUE INDEX IF NOT EXISTS campaigns_slug_uq    ON campaigns(slug);
CREATE INDEX        IF NOT EXISTS campaigns_status_idx ON campaigns(status, scheduled_at);

CREATE TABLE IF NOT EXISTS campaign_sends (
    id              INTEGER PRIMARY KEY,
    campaign_id     INTEGER NOT NULL,
    subscriber_id   INTEGER NOT NULL,
    sent_at         TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    delivered_at    TEXT,
    opened_at       TEXT,
    clicked_at      TEXT,
    bounced_at      TEXT,
    unsubscribed_at TEXT,
    error           TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS campaign_sends_uq
    ON campaign_sends(campaign_id, subscriber_id);
CREATE INDEX IF NOT EXISTS campaign_sends_campaign_idx
    ON campaign_sends(campaign_id, sent_at);

CREATE TABLE IF NOT EXISTS email_suppressions (
    email_lower TEXT PRIMARY KEY,
    reason      TEXT,
    added_at    TIMESTAMP DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    note        TEXT
);

CREATE TABLE IF NOT EXISTS ab_events (
    id         INTEGER PRIMARY KEY,
    experiment TEXT    NOT NULL,
    variant    TEXT    NOT NULL,
    event_type TEXT    NOT NULL,
    surface    TEXT,
    user_seed  TEXT,
    value      REAL    DEFAULT 1.0,
    ts         TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    ts_date    TEXT    DEFAULT (date('now'))
);
CREATE INDEX IF NOT EXISTS ab_events_exp_idx
    ON ab_events(experiment, event_type, ts_date);
CREATE INDEX IF NOT EXISTS ab_events_exp_variant_idx
    ON ab_events(experiment, variant, event_type);

CREATE TABLE IF NOT EXISTS data_snapshots (
    snapshot_date TEXT    NOT NULL,
    kind          TEXT    NOT NULL,
    key           TEXT    NOT NULL,
    value         INTEGER NOT NULL,
    PRIMARY KEY (snapshot_date, kind, key)
);
CREATE INDEX IF NOT EXISTS data_snapshots_kind_idx
    ON data_snapshots(kind, snapshot_date);

-- AI-composed far-destination itineraries (Beograd->Bangkok etc.). Cached so
-- each pair hits Groq at most once; `hits` ranks the most-searched pairs for
-- the Phase-2 static SEO pages.
CREATE TABLE IF NOT EXISTS composed_routes (
    pair_key   TEXT NOT NULL,
    lang       TEXT NOT NULL,
    from_city  TEXT,
    to_city    TEXT,
    payload    TEXT NOT NULL,
    hits       INTEGER DEFAULT 1,
    created_at TEXT    DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    PRIMARY KEY (pair_key, lang)
);
CREATE INDEX IF NOT EXISTS composed_routes_hits_idx
    ON composed_routes(hits DESC);

-- BusTicket4 affiliate SALES (conversions), mirrored hourly from their flaky
-- panel by scripts/bt4_sales_fetch.py so we can read them in our own admin.
-- One row per calendar day; upserted each fetch (last run wins).
CREATE TABLE IF NOT EXISTS bt4_sales (
    ymd        TEXT PRIMARY KEY,   -- '2026-06-13'
    tickets    INTEGER NOT NULL,
    value      REAL    NOT NULL,
    fetched_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
"""


def init_schema() -> None:
    """Idempotent schema creation. Runs every app boot."""
    try:
        conn = _get_conn()
        conn.executescript(_SCHEMA_SQL)
        # Migration: add ba_clicks.partner to DBs created before it existed so
        # outbound clicks break down per affiliate. ADD COLUMN is a no-op error
        # ("duplicate column name") once applied — swallow it.
        try:
            conn.execute("ALTER TABLE ba_clicks ADD COLUMN partner TEXT")
        except sqlite3.OperationalError:
            pass
        logger.info("analytics_db schema ready at %s", _path())
    except sqlite3.Error as exc:
        logger.error("analytics_db init failed: %s", exc)
        observability.capture_exception(exc, subsystem='analytics_db', op='init_schema')


def hash_ip(ip: str) -> str:
    salt = current_app.config.get('IP_HASH_SALT', '') or 'dev-only-rotate-me'
    return hashlib.sha256((salt + '|' + (ip or '')).encode('utf-8')).hexdigest()[:32]


def insert_ba_click(
    route_slug: str,
    surface: str,
    operator: str,
    trip_time: str,
    ip: str,
    user_agent: str,
    referrer: str,
    partner: str = '',
) -> None:
    try:
        _get_conn().execute(
            "INSERT INTO ba_clicks (route_slug, surface, operator, trip_time, partner, ip_hash, user_agent, referrer) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (route_slug or '')[:200],
                (surface or '')[:40],
                (operator or '')[:100],
                (trip_time or '')[:10],
                (partner or '')[:40],
                hash_ip(ip),
                (user_agent or '')[:300],
                (referrer or '')[:500],
            ],
        )
    except sqlite3.Error as exc:
        logger.error("insert_ba_click failed: %s", exc)
        observability.capture_exception(
            exc, subsystem='analytics_db', op='insert_ba_click',
            route_slug=route_slug, surface=surface,
        )
        _local.conn = None


def upsert_bt4_sales(rows: list[dict]) -> int:
    """Insert/refresh daily BusTicket4 sales. Each row: {ymd, tickets, value}.

    Mirrored from BusTicket4's affiliate panel by scripts/bt4_sales_fetch.py.
    Upserts per day (last fetch wins). Returns rows written; autocommit."""
    if not rows:
        return 0
    try:
        _get_conn().executemany(
            "INSERT INTO bt4_sales (ymd, tickets, value) VALUES (?, ?, ?) "
            "ON CONFLICT(ymd) DO UPDATE SET tickets=excluded.tickets, "
            "value=excluded.value, "
            "fetched_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')",
            [(r['ymd'], int(r.get('tickets') or 0), float(r.get('value') or 0)) for r in rows],
        )
        return len(rows)
    except (sqlite3.Error, KeyError, ValueError, TypeError) as exc:
        logger.error("upsert_bt4_sales failed: %s", exc)
        observability.capture_exception(exc, subsystem='analytics_db', op='upsert_bt4_sales')
        _local.conn = None
        return 0


def bt4_sales_summary(days: int = 30) -> dict:
    """All-time totals + recent non-zero daily rows for the admin. Empty-safe."""
    try:
        agg = query(
            "SELECT COALESCE(SUM(tickets),0) AS t, COALESCE(SUM(value),0) AS v, "
            "MAX(fetched_at) AS f, COUNT(*) AS n FROM bt4_sales"
        )
        recent = query(
            "SELECT ymd, tickets, value FROM bt4_sales "
            "WHERE date(ymd) >= date('now', ?) AND tickets > 0 ORDER BY ymd DESC",
            [f'-{int(days)} days'],
        )
        row = agg[0] if agg else {}
        return {
            'total_tickets': row.get('t') or 0,
            'total_value': row.get('v') or 0,
            'last_fetched': row.get('f'),
            'days_with_data': row.get('n') or 0,
            'recent': recent,
        }
    except sqlite3.Error as exc:
        logger.error("bt4_sales_summary failed: %s", exc)
        return {'total_tickets': 0, 'total_value': 0, 'last_fetched': None,
                'days_with_data': 0, 'recent': []}


def insert_ab_event(
    experiment: str,
    variant: str,
    event_type: str,
    surface: str = '',
    user_seed: str = '',
    value: float = 1.0,
) -> None:
    try:
        _get_conn().execute(
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
    except sqlite3.Error as exc:
        logger.error("insert_ab_event failed: %s", exc)
        observability.capture_exception(
            exc, subsystem='analytics_db', op='insert_ab_event',
            experiment=experiment, variant=variant,
        )
        _local.conn = None


def ab_event_summary(experiment: str) -> list[dict]:
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
    return query(
        """
        SELECT ts_date, variant, COUNT(*) AS exposures
        FROM ab_events
        WHERE experiment = ?
          AND event_type = 'exposure'
          AND ts_date >= date('now', ? || ' days')
        GROUP BY ts_date, variant
        ORDER BY ts_date DESC, variant
        """,
        [experiment, f'-{max(0, int(days))}'],
    )


def ab_export_rows(experiment: str | None = None) -> list[dict]:
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
    try:
        cur = _get_conn().execute(sql, params or [])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    except sqlite3.Error as exc:
        logger.error("analytics_db query failed: %s | %s", exc, sql)
        _local.conn = None
        return []


# ── composed (AI) far-destination routes ────────────────────────────────


def get_composed_route(pair_key: str, lang: str) -> str | None:
    """Return the cached itinerary JSON for a pair+lang, or None. Bumps `hits`
    so the most-searched far pairs surface first for Phase-2 SEO generation."""
    rows = query(
        "SELECT payload FROM composed_routes WHERE pair_key = ? AND lang = ?",
        [pair_key, lang],
    )
    if not rows:
        return None
    try:
        _get_conn().execute(
            "UPDATE composed_routes SET hits = hits + 1 "
            "WHERE pair_key = ? AND lang = ?",
            [pair_key, lang],
        )
    except sqlite3.Error:
        pass
    return rows[0]['payload']


def composed_far_pairs(lang: str) -> list[dict]:
    """Far pairs with a FEASIBLE cached itinerary for `lang`, sorted by
    pair_key. Shape: [{'pair_key','from_city','to_city','created_at'}].

    Infeasible rows are cached too (so Groq isn't re-asked about impossible
    trips) but are filtered out here: their /voznja pages render no itinerary
    and stay noindex, so the sitemap and internal links must skip them."""
    import json as _json
    out = []
    for row in query(
        "SELECT pair_key, from_city, to_city, payload, created_at "
        "FROM composed_routes WHERE lang = ? ORDER BY pair_key", [lang],
    ):
        try:
            data = _json.loads(row.get('payload') or '')
        except ValueError:
            continue
        if not (isinstance(data, dict) and data.get('feasible')):
            continue
        out.append({k: row.get(k)
                    for k in ('pair_key', 'from_city', 'to_city', 'created_at')})
    return out


def upsert_composed_route(
    pair_key: str, lang: str, from_city: str, to_city: str, payload: str,
) -> None:
    """Store (or refresh) an AI-composed itinerary. Idempotent per pair+lang."""
    try:
        _get_conn().execute(
            "INSERT INTO composed_routes (pair_key, lang, from_city, to_city, payload) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(pair_key, lang) DO UPDATE SET "
            "payload = excluded.payload, hits = composed_routes.hits + 1",
            [pair_key[:120], lang[:8], (from_city or '')[:120],
             (to_city or '')[:120], payload],
        )
    except sqlite3.Error as exc:
        logger.error("upsert_composed_route failed: %s", exc)


def top_composed_routes(limit: int = 300) -> list[dict]:
    """Most-searched composed pairs (feeds Phase-2 static SEO pages)."""
    return query(
        "SELECT pair_key, lang, from_city, to_city, payload, hits "
        "FROM composed_routes ORDER BY hits DESC LIMIT ?",
        [limit],
    )


# ── reviews ─────────────────────────────────────────────────────────────


def hash_email(email: str) -> str:
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
        cur = _get_conn().execute(
            "INSERT INTO reviews (route_slug, rating, comment, author_name, "
            "email_hash, lang, status, ip_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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
        return cur.lastrowid
    except sqlite3.Error as exc:
        logger.error("insert_review failed: %s", exc)
        _local.conn = None
        return None


def is_trusted_author(email: str) -> bool:
    if not email:
        return False
    try:
        cur = _get_conn().execute(
            "SELECT COUNT(*) FROM reviews WHERE email_hash = ? AND status = 'approved'",
            [hash_email(email)],
        )
        row = cur.fetchone()
        return bool(row and row[0] >= 3)
    except sqlite3.Error as exc:
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


def review_block(route_slug: str) -> tuple[list[dict], dict | None]:
    """(approved reviews, aggregate rating) for a slug. Degrades to ([], None)
    on any analytics-DB failure but REPORTS it — the route-level callers used to
    swallow this silently, so a locked/corrupt analytics DB just made reviews
    vanish site-wide with nothing in monitoring."""
    try:
        return approved_reviews(route_slug), aggregate_rating(route_slug)
    except Exception as exc:  # noqa: BLE001 — page must render without reviews
        observability.capture_exception(exc, subsystem='reviews', slug=route_slug)
        return [], None


def pending_reviews(limit: int = 100) -> list[dict]:
    return query(
        "SELECT id, route_slug, rating, comment, author_name, lang, ts, "
        "       deletion_requested, email_hash "
        "FROM reviews WHERE status = 'pending' OR deletion_requested = 1 "
        "ORDER BY deletion_requested DESC, ts ASC LIMIT ?",
        [limit],
    )


def set_review_status(review_id: int, status: str, note: str = '') -> bool:
    if status not in ('approved', 'rejected', 'deleted'):
        return False
    try:
        conn = _get_conn()
        if status == 'deleted':
            conn.execute(
                "UPDATE reviews SET status='deleted', "
                "moderated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), "
                "moderator_note=?, author_name='[deleted]', comment='[deleted]', "
                "email_hash=NULL, deletion_requested=0 "
                "WHERE id = ?",
                [note[:200], review_id],
            )
        else:
            conn.execute(
                "UPDATE reviews SET status=?, "
                "moderated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), "
                "moderator_note=? WHERE id = ?",
                [status, note[:200], review_id],
            )
        return True
    except sqlite3.Error as exc:
        logger.error("set_review_status failed: %s", exc)
        _local.conn = None
        return False


# ── subscribers ─────────────────────────────────────────────────────────

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

        confirm_t = _new_token()
        unsub_t = _new_token()
        conn.execute(
            "UPDATE subscribers SET confirm_token = ?, unsubscribe_token = ?, "
            "ts = strftime('%Y-%m-%dT%H:%M:%SZ','now'), lang = ?, source = ?, "
            "referrer = ?, ip_hash = ?, unsubscribed_at = NULL, route_slug = ? "
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
    except sqlite3.Error as exc:
        logger.error("insert_or_refresh_subscriber failed: %s", exc)
        _local.conn = None
        return None


def confirm_subscriber(token: str) -> tuple[str, dict | None]:
    if not token:
        return 'invalid', None
    try:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT id, email, lang, unsubscribe_token, confirmed_at, ts "
            "FROM subscribers WHERE confirm_token = ?",
            [token],
        )
        rows = cur.fetchall()
        if not rows:
            return 'invalid', None
        sub_id, email, lang, unsub_token, confirmed_at, created_at = rows[0]
        row = {'id': sub_id, 'email': email, 'lang': lang, 'unsubscribe_token': unsub_token}
        if confirmed_at is not None:
            return 'already', row
        from datetime import datetime, timedelta
        if created_at is not None:
            try:
                if isinstance(created_at, str):
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_dt = created_at
                age = (datetime.now(created_dt.tzinfo) if created_dt.tzinfo else datetime.utcnow()) - created_dt
                if age > timedelta(days=_CONFIRM_TTL_DAYS):
                    return 'expired', row
            except (ValueError, AttributeError):
                pass
        conn.execute(
            "UPDATE subscribers SET confirmed_at = strftime('%Y-%m-%dT%H:%M:%SZ','now'), "
            "confirm_token = NULL WHERE id = ?",
            [sub_id],
        )
        return 'ok', row
    except sqlite3.Error as exc:
        logger.error("confirm_subscriber failed: %s", exc)
        _local.conn = None
        return 'invalid', None


def unsubscribe_subscriber(token: str) -> bool:
    if not token:
        return False
    try:
        cur = _get_conn().execute(
            "UPDATE subscribers SET unsubscribed_at = strftime('%Y-%m-%dT%H:%M:%SZ','now') "
            "WHERE unsubscribe_token = ? AND unsubscribed_at IS NULL "
            "RETURNING id",
            [token],
        )
        return cur.fetchone() is not None
    except sqlite3.Error as exc:
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


# ── price alerts ─────────────────────────────────────────────────────────


def insert_or_refresh_price_snapshot(
    route_slug: str,
    *,
    snapshot_date,
    min_price: int | None,
    max_price: int | None,
    avg_price: float | None,
    trip_count: int,
) -> bool:
    conn = None
    try:
        conn = _get_conn()
        conn.execute("BEGIN")
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
    except sqlite3.Error as exc:
        if conn is not None:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.Error:
                pass
        logger.error("insert_or_refresh_price_snapshot failed: %s", exc)
        _local.conn = None
        return False


def price_snapshots_for_route(route_slug: str, days: int = 7) -> list[dict]:
    days_i = max(0, int(days))
    rows = query(
        "SELECT date, min_price, max_price, avg_price, trip_count "
        "FROM price_snapshots "
        f"WHERE route_slug = ? AND date >= date('now', '-{days_i} days') "
        "ORDER BY date DESC",
        [route_slug],
    )
    # Convert ISO date strings back to Python date objects so evaluate_snapshots
    # can compare with date.today() directly (matches DuckDB's return type).
    for row in rows:
        if isinstance(row.get('date'), str):
            try:
                row['date'] = _date.fromisoformat(row['date'])
            except ValueError:
                pass
    return rows


def subscribers_for_route_alerts(route_slug: str) -> list[dict]:
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
    days_i = max(0, int(within_days))
    rows = query(
        "SELECT 1 FROM price_alerts_sent "
        "WHERE subscriber_id = ? AND route_slug = ? "
        f"  AND sent_at >= datetime('now', '-{days_i} days') "
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
        _get_conn().execute(
            "INSERT INTO price_alerts_sent "
            "(subscriber_id, route_slug, old_price, new_price, drop_pct, delivered_ok) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [subscriber_id, route_slug, old_price, new_price, drop_pct, int(delivered_ok)],
        )
    except sqlite3.Error as exc:
        logger.error("record_price_alert_sent failed: %s", exc)
        _local.conn = None


def request_review_deletion(review_id: int, email: str) -> bool:
    if not email:
        return False
    try:
        cur = _get_conn().execute(
            "UPDATE reviews SET deletion_requested = 1 "
            "WHERE id = ? AND email_hash = ? AND status != 'deleted' "
            "RETURNING id",
            [review_id, hash_email(email)],
        )
        return cur.fetchone() is not None
    except sqlite3.Error as exc:
        logger.error("request_review_deletion failed: %s", exc)
        return False


# ── data snapshots ───────────────────────────────────────────────────────


def record_snapshot(snapshot_date: str, kind: str, key: str, value: int) -> None:
    try:
        _get_conn().execute(
            "INSERT OR REPLACE INTO data_snapshots "
            "(snapshot_date, kind, key, value) VALUES (?, ?, ?, ?)",
            [snapshot_date, kind, key, value],
        )
    except sqlite3.Error as exc:
        logger.error("record_snapshot failed: %s", exc)
        _local.conn = None


def diff_snapshots(
    kind: str,
    date_a: str | None = None,
    date_b: str | None = None,
) -> list[dict]:
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
    except sqlite3.Error as exc:
        logger.error("diff_snapshots failed: %s", exc)
        return []

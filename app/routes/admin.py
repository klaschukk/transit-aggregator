"""Admin dashboards — basic-auth gated, noindex, noexport.

Only ADMIN_USER + ADMIN_PASS env vars unlock access. When either is unset
the routes return 503 so we don't silently run wide-open on misconfigured
deployments.
"""
import hmac
from functools import wraps

from flask import (
    Blueprint, render_template, current_app, Response, request, redirect,
    url_for, flash,
)

from app import analytics_db
from app.extensions import csrf

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _basic_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_app.config.get('ADMIN_USER') or ''
        pw = current_app.config.get('ADMIN_PASS') or ''
        if not user or not pw:
            # Ops hasn't provisioned creds — refuse rather than expose.
            return Response('admin disabled', status=503)
        auth = request.authorization
        if (
            not auth
            or not hmac.compare_digest(auth.username or '', user)
            or not hmac.compare_digest(auth.password or '', pw)
        ):
            return Response(
                'auth required',
                status=401,
                headers={'WWW-Authenticate': 'Basic realm="prevozni-admin"'},
            )
        return f(*args, **kwargs)
    return wrapper


@admin_bp.after_request
def _no_index(resp):
    # Belt-and-braces — admin pages must never end up in a search index.
    resp.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
    resp.headers['Cache-Control'] = 'private, no-store'
    return resp


@admin_bp.route('/revenue')
@_basic_auth_required
def revenue():
    """Dashboard: Bookaway affiliate click metrics from analytics.duckdb."""
    totals_7 = _total_clicks_since(7)
    totals_30 = _total_clicks_since(30)

    top_routes_7 = analytics_db.query("""
        SELECT route_slug, surface, COUNT(*) AS clicks
        FROM ba_clicks
        WHERE ts >= CURRENT_TIMESTAMP - INTERVAL '7 days'
          AND route_slug != ''
        GROUP BY route_slug, surface
        ORDER BY clicks DESC
        LIMIT 20
    """)
    top_routes_30 = analytics_db.query("""
        SELECT route_slug, surface, COUNT(*) AS clicks
        FROM ba_clicks
        WHERE ts >= CURRENT_TIMESTAMP - INTERVAL '30 days'
          AND route_slug != ''
        GROUP BY route_slug, surface
        ORDER BY clicks DESC
        LIMIT 20
    """)

    by_surface_30 = analytics_db.query("""
        SELECT COALESCE(NULLIF(surface, ''), 'unknown') AS surface, COUNT(*) AS clicks
        FROM ba_clicks
        WHERE ts >= CURRENT_TIMESTAMP - INTERVAL '30 days'
        GROUP BY surface
        ORDER BY clicks DESC
    """)

    daily = analytics_db.query("""
        SELECT CAST(ts AS DATE) AS day, COUNT(*) AS clicks
        FROM ba_clicks
        WHERE ts >= CURRENT_TIMESTAMP - INTERVAL '30 days'
        GROUP BY day
        ORDER BY day
    """)

    # Normalise for the bar chart: max daily for sizing bars.
    max_daily = max((r['clicks'] for r in daily), default=1) or 1
    for r in daily:
        r['pct'] = int((r['clicks'] / max_daily) * 100)

    return render_template(
        'admin/revenue.html',
        totals_7=totals_7,
        totals_30=totals_30,
        top_routes_7=top_routes_7,
        top_routes_30=top_routes_30,
        by_surface_30=by_surface_30,
        daily=daily,
    )


def _total_clicks_since(days: int) -> int:
    # DuckDB doesn't bind INTERVAL via parameters, but `days` is an int literal
    # we control, not user input.
    days = max(1, int(days))
    rows = analytics_db.query(
        f"SELECT COUNT(*) AS c FROM ba_clicks WHERE ts >= CURRENT_TIMESTAMP - INTERVAL '{days} days'"
    )
    return rows[0]['c'] if rows else 0


# ── Reviews moderation ────────────────────────────────────────────────


@admin_bp.route('/reviews')
@_basic_auth_required
def reviews():
    """Moderation queue: pending reviews + deletion requests.

    Approved/rejected history is not shown by default to keep the queue
    visually tight — add `?all=1` to see the full log.
    """
    show_all = request.args.get('all') == '1'
    if show_all:
        items = analytics_db.query(
            "SELECT id, route_slug, rating, comment, author_name, status, "
            "       lang, ts, deletion_requested, email_hash, moderator_note "
            "FROM reviews ORDER BY ts DESC LIMIT 200"
        )
    else:
        items = analytics_db.pending_reviews(limit=200)

    stats = analytics_db.query(
        "SELECT status, COUNT(*) AS c FROM reviews GROUP BY status"
    )
    counts = {row['status']: row['c'] for row in stats}

    return render_template(
        'admin/reviews.html',
        items=items, counts=counts, show_all=show_all,
    )


@admin_bp.route('/reviews/<int:review_id>/<action>', methods=['POST'])
@_basic_auth_required
@csrf.exempt
def review_action(review_id: int, action: str):
    """Approve / reject / delete a review. All three are POST-only so a
    stray GET crawl can't mutate state."""
    if action not in ('approve', 'reject', 'delete'):
        return Response('bad action', status=400)

    note = (request.form.get('note') or '')[:200]
    status_map = {'approve': 'approved', 'reject': 'rejected', 'delete': 'deleted'}
    new_status = status_map[action]

    ok = analytics_db.set_review_status(review_id, new_status, note)
    if not ok:
        return Response('update failed', status=500)

    # "Approved" notifications are best-effort — we don't retain plaintext
    # emails, so this is a no-op in the current infra. Kept as a stub so
    # the callsite exists when Mailgun lands.
    if new_status == 'approved':
        from app.notifier import notify_author
        # We no longer have the plaintext email at moderation time, so we
        # log a stub record. Admin UI can show "approved" manually.
        notify_author(
            email='',
            subject='Your review is live on Prevozni.com',
            body=f'Review id {review_id} was approved. '
                 f'Once SMTP is configured this will become a real email.',
        )

    return redirect(url_for('admin.reviews'))

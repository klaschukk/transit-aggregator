"""Admin dashboards — basic-auth gated, noindex, noexport.

Only ADMIN_USER + ADMIN_PASS env vars unlock access. When either is unset
the routes return 503 so we don't silently run wide-open on misconfigured
deployments.
"""
import hmac
from functools import wraps

from flask import Blueprint, render_template, current_app, Response, request

from app import analytics_db

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

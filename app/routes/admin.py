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


@admin_bp.route('/subscribers')
@_basic_auth_required
def subscribers():
    """Newsletter + price-alert subscribers, filterable by source/route.

    `?source=price_alert&route=<slug>` narrows to a single route; without
    filters the latest 200 rows across all signups are shown. Emails are
    truncated in the listing — full addresses are visible only by clicking
    into a row (future improvement; for now we show first/last 3 chars).
    """
    source = (request.args.get('source') or '').strip()[:40]
    route = (request.args.get('route') or '').strip()[:200]

    where = []
    params: list = []
    if source:
        where.append('source = ?')
        params.append(source)
    if route:
        where.append('route_slug = ?')
        params.append(route)
    clause = ('WHERE ' + ' AND '.join(where)) if where else ''

    items = analytics_db.query(
        f"SELECT id, email, lang, source, route_slug, ts, "
        f"       confirmed_at, unsubscribed_at "
        f"FROM subscribers {clause} "
        f"ORDER BY ts DESC LIMIT 200",
        params,
    )
    stats = analytics_db.subscriber_stats()
    # By-source breakdown for the filter chip row.
    by_source = analytics_db.query(
        "SELECT COALESCE(NULLIF(source, ''), 'unknown') AS source, "
        "       COUNT(*) AS total, "
        "       COUNT(*) FILTER (WHERE confirmed_at IS NOT NULL "
        "                        AND unsubscribed_at IS NULL) AS confirmed "
        "FROM subscribers GROUP BY source ORDER BY total DESC"
    )
    # Top-10 routes by confirmed-subscriber count (price_alert only).
    top_routes = analytics_db.query(
        "SELECT route_slug, COUNT(*) AS total "
        "FROM subscribers "
        "WHERE source = 'price_alert' AND route_slug IS NOT NULL "
        "  AND confirmed_at IS NOT NULL AND unsubscribed_at IS NULL "
        "GROUP BY route_slug ORDER BY total DESC LIMIT 10"
    )
    return render_template(
        'admin/subscribers.html',
        items=items, stats=stats, by_source=by_source, top_routes=top_routes,
        filter_source=source, filter_route=route,
    )


@admin_bp.route('/price-alerts')
@_basic_auth_required
def price_alerts():
    """History of sent price-drop emails — one row per delivery.

    Success rate here is "delivered_ok from the SMTP layer", not
    open/click — for that we'd need a webhook integration (Mailgun,
    Postmark). Until then this is the best on-box signal we have.
    """
    items = analytics_db.query(
        "SELECT pa.id, pa.route_slug, pa.old_price, pa.new_price, pa.drop_pct, "
        "       pa.sent_at, pa.delivered_ok, "
        "       s.email, s.lang "
        "FROM price_alerts_sent pa "
        "LEFT JOIN subscribers s ON s.id = pa.subscriber_id "
        "ORDER BY pa.sent_at DESC LIMIT 200"
    )
    totals = analytics_db.query(
        "SELECT "
        "  COUNT(*) AS total, "
        "  COUNT(*) FILTER (WHERE delivered_ok = TRUE) AS delivered, "
        "  COUNT(*) FILTER (WHERE delivered_ok = FALSE) AS failed, "
        "  COUNT(DISTINCT subscriber_id) AS recipients, "
        "  COUNT(DISTINCT route_slug) AS routes "
        "FROM price_alerts_sent"
    )
    by_day = analytics_db.query(
        "SELECT CAST(sent_at AS DATE) AS day, COUNT(*) AS c "
        "FROM price_alerts_sent "
        "WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '30 days' "
        "GROUP BY day ORDER BY day DESC"
    )
    return render_template(
        'admin/price_alerts.html',
        items=items,
        totals=(totals[0] if totals else {}),
        by_day=by_day,
    )


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


# ── Newsletter compose + dispatch + Mailgun webhook ────────────────────

import json as _json
import hmac as _hmac
import hashlib as _hashlib

from app.newsletter import campaigns as _cmp
from app.newsletter import audience as _aud
from app.newsletter import validator as _val
from app.newsletter import dispatch as _disp
from app.newsletter import render as _render
from app import mailer as _mailer


@admin_bp.route('/newsletter')
@_basic_auth_required
def newsletter_index():
    """List all campaigns with quick stats — entry point for the admin."""
    rows = _cmp.list_campaigns(limit=100)
    # Live stats per campaign — drives the open/click rate display.
    for row in rows:
        row['live_stats'] = _cmp.stats(int(row['id']))
    suppressions = _cmp.list_suppressions(limit=20)
    return render_template(
        'admin/newsletter/index.html',
        campaigns=rows, suppressions=suppressions,
    )


@admin_bp.route('/newsletter/<int:campaign_id>', methods=['GET', 'POST'])
@_basic_auth_required
@csrf.exempt
def newsletter_compose(campaign_id: int):
    """Compose / preview / validate / test-send / schedule.

    POST verbs (form field `op`):
      save        — persist edits, status stays 'draft'
      validate    — return JSON {score, reasons, details, audience_count}
      test        — send to ADMIN_EMAIL only, no DB writes
      send_now    — full dispatch; redirects to index when done
    """
    campaign = _cmp.get_campaign(campaign_id)
    if not campaign:
        return Response('not found', status=404)

    if request.method == 'POST':
        op = request.form.get('op', '')

        # Read shared edit fields up-front for save / validate paths.
        subjects = {l: (request.form.get(f'subject_{l}') or '').strip()
                    for l in ('sr', 'en', 'ru')}
        preheaders = {l: (request.form.get(f'preheader_{l}') or '').strip()
                      for l in ('sr', 'en', 'ru')}
        bodies = {l: request.form.get(f'body_md_{l}') or ''
                  for l in ('sr', 'en', 'ru')}
        try:
            audience_filter = _json.loads(
                request.form.get('audience_filter_json') or '{}'
            )
        except (ValueError, TypeError):
            audience_filter = {}

        if op == 'validate':
            # Per-language validation; fail = worst across all 3 languages.
            results = {}
            for l in ('sr', 'en', 'ru'):
                if not bodies[l].strip():
                    continue
                score, reasons, details = _val.validate(
                    subjects[l], preheaders[l], bodies[l],
                )
                results[l] = {
                    'score': score,
                    'reasons': [
                        {'severity': r.severity, 'message': r.message,
                         'detail': r.detail} for r in reasons
                    ],
                    'details': details,
                }
            audience_count = _aud.estimate_count(audience_filter)
            return {
                'per_language': results,
                'audience_count': audience_count,
                'passing_score': _val.PASSING_SCORE,
            }

        if op == 'save':
            _cmp.upsert_campaign(
                slug=campaign['slug'],
                template_kind=campaign.get('template_kind') or 'oneoff',
                subjects=subjects,
                preheaders=preheaders,
                bodies=bodies,
                audience_filter=audience_filter,
                status='draft',
            )
            flash('Saved.')
            return redirect(url_for('admin.newsletter_compose',
                                    campaign_id=campaign_id))

        if op == 'test':
            # Save first so the test send reflects the operator's latest edits.
            _cmp.upsert_campaign(
                slug=campaign['slug'],
                template_kind=campaign.get('template_kind') or 'oneoff',
                subjects=subjects, preheaders=preheaders, bodies=bodies,
                audience_filter=audience_filter, status='draft',
            )
            admin_email = (current_app.config.get('ADMIN_EMAIL') or '').strip()
            if not admin_email:
                flash('ADMIN_EMAIL not configured — set env var to receive tests.')
                return redirect(url_for('admin.newsletter_compose',
                                        campaign_id=campaign_id))
            base = current_app.config.get('BASE_URL') or 'https://prevozni.com'
            res = _disp.send_campaign(
                campaign_id,
                send_fn=_mailer.send_mail,
                unsub_base_url=base,
                test_email=admin_email,
                dry_run=False,
            )
            flash(f'Test sent to {admin_email}: {res}')
            return redirect(url_for('admin.newsletter_compose',
                                    campaign_id=campaign_id))

        if op == 'send_now':
            # Save first, then dispatch — the validator should have run
            # client-side; the server still re-checks before the loop kicks.
            _cmp.upsert_campaign(
                slug=campaign['slug'],
                template_kind=campaign.get('template_kind') or 'oneoff',
                subjects=subjects, preheaders=preheaders, bodies=bodies,
                audience_filter=audience_filter, status='draft',
            )
            base = current_app.config.get('BASE_URL') or 'https://prevozni.com'
            res = _disp.send_campaign(
                campaign_id,
                send_fn=_mailer.send_mail,
                unsub_base_url=base,
                min_delay_s=0.6,
            )
            flash(f'Send result: {res}')
            return redirect(url_for('admin.newsletter_index'))

        return Response('bad op', status=400)

    # GET — render the compose page.
    audience = _cmp.parse_audience(campaign)
    audience_count = _aud.estimate_count(audience)
    return render_template(
        'admin/newsletter/compose.html',
        campaign=campaign,
        audience_filter_json=_json.dumps(audience, ensure_ascii=False, indent=2),
        audience_count=audience_count,
        passing_score=_val.PASSING_SCORE,
    )


@admin_bp.route('/newsletter/<int:campaign_id>/preview/<lang>')
@_basic_auth_required
def newsletter_preview(campaign_id: int, lang: str):
    """Render the brand-framed HTML preview the operator sees in the
    compose iframe. Lives behind admin auth so search engines can't
    accidentally index it (the X-Robots-Tag also covers this)."""
    if lang not in ('sr', 'en', 'ru'):
        return Response('bad lang', status=400)
    campaign = _cmp.get_campaign(campaign_id)
    if not campaign:
        return Response('not found', status=404)

    subject = campaign.get(f'subject_{lang}') or ''
    preheader = campaign.get(f'preheader_{lang}') or ''
    body_md = campaign.get(f'body_md_{lang}') or ''
    base = current_app.config.get('BASE_URL') or 'https://prevozni.com'
    _, html, _ = _render.render_email(
        subject=subject, preheader=preheader, body_md=body_md, lang=lang,
        unsub_url=f"{base}/api/unsubscribe/PREVIEW",
        source='preview', confirmed_date='',
    )
    return Response(html, mimetype='text/html; charset=utf-8')


# ── Mailgun webhook (signature-verified) ─────────────────────────────

@admin_bp.route('/api/mailgun-webhook', methods=['POST'])
@csrf.exempt
def mailgun_webhook():
    """Mailgun → us. Verifies HMAC signature, updates campaign_sends.

    Lives under /admin so `_no_index` adds X-Robots-Tag (no SEO leak)
    and the basic-auth decorator is *not* applied here — the signing
    key is the auth. The route is csrf-exempt and idempotent: a replayed
    event sets the same column to the same timestamp.
    """
    body = request.get_data() or b''
    signing_key = (current_app.config.get('MAILGUN_WEBHOOK_SIGNING_KEY')
                   or current_app.config.get('MAILGUN_API_KEY') or '')

    # Mailgun event payload format: signature{token, timestamp, signature},
    # event-data{event, recipient, message{headers{message-id}}, ...}
    try:
        payload = _json.loads(body or b'{}')
    except (ValueError, TypeError):
        return Response('invalid json', status=400)

    if signing_key:
        sig = (payload.get('signature') or {})
        token = str(sig.get('token') or '')
        ts = str(sig.get('timestamp') or '')
        provided = str(sig.get('signature') or '')
        expected = _hmac.new(
            signing_key.encode('utf-8'),
            (ts + token).encode('utf-8'),
            _hashlib.sha256,
        ).hexdigest()
        if not _hmac.compare_digest(expected, provided):
            return Response('bad signature', status=403)
    elif current_app.config.get('FLASK_ENV') == 'production':
        # Refuse to accept unsigned events in prod — reputation risk.
        return Response('signing key not configured', status=503)

    event_data = payload.get('event-data') or {}
    event = event_data.get('event') or ''
    recipient = (event_data.get('recipient') or '').lower().strip()
    if not recipient or event not in (
        'delivered', 'opened', 'clicked', 'failed',
        'complained', 'unsubscribed',
    ):
        return Response('ignored', status=200)

    # Mailgun event → DB column.
    column = {
        'delivered': 'delivered_at',
        'opened': 'opened_at',
        'clicked': 'clicked_at',
        'failed': 'bounced_at',
        'complained': 'bounced_at',
        'unsubscribed': 'unsubscribed_at',
    }[event]

    # Resolve recipient email → subscriber id; ignore if not found.
    rows = analytics_db.query(
        "SELECT id FROM subscribers WHERE email_lower = ?", [recipient],
    )
    if not rows:
        return Response('subscriber not found', status=200)
    subscriber_id = int(rows[0]['id'])

    # Find the most recent send for this subscriber to attach the event.
    latest = analytics_db.query(
        "SELECT campaign_id FROM campaign_sends WHERE subscriber_id = ? "
        "ORDER BY sent_at DESC LIMIT 1",
        [subscriber_id],
    )
    if not latest:
        return Response('no matching send', status=200)
    campaign_id = int(latest[0]['campaign_id'])

    conn = analytics_db._get_conn()
    conn.execute(
        f"UPDATE campaign_sends SET {column} = CURRENT_TIMESTAMP "
        "WHERE campaign_id = ? AND subscriber_id = ?",
        [campaign_id, subscriber_id],
    )

    # Auto-suppress on hard bounce or complaint — protect sender rep.
    if event in ('failed', 'complained'):
        _cmp.suppress_email(recipient,
                            'bounce' if event == 'failed' else 'complaint',
                            note=f'mailgun:{event}')

    return Response('ok', status=200)


# ── GDPR data export ─────────────────────────────────────────────────

@admin_bp.route('/api/subscriber-data', methods=['GET'])
@csrf.exempt
def subscriber_data_export():
    """Self-service data export keyed by the subscriber's unsubscribe
    token (which they have on every email they've ever received from us).

    Returns the personal data we hold about that subscriber as JSON —
    GDPR Article 15 access request, satisfied without a manual ticket.
    Output excludes other users' data (campaign_sends rows are filtered
    to this subscriber)."""
    token = request.args.get('token', '').strip()
    if not token:
        return Response('token required', status=400)
    rows = analytics_db.query(
        "SELECT id, email, lang, source, ts, confirmed_at, unsubscribed_at, "
        "       route_slug FROM subscribers WHERE unsubscribe_token = ?",
        [token],
    )
    if not rows:
        return Response('not found', status=404)
    sub = rows[0]
    sends = analytics_db.query(
        "SELECT campaign_id, sent_at, delivered_at, opened_at, clicked_at, "
        "       bounced_at, unsubscribed_at "
        "FROM campaign_sends WHERE subscriber_id = ?",
        [int(sub['id'])],
    )
    return {
        'subscriber': {
            'email': sub['email'],
            'lang': sub.get('lang'),
            'source': sub.get('source'),
            'subscribed_at': str(sub.get('ts') or ''),
            'confirmed_at': str(sub.get('confirmed_at') or ''),
            'unsubscribed_at': str(sub.get('unsubscribed_at') or ''),
            'route_slug': sub.get('route_slug'),
        },
        'campaign_sends': [
            {k: str(v) if v is not None else None for k, v in row.items()}
            for row in sends
        ],
    }


# ── A/B experiment dashboard ─────────────────────────────────────────────


@admin_bp.route('/ab')
@_basic_auth_required
def ab_index():
    """List of live experiments + headline numbers per variant."""
    from app.ab_config import EXPERIMENTS

    rows = []
    for key, spec in EXPERIMENTS.items():
        summary = analytics_db.ab_event_summary(key)
        per_variant: dict[str, dict] = {v: {'exposures': 0, 'conversions': 0}
                                         for v in spec.variants}
        for r in summary:
            v = r['variant']
            if v not in per_variant:
                continue
            if r['event_type'] == 'exposure':
                per_variant[v]['exposures'] += int(r['count'] or 0)
            elif (r['event_type'] or '').startswith('conv:'):
                per_variant[v]['conversions'] += int(r['count'] or 0)
        rows.append({'key': key, 'spec': spec, 'per_variant': per_variant})
    return render_template('admin/ab.html', rows=rows)


@admin_bp.route('/ab/<key>')
@_basic_auth_required
def ab_detail(key: str):
    """Per-experiment funnel: Wilson CI, p-values, sample-size estimate."""
    from app.ab_config import get_spec
    from app.ab_power import (
        wilson_interval, two_proportion_z_test, required_sample_size,
    )
    from datetime import date

    spec = get_spec(key)
    if spec is None:
        return Response('experiment not found', status=404)

    summary = analytics_db.ab_event_summary(key)
    daily = analytics_db.ab_daily_exposures(key, days=14)

    per_variant: dict[str, dict] = {v: {
        'exposures': 0, 'conversions': 0, 'unique_users': 0,
    } for v in spec.variants}
    for r in summary:
        v = r['variant']
        if v not in per_variant:
            continue
        if r['event_type'] == 'exposure':
            per_variant[v]['exposures'] += int(r['count'] or 0)
            per_variant[v]['unique_users'] += int(r['unique_users'] or 0)
        elif (r['event_type'] or '').startswith('conv:'):
            per_variant[v]['conversions'] += int(r['count'] or 0)

    for v, d in per_variant.items():
        n = d['exposures']
        c = d['conversions']
        d['rate'] = (c / n) if n > 0 else 0.0
        low, high = wilson_interval(c, n, alpha=0.05)
        d['ci_low'] = low
        d['ci_high'] = high

    control = spec.variants[0]
    control_d = per_variant[control]
    verdicts = []
    for v in spec.variants[1:]:
        d = per_variant[v]
        z = two_proportion_z_test(
            successes_a=control_d['conversions'], n_a=control_d['exposures'],
            successes_b=d['conversions'], n_b=d['exposures'],
        )
        sufficient = (control_d['conversions'] >= 100
                      and d['conversions'] >= 100)
        verdicts.append({
            'variant': v, 'control': control, 'p_value': z.p_value,
            'lift': z.lift_relative, 'z': z.z,
            'significant': z.significant and sufficient,
            'sufficient': sufficient,
        })

    rate = control_d['rate']
    sample = required_sample_size(rate or 0.04, mde_relative=0.10)
    daily_per_variant = (sum(r['exposures'] for r in daily) / max(1, len(daily))
                         / max(1, len(spec.variants)))
    days_to_sig = sample.days_at_rate(daily_per_variant) if rate > 0 else None

    today = date.today().isoformat()
    runtime_days = (date.today() - date.fromisoformat(spec.started_at)).days \
        if spec.started_at <= today else 0
    eligible_to_call = runtime_days >= spec.min_runtime_days

    return render_template(
        'admin/ab_detail.html',
        spec=spec, per_variant=per_variant, verdicts=verdicts,
        daily=daily, sample=sample, days_to_sig=days_to_sig,
        runtime_days=runtime_days, eligible_to_call=eligible_to_call,
    )


@admin_bp.route('/ab/<key>.csv')
@_basic_auth_required
def ab_export_csv(key: str):
    """Raw event export — one row per exposure/conversion."""
    import csv
    import io
    from app.ab_config import get_spec

    spec = get_spec(key)
    if spec is None:
        return Response('experiment not found', status=404)

    rows = analytics_db.ab_export_rows(experiment=key)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['ts', 'experiment', 'variant', 'event_type', 'surface',
                     'user_seed', 'value'])
    for r in rows:
        writer.writerow([
            r.get('ts'), r.get('experiment'), r.get('variant'),
            r.get('event_type'), r.get('surface'), r.get('user_seed'),
            r.get('value'),
        ])
    return Response(
        buf.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="ab_{key}.csv"'},
    )

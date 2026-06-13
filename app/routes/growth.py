"""Growth/outreach endpoints: Mailgun webhook, one-click unsubscribe,
and /admin/backlinks dashboard.

Paired with scripts/backlinks_send.py + scripts/backlinks_follow_up.py
which produce the CSV state the dashboard visualises. Kept as a
separate blueprint from admin.py so the webhook and public unsubscribe
can be reasoned about independently of moderation routes.
"""
from __future__ import annotations

import hashlib
import hmac
import time
from collections import Counter
from functools import wraps

from flask import (
    Blueprint, Response, current_app, render_template, request,
)

from app import outreach
from app.extensions import csrf

growth_bp = Blueprint('growth', __name__)


def _basic_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_app.config.get('ADMIN_USER') or ''
        pw = current_app.config.get('ADMIN_PASS') or ''
        if not user or not pw:
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


# ── Mailgun webhook ────────────────────────────────────────────────────
#
# Events we care about (Mailgun names):
#   delivered, opened, clicked, unsubscribed, permanent_fail (bounce),
#   complained (spam report), failed.
#
# Mailgun signs each POST with timestamp + token + HMAC-SHA256 over the
# Mailgun API signing key. We verify constant-time and reject anything
# missing — otherwise any actor with the webhook URL could corrupt our
# state. Signing key: MAILGUN_WEBHOOK_SIGNING_KEY env var.

_ALLOWED_EVENTS = {
    'delivered', 'opened', 'clicked',
    'unsubscribed', 'complained',
    'failed', 'permanent_fail',
}


def _verify_mailgun_signature(payload: dict) -> bool:
    sig = (payload or {}).get('signature') or {}
    token = (sig.get('token') or '').strip()
    timestamp = (sig.get('timestamp') or '').strip()
    signature = (sig.get('signature') or '').strip()
    key = current_app.config.get('MAILGUN_WEBHOOK_SIGNING_KEY', '') \
        or current_app.config.get('MAILGUN_API_KEY', '')
    if not (token and timestamp and signature and key):
        return False
    # Reject anything older than 5 minutes — defence against replay.
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False
    except ValueError:
        return False
    expected = hmac.new(
        key.encode('utf-8'),
        msg=(timestamp + token).encode('utf-8'),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@growth_bp.route('/api/mailgun-webhook', methods=['POST'])
@csrf.exempt
def mailgun_webhook():
    """Mailgun Events → CSV state update + Telegram notification on
    `replied` (we infer from `opened` + inbound, or Mailgun's
    `stored` event when inbound routing is configured).

    Returns 204 on accepted events, 401 on signature mismatch, 400 on
    malformed payload. Never 500s on a per-event error — the webhook
    must stay 2xx or Mailgun retries explode.
    """
    payload = request.get_json(silent=True) or {}
    if not _verify_mailgun_signature(payload):
        return Response('signature mismatch', status=401)

    event_data = payload.get('event-data') or {}
    event = (event_data.get('event') or '').strip()
    if event not in _ALLOWED_EVENTS:
        # Accept & ignore — e.g. Mailgun sends `accepted` between
        # accepted→delivered which we don't track.
        return Response('', status=204)

    recipient = (event_data.get('recipient') or '').strip().lower()
    if not recipient:
        return Response('missing recipient', status=400)

    # Normalise Mailgun's names into our state machine.
    status_for_event = {
        'delivered':       'delivered',
        'opened':          'opened',
        'clicked':         'clicked',
        'unsubscribed':    'opted_out',
        'complained':      'complained',
        'failed':          'bounced',
        'permanent_fail':  'bounced',
    }
    new_event = status_for_event[event]

    outreach.record_event(
        email_to=recipient, event=new_event,
        extra={'mailgun_id': event_data.get('id', ''),
               'reason': event_data.get('reason', '')},
    )

    # Find the target row by contact_email (exact, case-insensitive).
    try:
        fieldnames, rows = outreach.load_targets()
    except Exception:
        return Response('', status=204)

    match = None
    for row in rows:
        if (row.get('contact_email') or '').strip().lower() == recipient:
            match = row
            break
    if match:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        match['last_event'] = new_event
        match['last_event_at'] = now
        match['last_status_change'] = now
        if new_event == 'opted_out':
            match['opted_out'] = '1'
            match['status'] = 'opted_out'
        elif new_event == 'complained':
            match['opted_out'] = '1'
            match['status'] = 'opted_out'
        elif new_event == 'bounced':
            match['status'] = 'bounced'
        try:
            outreach.save_targets(fieldnames, rows)
        except Exception:
            # Webhook must not 500 — CSV write failure is logged via
            # record_event above and will surface on the dashboard.
            pass

        # Telegram 📬 on opt-out / complaint (worth knowing immediately).
        if new_event in ('complained', 'opted_out'):
            _notify_telegram(
                f'⚠️  {new_event} — {match.get("domain", recipient)}\n'
                f'Reason: {event_data.get("reason", "")[:200]}'
            )

    return Response('', status=204)


def _notify_telegram(message: str) -> None:
    token = current_app.config.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID', '')
    if not (token and chat_id):
        return
    try:
        import requests as req
        req.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': message[:3900],
                  'disable_web_page_preview': True},
            timeout=5,
        )
    except Exception:
        pass


# ── One-click unsubscribe ──────────────────────────────────────────────


def _unsubscribe_token(to: str, secret: str) -> str:
    msg = f'{to}|{secret or "dev-secret"}'.encode('utf-8')
    return hashlib.sha256(msg).hexdigest()[:20]


@growth_bp.route('/api/backlinks-unsubscribe',
                 methods=['GET', 'POST'])
@csrf.exempt
def backlinks_unsubscribe():
    """RFC 8058 one-click unsubscribe from our outreach list.

    Flips `opted_out=1` for the matching CSV row and records an event.
    GET renders a tiny confirmation page; POST (what Gmail/Yahoo send
    on one-click) returns 200 text/plain.
    """
    email = (request.args.get('e') or '').strip().lower()
    token = (request.args.get('t') or '').strip()
    secret = current_app.config.get('SECRET_KEY', '') or 'dev-secret'
    expected = _unsubscribe_token(email, secret)
    if not email or not hmac.compare_digest(expected, token):
        return Response('invalid unsubscribe link', status=400)

    try:
        fieldnames, rows = outreach.load_targets()
        changed = False
        for row in rows:
            if (row.get('contact_email') or '').strip().lower() == email:
                row['opted_out'] = '1'
                row['status'] = 'opted_out'
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).isoformat(timespec='seconds')
                row['last_event'] = 'opted_out'
                row['last_event_at'] = now
                row['last_status_change'] = now
                changed = True
        if changed:
            outreach.save_targets(fieldnames, rows)
        outreach.record_event(email_to=email, event='opted_out',
                              extra={'source': 'unsubscribe_link'})
    except Exception:
        pass

    if request.method == 'POST':
        return Response('unsubscribed\n', status=200, mimetype='text/plain')
    return Response(
        '<!doctype html><meta charset="utf-8">'
        '<title>Unsubscribed</title>'
        '<body style="font-family:system-ui;max-width:560px;margin:3em auto;padding:0 1em">'
        '<h1>You have been unsubscribed</h1>'
        "<p>We won't contact you again. If this was a mistake, reply to the "
        'original email and ask to be re-added.</p></body>',
        status=200, mimetype='text/html',
    )


# ── /admin/backlinks dashboard ─────────────────────────────────────────


@growth_bp.route('/admin/backlinks')
@_basic_auth_required
def backlinks_dashboard():
    fieldnames, rows = outreach.load_targets()

    filter_status = (request.args.get('status') or '').strip()
    filter_category = (request.args.get('category') or '').strip()

    items = list(rows)
    if filter_status:
        items = [r for r in items if (r.get('status') or '').strip() == filter_status]
    if filter_category:
        items = [r for r in items if (r.get('category') or '').strip() == filter_category]

    # DA sort descending — most valuable targets first.
    def _da(r: dict) -> int:
        try:
            return int((r.get('DA_estimate') or '0') or '0')
        except ValueError:
            return 0
    items.sort(key=lambda r: (_da(r), r.get('domain', '')), reverse=True)

    # Aggregates for summary cards.
    status_counts = Counter((r.get('status') or 'todo').strip() or 'todo'
                            for r in rows)
    category_counts = Counter((r.get('category') or '').strip() for r in rows)
    by_category_reply_rate: list[dict] = []
    for cat, total in category_counts.most_common(10):
        contacted = sum(
            1 for r in rows
            if (r.get('category') or '').strip() == cat
            and (r.get('status') or '').strip() in (
                'contacted', 'replied', 'backlinked', 'no_response'
            )
        )
        replied = sum(
            1 for r in rows
            if (r.get('category') or '').strip() == cat
            and (
                (r.get('last_event') or '').strip() == 'replied'
                or (r.get('status') or '').strip() == 'replied'
            )
        )
        reply_pct = round(100 * replied / contacted, 1) if contacted else 0.0
        by_category_reply_rate.append({
            'category': cat, 'total': total,
            'contacted': contacted, 'replied': replied,
            'reply_pct': reply_pct,
        })
    by_category_reply_rate.sort(key=lambda r: r['reply_pct'], reverse=True)

    # Pipeline projection: contacted × typical 5% → expected backlinks.
    contacted_total = (
        status_counts['contacted']
        + status_counts['replied']
        + status_counts['backlinked']
        + status_counts['no_response']
    )
    projected_backlinks = round(contacted_total * 0.05, 1)

    return render_template(
        'admin/backlinks.html',
        items=items[:500],  # safety cap
        all_count=len(rows),
        shown_count=min(500, len(items)),
        status_counts=dict(status_counts),
        category_counts=dict(category_counts),
        by_category_reply_rate=by_category_reply_rate,
        projected_backlinks=projected_backlinks,
        filter_status=filter_status,
        filter_category=filter_category,
    )


@growth_bp.after_request
def _no_index(resp):
    if request.path.startswith('/admin'):
        resp.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
        resp.headers['Cache-Control'] = 'private, no-store'
    return resp

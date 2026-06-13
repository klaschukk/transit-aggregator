"""Newsletter subscription — double-opt-in API.

Backend only. The home/footer signup form and price-alert widget land
in a follow-up phase; for now the endpoints are callable via curl or
the future forms, and every outbound message carries an unsubscribe
link so we're CAN-SPAM / GDPR compliant from day one.
"""
from __future__ import annotations

import re

from flask import Blueprint, abort, current_app, jsonify, render_template, request, g

from app import analytics_db
from app.extensions import _client_ip, csrf, limiter
from app.mailer import send_mail

subscribe_bp = Blueprint('subscribe', __name__)

_EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
_EMAIL_MAX = 100
_SOURCE_MAX = 40
_ROUTE_SLUG_MAX = 200
_ROUTE_SLUG_RE = re.compile(r'^[a-z0-9-]+$')  # match app.slug.normalize_slug output
_ALLOWED_SOURCES = {
    'home', 'footer', 'route_detail', 'city_pair',
    'price_alert', 'guide', 'other',
}


def _confirm_url(token: str) -> str:
    base = current_app.config.get('BASE_URL', '').rstrip('/')
    return f"{base}/api/subscribe/confirm/{token}"


def _unsubscribe_url(token: str) -> str:
    base = current_app.config.get('BASE_URL', '').rstrip('/')
    return f"{base}/api/unsubscribe/{token}"


def _confirm_email_body(confirm_url: str, unsub_url: str,
                        lang: str) -> tuple[str, str, str]:
    """Return (subject, text, html). Three languages inline so Phase 1 has
    no template dependency — lifted into Jinja files in Phase 2 when the
    designer polish pass happens."""
    if lang == 'en':
        subject = 'Confirm your Prevozni newsletter subscription'
        intro = 'Thanks for subscribing. Click to confirm:'
        cta = 'Confirm subscription'
        foot = ("If this wasn't you, ignore the email — without a click "
                "you stay unsubscribed. Unsubscribe anytime: ")
    elif lang == 'ru':
        subject = 'Подтвердите подписку Prevozni'
        intro = 'Спасибо за подписку. Подтвердите переход по ссылке:'
        cta = 'Подтвердить подписку'
        foot = ("Если это не вы — просто проигнорируйте письмо. "
                "Отписаться можно здесь: ")
    else:
        subject = 'Potvrdite pretplatu na Prevozni newsletter'
        intro = 'Hvala na pretplati. Kliknite da potvrdite:'
        cta = 'Potvrdi pretplatu'
        foot = ("Ako ovo niste vi, ignorišite poruku — bez klika "
                "ostajete nepretplaćeni. Odjava: ")

    text = (
        f"{intro}\n\n{confirm_url}\n\n{foot}{unsub_url}\n"
    )
    html = (
        '<!doctype html><html><body style="font-family:system-ui,sans-serif;'
        'max-width:560px;margin:0 auto;color:#111">'
        '<table width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="background:#0d9488;color:#fff;padding:20px 24px">'
        '<tr><td><strong>Prevozni</strong></td></tr></table>'
        f'<div style="padding:24px"><p>{intro}</p>'
        f'<p><a href="{confirm_url}" style="background:#0d9488;color:#fff;'
        'padding:12px 20px;text-decoration:none;border-radius:6px;'
        f'display:inline-block">{cta}</a></p>'
        f'<p style="color:#666;font-size:13px;margin-top:32px">{foot}'
        f'<a href="{unsub_url}" style="color:#0d9488">{unsub_url}</a>.</p>'
        '</div></body></html>'
    )
    return subject, text, html


def _welcome_email_body(unsub_url: str, lang: str) -> tuple[str, str, str]:
    if lang == 'en':
        subject = 'Welcome to Prevozni newsletter'
        body = ("You're in. Expect one email a week with the cheapest "
                "tickets, new routes, and practical tips for travel in "
                "Serbia.\n\nBrowse guides while you wait: "
                "https://prevozni.com/vodici/")
        foot = 'Unsubscribe: '
    elif lang == 'ru':
        subject = 'Добро пожаловать в Prevozni newsletter'
        body = ("Подписка активна. Раз в неделю будем присылать самые "
                "дешёвые билеты, новые маршруты и советы по "
                "путешествиям по Сербии.\n\nГиды пока тут: "
                "https://prevozni.com/ru/vodici/")
        foot = 'Отписаться: '
    else:
        subject = 'Dobrodošli u Prevozni newsletter'
        body = ("Pretplata potvrđena. Jednom nedeljno šaljemo "
                "najjeftinije karte, nove rute i praktične savete.\n\n"
                "Pročitajte vodiče: https://prevozni.com/vodici/")
        foot = 'Odjava: '

    text = f"{body}\n\n{foot}{unsub_url}\n"
    html = (
        '<!doctype html><html><body style="font-family:system-ui,sans-serif;'
        'max-width:560px;margin:0 auto;color:#111">'
        '<table width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="background:#0d9488;color:#fff;padding:20px 24px">'
        '<tr><td><strong>Prevozni</strong></td></tr></table>'
        f'<div style="padding:24px"><p>{body.replace(chr(10), "<br>")}</p>'
        f'<p style="color:#666;font-size:13px;margin-top:32px">{foot}'
        f'<a href="{unsub_url}" style="color:#0d9488">{unsub_url}</a>.</p>'
        '</div></body></html>'
    )
    return subject, text, html


@subscribe_bp.route('/api/subscribe', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per hour")
def api_subscribe():
    """Accept an email, create or refresh a pending row, send confirm letter.

    Returns 202 on any acceptable outcome (new signup OR re-send of confirm
    letter) so the form UX is the same regardless of whether the user has
    clicked this button before. Already-confirmed addresses get a gentle
    200 + already_subscribed message instead of a silent no-op — the user
    hasn't done anything wrong, they've just forgotten.
    """
    data = request.form.to_dict() or request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()[:_EMAIL_MAX + 1]
    source = (data.get('source') or 'unknown').strip()[:_SOURCE_MAX]
    route_slug = (data.get('route_slug') or '').strip()[:_ROUTE_SLUG_MAX]
    consent = (data.get('consent') or '').strip().lower() in (
        '1', 'on', 'true', 'yes',
    )

    if source not in _ALLOWED_SOURCES:
        source = 'other'
    # Only accept route_slug for the price-alert source — ignore it everywhere
    # else so a generic footer signup can't accidentally bind to a route.
    if route_slug and (source != 'price_alert' or not _ROUTE_SLUG_RE.match(route_slug)):
        route_slug = ''
    if source == 'price_alert' and not route_slug:
        return jsonify(ok=False, error='subscribe.error.route_required'), 400
    if not email or len(email) > _EMAIL_MAX or not _EMAIL_RE.match(email):
        return jsonify(ok=False, error='subscribe.error.email_invalid'), 400
    if not consent:
        # Without the privacy checkbox we can't store the address legally.
        return jsonify(ok=False, error='subscribe.error.consent_required'), 400

    lang = getattr(g, 'lang', 'sr')
    row = analytics_db.insert_or_refresh_subscriber(
        email=email,
        lang=lang,
        source=source,
        referrer=(request.referrer or '')[:500],
        ip=_client_ip(),
        route_slug=route_slug or None,
    )
    if row is None:
        return jsonify(ok=False, error='subscribe.error.db'), 500

    action = row.get('_action')
    if action == 'already_confirmed':
        return jsonify(
            ok=True, status='already_subscribed',
            message='subscribe.ok.already',
        ), 200

    subject, text, html = _confirm_email_body(
        _confirm_url(row['confirm_token']),
        _unsubscribe_url(row['unsubscribe_token']),
        lang,
    )
    send_mail(to=email, subject=subject, text=text, html=html)

    return jsonify(
        ok=True, status='pending_confirm',
        message='subscribe.ok.check_inbox',
    ), 202


@subscribe_bp.route('/api/subscribe/confirm/<token>', methods=['GET'])
@csrf.exempt
def api_subscribe_confirm(token: str):
    """Finalise the double-opt-in. GET so the confirm link works from any
    email client without a JS round-trip."""
    if not token or len(token) > 64 or not token.isalnum():
        abort(404)

    result, row = analytics_db.confirm_subscriber(token)
    if result == 'invalid':
        abort(404)

    status_code = 200 if result in ('ok', 'already') else 410

    if result == 'ok' and row:
        unsub_url = _unsubscribe_url(row['unsubscribe_token'])
        subject, text, html = _welcome_email_body(unsub_url, row.get('lang') or 'sr')
        # One-click List-Unsubscribe (RFC 8058) on this first post-opt-in mail —
        # Gmail/Yahoo bulk rules want it and it keeps the welcome out of spam.
        send_mail(to=row['email'], subject=subject, text=text, html=html,
                  list_unsubscribe=unsub_url)

    return render_template(
        'subscribe_confirmed.html', result=result,
    ), status_code


@subscribe_bp.route('/api/unsubscribe/<token>', methods=['GET'])
@csrf.exempt
def api_unsubscribe(token: str):
    """Act on one-click unsubscribe links from email footers."""
    if not token or len(token) > 64 or not token.isalnum():
        abort(404)
    ok = analytics_db.unsubscribe_subscriber(token)
    return render_template(
        'subscribe_unsubscribed.html', ok=ok,
    ), (200 if ok else 410)

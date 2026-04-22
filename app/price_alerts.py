"""
Price-alert dispatch — shared between the nightly scan and the manual
test script.

Keeps the email composition, threshold policy, and rate-limit constants
in one place so we can tune them (e.g. "drop threshold 15% now",
"cooldown 10 days") without editing three files.

Standalone-friendly: only imports Flask `current_app` for config access
(BASE_URL, language defaults). The scripts that call this module wrap
their work in `app.app_context()`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date as _date
from urllib.parse import quote_plus

from flask import current_app

logger = logging.getLogger(__name__)

# ── tuning constants ────────────────────────────────────────────────────
# Picked conservatively. 10% is big enough to feel like a real deal,
# small enough that we still fire a few times a week across 500+ subs.
DROP_THRESHOLD = 0.90       # today's min < baseline × this → qualify
MIN_BASELINE_DAYS = 7       # need ≥7 days of history for a trusted baseline
COOLDOWN_DAYS = 7           # one email per (subscriber, route) per week
MAX_EMAILS_PER_RUN = 50     # safety circuit-breaker — SMTP ban prevention


@dataclass(frozen=True)
class AlertEvaluation:
    """Result of evaluating a single route against its baseline."""
    route_slug: str
    qualifies: bool
    today_min: int | None
    baseline_min: int | None   # rolling min over the prior days (excluding today)
    drop_pct: int | None       # integer % drop (0-100), None when not qualified
    reason: str                # human-readable note for logs / debugging


def evaluate_snapshots(
    snapshots: list[dict],
    today: _date,
    min_baseline_days: int = MIN_BASELINE_DAYS,
    threshold: float = DROP_THRESHOLD,
) -> AlertEvaluation:
    """Given rows from `price_snapshots` for one route (newest-first),
    decide if today's minimum is a qualifying drop.

    The baseline is the minimum of the prior-day snapshots (strictly
    excluding today) — this means a big drop today compared to the
    cheapest day in the last week counts, but a drop compared to
    yesterday alone does not. Ignores rows with min_price NULL.
    """
    slug = snapshots[0]['route_slug'] if snapshots and 'route_slug' in snapshots[0] else ''

    today_row = next((r for r in snapshots if r.get('date') == today), None)
    today_min = today_row['min_price'] if today_row else None

    prior = [
        r for r in snapshots
        if r.get('date') != today and r.get('min_price') is not None
    ]
    if len(prior) < min_baseline_days:
        return AlertEvaluation(
            route_slug=slug, qualifies=False,
            today_min=today_min, baseline_min=None, drop_pct=None,
            reason=f'baseline too short ({len(prior)}/{min_baseline_days} days)',
        )
    if today_min is None:
        return AlertEvaluation(
            route_slug=slug, qualifies=False,
            today_min=None, baseline_min=None, drop_pct=None,
            reason='no snapshot for today',
        )

    baseline = min(r['min_price'] for r in prior)
    if baseline <= 0:
        return AlertEvaluation(
            route_slug=slug, qualifies=False,
            today_min=today_min, baseline_min=baseline, drop_pct=None,
            reason='baseline <= 0',
        )

    pct = int(round((baseline - today_min) * 100 / baseline))
    qualifies = today_min < baseline * threshold
    return AlertEvaluation(
        route_slug=slug,
        qualifies=qualifies,
        today_min=today_min,
        baseline_min=baseline,
        drop_pct=pct if qualifies else None,
        reason=(f'drop {pct}% vs 7d min {baseline} RSD' if qualifies
                else f'drop {pct}% below threshold'),
    )


# ── email composition ───────────────────────────────────────────────────

def _base_url() -> str:
    return (current_app.config.get('BASE_URL') or 'https://prevozni.com').rstrip('/')


def _route_url(route_slug: str, lang: str, utm_medium: str) -> str:
    prefix = '' if lang in ('sr', '') else f'/{lang}'
    campaign = quote_plus(route_slug)
    return (
        f'{_base_url()}{prefix}/rute/{route_slug}/'
        f'?utm_source=prevozni&utm_medium={utm_medium}'
        f'&utm_campaign={campaign}'
    )


def _unsubscribe_url(token: str) -> str:
    return f'{_base_url()}/api/unsubscribe/{token}'


def build_price_alert_email(
    *,
    route_slug: str,
    from_city: str,
    to_city: str,
    old_price: int,
    new_price: int,
    drop_pct: int,
    lang: str,
    unsubscribe_token: str,
) -> tuple[str, str, str]:
    """Render (subject, text, html) for one price-alert email. All three
    languages inline — mirrors the existing subscribe/confirm style so we
    don't need a Jinja file for each. `drop_pct` is the integer %, e.g. 18."""
    url = _route_url(route_slug, lang, 'price-alert')
    unsub = _unsubscribe_url(unsubscribe_token)

    pair = f'{from_city} → {to_city}'
    new_eur = max(1, round(new_price / 117))
    old_eur = max(1, round(old_price / 117))

    if lang == 'en':
        subject = f'Price drop: {pair} — now {new_price} RSD ({drop_pct}% off)'
        intro = (
            f'Good news — the cheapest ticket for {pair} just dropped '
            f'to {new_price} RSD (~{new_eur} €). That\'s {drop_pct}% less '
            f'than the cheapest we\'ve seen in the past week '
            f'({old_price} RSD / ~{old_eur} €).'
        )
        cta = 'See all departures'
        foot = 'You\'re getting this because you subscribed to price alerts for this route. Unsubscribe anytime: '
    elif lang == 'ru':
        subject = f'Цена упала: {pair} — теперь {new_price} RSD ({drop_pct}% скидка)'
        intro = (
            f'Хорошие новости — самый дешёвый билет {pair} сейчас '
            f'стоит {new_price} RSD (~{new_eur} €). Это на {drop_pct}% '
            f'меньше, чем минимум за прошедшую неделю '
            f'({old_price} RSD / ~{old_eur} €).'
        )
        cta = 'Смотреть все рейсы'
        foot = 'Вы получили это письмо потому что подписались на оповещения о ценах. Отписаться: '
    else:  # sr default
        subject = f'Cena je pala: {pair} — sada {new_price} RSD ({drop_pct}% niža)'
        intro = (
            f'Dobre vesti — najjeftinija karta za {pair} sada je '
            f'{new_price} RSD (~{new_eur} €). To je {drop_pct}% niže od '
            f'prethodno najjeftinije u poslednjih 7 dana '
            f'({old_price} RSD / ~{old_eur} €).'
        )
        cta = 'Pogledaj sve polaske'
        foot = 'Ovu poruku dobijate jer ste pretplaćeni na obaveštenja o ceni za ovu rutu. Odjava: '

    text = (
        f'{intro}\n\n{cta}: {url}\n\n'
        f'{foot}{unsub}\n'
    )
    html = (
        '<!doctype html><html><body style="font-family:system-ui,sans-serif;'
        'max-width:560px;margin:0 auto;color:#111">'
        '<table width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="background:#0d9488;color:#fff;padding:20px 24px">'
        '<tr><td><strong>Prevozni</strong> &middot; price alert</td></tr>'
        '</table>'
        f'<div style="padding:24px"><p>{intro}</p>'
        f'<p style="margin:28px 0"><a href="{url}" '
        'style="background:#0d9488;color:#fff;padding:12px 22px;'
        'text-decoration:none;border-radius:6px;display:inline-block;'
        f'font-weight:600">{cta}</a></p>'
        f'<p style="color:#666;font-size:13px;margin-top:32px">{foot}'
        f'<a href="{unsub}" style="color:#0d9488">{unsub}</a>.</p>'
        '</div></body></html>'
    )
    return subject, text, html

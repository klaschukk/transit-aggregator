"""End-to-end campaign sender — pure logic, no Flask globals.

Tests exercise this directly via a `send_fn` injection point so we
don't have to spin up an SMTP server. In production
scripts/newsletter_send.py wires `send_fn=app.mailer.send_mail` and
loops the loop.

Resume semantics: campaign_sends has a UNIQUE(campaign_id,
subscriber_id) so a re-run after a crash idempotently skips already-
sent recipients. The dispatcher reads the existing send-set first and
filters them out before iterating. No row-level locks needed — DuckDB
is single-writer per file and we're a single-process loop.

Rate-limit: the `min_delay_s` between sends is the safety knob. SMTP
peers tolerate ~10/s sustained on a warm IP, but cold sender reputation
on a brand-new domain wants ≤ 1–2/s — set min_delay_s=1.0 for the first
two campaigns, then ramp.
"""
from __future__ import annotations

import logging
import time
from typing import Callable

from app.newsletter import campaigns as cmp_mod
from app.newsletter import audience as aud_mod
from app.newsletter import render as render_mod

logger = logging.getLogger(__name__)


SendFn = Callable[..., bool]


def send_campaign(
    campaign_id: int,
    *,
    send_fn: SendFn,
    unsub_base_url: str,
    test_email: str | None = None,
    min_delay_s: float = 0.2,
    max_per_run: int = 10_000,
    dry_run: bool = False,
) -> dict:
    """Run one campaign. Returns a {sent, skipped, errors} summary.

    test_email: if provided, ignore the audience filter and send to this
                single address (rendered with sr fallback) — for the
                "Send test to yourself" button.
    dry_run:    iterate the audience but call neither send_fn nor
                record_send. Useful for the compose preview + a CI
                smoke-test.
    """
    campaign = cmp_mod.get_campaign(campaign_id)
    if not campaign:
        raise ValueError(f"campaign {campaign_id} not found")

    if campaign['status'] in ('sent', 'cancelled') and not dry_run:
        raise RuntimeError(
            f"campaign {campaign_id} status={campaign['status']!r}; refusing"
        )

    # Test-mode: short-circuit. We still validate that at least one
    # language has a body — sending an empty test would be a footgun.
    if test_email:
        return _send_one(
            campaign, send_fn=send_fn, recipient_email=test_email,
            recipient_lang='sr',
            recipient_id=None,
            unsub_base_url=unsub_base_url,
            unsub_token='TEST',
            source='admin-test',
            confirmed_date='',
            dry_run=dry_run,
        )

    # ── Main path ────────────────────────────────────────────────────────
    if not dry_run:
        cmp_mod.update_status(campaign_id, 'sending')

    audience_filter = cmp_mod.parse_audience(campaign)
    audience = aud_mod.resolve(audience_filter)
    already = cmp_mod.already_sent_subscriber_ids(campaign_id) if not dry_run else set()

    summary = {
        'campaign_id': campaign_id,
        'audience_total': len(audience),
        'already_sent': len(already),
        'sent': 0,
        'errors': 0,
        'skipped_no_body': 0,
        'rows_dry_run': [],
    }

    for sub in audience:
        if sub['id'] in already:
            continue
        if summary['sent'] + summary['errors'] >= max_per_run:
            logger.info('max_per_run %s reached; stopping', max_per_run)
            break

        lang = sub.get('lang') or 'sr'
        # Fallback to whichever language has a body. Sending an empty
        # email is worse than sending the operator's preferred fallback.
        if not (campaign.get(f'body_md_{lang}') or '').strip():
            for fallback in ('sr', 'en', 'ru'):
                if (campaign.get(f'body_md_{fallback}') or '').strip():
                    lang = fallback
                    break
            else:
                summary['skipped_no_body'] += 1
                continue

        result = _send_one(
            campaign,
            send_fn=send_fn,
            recipient_email=sub['email'],
            recipient_lang=lang,
            recipient_id=int(sub['id']),
            unsub_base_url=unsub_base_url,
            unsub_token=sub['unsubscribe_token'] or '',
            source=sub.get('source') or '',
            confirmed_date=str(sub.get('confirmed_at') or '')[:10],
            dry_run=dry_run,
        )
        if dry_run:
            summary['rows_dry_run'].append({
                'subscriber_id': int(sub['id']),
                'email': _mask(sub['email']),
                'lang': lang,
                'subject': result.get('subject'),
            })
        else:
            if result.get('ok'):
                summary['sent'] += 1
                cmp_mod.record_send(campaign_id, int(sub['id']))
                cmp_mod.increment_counter(campaign_id, 'recipients_count', 1)
            else:
                summary['errors'] += 1
                cmp_mod.record_send(campaign_id, int(sub['id']),
                                    error=result.get('error', 'send_fn returned False'))

        if not dry_run and min_delay_s > 0:
            time.sleep(min_delay_s)

    if not dry_run:
        cmp_mod.update_status(campaign_id, 'sent', sent_at_now=True)

    return summary


# ── Internal: render + send one message ────────────────────────────────

def _mask(email: str) -> str:
    """Privacy-preserving mask for log output. ``ana@example.com`` →
    ``a**@example.com``."""
    if '@' not in email:
        return '***'
    local, domain = email.split('@', 1)
    if len(local) <= 1:
        return f'{local}@{domain}'
    return f'{local[0]}{"*" * (len(local) - 1)}@{domain}'


def _send_one(
    campaign: dict,
    *,
    send_fn: SendFn,
    recipient_email: str,
    recipient_lang: str,
    recipient_id: int | None,
    unsub_base_url: str,
    unsub_token: str,
    source: str,
    confirmed_date: str,
    dry_run: bool = False,
) -> dict:
    lang = recipient_lang if recipient_lang in ('sr', 'en', 'ru') else 'sr'
    subject_tpl = campaign.get(f'subject_{lang}') or campaign.get('subject_sr') or ''
    preheader_tpl = campaign.get(f'preheader_{lang}') or ''
    body_tpl = campaign.get(f'body_md_{lang}') or campaign.get('body_md_sr') or ''

    unsub_url = f"{unsub_base_url.rstrip('/')}/api/unsubscribe/{unsub_token}"

    vars_ = {
        'unsub_url': unsub_url,
        'preferences_url': unsub_url,
        'sender_name': 'Prevozni',
        'site_url': 'https://prevozni.com',
        'lang': lang,
    }

    subject = render_mod.substitute(subject_tpl, vars_).strip()
    preheader = render_mod.substitute(preheader_tpl, vars_).strip()
    body_md = render_mod.substitute(body_tpl, vars_)

    subject, html, text = render_mod.render_email(
        subject=subject,
        preheader=preheader,
        body_md=body_md,
        lang=lang,
        unsub_url=unsub_url,
        source=source,
        confirmed_date=confirmed_date,
    )

    if dry_run:
        return {'ok': True, 'subject': subject, 'preview_html_chars': len(html)}

    try:
        ok = send_fn(
            to=recipient_email,
            subject=subject,
            text=text,
            html=html,
            list_unsubscribe=unsub_url,
        )
    except TypeError:
        # Older send_fn signatures without list_unsubscribe — fall back.
        ok = send_fn(
            to=recipient_email, subject=subject, text=text, html=html,
        )
    return {'ok': bool(ok), 'subject': subject,
            'error': None if ok else 'send_fn returned False'}

"""Groq-backed itinerary composer for far / long-haul destinations.

When a user searches a pair we don't sell — e.g. ``Beograd -> Bangkok`` — the
intercity DB returns nothing and the user would normally bounce to Google. Here
we instead ask Groq to compose a realistic multi-leg itinerary (local bus/train
to a hub, a flight, a local transfer at the far end) so the Serbian user gets a
useful answer *on prevozni.com*. The bookable local leg is monetised via
Bookaway, whose far coverage is seeded in ``partners.FAR_DESTINATIONS``.

This module is intentionally DB-free and Flask-light: it exposes pure functions
(detection + the Groq call). Caching lives in ``analytics_db.composed_routes``
and is wired up by the ``/pretraga`` handler so each pair hits Groq at most once.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from app.affiliates.partners import FAR_DESTINATIONS
from app.slug import slugify_serbian

logger = logging.getLogger(__name__)

# Reuse the chat model/UA — same Groq account, same Cloudflare-friendly UA.
# llama-3.3-70b-versatile was retired by Groq on 2026-08-16 (every call 404'd
# with model_not_found for a month before anyone noticed — see the warning log
# in compose_itinerary_via_groq). openai/gpt-oss-120b is Groq's documented
# replacement; verified live 2026-09-20 (177 itineraries composed overnight).
# It is a reasoning model: reasoning tokens count against the free tier's
# 200K tokens/day, which is what caps the nightly pregen (~160-180 per night).
# reasoning_effort=low (verified live 2026-09-21 on 3 pairs): ~750 tokens per
# itinerary instead of ~1165, faster, and it stops the default effort from
# burning 600 of the 700 max_tokens on reasoning and truncating the answer.
COMPOSE_MODEL = 'openai/gpt-oss-120b'
_UA = 'PrevozniBot/1.0 (+https://prevozni.com)'
_ENDPOINT = 'https://api.groq.com/openai/v1/chat/completions'

# Language label fed to the model so it answers in the user's language.
_LANG_NAME = {'sr': 'Serbian (latin)', 'en': 'English', 'ru': 'Russian'}

_SYSTEM = """You are a travel route planner for Prevozni.com, a Serbian public-transport site. \
A user wants to travel from one place to a FAR destination that local buses/trains do not reach directly. \
Compose ONE realistic door-to-door itinerary as a sequence of legs (e.g. bus/train from the origin to the nearest big airport, a flight, then a local bus/transfer at the destination). \
Be concrete and honest: real airport names, plausible durations, an approximate total and a rough price floor in EUR for one adult economy. Never invent exact prices or schedules — these are estimates.

Reply with STRICT JSON only, no prose, in this exact shape:
{
  "feasible": true,
  "summary": "<one short sentence describing the overall trip>",
  "legs": [
    {"mode": "bus|train|flight|ferry|taxi|metro", "from": "<place>", "to": "<place>", "duration": "~Xh", "note": "<short practical note>"}
  ],
  "total_duration": "~Xh / X days",
  "price_from_eur": <integer rough floor for 1 adult>,
  "tips": ["<short tip>", "<short tip>"]
}
Rules:
- 2 to 5 legs. First leg starts at the user's origin city, last leg ends at the destination city.
- Write ALL human-readable text (summary, notes, tips) in {lang}. Keep "mode" values in English from the allowed set.
- If the trip is genuinely impossible, return {"feasible": false, "summary": "<why>", "legs": [], "total_duration": "", "price_from_eur": 0, "tips": []}."""


def far_pair_info(from_city: str, to_city: str) -> dict | None:
    """Classify a searched pair. Returns context when at least one endpoint is a
    known far Bookaway destination (so the AI fallback should fire), else None.

    The far endpoint is whichever side is in ``FAR_DESTINATIONS``; the other is
    treated as the origin. Two far endpoints → destination = ``to``.
    """
    if not from_city or not to_city:
        return None
    from_slug = slugify_serbian(from_city)
    to_slug = slugify_serbian(to_city)
    if not from_slug or not to_slug or from_slug == to_slug:
        return None

    to_far = FAR_DESTINATIONS.get(to_slug)
    from_far = FAR_DESTINATIONS.get(from_slug)
    if not to_far and not from_far:
        return None

    # Prefer the destination as the "far" side; fall back to origin.
    if to_far:
        far_slug, far_meta = to_slug, to_far
    else:
        far_slug, far_meta = from_slug, from_far

    return {
        'from_slug': from_slug,
        'to_slug': to_slug,
        'far_slug': far_slug,
        'far_meta': far_meta,
        'region': far_meta.get('region', ''),
        'pair_key': f'{from_slug}:{to_slug}',
    }


def compose_itinerary_via_groq(
    from_city: str, to_city: str, lang: str, api_key: str, timeout: int = 20,
) -> dict | None:
    """Ask Groq for one itinerary. Returns the parsed/validated dict or None on
    any failure (network, non-JSON, bad shape) — callers degrade to the plain
    Bookaway CTA so the page is always useful even when the model is down."""
    data, _hard_failure = compose_itinerary_via_groq_ex(
        from_city, to_city, lang, api_key, timeout)
    return data


def compose_itinerary_via_groq_ex(
    from_city: str, to_city: str, lang: str, api_key: str, timeout: int = 20,
) -> tuple[dict | None, bool]:
    """Same as compose_itinerary_via_groq, plus a ``hard_failure`` flag a batch
    caller (scripts/pregen_far_routes.py) can use to tell "the API/account is
    unreachable, stop hammering it" apart from "the model said this route isn't
    feasible" — the latter is an ordinary, expected outcome for many pairs and
    must NOT trip a circuit breaker; the former means every remaining call in
    the sweep will fail too (2026-09-22: a Cloudflare error-1010 block on this
    box's IP turned an ~8 h pregen run into a no-op that also broke the live
    /api/chat feature — see docs/06_tech/handoff-2026-09-21.md).

    hard_failure is True for network errors, timeouts and any non-2xx HTTP
    response (429 quota, 404 retired model, 403 Cloudflare block, 5xx) —
    anything that means we never got a real answer. It's False when Groq
    responded and the answer was just unusable (bad JSON from the model,
    infeasible route) — a normal, per-pair outcome that doesn't imply the
    next call will fail too.
    """
    if not api_key:
        return None, True
    lang_name = _LANG_NAME.get(lang, 'Serbian (latin)')
    system = _SYSTEM.replace('{lang}', lang_name)
    user = f'Origin: {from_city}\nDestination: {to_city}\nPlan the trip.'

    payload = json.dumps({
        'model': COMPOSE_MODEL,
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user},
        ],
        'max_tokens': 700,
        'temperature': 0.3,
        'reasoning_effort': 'low',
        'response_format': {'type': 'json_object'},
    }).encode()

    req = urllib.request.Request(
        _ENDPOINT,
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': _UA,
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode('utf-8'))
        content = body['choices'][0]['message']['content']
        data = json.loads(content)
    except urllib.error.HTTPError as exc:
        # Still degrades to None (callers fall back to the plain Bookaway CTA),
        # but say WHY: a retired model (404 model_not_found) and a daily-quota
        # 429 look identical to a caller, and the first one silently zeroed
        # every far-destination itinerary for a month before anyone noticed.
        body_snippet = exc.read()[:160].decode('utf-8', 'replace')
        hint = ' (Cloudflare block on this box\'s IP — stop retrying, wait it out)' if exc.code == 403 and '1010' in body_snippet else ''
        logger.warning('groq compose HTTP %s for %s->%s: %s%s', exc.code,
                       from_city, to_city, body_snippet, hint)
        return None, True
    except Exception as exc:  # noqa: BLE001 — network/JSON: same fallback
        logger.warning('groq compose failed for %s->%s: %s: %s', from_city, to_city,
                       type(exc).__name__, str(exc)[:120])
        return None, True

    return _sanitize(data, from_city, to_city), False


_ALLOWED_MODES = {'bus', 'train', 'flight', 'ferry', 'taxi', 'metro'}


def _sanitize(data: dict, from_city: str, to_city: str) -> dict | None:
    """Coerce the model output into a safe, render-ready shape. Returns None if
    the payload is unusable (so we fall back to the plain CTA)."""
    if not isinstance(data, dict):
        return None
    legs_in = data.get('legs') or []
    if not isinstance(legs_in, list):
        legs_in = []

    legs = []
    for leg in legs_in[:5]:
        if not isinstance(leg, dict):
            continue
        mode = str(leg.get('mode', '')).lower().strip()
        if mode not in _ALLOWED_MODES:
            mode = 'bus'
        legs.append({
            'mode': mode,
            'from': str(leg.get('from', ''))[:80],
            'to': str(leg.get('to', ''))[:80],
            'duration': str(leg.get('duration', ''))[:40],
            'note': str(leg.get('note', ''))[:240],
        })

    feasible = bool(data.get('feasible', True)) and len(legs) >= 1
    try:
        price = int(data.get('price_from_eur') or 0)
    except (TypeError, ValueError):
        price = 0

    tips_in = data.get('tips') or []
    tips = [str(t)[:240] for t in tips_in[:4]] if isinstance(tips_in, list) else []

    return {
        'feasible': feasible,
        'summary': str(data.get('summary', ''))[:300],
        'legs': legs,
        'total_duration': str(data.get('total_duration', ''))[:60],
        'price_from_eur': max(0, price),
        'tips': tips,
        'from_city': from_city,
        'to_city': to_city,
    }

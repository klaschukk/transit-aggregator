"""Lightweight A/B experimentation framework.

Design goals:
  - Zero JS libraries on the page. Assignment happens server-side at render
    time, the variant is baked into the HTML, and one fetch `/api/ab-convert`
    fires on the conversion event.
  - Stickiness without server-side state. The chosen variant is written back
    into a per-experiment cookie (`ab_<key>`) so changing `EXPERIMENTS`
    weights mid-flight does not reshuffle existing users.
  - Cohort filters (lang, country, device, returning) live in config, not
    in callers. `assign()` returns None when the user is outside the cohort;
    template helper falls back to the default variant.
  - Deterministic on a fixed user seed. Same `(experiment_key, ab_id)` →
    same variant on every request, even when cookies are disabled (falls
    back to IP-hash seed).

Not goals:
  - Multi-armed bandits. Classic fixed-allocation A/B is what we need to
    measure lift with chi-square, and the operator explicitly ships
    winners via `EXPERIMENTS` edits.
  - Real-time serving from a DB. Assignment is pure-function; writes only
    happen on exposure and conversion, async in a best-effort way.
"""
from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Iterable

from flask import current_app, g, request

from . import analytics_db

logger = logging.getLogger(__name__)

# Cookie names.
AB_ID_COOKIE = 'ab_id'                 # Per-browser stable UUID.
AB_VARIANT_COOKIE_PREFIX = 'ab_'       # e.g. ab_cta_copy_v1=Kupi
AB_COOKIE_MAX_AGE = 60 * 60 * 24 * 180  # 180 days — long enough to re-expose returning users.


@dataclass(frozen=True)
class ExperimentSpec:
    """Static description of one experiment, read from ab_config."""
    key: str
    variants: tuple[str, ...]
    weights: tuple[float, ...]
    surface: str           # where the experiment is rendered (for joins)
    started_at: str        # ISO date; future-dated experiments aren't served
    min_runtime_days: int = 7
    cohort: dict | None = None   # e.g. {'lang': ['en', 'ru']}, or None

    def is_live(self, today_iso: str) -> bool:
        return self.started_at <= today_iso


# ── User seed ───────────────────────────────────────────────────────────


def _ip_hash(ip: str) -> str:
    """Non-PII fallback seed. Salt comes from config (IP_HASH_SALT) so we can
    rotate it; same policy as analytics_db.hash_ip."""
    salt = (current_app.config.get('IP_HASH_SALT') if current_app else '') or 'ab-dev-salt'
    return hashlib.sha256(f'ab|{salt}|{ip or ""}'.encode('utf-8')).hexdigest()[:32]


def get_or_create_ab_id() -> str:
    """Return a stable per-browser seed.

    Priority:
      1. `ab_id` cookie — the normal path for any returning browser.
      2. Previously computed value on `flask.g` (one request can set it
         in before_request, reuse in Jinja helper and conversion POST).
      3. A fresh UUID, which the caller *may* persist via cookie when it
         sets headers. We do NOT mutate response cookies here — the
         after_request hook handles that so this function stays pure.

    Never returns empty. IP fallback is only used when we could not even
    reach the request context (e.g. in unit tests) — caller passes it in.
    """
    existing = request.cookies.get(AB_ID_COOKIE) if request else None
    if existing:
        return existing
    pending = getattr(g, 'ab_id', None) if g else None
    if pending:
        return pending
    new_id = uuid.uuid4().hex
    try:
        g.ab_id = new_id
    except RuntimeError:
        # No app context — tests call `assign(seed=...)` directly.
        pass
    return new_id


def assignment_seed() -> str:
    """The seed used for deterministic variant picking.

    Falls back through: `ab_id` cookie → g.ab_id → SHA256(IP+salt). The IP
    fallback only kicks in for the subset of users who block cookies; the
    first exposure for them is still stable across a session (same IP within
    a short window → same variant).
    """
    if request is None:
        return ''
    cookie_id = request.cookies.get(AB_ID_COOKIE)
    if cookie_id:
        return cookie_id
    pending = getattr(g, 'ab_id', None)
    if pending:
        return pending
    return _ip_hash(request.remote_addr or '')


# ── Cohort gating ───────────────────────────────────────────────────────


def _accept_lang_prefix() -> str:
    """First two letters of Accept-Language. Treats empty as 'sr' since
    the site default is Serbian."""
    if request is None:
        return 'sr'
    raw = (request.headers.get('Accept-Language') or '').strip()
    if not raw:
        return 'sr'
    first = raw.split(',', 1)[0].strip().lower()
    return first[:2] if first else 'sr'


def _cohort_match(spec: ExperimentSpec) -> bool:
    """Check the user fits the experiment cohort. Missing cohort → match all."""
    if not spec.cohort:
        return True

    # 'lang' — checks flask.g.lang (URL-prefix lang) AND Accept-Language.
    wanted_langs = spec.cohort.get('lang')
    if wanted_langs:
        user_lang = getattr(g, 'lang', None) if g else None
        acc = _accept_lang_prefix()
        if user_lang not in wanted_langs and acc not in wanted_langs:
            return False

    # 'not_lang' — exclude Serbian-reading visitors from tourist-targeted tests.
    # Serbo-Croatian shares codes sr/hr/bs/me (Bosnian, Croatian, Montenegrin).
    excl_langs = spec.cohort.get('not_lang')
    if excl_langs:
        user_lang = getattr(g, 'lang', None) if g else None
        acc = _accept_lang_prefix()
        if user_lang in excl_langs or acc in excl_langs:
            return False

    # 'device' — 'mobile' or 'desktop'. Based on a conservative UA substring
    # check; we only need a coarse split, not full UA parsing.
    dev_wanted = spec.cohort.get('device')
    if dev_wanted:
        ua = (request.headers.get('User-Agent') or '').lower() if request else ''
        is_mobile = any(kw in ua for kw in ('mobi', 'android', 'iphone', 'ipad'))
        if dev_wanted == 'mobile' and not is_mobile:
            return False
        if dev_wanted == 'desktop' and is_mobile:
            return False

    return True


# ── Variant assignment ──────────────────────────────────────────────────


def _weighted_pick(spec: ExperimentSpec, seed: str) -> str:
    """Deterministic weighted choice.

    Hashes (key + seed) into a [0, 1) float and walks the cumulative weight
    array. Ties broken by list order. Output is fully determined by the pair
    so load balancers / rolling deploys never flip a user.
    """
    digest = hashlib.sha256(f'{spec.key}|{seed}'.encode('utf-8')).digest()
    # 53 bits gives us > resolution than any reasonable weight granularity.
    bits = int.from_bytes(digest[:7], 'big')
    r = bits / (1 << 56)

    total = sum(spec.weights) or 1.0
    acc = 0.0
    for v, w in zip(spec.variants, spec.weights):
        acc += w / total
        if r < acc:
            return v
    return spec.variants[-1]


def assign(spec: ExperimentSpec, seed: str | None = None) -> str | None:
    """Return the variant for the current user, or None if out-of-cohort.

    Sticky: existing `ab_<key>` cookie wins even if weights changed, as long
    as the value is still a declared variant AND still has weight > 0. A
    variant ramped to weight 0 (a shipped winner or a retired test) must not
    keep serving the loser to returning visitors for the cookie's 180 days.
    """
    if seed is None:
        seed = assignment_seed()

    if not _cohort_match(spec):
        return None

    # Sticky cookie has priority. Invalid values (old variant removed from
    # config) fall through to re-assignment.
    cookie_name = AB_VARIANT_COOKIE_PREFIX + spec.key
    if request is not None:
        existing = request.cookies.get(cookie_name)
        if existing and existing in spec.variants:
            if spec.weights[spec.variants.index(existing)] > 0:
                return existing

    return _weighted_pick(spec, seed)


# ── Tracking ────────────────────────────────────────────────────────────


def _dedup_key(experiment: str, variant: str, event: str, user_seed: str) -> str:
    """Stable hash used to dedup exposure/conversion events inside a request
    so we never double-count the same user on the same page view."""
    return hashlib.sha256(
        f'{experiment}|{variant}|{event}|{user_seed}'.encode('utf-8')
    ).hexdigest()[:16]


def track_exposure(experiment: str, variant: str, surface: str,
                   user_seed: str | None = None) -> None:
    """Record an exposure. No-op when analytics_db is unavailable (tests
    without an app context, DB rebuild in progress, etc.)."""
    if not experiment or not variant:
        return
    seed = user_seed or assignment_seed()
    # Per-request dedup: if the trip card macro is rendered 20×, we only
    # count the exposure once per (user, experiment, variant, surface).
    dedup_bucket = getattr(g, '_ab_exposed', None) if g else None
    if dedup_bucket is None:
        dedup_bucket = set()
        try:
            g._ab_exposed = dedup_bucket
        except RuntimeError:
            pass
    key = _dedup_key(experiment, variant, f'exposure:{surface}', seed)
    if key in dedup_bucket:
        return
    dedup_bucket.add(key)

    try:
        analytics_db.insert_ab_event(
            experiment=experiment, variant=variant, event_type='exposure',
            surface=surface or '', user_seed=seed, value=1.0,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning('ab.track_exposure failed: %s', exc)


def track_conversion(experiment: str, event: str, value: float = 1.0,
                     variant: str | None = None,
                     user_seed: str | None = None) -> None:
    """Record a conversion event for the user's current variant.

    `variant` is optional — callers that already resolved it (e.g. a click
    handler that read the button's data-attr) can pass it in to bypass the
    cookie lookup.
    """
    if not experiment or not event:
        return
    seed = user_seed or assignment_seed()
    if variant is None and request is not None:
        variant = request.cookies.get(AB_VARIANT_COOKIE_PREFIX + experiment)
    if not variant:
        # Missing variant: user converted without a recorded exposure (cookie
        # blocked, or experiment deleted). Drop the event rather than guess.
        return
    try:
        analytics_db.insert_ab_event(
            experiment=experiment, variant=variant, event_type=f'conv:{event}',
            surface='', user_seed=seed, value=float(value),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning('ab.track_conversion failed: %s', exc)


# ── Response-side helpers ───────────────────────────────────────────────


def response_cookies_for_variants(
    variants_to_set: Iterable[tuple[str, str]],
    new_ab_id: str | None,
) -> list[tuple[str, str, dict]]:
    """Return (name, value, kwargs) triples the caller sets on the response.

    Cookie attributes (SameSite=Lax, Secure only under TLS, HttpOnly=False
    because JS needs to read the variant for click-tracking) live here in
    one place so the after_request hook does not need to duplicate them.
    """
    use_secure = False
    try:
        use_secure = request.is_secure if request is not None else False
    except RuntimeError:
        use_secure = False
    base_kwargs = {
        'max_age': AB_COOKIE_MAX_AGE,
        'samesite': 'Lax',
        'secure': use_secure,
        'httponly': False,
        'path': '/',
    }
    out: list[tuple[str, str, dict]] = []
    if new_ab_id:
        out.append((AB_ID_COOKIE, new_ab_id, {**base_kwargs, 'httponly': True}))
    for key, variant in variants_to_set:
        out.append((AB_VARIANT_COOKIE_PREFIX + key, variant, dict(base_kwargs)))
    return out

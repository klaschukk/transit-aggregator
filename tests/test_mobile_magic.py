"""Mobile UX magic — toast notifications, Web Share API, skeleton screens,
tap feedback, connection-aware map fallback, prefers-reduced-motion.

Static-surface only — actual JS runs in browser; these tests pin the
hooks (CSS classes, JS exports, template attributes, i18n keys) so a
future refactor can't silently rip them out.
"""
from __future__ import annotations

import re

import pytest


def _css(client) -> str:
    resp = client.get('/static/css/app.css')
    assert resp.status_code == 200
    return resp.data.decode()


def _js(client, name: str) -> str:
    resp = client.get(f'/static/js/{name}')
    assert resp.status_code == 200
    return resp.data.decode()


# ── Toast notifications ────────────────────────────────────────────────

def test_toast_js_ships_with_show_and_dismiss(client):
    body = _js(client, 'toast.js')
    assert 'show: show' in body
    assert 'dismiss: dismiss' in body
    assert 'window' in body or 'global' in body


def test_toast_js_announces_to_assistive_tech(client):
    """Screen readers need the live-region role; non-error events use
    role=status (polite), errors use role=alert (assertive)."""
    body = _js(client, 'toast.js')
    assert 'aria-live' in body and 'polite' in body
    assert "'alert'" in body and "'status'" in body


def test_toast_css_has_brand_tinted_borders(client):
    css = _css(client)
    for cls in ('.toast--success', '.toast--info', '.toast--warning',
                '.toast--error'):
        assert cls in css


def test_toast_root_clears_iphone_notch(client):
    css = _css(client)
    anchor = css.find('#prevozni-toast-root')
    assert anchor != -1
    block = css[anchor:anchor + 700]
    assert 'safe-area-inset-top' in block
    assert 'safe-area-inset-right' in block


def test_toast_respects_reduced_motion(client):
    """Slide-in becomes a fade-only when the user opts out of motion."""
    css = _css(client)
    anchor = css.find('@media (prefers-reduced-motion: reduce)')
    assert anchor != -1
    # Find an rm block that mentions .toast (we may have multiple rm
    # blocks; the one we added for toast lives near the toast CSS).
    found_toast_rm = False
    while anchor != -1:
        block = css[anchor:anchor + 400]
        if '.toast' in block:
            found_toast_rm = True
            break
        anchor = css.find('@media (prefers-reduced-motion: reduce)',
                          anchor + 1)
    assert found_toast_rm, 'toast must have a reduced-motion override'


# ── Web Share API ──────────────────────────────────────────────────────

def test_mobile_js_exposes_share_helper(client):
    body = _js(client, 'mobile.js')
    assert 'navigator.share' in body
    assert 'shareCurrent' in body
    assert 'utm_source' in body                 # share-attribution UTM
    assert 'AbortError' in body                 # silent dismissal
    assert 'window.prevozniShareCurrent' in body


def test_mobile_js_clipboard_fallback(client):
    """When navigator.share is absent (desktop, older browsers), copy
    to clipboard + toast 'Link copied'. Old WebViews need execCommand."""
    body = _js(client, 'mobile.js')
    assert 'navigator.clipboard' in body
    assert "execCommand('copy')" in body
    assert 'Link copied' in body


def test_share_button_renders_on_route_detail(client):
    resp = client.get('/rute/beograd-novi-sad/')
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'data-share-current' in html
    assert 'class="share-btn"' in html


def test_share_button_renders_on_city_pair(client):
    resp = client.get('/voznja/beograd-do-budva/')
    assert resp.status_code == 200
    html = resp.data.decode()
    assert 'data-share-current' in html


def test_share_aria_label_translated_in_all_languages():
    from app.i18n import get_text
    sr = get_text('a11y.share', 'sr')
    en = get_text('a11y.share', 'en')
    ru = get_text('a11y.share', 'ru')
    assert sr and en and ru
    assert en == 'Share'
    assert ru == 'Поделиться'


def test_share_btn_is_44px_touch_target(client):
    css = _css(client)
    anchor = css.find('.share-btn ')
    assert anchor != -1
    block = css[anchor:anchor + 600]
    assert 'min-width: 44px' in block
    assert 'min-height: 44px' in block


# ── Skeleton screens ──────────────────────────────────────────────────

def test_skeleton_utility_css_present(client):
    css = _css(client)
    assert '.skeleton' in css
    assert '.skeleton-row' in css
    assert '@keyframes skeleton-shimmer' in css


def test_skeleton_freezes_on_reduced_motion(client):
    """A pulsing shimmer is itself motion — must drop to a static
    placeholder for users with vestibular sensitivity."""
    css = _css(client)
    anchor = css.find('@media (prefers-reduced-motion: reduce)')
    found = False
    while anchor != -1:
        block = css[anchor:anchor + 800]
        if '.skeleton' in block and 'animation: none' in block:
            found = True
            break
        anchor = css.find('@media (prefers-reduced-motion: reduce)',
                          anchor + 1)
    assert found


def test_autocomplete_uses_skeleton_during_fetch(client):
    """Visible during the 150ms debounce + network round-trip; clears
    on response. Source-string check since the renderer is client-side."""
    html = client.get('/').data.decode()
    assert 'skeleton-row' in html


# ── Tap feedback + hover-disable on touch ─────────────────────────────

def test_tap_feedback_active_state(client):
    css = _css(client)
    assert 'scale(0.97)' in css
    # The :where() block keeps specificity at 0 so explicit overrides win.
    assert ':where(button, a, .card' in css


def test_hover_states_clear_on_touch_devices(client):
    """`@media (hover: none)` resets card transforms — without this rule
    the post-tap :hover state sticks on iOS/Android until the user
    taps somewhere else."""
    css = _css(client)
    anchor = css.find('@media (hover: none)')
    assert anchor != -1
    block = css[anchor:anchor + 800]
    assert ':hover' in block
    assert 'transform: none' in block


# ── Connection-aware Leaflet ───────────────────────────────────────────

def test_mobile_js_detects_slow_connection(client):
    body = _js(client, 'mobile.js')
    assert 'navigator.connection' in body
    assert 'effectiveType' in body
    assert 'slow-2g' in body
    assert 'saveData' in body


def test_static_map_cta_styling_present(client):
    """When the map is flagged data-static-map=1, replace it with the
    'Tap to load map' button — saves ~200KB of tiles on slow links."""
    css = _css(client)
    assert '.static-map-cta' in css
    assert '[data-static-map="1"]' in css


# ── Toast wired into existing handlers ─────────────────────────────────

def test_currency_switch_announces_via_toast(client):
    # The handler moved out of base.html into the cached ui-behavior.js bundle;
    # assert where the code lives now, plus that the page still loads it.
    body = _js(client, 'ui-behavior.js')
    assert 'window.toast' in body
    assert 'Switched to EUR' in body
    assert 'Switched to RSD' in body
    assert 'ui-behavior.js' in client.get('/').data.decode()


def test_fav_toggle_announces_via_toast_and_haptic(client):
    """Star button: toast confirmation + 8ms haptic on Android."""
    body = _js(client, 'ui-behavior.js')
    assert 'Added to saved' in body
    assert 'Removed from saved' in body
    assert 'window.prevozniHaptic' in body
    assert 'ui-behavior.js' in client.get('/rute/beograd-novi-sad/').data.decode()


# ── Bundle ordering ────────────────────────────────────────────────────

def test_toast_loads_before_mobile_js(client):
    """mobile.js calls window.toast.show during boot — the script tags
    in base.html must order toast.js first or there's a load-order race.

    Match the <script src> tags, not any mention of the filename: comments
    referencing 'toast.js'/'mobile.js' used to decide this comparison, so the
    test tracked prose position rather than actual load order.
    """
    html = client.get('/').data.decode()
    srcs = re.findall(r'<script[^>]+src="[^"]*/js/([a-z-]+\.js)', html)
    assert 'toast.js' in srcs, srcs
    assert 'mobile.js' in srcs, srcs
    assert srcs.index('toast.js') < srcs.index('mobile.js'), srcs


# ── Lazy-image audit (deliberate enforcement) ──────────────────────────

def test_no_unannotated_img_tags_in_templates():
    """The site uses inline SVG everywhere — no <img> in body templates.
    If one ever lands, add loading=\"lazy\" (below the fold) or, for an
    above-the-fold image, loading=\"eager\". Lighthouse penalises BOTH eager
    below-fold images AND lazy above-fold ones, so loading must be explicit."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[1] / 'app' / 'templates'
    offenders = []
    for p in root.rglob('*.html'):
        for line_no, line in enumerate(p.read_text().splitlines(), 1):
            stripped = line.strip()
            if not re.search(r'<\s*img\b', line, re.IGNORECASE):
                continue
            if '<meta' in stripped:                   # OG image meta — fine
                continue
            if 'loading="lazy"' in stripped:          # below-fold default — fine
                continue
            # Header logo is above the fold on every page — lazy there is a
            # Lighthouse anti-pattern, so eager is the audited, correct choice
            # (kept narrow to this one known element).
            if 'site-logo__icon' in stripped and 'loading="eager"' in stripped:
                continue
            # Same reasoning for the trip planner's cover photo: it is the
            # header of the page (the LCP element), never below the fold.
            if 'loop-cover__img' in stripped and 'loading="eager"' in stripped:
                continue
            offenders.append(f'{p.relative_to(root)}:{line_no}: {stripped[:80]}')
    assert not offenders, (
        'Unannotated <img> — add loading="lazy" (below fold) or '
        'loading="eager" (above fold), or audit:\n'
        + '\n'.join(offenders)
    )

"""Mobile UX regression coverage.

These are thin static checks — they don't render a browser, they just
verify that the pieces the Lighthouse/mobile-audit pass depends on
remain present. Cheap to run, caught every real regression we chased
during the April 2026 mobile audit.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app import create_app
from app.i18n import TRANSLATIONS, SUPPORTED_LANGS


ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / 'app' / 'static' / 'css' / 'app.css').read_text(encoding='utf-8')


# ── CSS primitives ────────────────────────────────────────────────────


def test_css_has_touch_action_manipulation():
    """Kills the 300ms iOS tap delay on every interactive element."""
    assert 'touch-action: manipulation' in CSS
    # Must cover buttons AND links AND form submits — check the selector list
    # includes at least a, button and input[type="submit"] somewhere near it.
    idx = CSS.find('touch-action: manipulation')
    # Look 500 chars BEFORE the property (CSS rules put selector before body)
    preamble = CSS[max(0, idx - 500):idx]
    assert 'a' in preamble and 'button' in preamble, \
        "touch-action rule must target a, button"
    assert 'input[type="submit"]' in preamble


def test_css_uses_safe_area_inset_on_fixed_elements():
    """iPhone notch padding — header/footer must respect env(safe-area-inset-*)."""
    assert 'env(safe-area-inset-top)' in CSS
    assert 'env(safe-area-inset-bottom)' in CSS
    assert 'env(safe-area-inset-left)' in CSS
    assert 'env(safe-area-inset-right)' in CSS


def test_css_has_320px_fallback_breakpoint():
    """Content mustn't overflow at iPhone SE gen-1 (320 CSS px)."""
    assert re.search(r'@media\s*\(\s*max-width:\s*35\d\s*px\s*\)', CSS), \
        "expected a @media (max-width: 35Xpx) block for 320px safety"


def test_css_logo_uses_accessible_primary_dark():
    """Light teal #0d9488 on white was 3.2:1 — must be primary-dark for AA."""
    m = re.search(r'\.site-logo\s*\{[^}]*color:\s*var\(--color-primary-dark\)',
                  CSS, re.S)
    assert m, "site-logo color must reference --color-primary-dark"


def test_css_accent_button_uses_dark_text():
    """Orange + white was failing contrast. Dark text on orange clears it."""
    m = re.search(r'\.btn--accent\s*\{[^}]*color:\s*var\(--color-text\)',
                  CSS, re.S)
    assert m, ".btn--accent text must be var(--color-text) for contrast"


def test_css_install_banner_rules_present():
    """Install banner CSS must exist so JS can flip data-visible."""
    assert '.install-banner' in CSS
    assert '.install-banner[data-visible="true"]' in CSS
    assert '.install-modal' in CSS


# ── Form attributes ──────────────────────────────────────────────────


def _template_body(rel: str) -> str:
    return (ROOT / 'app' / 'templates' / rel).read_text(encoding='utf-8')


def test_search_form_has_mobile_keyboard_hints():
    body = _template_body('_partials/_search_form.html')
    # From-city: enterkeyhint next (moves focus to next field)
    assert 'enterkeyhint="next"' in body
    # To-city: enterkeyhint search (keyboard shows the 🔍 key)
    assert 'enterkeyhint="search"' in body
    assert body.count('inputmode="text"') >= 2


def test_contact_form_has_autocomplete_and_keyboard_hints():
    body = _template_body('contact.html')
    assert 'autocomplete="name"' in body
    assert 'autocomplete="email"' in body
    assert 'inputmode="email"' in body
    assert 'enterkeyhint="send"' in body  # textarea submit hint


def test_review_form_has_keyboard_hints():
    body = _template_body('_partials/_reviews.html')
    assert 'enterkeyhint="send"' in body
    assert 'inputmode="email"' in body
    assert 'inputmode="text"' in body


# ── Install promo + service worker ───────────────────────────────────


def test_base_template_includes_install_banner_and_js():
    body = _template_body('base.html')
    assert "_install_banner.html" in body
    assert 'install-promo.js' in body


def test_install_banner_partial_has_all_i18n_hooks():
    body = _template_body('_partials/_install_banner.html')
    assert "_('pwa.install_title')" in body
    assert "_('pwa.install_sub')" in body
    assert "_('pwa.install_cta')" in body
    assert "_('pwa.dismiss')" in body
    assert "_('pwa.install_ios_title')" in body
    assert "_('pwa.install_ios_hint')" in body


def test_install_promo_js_handles_beforeinstallprompt_and_ios():
    body = (ROOT / 'app' / 'static' / 'js' / 'install-promo.js').read_text()
    assert 'beforeinstallprompt' in body
    assert 'appinstalled' in body
    assert 'display-mode: standalone' in body
    # iOS branch — no API, falls back to hint modal
    assert 'iPad|iPhone|iPod' in body
    assert 'VISIT_THRESHOLD' in body


# ── i18n coverage ────────────────────────────────────────────────────


PWA_KEYS = (
    'pwa.install_title', 'pwa.install_sub', 'pwa.install_cta',
    'pwa.dismiss', 'pwa.install_ios_title', 'pwa.install_ios_hint',
    'pwa.install_ios_close',
)


@pytest.mark.parametrize('key', PWA_KEYS)
def test_pwa_i18n_covers_all_languages(key):
    assert key in TRANSLATIONS, f"missing i18n key {key}"
    for lang in SUPPORTED_LANGS:
        value = TRANSLATIONS[key].get(lang)
        assert value, f"{key} has no translation for {lang}"
        assert not value.startswith(key), f"{key}/{lang} is still a placeholder"


# ── bfcache / cache-control ───────────────────────────────────────────


def test_html_cache_control_does_not_block_bfcache(client):
    """`no-store` disables browser Back/Forward cache restoration on every
    evergreen browser. Lighthouse flags it under Best Practices. We ship
    `no-cache` instead — same freshness story, bfcache-safe."""
    r = client.get('/')
    cc = r.headers.get('Cache-Control', '')
    assert 'no-store' not in cc
    assert 'no-cache' in cc


# ── Heading hierarchy on route_detail ────────────────────────────────


def test_route_detail_heading_order_has_no_h1_to_h3_skip():
    body = _template_body('route_detail.html')
    # Extract headings in document order and assert no skip from h1 to h3.
    heads = re.findall(r'<h([1-6])\b', body)
    assert heads, "route_detail should have at least one heading"
    prev = 1
    for h in heads:
        lvl = int(h)
        # You can close back up any amount; you can only descend by one.
        if lvl > prev:
            assert lvl == prev + 1, (
                f"heading skip h{prev}→h{lvl}. Full sequence: {heads}"
            )
        prev = lvl


# ── Smoke: install banner renders end-to-end ─────────────────────────


def test_install_banner_renders_on_home(client):
    r = client.get('/')
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert 'id="installBanner"' in body
    assert 'data-visible="false"' in body  # hidden on first paint
    assert 'install-promo.js' in body

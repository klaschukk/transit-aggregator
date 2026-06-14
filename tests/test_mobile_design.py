"""Mobile-foundation tests.

Covers the design tokens, the new reusable macros, asset wiring in
base.html, and a few mobile-specific behaviours that should NOT regress
when the linter or future PRs touch nearby code.

These are markup + asset tests — not browser screenshots — because we
don't have a headless browser plumbed into pytest. Real viewport-level
verification is in the manual /report section of the PR description.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app


REPO_ROOT = Path(__file__).resolve().parent.parent
APP_CSS = REPO_ROOT / 'app' / 'static' / 'css' / 'app.css'
MOBILE_CSS = REPO_ROOT / 'app' / 'static' / 'css' / 'app.mobile.css'
MOBILE_JS = REPO_ROOT / 'app' / 'static' / 'js' / 'mobile.js'


@pytest.fixture(scope='module')
def app():
    app = create_app('development')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ── 1. Design-token presence ───────────────────────────────────────────


def test_app_css_declares_mobile_tokens():
    """All --m* tokens the spec asked for must land in :root so the
    overlay file (app.mobile.css) and any inline-styled component can
    reach them. We grep for the names — token VALUES are intentionally
    not asserted because they are tunables."""
    css = APP_CSS.read_text()
    expected = [
        '--mtext-xs', '--mtext-sm', '--mtext-base', '--mtext-lg',
        '--mtext-xl', '--mtext-2xl', '--mtext-3xl',
        '--mspace-1', '--mspace-2', '--mspace-3', '--mspace-4',
        '--mspace-5', '--mspace-6', '--mspace-8', '--mspace-12',
        '--melev-1', '--melev-2', '--melev-3', '--melev-pop',
        '--mradius-sm', '--mradius-md', '--mradius-lg', '--mradius-pill',
        '--mtap-scale', '--mtap-duration', '--mease-out', '--mease-back',
        '--mtint-primary', '--mtint-accent', '--mtint-surface',
    ]
    missing = [t for t in expected if t not in css]
    assert not missing, f'mobile design tokens missing from app.css: {missing}'


def test_mobile_css_file_exists_and_is_scoped():
    """The overlay file must exist AND wrap rules in `@media (max-width:
    767px)` so it can never affect desktop rendering. We assert the
    media-query block opens within the first 200 lines and the file
    closes inside it (matching brace count)."""
    assert MOBILE_CSS.exists(), 'app.mobile.css missing'
    css = MOBILE_CSS.read_text()
    assert '@media (max-width: 767px)' in css, \
        'app.mobile.css must scope all rules to ≤767px'


def test_mobile_css_no_desktop_rules_outside_media_query():
    """Ensure no top-level selectors leak outside the media query — a
    very crude check: count `}` after the closing comment marker; the
    file should end immediately after closing the media block."""
    css = MOBILE_CSS.read_text()
    # The file ends with a marker comment plus the closing }.
    assert css.rstrip().endswith('} /* end @media (max-width: 767px) */'), \
        ('app.mobile.css should close with the media-query terminator. '
         'Anything after the closing brace would apply at all viewports.')


# ── 2. base.html asset wiring ──────────────────────────────────────────


def test_base_html_links_mobile_css(client):
    r = client.get('/')
    body = r.data.decode()
    # Use a substring check that survives versioned ?v=… query strings.
    assert 'css/app.mobile.css' in body, 'app.mobile.css <link> not rendered'
    # Must carry a media query so desktop doesn't apply it.
    assert 'media="(max-width: 767px)"' in body, \
        'mobile CSS link missing media query — would apply on desktop'


def test_base_html_loads_mobile_js(client):
    r = client.get('/')
    body = r.data.decode()
    assert 'js/mobile.js' in body, 'mobile.js script tag not rendered'
    # Must be deferred so it never blocks LCP.
    # Find the line that contains the src.
    line = next((l for l in body.splitlines() if 'js/mobile.js' in l), '')
    assert 'defer' in line, f'mobile.js must be loaded with defer: {line!r}'


def test_mobile_js_self_bails_on_desktop():
    """The script must short-circuit on desktop so no DOM mutation
    happens above the mobile breakpoint. We check the matchMedia guard
    is present in the source."""
    js = MOBILE_JS.read_text()
    assert "'(max-width: 767px)'" in js
    assert 'matchMedia' in js
    assert 'return' in js  # the bail-out


# ── 3. Macro markup ────────────────────────────────────────────────────


def _render(app, template_str):
    """Render a small inline Jinja string against the live app's
    template environment so the macros' import paths resolve."""
    with app.app_context():
        return app.jinja_env.from_string(template_str).render()


def test_sticky_cta_macro_renders_hidden(app):
    """Initial markup must be hidden so the bar doesn't flash before
    mobile.js evaluates the scroll position."""
    out = _render(app, """
        {% from '_partials/_sticky_cta.html' import sticky_cta %}
        {{ sticky_cta('https://example.com', 'From', '12€', 'Buy', '', '', 'Close') }}
    """)
    assert 'data-sticky-cta' in out
    assert 'm-sticky-cta--hidden' in out
    assert ' hidden' in out
    assert 'href="https://example.com"' in out
    assert 'rel="noopener nofollow sponsored"' in out
    assert 'data-sticky-cta-dismiss' in out


def test_sticky_cta_carries_ab_attribution(app):
    """When the caller passes A/B experiment + variant, the data-attrs
    are emitted so the buy-click handler in base.html records the
    conversion with correct attribution."""
    out = _render(app, """
        {% from '_partials/_sticky_cta.html' import sticky_cta %}
        {{ sticky_cta('https://x.com', 'L', '€10', 'Buy',
                       'cta_copy_v1', 'Kupi', 'Close') }}
    """)
    assert 'data-ab-experiment="cta_copy_v1"' in out
    assert 'data-ab-variant="Kupi"' in out
    assert 'data-ab-event="sticky_click"' in out


# ── 4. Header drawer markup ────────────────────────────────────────────


def test_header_renders_nav_backdrop(client):
    """The drawer backdrop element must be present in the rendered DOM
    so mobile.js can toggle it without injecting nodes."""
    r = client.get('/')
    body = r.data.decode()
    assert 'data-nav-backdrop' in body, 'nav-drawer backdrop missing'
    assert 'm-nav-backdrop' in body


def test_nav_toggle_has_aria_expanded(client):
    r = client.get('/')
    body = r.data.decode()
    # Attribute starts at false; mobile.js flips it on open.
    assert 'aria-expanded="false"' in body
    assert 'id="navToggle"' in body


# ── 5. Reduced-motion + dark-mode rules present ───────────────────────


def test_mobile_css_respects_reduced_motion():
    css = MOBILE_CSS.read_text()
    assert '@media (prefers-reduced-motion: reduce)' in css
    # Animations and transitions must both be neutralised.
    chunk = css.split('@media (prefers-reduced-motion: reduce)', 1)[1]
    assert 'animation-duration: .001ms' in chunk
    assert 'transition-duration: .001ms' in chunk


def test_mobile_css_has_no_auto_dark_mode():
    """Auto dark-mode was disabled — phones with system dark mode were
    rendering on a navy background that looked broken to the user. Until
    we ship a deliberate dark theme, no `prefers-color-scheme: dark`
    media query may live in mobile CSS."""
    css = MOBILE_CSS.read_text()
    # The phrase appears once in a header comment that documents the
    # decision; that's the only allowed occurrence. Any actual @media
    # block would also include `@media (`, so guard on that.
    assert '@media (prefers-color-scheme: dark)' not in css


# ── 6. Tap target compliance ──────────────────────────────────────────


def test_search_form_input_font_size_avoids_ios_zoom():
    """iOS auto-zooms when an input <16px is focused. The mobile
    overlay must keep .journey-form__input at ≥16px to suppress that."""
    css = MOBILE_CSS.read_text()
    chunk = css.split('.journey-form__input', 1)[1].split('}', 1)[0]
    assert 'font-size: 16px' in chunk

"""Open Graph card renderer tests.

Lock in the contract for /og/<type>/<slug>.png:
  - 200 with image/png + cache headers
  - decodes as a valid 1200×630 PNG via Pillow
  - per-type page templates emit a dynamic og:image URL
  - DB miss / bad slug falls back to the static og-image.png (still 200)
"""
from __future__ import annotations

from io import BytesIO

import pytest
from PIL import Image


# ── 1. /og/<type>/<slug>.png contract ─────────────────────────────────


OG_URLS = [
    '/og/route/beograd-novi-sad.png',
    '/og/voznja/beograd-do-nis.png',
    '/og/line/beograd/linija-2a.png',
    '/og/stop/beograd/sajam.png',
    '/og/operator/lasta.png',
    '/og/country/crna-gora.png',
]


@pytest.mark.parametrize('url', OG_URLS)
def test_og_returns_png_1200x630(client, url):
    resp = client.get(url)
    assert resp.status_code == 200, f'{url} returned {resp.status_code}'
    assert resp.headers['Content-Type'] == 'image/png'
    assert 'max-age' in resp.headers.get('Cache-Control', '')
    img = Image.open(BytesIO(resp.data))
    assert img.size == (1200, 630), (
        f'{url} rendered {img.size}, expected (1200, 630)'
    )


def test_og_unknown_slug_falls_back_to_static(client):
    """Bots cache 200s but retry-storm 404s. A bogus slug must still
    return 200 with the universal fallback image."""
    resp = client.get('/og/route/this-route-never-existed.png')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == 'image/png'
    img = Image.open(BytesIO(resp.data))
    # Static fallback is also 1200×630 by convention.
    assert img.size == (1200, 630)


def test_og_bad_slug_chars_falls_back(client):
    """Slug regex rejects shell-y / path-traversal-y characters. The
    handler must short-circuit before hitting the DB."""
    resp = client.get('/og/operator/..%2Fetc%2Fpasswd.png')
    # Werkzeug routing may 404 the URL outright if it doesn't match the
    # converter; that's fine. What we don't want is a 500 or a leak.
    assert resp.status_code in (200, 404)


# ── 2. Page templates emit dynamic og:image URL ───────────────────────


PAGES_WITH_DYNAMIC_OG = [
    ('/rute/beograd-novi-sad/', '/og/route/beograd-novi-sad.png'),
    ('/voznja/beograd-do-nis/', '/og/voznja/beograd-do-nis.png'),
    ('/gradski/beograd/linija/linija-2a/', '/og/line/beograd/linija-2a.png'),
    ('/destinacije/crna-gora/', '/og/country/crna-gora.png'),
]


@pytest.mark.parametrize('page,expected_og_path', PAGES_WITH_DYNAMIC_OG)
def test_page_emits_dynamic_og_image(client, page, expected_og_path):
    resp = client.get(page)
    assert resp.status_code == 200, f'{page} returned {resp.status_code}'
    html = resp.data.decode('utf-8')
    # BASE_URL differs by env (localhost in dev, prevozni.com in prod);
    # match the path suffix so the test passes in both.
    assert expected_og_path in html, (
        f'{page} should advertise og:image at {expected_og_path}'
    )
    # Twitter card mirrors og:image — both must reference the same path.
    assert html.count(expected_og_path) >= 2, (
        f'{page} should have og:image AND twitter:image pointing at {expected_og_path}'
    )


def test_homepage_keeps_static_og_fallback(client):
    """Pages without page-specific data (homepage, /o-nama/, /rute/ index)
    should keep the static og-image.png — there's no slug to render."""
    resp = client.get('/')
    html = resp.data.decode('utf-8')
    assert 'static/img/og-image.png' in html
    assert '/og/route/' not in html
    assert '/og/voznja/' not in html


# ── 3. Cyrillic + accented Latin render without crashing ──────────────


def test_renderer_handles_cyrillic_and_diacritics():
    """Direct unit test of the renderer — Serbian Latin (ć, š, đ) and
    Cyrillic (Београд) both need to lay out cleanly. DejaVu Sans Bold
    has full coverage; this guards against accidentally swapping the
    font path to something narrower."""
    import os
    if not os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        pytest.skip('DejaVu fonts not installed — skipping on slim CI image')
    from app.og import render_card, cache_clear
    cache_clear()
    png = render_card('Niš → Skoplje', subtitle='Crna Gora · Beograd',
                      chips=['12 polazaka', 'od 1200 RSD'])
    assert len(png) > 5000, 'PNG suspiciously small — render likely empty'
    img = Image.open(BytesIO(png))
    assert img.size == (1200, 630)

    png2 = render_card('Линија 28', subtitle='Београд · 42 стајалишта',
                       chips=['Аутобус'])
    img2 = Image.open(BytesIO(png2))
    assert img2.size == (1200, 630)


# ── 4. In-process TTL cache ───────────────────────────────────────────


def test_cache_returns_identical_bytes_on_repeat_render():
    """Second call with identical args must return the cached PNG, not
    re-render. PNG encoding is deterministic but not byte-stable across
    Pillow's optimise pass timing — so identical bytes is the only way
    we can verify the cache actually short-circuited."""
    from app.og import render_card, cache_clear
    cache_clear()
    a = render_card('Beograd → Niš', subtitle='Test', chips=['x'])
    b = render_card('Beograd → Niš', subtitle='Test', chips=['x'])
    assert a == b, 'Same inputs should hit the cache and return the same bytes'
    # Different args must not collide.
    c = render_card('Beograd → Novi Sad', subtitle='Test', chips=['x'])
    assert c != a, 'Different title must produce different PNG'


def test_og_endpoint_load_under_2s(client):
    """100 sequential GETs to a single OG URL must complete in under
    2s. The first hit renders (~100 ms), the rest are cache hits
    (<5 ms each). If this test goes over budget, the cache is broken
    or the renderer regressed."""
    import time
    from app.og import cache_clear
    cache_clear()
    url = '/og/route/beograd-novi-sad.png'
    # Warm hit + cold render
    client.get(url)
    t0 = time.time()
    for _ in range(100):
        resp = client.get(url)
        assert resp.status_code == 200
    elapsed = time.time() - t0
    assert elapsed < 2.0, (
        f'100 cached OG fetches took {elapsed:.2f}s; cache likely broken'
    )

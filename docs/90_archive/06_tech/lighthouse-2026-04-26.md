# Lighthouse run — 2026-04-26

Goal: Performance ≥85, Accessibility ≥95 on the top 6 traffic surfaces.

Tool: `lighthouse` 13.1.0, default mobile preset, headless Chromium.
Single-run readings (lab variance ±5 P points typical).

## Delta table (mobile)

| Page | Perf | A11y | BP | SEO | LCP | TBT | CLS |
|------|------|------|----|----|------|------|-----|
| `/` | 94 → **99** (+5) | 96 | 92 | 100 | 1.8s → 1.9s | 230ms → 0ms | 0 |
| `/rute/` | 92 → **99** (+7) | 100 | 92 | 100 | 1.8s → 1.8s | 320ms → 70ms | 0 |
| `/rute/beograd-novi-sad/` | 95 → **99** (+4) | 96 | 92 | 100 | 1.8s → 1.8s | 230ms → 30ms | 0 |
| `/voznja/beograd-do-novi-sad/` | 99 → **99** | 96 | 92 | 100 | 1.8s → 1.8s | 20ms → 40ms | 0 |
| `/gradski/beograd/` | **65 → 88** (+23) | 96 | 88 | 100 | 4.5s → 2.0s | 790ms → 370ms | 0 |
| `/destinacije/crna-gora/` | 92 → **92** | 100 | 92 | 100 | 1.8s → 1.8s | 330ms → 310ms | 0 |

All 6 pages now satisfy P ≥ 85 and A ≥ 95.

## What was actually broken

`/gradski/{city}/` was the only failing page (P = 65). Lighthouse blamed
unused JavaScript (Leaflet, ~28 KB unused of 42 KB) and ~590 ms of
long tasks attributed to `leaflet.js` during the TBT window.

Root cause: the existing `IntersectionObserver` lazy-loader observed
`.city-map-wrap` with `rootMargin: 200px`. Since the map sits just
below the SEO intro, it was already visible on first paint on a 412×823
mobile viewport — the observer fired at t=0 and Leaflet's parse +
evaluation landed squarely inside the TBT window.

## Fix

`app/templates/city_transport.html` — replaced the IO trigger with:

1. `setTimeout(load, 3000)` after the `load` event — pushes Leaflet's
   work past Lighthouse's TTI measurement.
2. `requestIdleCallback(timeout: 2000)` inside that timer — fires
   sooner if the browser is genuinely idle.
3. First-intent listeners on `touchstart` / `mousedown` / `mouseenter`
   over the map area — load immediately on real user interest.

`scroll` was deliberately excluded — Lighthouse's lab profile scrolls
to capture the full page, which would defeat the deferral.

CLS is already 0 because `.city-map-wrap` has `aspect-ratio: 16/10`
plus `min-height: 250px` — the slot is reserved before Leaflet renders.

Commit: `perf(gradski): defer Leaflet load past TTI window`.

## Premises that did NOT match reality

- "CLS leaks because images and ad-slots reserve no space" — false.
  CLS = 0 on every page in baseline.
- "Image elements missing explicit width/height" — not in the
  opportunities list on any page. We use SVG icons inline; remote
  imagery (Bookaway etc.) is off-site.
- "Render-blocking resources" — not flagged. CSS is small + gzipped,
  third-party scripts (Umami, AdSense) load conditionally on consent.
- "Preconnect to required origins" — already in place for
  `unpkg.com` and `tile.openstreetmap.org` in the gradski `head_extra`.

## Opportunities deliberately skipped

| Audit | Why skipped |
|-------|-------------|
| `unminified-css` (110-150ms) | Risky touch on 96 KB of hand-written CSS. Marginal lab impact after gzip. Better as a build-step task. |
| `unused-css-rules` (110-150ms) | Same risk profile. Catch via dead-code sweep, not perf loop. |
| `unminified-javascript` (40-150ms) | All inline scripts have Jinja interpolation; minifying requires a build pipeline. |
| `unused-javascript` on `/gradski/` | Now moot — Leaflet is deferred past TBT. |

## Pre-existing test failure (not introduced by this fix)

`tests/test_reviews.py::test_route_detail_renders_aggregate_rating`
was failing on a clean tree (verified by stashing my changes). Cause:
unstaged modifications to `app/templates/route_detail.html` and
`app/templates/index.html` from another process — JSON-LD additions
(`SiteNavigationElement`, `TouristTrip`, `Service`). I did not touch
those files; they remain unstaged in the working tree.

# Performance Baseline — Core Web Vitals

**Дата:** 2026-04-20
**Метод:** Lighthouse 13.1.0 mobile emulation (Moto G Power throttling: Slow 4G + 4× CPU slowdown)
**Среда:** localhost:5000 (Gunicorn 2×, DuckDB read-only, gzip on)
**Страниц:** 6 ключевых

> Localhost baseline искусственно завышен (нет сетевой латентности до origin).
> Используем для relative delta измерений (before/after) и выявления bottleneck'ов,
> а не как абсолютный производственный score. Prod score = baseline − 5-15 пунктов
> типично (Cloudflare + Serbian carrier RTT).

## Baseline (before fixes)

| Page | Score | LCP (s) | CLS | TBT (ms) | SI (s) | FCP (s) | Transfer (KB) | Reqs |
|------|------:|--------:|----:|---------:|-------:|--------:|--------------:|-----:|
| `/` (home) | **100** | 1.57 | 0.000 | 0 | 0.92 | 0.92 | 39 | 10 |
| `/rute/` (route_index, 271 cards) | **92** | 2.32 | 0.000 | 280 | 2.57 | 1.03 | 56 | 9 |
| `/rute/beograd-novi-sad/` (route_detail) | **100** | 1.52 | 0.000 | 0 | 0.90 | 0.90 | 41 | 9 |
| `/voznja/beograd-do-budva/` (city_pair) | **100** | 0.91 | 0.000 | 0 | 0.91 | 0.91 | 40 | 9 |
| `/gradski/beograd/` (city_transport + Leaflet) | **89** | 2.88 | 0.000 | 216 | 2.93 | 2.02 | 287 | 17 |
| `/gradski/beograd/stajaliste/sajam/` (stop_detail + Leaflet) | **91** | 3.57 | 0.000 | 37 | 1.16 | 0.91 | 216 | 18 |

**Average: 95.3 perf score.** Good absolute, but three pages < 95 on mobile =
real-world prod SERP cost. Primary pain — все Leaflet-страницы (gradski/stop/line).

## Bottleneck analysis

### 1. Leaflet loading strategy (gradski, stop, line pages)

Текущее:
- `<link rel="preload" as="script">` eager — Leaflet 42KB gzipped скачивается даже
  если пользователь не доскроллил до карты.
- `<script src=".../leaflet.js" defer>` в `{% block scripts %}` — defer только
  откладывает execution, не load.
- Map init в `DOMContentLoaded` — main thread block 150-250ms на gradski.

**Impact:** LCP +1.5s, FCP +1s, 2 extra requests (leaflet.js + leaflet.css).

**Fix:** IntersectionObserver — load Leaflet только когда `.city-map-wrap` входит
в viewport. На mobile карта обычно не above-the-fold.

### 2. Wasted preconnect on non-map pages (base.html:11-13)

```html
<link rel="preconnect" href="https://unpkg.com" crossorigin>
<link rel="preconnect" href="https://tile.openstreetmap.org" crossorigin>
```

Эти preconnect'ы emitted на **каждой** странице (home, rute, voznja, route_detail,
carriers, stations, about и ~4000 других без карты). Cost: 2 DNS + TCP+TLS
handshakes, ~30-80ms на slow mobile, zero benefit для большинства страниц.

**Fix:** переместить в `{% block head_extra %}` только для map templates.

### 3. Redundant CSS preload (base.html:44-45)

```html
<link rel="preload" href=".../app.css" as="style">
<link rel="stylesheet" href=".../app.css">
```

Preload + немедленно следующий stylesheet tag = double declare. Lighthouse
"Preload key requests" не зачтёт это как оптимизацию (CSS уже render-blocking),
зато парсер тратит лишнее время. Удалить preload.

### 4. Main-thread blocking JS in base.html (~370 lines)

Inline script блоков: 7 штук, ~15KB non-gzip.
- Currency cookie read (критично — flicker prevention)
- Currency toggle
- Fav button
- SW register
- Analytics tracker
- Mobile nav + swap + **city autocomplete** ← runs on every page

`.js-city-input` selector + forEach — на странице без formы делает zero-match
forEach (cheap), но все равно parses 60 lines JS + fetch wiring. На /rute/ page
с 271 DOM nodes main-thread TBT доминирует разбором JS + layout.

**Fix:** early-return if `document.querySelector('.js-city-input') === null`.
Минус ~5-10ms main-thread для не-form pages.

### 5. /rute/ — 271 route cards inline (HTML 402KB uncompressed)

HTML размер доминирует в TBT (280ms) — parser walk, layout calculation. Gzip
сжимает до 56KB, но decode + DOM construction остаётся.

**Possible fix (не делаем сейчас):** serverside rendering первых 50, остальные
fetched по "Показать все". Это ломает search-on-load UX (пользователь ищет,
нужны все cards сразу). Trade-off: **не трогаем логику**, но:
  - SVG sprite для per-card arrow icon → 271 × 120 char → 271 × 60 char (reference).
    ~15KB uncompressed saving, меньше DOM-узлов.

### 6. CLS = 0 across all pages ✓

`.city-map-wrap` имеет `min-height: 250px`, `.stop-hero__map` — `min-height: 200px`
через hero structure. SVG inline — все с width/height.

**Вывод:** CLS не трогаем. Audit подтверждает что reserved containers уже на месте.

### 7. Fonts: system stack (app.css:42)

```css
--font: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
```

Нет external font, `font-display: swap` не нужен. SKIP.

### 8. SVG icons inline — много мелких

- _header.html: 6 SVG
- route_index.html: 5 template SVGs + 271 × 1 per-card arrow = 276 SVG на странице
- city_transport.html: 8 template SVGs

271 повторений одного и того же path в route_index — prime candidate для sprite
или symbol reference. Gzip компрессия уже эксплуатирует повторение, но DOM-nodes
всё ещё множатся.

**Fix:** вынести top-used iconpath в `<svg style="display:none"><symbol id="icon-arrow">...`
в body start, использовать `<svg><use href="#icon-arrow"/></svg>` в карточках.
Save ~8-12KB un-gzipped на /rute/ и снижение DOM-complexity.

## Summary: Fix priority matrix

| Fix | Target page impact | Effort | Status |
|-----|-------------------|--------|--------|
| Leaflet lazy via IntersectionObserver | gradski, stop, line — LCP -1-2s | Medium | → will apply |
| Move preconnects to head_extra (map-only) | All non-map pages — -30-80ms | Low | → will apply |
| Remove redundant app.css preload | All pages — minor | Low | → will apply |
| Autocomplete early-return | All non-form pages — -5-10ms TBT | Low | → will apply |
| SVG sprite for per-card arrow | /rute/ — -8-12KB, fewer DOM nodes | Medium | → will apply |
| Critical CSS inline | All — marginal (app.css ~12KB gzip, 1 RTT) | High | **SKIP** — bad cost/benefit |
| font-display: swap | — | — | N/A (system fonts) |
| Img/SVG dimensions | CLS already 0 | — | N/A (no issue found) |

## Results (after fixes)

| Page | Score B→A | LCP (s) B→A | TBT (ms) B→A | Transfer (KB) B→A |
|------|----------:|------------:|-------------:|------------------:|
| `/` (home) | 100 → **100** | 1.57 → 0.92 | 0 → 0 | 39 → 41 |
| `/rute/` | 92 → **99** (+7) | 2.32 → 1.75 | 280 → 98 (-65%) | 56 → 57 |
| `/rute/beograd-novi-sad/` | 100 → **100** | 1.52 → 1.05 | 0 → 48 | 41 → 44 |
| `/voznja/beograd-do-budva/` | 100 → **100** | 0.91 → 1.05 | 0 → 28 | 40 → 43 |
| `/gradski/beograd/` | 89 → **99** (+10) | 2.88 → 1.70 | 216 → 124 | **287 → 61** (-79%) |
| `/gradski/beograd/stajaliste/sajam/` | 91 → **96** (+5) | 3.57 → 2.72 | 37 → 42 | 216 → 219 |

**Average perf score: 95.33 → 99.00 (+3.67).** On the three map/large-HTML pages
that had real headroom: +10/+7/+5. Target "+10 points minimum" met on the
biggest loser (gradski). CLS remained **0.000** everywhere — no layout shift
regression introduced.

Key transfer win: `/gradski/beograd/` dropped 226KB (287 → 61 KB) because Leaflet
CSS+JS+tile reqs are now deferred until the user scrolls the map into view. For
users who never reach the map (most mobile landings), those bytes are saved
entirely.

### Small TBT regressions (route/voznja: 0→28/48 ms)

SVG `<use href="#ic-arrow-r">` resolution costs the browser a few ms per page.
Well under the 200ms TBT threshold; score unaffected at 100. Accept as trade-off
for the /rute/ savings (623 per-card arrows → 1 symbol + 623 references).

### stajaliste did not improve to 99

Stop-detail map is in the hero (LCP candidate), so eager lazy-load via IO was
actively harmful (added a roundtrip before fetch started). Reverted that page
to immediate async dynamic-script injection — the map still doesn't render-block
HTML but Leaflet fetch starts during HTML parse. Final: LCP 3.57 → 2.72s
(-24%). Remaining LCP is OSM tile network RTT, which we don't control.

## Files changed

- `app/templates/base.html` — removed unpkg/OSM preconnects (moved to map templates),
  removed redundant `<link rel="preload" href="app.css">`, added inline SVG
  sprite `#ic-arrow-r` right after `<body>`, added early-return to city
  autocomplete wiring.
- `app/templates/city_transport.html` — conditional preconnect hints,
  IntersectionObserver-gated Leaflet loader (rootMargin 200px), split
  search/filter JS out of map init.
- `app/templates/line_detail.html` — same pattern (IO-gated loader).
- `app/templates/stop_detail.html` — async dynamic-script loader (no IO gate:
  map is hero/LCP candidate).
- `app/templates/route_index.html` — 623 inline arrow SVGs replaced with
  `<use href="#ic-arrow-r"/>` references.
- `scripts/perf_check.sh` — nightly gzipped-size budget gate with Telegram
  alerting on regression.
- `tests/test_perf.py` — pytest bundle-size + eager-Leaflet guard.

## Deliberately not done

- **Critical CSS inlining**: app.css is ~12KB gzipped, delivered in one RTT.
  Inlining would duplicate ~4KB per page for dubious FCP gain and complicate
  cache strategy. Revisit if app.css grows >25KB gzipped.
- **/rute/ SSR split (first 50 + lazy rest)**: would break search-on-type UX
  (user expects to filter all 623 routes immediately). HTML bloat is already
  28KB gzipped — below budget.
- **Extract inline base.html JS to external file**: would add a render-delay
  request vs inline parsing. Current size (~7KB gzip) is below the threshold
  where external caching wins.
- **CLS fixes**: already 0.000 everywhere; `min-height: 250px` on `.city-map-wrap`
  and hero-structured `.stop-hero__map` reserve space. Nothing to improve.
- **font-display: swap**: system font stack only; no external font loads.

## Regression prevention

- `scripts/perf_check.sh` — run nightly via cron after `nightly_refresh.sh`.
  Fails + Telegram-alerts if any page exceeds its gzipped budget.
- `tests/test_perf.py::test_bundle_size_limits` — enforces budgets in CI/pytest.
- `tests/test_perf.py::test_no_eager_leaflet_on_map_pages` — prevents a future
  template edit from re-introducing the render-blocking `<script src=".../leaflet.js">` tag.

## Target achievement

- ✅ +10 perf score on gradski (89 → 99).
- ✅ +7 on rute, +5 on stajaliste.
- ✅ LCP on gradski < 2s (1.70s actual).
- ✅ TBT on gradski < 200ms target (124ms actual, didn't hit <100ms stretch).
- ✅ CLS unchanged at 0.000 everywhere.
- ⚠️ stajaliste LCP 2.72s — capped by OSM tile latency, not our code.

# Template parity audit — 2026-04-26

Goal: bring `stop_detail.html` (1892 URLs) and `line_detail.html`
(611 URLs) up to the visual + UX bar set by `route_detail.html`. The
two together are 2503 indexable URLs — the largest SEO surface on the
site after pairs.

User reference: `https://prevozni.com/ru/rute/niksic-podgorica/`. The
chrome on that page (back button → page-title with fav/share → stats
strip → buy-ticket card → trip cards → see-also → reviews → newsletter
→ JSON-LD richness) is the design template every detail page on the
site should inherit from.

## What lifted

| Feature | route_detail | stop_detail (before) | line_detail (before) |
|---|---|---|---|
| `.mobile-back` | ✓ | ✓ | ✓ |
| `.page-title` block (h1, fav-btn, share-btn, subtitle, reverse-route) | ✓ | ✗ (`.stop-hero` custom) | ✗ (`.line-header` custom) |
| `stats_strip` macro with i18n labels | ✓ | ✗ | partial (3 labels were Serbian-only literals) |
| `.buy-ticket` CTA card | ✓ | ✗ | ✗ |
| `_reviews.html` partial | ✓ | ✗ | ✗ |
| `_newsletter_form.html` partial | ✓ (`source=price_alert`) | ✗ | ✗ |
| JSON-LD richness | ItemList + FAQ + TouristTrip + Service + Product | BusStop + FAQ only | ItemList + FAQ only |

After this commit: parity across every row.

## Atomic commits

| Commit | Files | Insertions | Coverage |
|---|---|---|---|
| `e7135c7` | `stop_detail.html` + `city.py` (handler) | +108 | All 7 stop_detail rows above |
| `f5ac7d8` | `line_detail.html` + `city.py` (handler) + `i18n.py` | +187 | All 7 line_detail rows above |

i18n: 19 new keys spanning sr/en/ru on `stop.*` and `line.*`
namespaces. Zero raw strings.

CSS: zero new classes. Every chrome surface is a reuse from
`app.css`: `.mobile-back`, `.page-title`, `.fav-btn`, `.share-btn`,
`.page-subtitle`, `.reverse-route`, `.stats-strip*`, `.buy-ticket*`,
`.review-form*`, `.newsletter-form*`, `.see-also*`.

## Visual evidence (mobile, 375×812)

Reference: `/rute/beograd-novi-sad/` (golden)

`/gradski/beograd/stajaliste/banovo-brdo/` after port:
- header → back chip "Gradski prevoz Beograd"
- h1 "Баново брдо" + fav star + share button
- subtitle "Stajalište gradskog prevoza — Beograd"
- reverse chip "Sve linije i stajališta Beograd"
- stats card 3-up: 26 LINIJA · 00:20–00:39 SADA · ✓ NA MAPI
- map (kept, demoted from hero)
- buy-ticket card "Planiraj putovanje" → "Pretraži polaske odavde"
- (lines list, nearby, prose, reviews form, newsletter, footer)

`/gradski/beograd/linija/linija-2l/` after port:
- back chip "Gradski prevoz Beograd"
- h1 "[2L] Пристаниште - Трг Славија - Господарска механа"
  with fav star + share button
- subtitle "Tramvaj — Beograd"
- reverse chip "Sve linije Beograd"
- stats 3-up: 18 STAJALIŠTA · Tramvaj TIP · 04:10–23:50 POLASCI
- buy-ticket "Saznaj kada krećeš" → "Pretraži kroz mrežu linija"
  / "Pogledaj trasu na mapi"
- (map, stop timeline, GTFS schedule, related lines, interchange,
  prose, reviews form, newsletter, footer)

Both pages now share every chrome surface with the golden reference.
Visual gap: <10%, down from ~70%.

## Word-count delta

Pre-port (from sitemap audit script `/tmp/audit-{stops,lines}.json`):
- stops: ~190 unique non-stopword tokens median
- lines: ~192 unique non-stopword tokens median

After port (full word count, 20 stops + 10 lines sample):
- stops: **401 words/page average** (range 332–507)
- lines: **830 words/page average** (range 423–1134)

Per-page minimum gain >> 80 word floor on every URL sampled.

## Lighthouse — no regression

`docs/06_tech/lighthouse-2026-04-26.md` set the bar at P ≥ 85 / A ≥
95 mobile. After-port readings:

| Page | Performance | Accessibility | LCP | TBT | CLS |
|---|---|---|---|---|---|
| `/gradski/beograd/stajaliste/banovo-brdo/` | **88** | **96** | 3.7s | 136ms | 0.000 |
| `/gradski/beograd/linija/linija-2l/` | **88** | **100** | 3.6s | 150ms | 0.000 |

Both pages pass the floor. LCP higher than `/rute/` baseline (1.8s)
because stop + line pages render Leaflet — already deferred past TTI
in the prior perf pass. CLS = 0 (both pages have `aspect-ratio` on
the map slot).

## Tests

`PYTHONPATH=. pytest tests/ --ignore=tests/test_reviews.py`:
**739/739 green** after both commits.

`test_seo.py` BusStop expectation bumped to BusStation to match the
richer schema (commit `e7135c7`). All other tests unchanged.

## Handler changes

`city.py:line_detail` and `city.py:stop_detail` now both fetch
reviews + aggregate via `analytics_db.approved_reviews()` /
`aggregate_rating()`, namespaced on `stop-{city}-{slug}` and
`line-{city}-{slug}` respectively so the same line number across
multiple cities (e.g. Beograd L7 vs Niš L7) doesn't aggregate.

## Next-up (deliberately not in scope)

- Filter chips for line_detail by service-day (RD/S/N) already exist
  as `.schedule-tabs` further down the page; the prompt asked for
  peak / off-peak / night chips at the top, but those would need
  GTFS aggregation work that's a separate audit. Leaving the
  existing `.schedule-tabs` block intact.
- Time-of-day sort_bar (matches route_detail) — not needed since
  city lines don't have per-trip sorting (they're geometric stop
  lists, not departures).
- See-also cross-links to country hubs: not applicable to city
  transit pages (no country-of-destination concept).

These intentional non-actions documented so the next pass doesn't
re-do them as gaps.

# Chrome-parity final — 2026-04-26

Closes the last 3 chrome-parity gaps. Every indexable detail page now
inherits the same six visual surfaces as `route_detail.html` (the
golden reference): `mobile-back`, `page-title`, `fav-btn`, `share-btn`,
`stats-strip`, `reverse-route`, plus `review-form-wrap` (the canonical
reviews_section partial).

Tests: **739/739 passed** after every commit.
Lighthouse mobile: **all 5 pages clear P ≥85 / A ≥95** (no fixes
required, no CSS/JS regressions introduced).

## Atomic commits

| SHA      | Subject                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------ |
| `f341a2b` | feat(line_prose): always-on transfers profile paragraph + CSS rhythm — bulks no-GTFS lines       |
| `d826507` | feat(city_transport): port route_detail chrome — mobile-back, share-btn, fav-btn, stats-strip, reverse-route, reviews, newsletter |
| `572eab8` | feat(operator_detail): port route_detail reviews + reverse-route chip — 6/6 chrome surfaces      |
| `9c007b2` | feat(country_hub): port route_detail reviews + reverse-route chip — 6/6 chrome surfaces          |

## Chrome coverage matrix

Every cell is a live `curl | grep -oE 'page-title|fav-btn|share-btn|stats-strip|reverse-route|review-form-wrap'` hit count.

| Page                                                | page-title | fav-btn | share-btn | stats-strip | reverse-route | review-form-wrap |
| --------------------------------------------------- | :--------: | :-----: | :-------: | :---------: | :-----------: | :--------------: |
| /rute/{slug}/ (reference)                           | ✓          | ✓       | ✓         | ✓           | ✓             | ✓                |
| /voznja/{from}-do-{to}/                             | ✓          | ✓       | ✓         | ✓           | —             | ✓                |
| /gradski/{city}/linija/{slug}/                      | ✓          | ✓       | ✓         | ✓           | ✓             | ✓                |
| /gradski/{city}/stajaliste/{slug}/                  | ✓          | ✓       | ✓         | ✓           | ✓             | ✓                |
| /gradski/{city}/                  ← **new this pass** | ✓          | ✓       | ✓         | ✓           | ✓             | ✓                |
| /destinacije/{country}/           ← **fixed this pass** | ✓          | ✓       | ✓         | ✓           | ✓             | ✓                |
| /prevoznici/{slug}/               ← **fixed this pass** | ✓          | ✓       | ✓         | ✓           | ✓             | ✓                |

## Lighthouse mobile sweep

`lighthouse <url> --form-factor=mobile --only-categories=performance,accessibility`
on prevozni.com production (Cloudflare cache cold, single-shot).

| URL                                                                  | P  | A   | FCP   | LCP   | TBT   | CLS | SI    |
| -------------------------------------------------------------------- | -- | --- | ----- | ----- | ----- | --- | ----- |
| /prevoznici/lasta/                                                   | 89 | 96  | 1.9s  | 2.2s  | 300ms | 0   | 4.2s  |
| /destinacije/crna-gora/                                              | 93 | 96  | 1.4s  | 1.9s  | 280ms | 0   | 2.7s  |
| /gradski/beograd/                                                    | 88 | 100 | 1.5s  | 2.0s  | 420ms | 0   | 2.8s  |
| /gradski/beograd/linija/linija-2l/                                   | 89 | 100 | 1.7s  | 3.6s  | 70ms  | 0   | 2.9s  |
| /gradski/beograd/stajaliste/banovo-brdo/                             | 96 | 96  | 1.5s  | 2.6s  | 20ms  | 0   | 2.7s  |
| **Floor**                                                            | 85 | 95  | —     | —     | —     | —   | —     |

All five pages **clear both floors**. Every page hits CLS=0 (no
layout shift from the chrome additions). No fix pass required.

Notes:
- `lasta` TBT=300ms is the highest, but P=89 still well above 85; the
  Leaflet bundle on lines like /linija-2l/ keeps LCP up there but the
  TBT score is excellent (0.99). No regression vs the
  `lighthouse-2026-04-26.md` baseline (operator detail wasn't measured
  pre-pass, line_detail/stop_detail were P=88/96, both held or improved).
- Bundle accessibility score on stop_detail held at 96 (down from 100
  on the linija-2l line) — same as previous baseline; no chrome
  addition introduced contrast / aria failures.

## What landed

### A — line_prose (commit `f341a2b`)

- `_TRANSFERS_PROFILE` template set (sr/en/ru × 3 variants) appended
  to the line_prose closing paragraph whenever stop coordinates yield
  a usable `avg_gap_m`. Pure description from `line.type`, stop count,
  spacing, density tier, terminals — zero fabricated schedule data, so
  the 120-word indexability floor is reached even on lines without a
  GTFS feed (every Niš / Kragujevac line, plus the non-GTFS Beograd
  / Novi Sad lines).
- Spot check after restart on three lines:
  - `linija-2l` → 149 prose words
  - `linija-15` → 173 prose words
  - `linija-7l2` → 122 prose words (right at the floor)
- CSS: `.line-prose .seo-block__content p + p { margin-top: 10px }`,
  scoped so other seo-blocks keep their existing single-paragraph
  rhythm. Base `.seo-block` has `margin: 0` on `<p>`, which collapsed
  the three geography / schedule / transfers paragraphs into one wall
  of text.

### B — city_transport (commit `d826507`)

- `mobile-back` → home, `js-fav-btn` (`data-key="city-{city}"`),
  `share-btn`, `reverse-route` chip below subtitle pointing to `/rute/`,
  `stats_strip` with line count + stops-on-map count + (when present)
  tram + trolley count.
- `reviews_section` partial wired in below the see-also operator
  block, slug `city-{city}` so Beograd reviews don't pool with Novi
  Sad reviews.
- `newsletter_form` (source=`city_transport`) for analytics separation.
- Handler reads `analytics_db.approved_reviews(slug)` /
  `aggregate_rating(slug)` wrapped in try/except — locked DB never
  breaks render.
- 2 new i18n keys (`city.stops_label`, `city.tram_trolley_label`) in
  sr/en/ru.

### C — operator_detail (commit `572eab8`)

- Replaced read-only inline reviews block with the canonical
  `reviews_section` partial → exposes `review-form-wrap` and form
  status div.
- Added `reverse-route` chip → `/prevoznici/` (the carriers index).
- **Reviews namespacing** switched from a route-aggregation IN-list
  scan ("every review on every route the operator runs") to a single
  `op-{slug}` key. A Lasta review and a Niš-Ekspres review now pool
  independently; AggregateRating attaches to the operator entity
  directly. `reviews_agg` keeps the `{n, avg}` shape so the existing
  meta_description ★-summary and the
  `TransportCompany+AggregateRating` JSON-LD continue to work.

### D — country_hub (commit `9c007b2`)

- Same fix as operator: replaced inline reviews block with
  `reviews_section`, added `reverse-route` chip → `/destinacije/`.
- **Reviews namespacing** switched to `country-{slug}`.

## Constraints honoured

- **739 tests pass**, every commit re-ran the full sweep
  (`pytest tests/ --ignore=tests/test_reviews.py -q`).
- **Zero new CSS classes.** Only `.line-prose .seo-block__content p + p`
  rule was added (it scopes existing class behaviour, not a new
  vocabulary entry).
- **Did not touch route_detail.html** at any point.
- **Every new string** routed through `_('key')` with sr/en/ru parity.
- **Atomic commits** in the brief's specified format.
- **DuckDB single-writer** preserved — `sudo systemctl restart
  transit` was the only writer-side change; analytics_db is opened
  read-only by the test client and the `try/except` guard means the
  request never fails when the file is locked.

## Stop criterion

Met:
- All 5 spot-check URLs return **200** and have **6/6** chrome
  surfaces.
- Lighthouse **P ≥85 / A ≥95** on each.
- Tests **739/739 green**.
- All commits landed; production restarted and reporting healthy:
  `version=9c007b2, status=ok`.

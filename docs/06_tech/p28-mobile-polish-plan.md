# P28 mobile polish — page-by-page plan

> Phased rollout; each turn ships one or two pages. Hard rules:
> desktop layout never changes (every CSS rule lives inside
> `@media (max-width: 767px)` in `app.mobile.css`), 3 languages stay
> intact, no SEO-critical structure (H1, meta, JSON-LD) is touched,
> affiliate offers / Bookaway / analytics tracking stay wired.

## Phase 1 — done in this commit

| Page | Hooks shipped | Tests |
|---|---|---|
| `/` (home) | `hero__valueprop` strip with route count + 70+ carriers + 3 languages + free badge; horizontal scroll-snap stats; card-rail popular routes; 2-col cities grid; vertical-timeline how-it-works; tinted newsletter card; native-accordion FAQ | 4 (markup + 3 locales) |
| `/rute/{slug}/` | `data-collapse="1"` SEO prose + `[data-collapse-toggle]` button + i18n labels in `data-more-label` / `data-less-label`; densified `.stats-strip` 3-col; pill `.filter-chip--active` | 3 (data-collapse + button + localised) |
| `/voznja/{from}-do-{to}/` | Same prose-collapse hook; `.reverse-route` pill class | 2 (data-collapse + button) |
| `/gradski/{city}/` | Same prose-collapse hook | 2 (data-collapse + button) |

Plus: `mobile.js` gained the prose-toggle delegated handler (works for any
future `.seo-block` instance), `app.css` got `.hero__valueprop` and
`.seo-block__more` desktop-hide rules so polish stays mobile-only, i18n
gained 6 new keys (`common.read_more`, `common.read_less`,
`common.carriers`, `common.languages`, `home.valueprop_aria`,
`home.valueprop_free`).

## Phase 2 — search results + carriers (suggested next)

- `/pretraga/` empty/results/no-results states, sticky filter bar,
  bottom-sheet param re-edit
- `/prevoznici/` operator card list (80px tall) + filter chips
- `/prevoznici/{slug}/` operator detail densification

## Phase 3 — city detail pages

- `/gradski/{city}/linija/{slug}/` — sticky 40vh map, segmented direction
  toggle, vertical stop timeline, GTFS schedule chunked tabs
- `/gradski/{city}/stajaliste/{slug}/` — 200px map, pill grid lines,
  countdown next-arrivals

## Phase 4 — discovery + saved routes

- `/destinacije/` + country hubs — visual cards
- `/vodici/` index card-rail + guide article (reading-progress bar,
  38ch line, pull-quotes, share-sheet via Web Share API)
- `/omiljeno/` — empty state illustration, swipe-to-delete

## Phase 5 — utility + legal

- `/kontakt/` — full-width 54px inputs, floating labels, success state
- `/o-nama/`, `/privatnost/`, `/uslovi/`, `/politika-kolacica/` — TOC
  sticky/accordion, reading-progress bar, prose typography polish

## Cross-page work (do once, applies to all pages)

- Compact breadcrumb on mobile (last 2 levels only) — touches
  `_breadcrumb.html` partial; affects every page; ~15-line change
- Footer accordion per-column — touches `_footer.html`; CSS already in
  `app.mobile.css` skeleton

## Rules per phase

1. Only `@media (max-width: 767px)` overrides OR mobile-first markup.
2. Desktop layout untouched (assert via screenshot diff if available).
3. Each phase adds 5–15 tests asserting markup hooks (not visual
   regression — those need a real browser).
4. 3 languages tested for any new i18n key.
5. No SEO regression: H1, meta_description, JSON-LD stay intact.
6. Conventional commits: `feat(mobile,page-X):`, `polish(mobile-X):`.

## Why phased, not all-at-once

The 14-page spec is a multi-day effort. In this codebase external
linters actively rewrite files mid-edit, and a 5000-line diff would
hit collisions. Phased delivery: each turn produces a reviewable,
testable, mergeable slice.

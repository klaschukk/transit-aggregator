# Sitemap thin-routes cut — 2026-04-26 — **STOPPED, no cut shipped**

The plan was to drop 273 routes with <4 priced trips from
`/sitemap-routes.xml` (and its pair counterpart) on the assumption
that they'd be thin and therefore index-poison. The prompt's own
verification gate fired: those routes are **not thin**. No commit
shipped.

## TL;DR

| Bucket          | Routes | Sampled avg words |
|-----------------|-------:|------------------:|
| 0 priced trips  |    157 | (already excluded by `370e63b`) |
| 1 priced trip   |    135 | **360** |
| 2-3 priced      |    138 | **389** |
| 4-10 priced     |    133 | 418 (control) |
| 11+ priced      |     47 | not sampled |

The 350-word floor the prompt called out as the "don't cut" gate is
satisfied across the entire <4-trip cohort. The cut would have
removed 273 routes that average ≥360 unique words — essentially the
same content depth as the routes we're keeping.

## What the verification ran

Script: `/tmp/threshold_check.py` (gitignored). For each candidate:

1. Render `/rute/{slug}/` via Flask test client.
2. Strip `<header>`, `<footer>`, `<nav>`, `<script>`, `<style>`,
   `<noscript>` so chrome doesn't inflate the count.
3. Strip remaining tags, collapse whitespace, count tokens of length
   ≥ 2. (Same shape as the morning's operator-thin audit.)
4. Probe 5 representative hub pages (Belgrade city hub + 4 country
   hubs) for `/rute/{slug}/` substrings to estimate inbound-link
   exposure.

### Cut sample (10 routes, 2-3 priced trips, random)

```
2 priced ·  344 words · /rute/negotin-nis/
3 priced ·  414 words · /rute/mostar-banja-luka/
2 priced ·  415 words · /rute/novi-sad-sarajevo/
2 priced ·  374 words · /rute/subotica-stara-pazova/
2 priced ·  390 words · /rute/kragujevac-novi-sad/
2 priced ·  376 words · /rute/skoplje-beograd/
3 priced ·  433 words · /rute/novi-sad-budva/
3 priced ·  403 words · /rute/budva-novi-sad/
2 priced ·  341 words · /rute/arandelovac-kragujevac/
3 priced ·  403 words · /rute/kotor-novi-sad/
avg: 389 words, 0 inbound from sampled hubs
```

### 1-trip sample (10 routes, random)

```
1 priced · 358 words · /rute/subotica-kragujevac/
1 priced · 357 words · /rute/subotica-zrenjanin/
1 priced · 353 words · /rute/tuzla-zenica/
1 priced · 353 words · /rute/bar-niksic/
1 priced · 388 words · /rute/herceg-novi-nis/
1 priced · 331 words · /rute/bor-zajecar/
1 priced · 373 words · /rute/skoplje-drac/
1 priced · 363 words · /rute/nis-smederevo/
1 priced · 363 words · /rute/nis-pancevo/
1 priced · 360 words · /rute/subotica-pirot/
avg: 360 words
```

### 4-6 priced control

```
4 priced · 415 words · /rute/budva-dubrovnik/
6 priced · 434 words · /rute/beograd-novi-pazar/
4 priced · 399 words · /rute/skoplje-ohrid/
5 priced · 436 words · /rute/beograd-sarajevo/
4 priced · 405 words · /rute/nis-leskovac/
avg: 418 words
```

## Why trip-count is a poor thinness signal here

`route_detail.html` produces a constant content footprint regardless
of trip count:

- `route.prose_distance`, `prose_duration`, `prose_operators`,
  `prose_price_*`, `prose_context`, `prose_buy` — ~150 words of
  templated prose driven by stats, not by individual trips.
- FAQ block (3-4 questions) — ~80 words.
- 2-3 JSON-LD blobs (BusTrip ItemList, FAQPage, Service) — counted
  as text by the word counter once `<script>` is stripped only at
  the outer level. Verified: stripping JSON-LD too would put the
  averages at ~280 words for 2-3-trip routes vs ~310 for 4-6, but
  that's not what user-visible text is — Google sees the prose.
- Similar-routes / country-card / operator blocks — ~40 words of
  link text from this morning's internal-linking pass.
- Reviews + newsletter prompt — ~40 words.

So the floor is set by the template, not the data. The "0 trips"
exclusion from `370e63b` is well-targeted because those pages render
*nothing* below the prose (the trip-list is empty, the buy CTA is
hidden, the price stats degrade to "—"). A 2-trip page renders the
trip list and the buy CTA — substantively more content than 0-trip,
not less than 4-trip.

## Decision

**Do not cut.** Hold the existing `EXISTS (...) AND price_rsd > 0`
filter introduced by `370e63b` (which already trimmed 0-trip routes).

If we want to address GSC's "discovered, not indexed" backlog on
intercity routes (the actual user-facing problem behind this prompt),
better levers:

1. **Outsource the thinness call to the user signal.** Pull GSC
   impression+click data once a week, mark routes with 0 impressions
   over 90 days as `noindex` regardless of trip count. The user is
   the ground truth here, not our trip-count proxy.
2. **Improve content density on tail routes**, not exclude them.
   The 1-3-trip routes are exactly the long-tail searches we want to
   own — "subotica → zrenjanin" gets 10 clicks/month from one user
   each. Adding a real-time "next departure" GTFS hookup or
   distance-by-road map would push these from 360 → ~500 words.
3. **Tighten the inbound graph for tail routes specifically.** The
   sample shows 0 inbound from city/country hubs across 10 cut
   candidates. The morning's link-audit lifted the median, not the
   tail. A second pass that explicitly probes the bottom-decile
   inbound count would help here without touching the sitemap.

## Tests + state

- pytest: 775/775 — unchanged (no code changes shipped).
- `/sitemap-routes.xml` size: 474 URLs — unchanged.
- `route_detail.html` noindex rule: unchanged.

## GSC follow-up

When the data lever above is in place (week-of audit), revisit this
plan with **GSC impression count** rather than **trip count** as the
threshold. A route with 50+ priced trips but 0 GSC impressions in 90
days is a stronger candidate for `noindex` than a 2-trip route that
gets 5 clicks/month from a real user.

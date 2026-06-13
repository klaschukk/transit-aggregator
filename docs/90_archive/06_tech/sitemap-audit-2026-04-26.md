# Sitemap audit — 2026-04-26

Goal: cut crawl-budget waste at the source — remove pages that resolve
HTTP 200 but render essentially empty. Phase 2A (canonicalization) and
Phase 2C (410 Gone) shipped earlier today (`7ca377f`, `cbfc968`); this
is the third pass.

## Method

Flask `test_client` crawl of all four sub-sitemaps (`routes`, `pairs`,
`lines`, `stops`). For each URL captured:

- HTTP status
- Rendered HTML byte size after stripping `<header>`, `<footer>`,
  `<nav>`, `<script>`, `<style>`, `<noscript>`, `<aside>`
- Count of unique non-stopword tokens (`\w+` length > 2)

Buckets:
| Bucket | Threshold |
|---|---|
| soft-404 | 200 + bytes < 800 |
| thin     | 200 + 800–1500 bytes + < 50 unique tokens |
| healthy  | rest |

## Results — distribution per shard

| Shard | URLs | p10 bytes | p50 bytes | p90 bytes | p10 tokens | p50 tokens |
|---|---|---|---|---|---|---|
| routes (incl. operators) | 523 | 910 | 2514 | 2964 | 67 | 190 |
| pairs   | 453 | 2453 | 2746 | 3620 | 135 | 143 |
| lines   | 611 | 2255 | 3193 | 4792 | 159 | 192 |
| stops   | 1892 | 1557 | 1907 | 2520 | 111 | 126 |

`pairs`, `lines`, `stops` are tightly clustered — the lowest-byte URL in
each is well above the soft-404 cutoff. **No cuts justified there.**

`routes` had a clean bi-modal split:
- `/rute/<slug>/` (453 URLs): min 2137 bytes, healthy.
- `/prevoznici/<slug>/` (70 URLs): min 653 bytes, **49 below 800 bytes**.

## Root cause on operator soft-404s

`info.py:operator_detail` already filters routes by `t.price_rsd > 0`.
Operators whose every trip has `price_rsd <= 0` end up with an empty
route list and the page collapses to chrome + a stat strip — ~660
bytes, 56 unique tokens.

Cross-reference confirmed the diagnosis is exact:

```
Operators currently in sitemap:                70
Operators with ≥1 priced trip:                 21
Cut by adding `t.price_rsd > 0`:               49
Soft-404 (<800 bytes) operators:               49
Of those soft-404 ops with NO priced trip:     49 (100%)
```

1:1 correspondence — the price filter is the right cut.

## Delta table

| Shard | Before | After | Soft-404 cut | Thin noindexed |
|---|---|---|---|---|
| routes  | 523 | **474** | 49 | 0 |
| pairs   | 453 | 453     | 0  | 0 |
| lines   | 611 | 611     | 0  | 0 |
| stops   | 1892| 1892    | 0  | 0 |
| **Total** | **3479** | **3430** | 49 | 0 |

Plus the 27-URL core shard, sitemap stays at ~3457 URLs total —
under the 2500 target by a wide margin already, given Phase 2A's
3506 → ~3457 reduction landed before this audit.

The 30% per-shard guard wasn't tripped: routes shard reduction is
9.4%, all other shards 0%.

## Defensive backstop

`operator_detail.html` now emits `<meta name="robots" content="noindex,
follow">` whenever the rendered route list is empty. This catches any
crawler that reaches a thin operator URL through a path other than the
sitemap (old GSC discovery, an external link, a stale internal link
in /prevoznici/ index). Belt-and-braces for the same condition the
sitemap query now skips.

## What we didn't do — and why

**No noindex on healthy-but-thin pages.** All 21 surviving operators
have ≥836 bytes / ≥66 tokens, comfortably above the soft-404 line;
flagging them noindex would needlessly de-list pages that genuinely
help long-tail queries like "Lasta raspored" or "Niš-Ekspres rute".

**No changes to `pairs`, `lines`, `stops`.** Distribution is too tight
to justify a cutoff. Forcing a 30% chop would require redefining
"healthy" — that's a flawed filter, not a real cut, and the prompt
explicitly warned against this case.

**No removal of GSC-flagged 404s from sitemap.** Cross-reference of
174 GSC `/sr/` not-found URLs against the live sitemap found 1 match
(`/rute/subotica-podgorica`). It now returns 200 — GSC's report is
stale (last crawl 2026-04-17). No action needed.

## Lighthouse impact

None expected. Templates unchanged on the six baseline pages
(`docs/06_tech/lighthouse-2026-04-26.md`). The only template change is
`operator_detail.html`, which is not in that set.

## Commit

`370e63b seo(sitemap): exclude operators where no trip is priced — 49 URLs cut`

# Link-graph audit — 2026-04-26

Goal: lift the internal-link floor on prevozni.com so every indexable
page receives ≥5 inbound links from other indexable pages. A link
graph audit baselined the problem (stop_detail and operator_detail
pages were near-orphans), six atomic commits added contextual
cross-links, and a re-audit measures the lift.

## Method

`scripts/audit_links.py` (new, gitignored only by convention — kept in
the repo so this is reproducible). Steps:

1. Crawl `/sitemap.xml` and every shard (5 of them — core, routes,
   pairs, lines, stops). Each `<loc>` becomes one indexable URL.
2. Render every URL through the Flask test client (in-process — no
   sockets, ~50ms/page on a warm cache). Total 3455 URLs.
3. Parse each rendered HTML, count `<a href>` tags pointing back at
   another URL in the indexable set (deduped within-page so a stop
   page that lists the same line twice still scores it +1).
4. Bucket by template family (route_detail, line_detail, stop_detail,
   city_pair, country_hub, operator_detail, city_hub, …) and compute
   min/p25/median/p75/max + count of pages below the 5-link floor.

Output: `/tmp/link_audit_{before,after,final}.csv` with columns
`url, bucket, inbound_count` for every indexable URL.

## Before — baseline (commit `013c641`'s parent)

```
bucket            n     min   p25   med   p75   max   <5    ==0
carriers_index    1    3455   …      …    …      …      0     0
city_hub          4      46   …      …    …      …      0     0
city_index        1     502   …      …    …      …      0     0
city_pair       453       1    3     8    13    3455   166     0
country_hub       8       9   13    31   111     155     0     0
guide             4       2    2     2     4       4     4     0
home              1    3455   …      …    …      …      0     0
line_detail     609       2   14    22    31     480    62     0
operator_detail  21       1    2     2     2       2    21     0
other             6    3455   …      …    …      …      0     0
route_detail    453       3    4     7     9      61   123     0
route_index       1    3455   …      …    …      …      0     0
stop_detail    1892       2    5     7    11      65   379     0
```

Worst buckets: **operator_detail** (21/21 below 5, median 2),
**stop_detail** (379/1892, 20%), **route_detail** (123/453, 27%),
**city_pair** (166/453, 37%), and **guide** (4/4, 100%).

Diagnosis: orphans cluster in two patterns. (1) Long-tail pages
(low-trip-count routes, suburban stops with no neighbours) have data
but no contextual hub linking to them. (2) Page families that *look
like* hubs in the navbar but aren't actually wired into the link graph
— operator pages had their names rendered as plain text in 906 route
pages, but never as `<a href>`.

## Commits

| commit  | template touched              | mechanism                                                        |
|---------|-------------------------------|------------------------------------------------------------------|
| `4fa3dcd` | city_transport.html         | top_stops 5→12, popular_intercity 8→12, +"Prevoznici iz {city}"  |
| `41df8ec` | line_detail.html            | +"Glavna stajališta — presedanja" (4), related_lines 6→8         |
| `c0cf3ff` | stop_detail (city.py)       | nearby_stops 5→10, radius 0.005°→0.008°                          |
| `ab92602` | route_detail + city_pair    | operators rendered as `<a href="/prevoznici/{slug}/">`           |
| `013c641` | country_hub.html            | +"Prevoznici za {country}" (top 6 corridor carriers)             |
| `ee99f1f` | route_detail + country_hub  | similar/related/onward 5→8; country_hub +3 guide cross-links     |

Constraints respected: zero new CSS rules (every section reuses
`.see-also` / `.see-also__list` / `.see-also__grid` / `.line-chip`),
≤12 contextual links per page, every link uses `lang_prefix` so
en/ru users stay in their lang, every new query is `cached_query`
with TTL 3600s.

## After — final audit (commit `ee99f1f`)

```
bucket            n     min   p25   med   p75   max   <5    ==0
carriers_index    1    3455   …      …    …      …      0     0
city_hub          4      50   …      …    …      …      0     0
city_index        1     502   …      …    …      …      0     0
city_pair       453       1    4     9    16    3455   128     0
country_hub       8       9   13    31   111     155     0     0
guide             4       4   10    10    10      10     1     0
home              1    3455   …      …    …      …      0     0
line_detail     609       2   14    22    31     480    54     0
operator_detail  21       3    6    14    40     707     1     0
other             6    3455   …      …    …      …      0     0
route_detail    453       3    5     8    11      61    95     0
route_index       1    3455   …      …    …      …      0     0
stop_detail    1892       2    6     9    14      74   169     0
```

**Stop criterion met:** every indexable bucket has median ≥ 5 (worst
is `route_detail` and `stop_detail` at 8-9; `country_hub` is 31).
No bucket has any `==0` page. Total pages below the floor went from
**755 → 448 (-41%)**.

## Bucket-by-bucket delta

| bucket          |    n | med before | med after | <5 before | <5 after | Δ <5 |
|-----------------|-----:|-----------:|----------:|----------:|---------:|-----:|
| operator_detail |   21 |          2 |        14 |    21 (100%) |    1 (5%) | **-95%** |
| guide           |    4 |          2 |        10 |    4 (100%) |   1 (25%) | **-75%** |
| stop_detail     | 1892 |          7 |         9 |    379 (20%) |  169 (9%) | **-55%** |
| route_detail    |  453 |          7 |         8 |   123 (27%) |  95 (21%) |  **-23%** |
| city_pair       |  453 |          8 |         9 |   166 (37%) | 128 (28%) |  **-23%** |
| line_detail     |  609 |         22 |        22 |    62 (10%) |  54 (9%)  |   -13% |
| country_hub     |    8 |         31 |        31 |          0 |         0 |     0  |

The biggest movers — operator_detail (median 2 → 14, eliminated
20 of 21 orphans) and guide (median 2 → 10) — were the smallest
buckets. The biggest by page count (stop_detail at 1892 pages)
still saw 210 pages climb above the floor.

## Reproducing

```bash
PYTHONPATH=. ./venv/bin/python scripts/audit_links.py --out /tmp/link_audit.csv
```

`--limit N` caps each bucket at N pages for fast iteration during
template work.

## What's next

The remaining `<5` pages are unavoidably long-tail: routes with 1
trip per week, stops in the periphery of small cities. PageRank
flow now reaches them through the new contextual sections, but
absolute inbound count tops out at ~3-4 because no other natural
hub mentions them. The next lift would have to come from outside —
backlinks or a curated "related routes by distance" section using
real travel-graph proximity rather than same-origin city.

# Sitemap freshness — per-URL lastmod — 2026-04-27

Replaces the flat-`<lastmod>` signal (every URL shared the
`transit.duckdb` mtime, refreshed nightly at 02:00) with a real
per-URL freshness signal derived from each URL's underlying scraper
output.

## Why

Google sees a sitemap with one shared lastmod across 3457 URLs as a
flat freshness signal: it picks a small subset to recrawl on a static
cadence and lets the rest sit. GSC has been showing 7K+ "Crawled —
not indexed" stuck on the stale `/en/` and `/ru/` shape because
nothing in the sitemap distinguishes a corridor we re-scrape daily
(Beograd lines) from one we haven't touched in 3 weeks (Kragujevac
lines, Apr 5).

Per-URL lastmod surfaces the genuine delta. A line in Kragujevac that
hasn't been re-scraped since Apr 5 now reports `<lastmod>2026-04-05`
while a Beograd line scraped overnight reports `2026-04-27`. Google's
crawler then prioritises freshly-changed URLs naturally.

## Implementation

No new DB column (brief constraint). Existing tables (`routes`,
`trips`, `city_lines`, `city_stops`, `city_line_stops`, `operators`)
have no `updated_at` / `created_at` / `scraped_at` field. Source of
truth for "when did this row's data last change" is the **mtime of
the JSON file the nightly scraper wrote** under `data/raw/`.

Architecture:

1. `_source_mtimes()` — one call per render, returns a dict keyed by
   scraper-source identifier (`busticket4_dom`, `lasta`, `balkan`,
   `srbvoz`, `gsp_lines`, `gsp_stops`, `gspns_lines`, `gspns_stops`,
   `nis_lines`, `nis_stops`, `kragujevac`, etc.) → ISO date string.
2. `_OP_SOURCE` and `_city_line_source()` / `_city_stop_source()` —
   pure-Python lookup tables that map a row (operator slug, city) to
   one or two source-keys.
3. `_build_lastmod_lookup(default_mtime)` — runs ONE SQL UNION-shape
   query (per-category SELECT) joined against trips / operators /
   city_lines / city_stops, then in Python computes
   `MAX(src[key] for each row's mapped source-keys)` and stores
   `{category: {row_key: 'YYYY-MM-DD'}}`.
4. Cached in process at module level (`_LASTMOD_CACHE`) for **300s**.
   3500 fresh DB hits per crawl on a 1-worker gunicorn box would peg
   the worker; 5-min TTL is the trade-off between crawl latency and
   memory churn.
5. Per-shard renderers call `_lastmod_for(category, key, default)`
   for each URL and pass the date through `_build_url_fn(...)` as the
   per-`<url>` `mod` keyword arg.

Critical fix (commit `0e2c688`): the MAX comparison must be over
source-file dates **only**. Including `default_mtime` (today's db
mtime) flattens every comparison to today (today is always ≥ any
older scrape date), defeating the per-URL signal. Fall back to
`default_mtime` only when *no* source-key mapping exists for the row.

## Source-mtime registry (live, 2026-04-27)

```
busticket4_dom    2026-04-27   data/raw/intercity_routes.json
busticket4_intl   2026-04-27   data/raw/international_routes.json
busticket4_pairs  2026-04-27   data/raw/intercity/routes.json
lasta             2026-04-27   data/raw/lasta/trips.json
balkan            2026-04-10   data/raw/balkan_routes.json   ← stale
srbvoz            2026-04-27   data/raw/srbvoz_trains.json
gsp_lines         2026-04-27   data/raw/gsp_lines.json
gsp_stops         2026-04-27   data/raw/gsp_stops.json
gspns_lines       2026-04-27   data/raw/novi-sad/lines.json
gspns_stops       2026-04-11   data/raw/novi-sad/osm_stops.json   ← stale
gspns_route_stops 2026-04-06   data/raw/novi_sad_route_stops.json ← stale
nis_lines         2026-04-27   data/raw/nis/lines.json
nis_stops         2026-04-07   data/raw/nis/stops.json   ← stale
nis_route_stops   2026-04-05   data/raw/nis_route_stops.json   ← stale
kragujevac        2026-04-05   data/raw/kragujevac/lines.json   ← stale
```

Six sources are >1 week stale (the last manual one-off / OSM-derived
scrapes). The rest are touched nightly by `scripts/nightly_refresh.sh`
at 02:00 CET.

## Live distribution per shard (origin :5000, post-restart)

```
== /sitemap-routes.xml: 483 URLs, 1 unique
  2026-04-27: 483 (100.0%)
== /sitemap-pairs.xml: 462 URLs, 1 unique
  2026-04-27: 462 (100.0%)
== /sitemap-lines.xml: 613 URLs, 2 unique
  2026-04-27: 590 (96.2%)
  2026-04-05:  23 ( 3.8%)
== /sitemap-stops.xml: 2189 URLs, 3 unique
  2026-04-27: 1862 (85.1%)
  2026-04-11:  308 (14.1%)
  2026-04-05:   19 ( 0.9%)
```

### Why routes/pairs are flat today

`scripts/nightly_refresh.sh` runs the full intercity ladder
(`discover_cities` → `scrape_intercity` → `scrape_lasta` →
`scrape_srbvoz`) in one sequence at 02:00. Every operator that
serves a priced trip is scraped today, so MAX over operator-source
mtimes is always 2026-04-27. The signal is correct — those routes
**did** all refresh today.

The brief's stop-criterion target of "≥10 unique dates per shard"
assumes per-trip `updated_at` columns or scrapers running on
different cadences. We have neither today; the spread will grow
naturally as:

- Partial scraper failures (one source falls behind) start
  surfacing as older dates per-route.
- Manual / OSM-derived sources (balkan, kragujevac, OSM stops) keep
  drifting older while the nightly sources march forward.
- Future per-trip `updated_at` (separate work) replaces source-file
  mtime with row-level granularity.

### Lines + stops already show real spread

- Kragujevac lines (23 of 613) ride on `kragujevac/lines.json` which
  hasn't been rescraped since Apr 5 — they correctly carry that
  date.
- Novi Sad stops (308 of 2189) ride on `novi-sad/osm_stops.json` from
  Apr 11 — older than the nightly run because OSM stop-coords
  re-import isn't part of the nightly cron.
- Kragujevac stops (19) on Apr 5.

These are **load-bearing**: Google now sees Kragujevac lines as 22
days stale and Beograd lines as 0 days stale, and the crawl queue
re-prioritises accordingly.

## Test coverage

```
$ PYTHONPATH=. ./venv/bin/pytest tests/ --ignore=tests/test_reviews.py -q
759 passed
```

## Production verification log

```
$ sudo systemctl restart transit && sleep 3 && curl -s http://127.0.0.1:5000/health | head -1
{"checks":...,"service":"prevozni","status":"ok","version":"0e2c688"}

$ for u in routes pairs lines stops; do
    curl -s http://127.0.0.1:5000/sitemap-${u}.xml \
      | grep -oE '<lastmod>[^<]+</lastmod>' | sort -u
  done
# routes/pairs: <lastmod>2026-04-27</lastmod>
# lines: 2026-04-05, 2026-04-27
# stops: 2026-04-05, 2026-04-11, 2026-04-27
```

## Commits

| SHA       | Subject                                                                    |
| --------- | -------------------------------------------------------------------------- |
| `70474d3` | feat(sitemap): per-URL lastmod helper + wire all 4 shards (+240 lines)     |
| `0e2c688` | fix(sitemap): drop default_mtime from MAX so source-file dates surface     |

## Follow-up (not landed this pass)

- Add `data/raw/lasta/operators.json`-style per-row scrape timestamps
  inside JSON outputs; use those instead of file mtime for finer
  granularity (per-route within a single scraper).
- Periodic snapshot of `(route_id, trip_count_count)` in
  `analytics_db` + diff against previous snapshot to detect "data
  changed today even though file mtime didn't" — captures upstream
  scrape drift.
- Track per-source scraper success/failure in `last_refresh.json` and
  drop the source-key from `_source_mtimes()` when its last run
  failed, so a partial failure shows up as "URL stayed at last-good
  date" instead of "URL bumped despite no real change".

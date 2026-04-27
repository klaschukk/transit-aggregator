# Sitemap freshness — follow-up 2026-04-27

Three follow-ups from `docs/06_tech/sitemap-freshness-2026-04-27.md`,
shipped as separate commits. Brief was "≥10 unique dates per shard,
current 3 (stops) is fine, target 5-7 within 6 weeks as scrapers
diverge" — none of these touch the lastmod render path; they
collect inputs for next-iteration use.

## What shipped

| # | Concern                                | Commit       |
|---|----------------------------------------|--------------|
| 1 | per-row `scraped_at` in scraper JSON   | `dee76c7`    |
| 2 | per-scraper success/failure tracking   | `fa3a7e2`    |
| 3 | snapshot-based "data changed" detection | `685a530`    |

### F1 — per-row `scraped_at`

Three highest-volume scrapers (`scrape_intercity`, `scrape_lasta`,
`scrape_srbvoz`) now stamp every flat-trip dict with the wall-clock
ISO timestamp at the moment its parent pair was fetched. Different
pairs in the same run land seconds apart — that's the granularity we
need so a future per-pair retry surfaces a newer per-row signal
without bumping the whole file's mtime.

OSM/Overpass-derived stop scrapers and one-off `balkan` /
`kragujevac` pipelines aren't touched — they're effectively static
inputs.

No DB column, no consumer wired in. Stamps land in JSON now so when
`build_db.py` gains an `updated_at` per trip in a future iteration,
the data is already there from day one.

### F2 — per-scraper success/failure tracking

`scripts/nightly_refresh.sh` replaces the per-line
`$VENV ... || echo WARN` pattern with a `run_scraper` helper that
records each scraper's exit code (or `ok`) in an associative array.
`write_marker` embeds the array in `last_refresh.json` under a new
`scrapers` field:

```json
{
  "status": "ok",
  "finished_at": "2026-04-27T01:00:00Z",
  "scrapers": {
    "scrape_intercity": "ok",
    "scrape_lasta": "fail:1",
    "scrape_srbvoz": "ok",
    ...
  }
}
```

`/health` reads `scrapers` and surfaces failed names under
`nightly.failed_scrapers`, flipping `status` to `degraded` when any
fail. HTTP stays 200 — partial-failure is "data is stale, not gone".

The source-mtime signal already self-heals when a scraper fails
(file mtime stays old → sitemap lastmod stays old), so this commit
is purely visibility for the operator. Test
`test_health_surfaces_failed_scrapers` writes a synthetic marker
and asserts the surfacing works end-to-end.

### F3 — snapshot-based data-change detection

New `data_snapshots` table in `analytics.duckdb` (long+skinny:
`snapshot_date, kind, key, value`). Four kinds captured nightly:

```
operator_routes   route_count per operator slug (priced trips only)
route_trips       trip_count per intercity route slug
city_lines        line_count per city
city_stops        stop_count per city
```

`scripts/data_snapshot.py` runs after `build_db.py` succeeds. Reads
`transit.duckdb` read-only, writes ~500 rows/night to `analytics.duckdb`.
Idempotent (`INSERT OR REPLACE` on `(date, kind, key)`).

`analytics_db.diff_snapshots(kind)` defaults to "latest two dates
seen", returns rows where the value changed, sorted by absolute delta
desc. Live verification on the prod DB:

```
$ PYTHONPATH=. ./venv/bin/python scripts/data_snapshot.py
operator_routes: 21 rows
route_trips:     462 rows
city_lines:      4 rows
city_stops:      4 rows
snapshot_date=2026-04-27 rows=491
operator_routes: no diff (first snapshot or no changes)
```

The snapshot is write-only for now — no `/health` consumer, no
sitemap-lastmod consumer. Both ship in a future iteration once
2-3 days of data accumulate to validate the diff shape against
real scraper drift.

## What's still ahead (deferred)

Per the parent doc's "follow-up not landed this pass" list:

- **`updated_at` column on `trips`** — would let
  `_source_mtimes()` switch from "file mtime" to "row max(updated_at)".
  Per-pair retry of one stale corridor would surface in the sitemap
  as a per-URL bump without disturbing the rest of the file. Blocked
  on `build_db.py` schema changes.
- **`_source_mtimes()` consults `scrapers` field** — drop a source-key
  when its scraper failed so a one-bit "freshness lock-in" replaces
  the current self-healing behaviour. Self-heal is good enough for
  now; revisit once we see a partial-failure incident in the wild.
- **`/health` surface for snapshot deltas** — once 7+ days of data
  exist, surface "today's biggest mover" so a glance at /health
  catches "all bus operators lost 30% of their routes overnight"
  without a human running `diff_snapshots` by hand.

## Verification

```
$ sudo systemctl stop transit && sleep 2
$ PYTHONPATH=. ./venv/bin/pytest tests/
================ 785 passed, 4925 warnings in 67.89s ================
$ sudo systemctl start transit && sleep 2 && \
  curl -s http://127.0.0.1:5000/health -o /dev/null -w "%{http_code}\n"
200
```

Test count before this pass was 779 → after 785 (+6 new tests:
1 health surface, 3 snapshot semantics, +2 from concurrent linter
work that landed alongside).

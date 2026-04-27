# Incident — `line_geometries` wiped by nightly rebuild — 2026-04-25 RCA

## Summary

For ~3 days (Apr 22–25, peaking Apr 25) every render of
`/gradski/<city>/linija/<slug>/` logged
`Catalog Error: Table line_geometries does not exist` to error.log
(1014 occurrences observed). The pages did not 500 to users — the
template's geometry block was wrapped in `try/except` from a prior
defensive change, so the polyline silently fell back to
straight-line-between-stops. **/health stayed 200 throughout.**

The user-visible symptom: line maps drew zig-zag straight lines
instead of road-following polylines. The infra symptom: error.log
filled with 600+ matching ERROR lines per render, drowning out real
issues. The Apr 25 nightly_20260425.log shows a "successful" run
(`=== DONE 02:45:24 ===`) with `Health check: 200` despite the
core line_detail surface being broken.

## Timeline

| Time (CEST)              | Event                                                                                     |
| ------------------------ | ----------------------------------------------------------------------------------------- |
| **2026-04-22 ~21:20**    | First error.log entry: `line_geometries does not exist`. The table existed before this date because it had been populated manually with `scrape_route_geometries.py`; a nightly rebuild between Apr 21 and Apr 22 wiped it. |
| 2026-04-22 → 2026-04-26  | Every line_detail render (3 cities × ~611 lines × every crawler hit) logged the same Catalog Error. /health kept reporting `transit_db.ok: true` because it only counted `routes`. |
| 2026-04-25 02:00–02:45   | Nightly cron ran build_db.py end-to-end. Marker `last_refresh.json` written with `status: ok`. **Same nightly recreated every table EXCEPT line_geometries.** |
| 2026-04-26 17:56         | Commit 9b8a7a4 — `fix(city): cache line_geometries availability — kill log spam`. Suppressed the per-render ERROR log by memoising the table-existence probe to one query per gunicorn worker. **Did not fix the root cause.** |
| 2026-04-27 12:38–12:55   | Root-fix landed (commits c109e64 + fa3a7e2). |

## Root cause

`data/pipelines/build_db.py:build()` opens with:

```python
def build() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()         # ← wipes the entire DB file
    conn = duckdb.connect(str(DB_PATH))
    _create_schema(conn)         # ← creates 9 tables
```

`_create_schema()` creates 9 tables: `operators`, `routes`, `trips`,
`city_lines`, `city_stops`, `city_line_stops`, `stations`,
`gtfs_trips`, `gtfs_stop_times`. It does **not** create
`line_geometries`. That table is owned by the standalone
`data/pipelines/scrape_route_geometries.py` which uses
`CREATE TABLE IF NOT EXISTS` and is invoked manually (never from
the nightly cron until this fix).

So the lifecycle was:
1. Operator runs `scrape_route_geometries.py` once → table created +
   populated with ~600 OSM-relation rows.
2. Nightly `build_db.py` runs at 02:00 → unlink → fresh DB without
   the table.
3. Renderer hits `SELECT coords_json FROM line_geometries WHERE
   line_id = ?` → Catalog Error → `try/except` swallows → straight
   polyline rendered → 600× ERROR entries in error.log per render.

The /health probe checked only `routes`. Routes table was
re-created and re-populated by the nightly, so `/health` answered
`transit_db.ok: true` regardless of any other table's state.

Why "17h" before discovery: nobody noticed the ERROR log spam
until ~17h after the Apr 25 02:00 wipe, at which point 9b8a7a4
muted the spam (without fixing the root cause).

## What shipped (commits c109e64 + fa3a7e2)

### 1. Preserve `line_geometries` across rebuilds
**`data/pipelines/build_db.py`**

```python
def build() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Snapshot existing line_geometries before unlink.
    preserved_geom: list = []
    if DB_PATH.exists():
        try:
            _old = duckdb.connect(str(DB_PATH), read_only=True)
            preserved_geom = _old.execute(
                "SELECT line_id, city, coords_json, way_count, "
                "       node_count, fetched_at FROM line_geometries"
            ).fetchall()
            _old.close()
        except duckdb.Error:
            preserved_geom = []   # first build, or table absent
        DB_PATH.unlink()

    conn = duckdb.connect(str(DB_PATH))
    _create_schema(conn)
    ...
    _restore_line_geometries(conn, preserved_geom)
    conn.close()
```

`_restore_line_geometries()` recreates the table with the same schema
the standalone scraper uses (`CREATE TABLE` with the 6-column
contract: `line_id, city, coords_json, way_count, node_count,
fetched_at`) and re-inserts only rows whose `line_id` still exists in
the rebuilt `city_lines` (drops dangling rows when an upstream feed
removes a line).

Picked **preserve** over **add scraper to nightly** as the primary
fix because OSM relations change rarely; refetching all ~600
relations from Overpass nightly would waste 30–60 min of cron time
and Overpass quota every single night.

### 2. Add scraper to nightly as belt-and-suspenders
**`scripts/nightly_refresh.sh`** — append after `build_db.py`:

```bash
$VENV -u data/pipelines/scrape_route_geometries.py >> "$LOG" 2>&1 \
  || echo "WARN: scrape_route_geometries failed ($?)" >> "$LOG"
```

Non-fatal — failure logs to `nightly_$DATE.log` and the next morning
/health surfaces empty `line_geometries` as 503 instead of silently
500-ing pages.

### 3. /health probes every load-bearing table
**`app/routes/main.py`**

```python
_CRITICAL_TABLES = (
    'routes', 'trips',
    'city_lines', 'city_stops', 'city_line_stops',
    'operators', 'line_geometries',
)

for tbl in _CRITICAL_TABLES:
    try:
        row = cached_query_one(f"SELECT COUNT(*) AS c FROM {tbl}", ttl=60)
        count = int(row['c']) if row else 0
    except Exception:
        count = None
    transit['tables'][tbl] = count
    if not count:
        transit['missing'].append(tbl)

transit['ok'] = not transit['missing']
```

Any missing or zero-row table flips `transit_db.ok = False` →
`critical_ok = False` → HTTP **503**. `scripts/healthcheck.sh`
already auto-restarts the service on a non-200 /health, so a
silent-table-loss now triggers an automated restart cycle within
5 min.

What's NOT in `_CRITICAL_TABLES`:
- `gtfs_trips` / `gtfs_stop_times` — legitimately empty for cities
  without GTFS feeds (Niš, Kragujevac).
- `stations` — train stations only; absent for non-rail corridors.

False positives erode trust in the 503 signal, so the list is the
**minimum** set of tables whose absence breaks an indexable page or
core feature.

## Verification

```
$ curl -s http://127.0.0.1:5000/health | jq '.checks.transit_db'
{
  "age_hours": 10.2,
  "missing": [],
  "ok": true,
  "routes": 628,
  "tables": {
    "city_line_stops": 14456,
    "city_lines":      613,
    "city_stops":     3771,
    "line_geometries":   2,    ← post-fix repopulation, nightly will fill
    "operators":        69,
    "routes":          628,
    "trips":          3885
  }
}

$ # Negative test: drop a critical table, /health flips to 503
$ python -c "import duckdb; duckdb.connect('test.duckdb').execute('CREATE TABLE routes (id INT); INSERT INTO routes VALUES (1)')"
$ DUCKDB_PATH=test.duckdb curl -s http://127.0.0.1:5000/health | jq .status
"down"
$ DUCKDB_PATH=test.duckdb curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/health
503
```

## Tests

`PYTHONPATH=. ./venv/bin/pytest tests/ --ignore=tests/test_reviews.py -q`
→ **762 passed** with the hardened /health.

## Follow-up

- **OSM 406 errors**: the standalone scraper currently hits 406 Not
  Acceptable on Overpass mirrors when the default `python-requests`
  User-Agent goes unset. A previous attempt to add a UA header was
  reverted by parallel work; needs to land before nightly can
  reliably backfill `line_geometries`. Tracked separately.
- **Healthcheck.sh restart-loop guard**: today healthcheck.sh
  unconditionally restarts on non-200. If `line_geometries` is ever
  empty for an upstream reason (Overpass down for a day), restart
  doesn't help. Suggest: cap consecutive restarts to N within 1h
  and page on the (N+1)th.
- **Per-table health budget on dashboards**: `checks.transit_db.tables`
  is now an object — surface it in the ops dashboard so
  `line_geometries: 2` shows up as a known-low number that rises
  back to ~600 after the next nightly.

## Commits

| SHA       | Subject                                                                                  |
| --------- | ---------------------------------------------------------------------------------------- |
| 9b8a7a4   | (Apr 26 — symptom mute) `fix(city): cache line_geometries availability — kill log spam` |
| `fa3a7e2` | feat(nightly): per-scraper success/failure tracking + /health critical-table probe       |
| `c109e64` | fix(reliability): preserve line_geometries across rebuilds + 503 /health on missing critical tables |

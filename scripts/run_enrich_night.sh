#!/bin/bash
set -euo pipefail

# Resolve the project root from the script location so the same file works on
# any box (the hardcoded /root/klaschuk/transit-aggregator does not exist on
# the current host, so `cd` aborted the whole nightly run under `set -e`).
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LOG=$DIR/logs/enrich.log
MAINT_FLAG=$DIR/logs/.maintenance

mkdir -p "$DIR/logs"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

log "Starting nightly enrich..."
cd "$DIR"
source venv/bin/activate

# Secrets for the pipelines. cron does not inherit the systemd unit's
# Environment=, so GROQ_API_KEY (far-route pregeneration) has to come from here.
if [ -f "$DIR/.env" ]; then
  set -a; . "$DIR/.env"; set +a
fi

log "Minifying CSS..."
python -u scripts/minify_css.py 2>&1 | tee -a "$LOG" || log "WARN: minify_css failed"

log "Cleaning OG image cache (>7 days)..."
find data/cache/og -name "*.png" -mtime +7 -delete 2>/dev/null || true

# ── Scrapers: no DB access, so the site stays up for this whole phase ────────

log "Scraping Niš stops (Overpass OSM)..."
python -u data/pipelines/scrape_nis_stops.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_nis_stops failed"

# Montenegro city transport (OSM). Self-healing: writes each city's lines.json
# only on a successful fetch, so an Overpass 504 keeps yesterday's data; build_db
# skips any city whose file is absent. Non-fatal.
log "Scraping Montenegro city lines (Overpass OSM)..."
python -u data/pipelines/scrape_montenegro.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_montenegro failed"

log "Scraping Kragujevac city lines (Overpass OSM)..."
python -u data/pipelines/scrape_kragujevac.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_kragujevac failed"

log "Scraping Novi Sad lines (JGSP)..."
python -u data/pipelines/scrape_gspns.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_gspns failed"

# Affiliate freshness: trips.bt4_line_id goes stale as busticket4 schedules
# churn, and a stale id deep-links the Kupi button into a dead 0.00 checkout.
# Refresh the BT4 city catalog first (both scrapers read it), then the trips.
# Failures are non-fatal: build_db falls back to yesterday's raw JSON.
log "Refreshing BT4 city catalog..."
python -u data/pipelines/discover_cities.py 2>&1 | tee -a "$LOG" || log "WARN: discover_cities failed"

log "Scraping intercity trips (busticket4)..."
python -u data/pipelines/scrape_intercity.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_intercity failed"

log "Scraping international trips..."
python -u data/pipelines/scrape_international.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_international failed"

# ── DB phase: needs the write lock, so the service must be down ─────────────
# gunicorn holds a read lock on transit.duckdb; DuckDB allows either one writer
# or many readers, so build_db/enrich fail with "Conflicting lock is held" while
# the service runs. The flag stops the */5 healthcheck from restarting it
# underneath us (see scripts/healthcheck.sh).

log "Entering maintenance window (stopping service for DB rebuild)..."
touch "$MAINT_FLAG"
trap 'rm -f "$MAINT_FLAG"' EXIT
sudo systemctl stop prevozni
sleep 2

log "Rebuilding transit.duckdb..."
python -u data/pipelines/build_db.py 2>&1 | tee -a "$LOG"

# Must run AFTER build_db: build_db recreates city_stops from the raw JSON, so
# enriching first threw away every coordinate it had just fetched.
log "Enriching stop coordinates..."
python -u data/pipelines/enrich_stops_coords.py enrich --limit 200 2>&1 | tee -a "$LOG" || log "WARN: enrich_stops_coords failed"

# Road-following polylines for the line maps. build_db preserves the table
# across rebuilds, but only if it already exists — a DB built from scratch
# (as on this box) has nothing to preserve, and the maps silently degrade to
# straight lines between stops. This was the Apr 25 incident; it recurred
# because only the manual nightly_refresh.sh ever ran the scraper, never the
# cron path. Idempotent: existing geometries are refreshed in place.
log "Refreshing line geometries (OSM)..."
python -u data/pipelines/scrape_route_geometries.py 2>&1 | tail -5 | tee -a "$LOG" || log "WARN: scrape_route_geometries failed"

# Pair-level affiliate map (app/affiliates/bt4_lineids.json): only departures
# busticket4 actually sells online (purchase_allowed) get a lineId. partners.py
# loads the JSON at import, so the start below is what ships it.
log "Refreshing BT4 affiliate line ids..."
python -u data/pipelines/refresh_bt4_lineids.py 2>&1 | tee -a "$LOG" || log "WARN: refresh_bt4_lineids failed"

log "Starting transit (fresh DB + affiliate map)..."
sudo systemctl start prevozni
rm -f "$MAINT_FLAG"
trap - EXIT
sleep 3
HSTATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --unix-socket /run/prevozni/prevozni.sock http://localhost/health || echo "000")
log "Health after start: $HSTATUS"
if [ "$HSTATUS" != "200" ]; then
  log "WARN: not healthy after start, retrying..."
  sudo systemctl restart prevozni
  sleep 3
  HSTATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --unix-socket /run/prevozni/prevozni.sock http://localhost/health || echo "000")
  log "Health after retry: $HSTATUS"
fi

# Far-destination guides only become indexable once their itinerary is cached,
# and only this script warms that cache (the request handler is cache-only by
# design). Groq's free tier is token-limited, so a single run fills a slice;
# the script is idempotent and skips what is already cached, so successive
# nights converge. Runs with the service up — it touches only the analytics DB.
log "Pre-generating far-destination itineraries..."
if [ -n "${GROQ_API_KEY:-}" ]; then
  python -u scripts/pregen_far_routes.py 2>&1 | tail -5 | tee -a "$LOG" || log "WARN: pregen_far_routes failed"
else
  log "SKIP: GROQ_API_KEY not set (see .env) — far guides stay unindexable"
fi

log "Done!"

# Write last_refresh.json so /health shows nightly status
python3 -c "
import json, time
status = 'ok' if '$HSTATUS' == '200' else 'degraded'
with open('$DIR/logs/last_refresh.json', 'w') as f:
    json.dump({'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'finished_ts': time.time(), 'status': status, 'health_http': '$HSTATUS'}, f)
"

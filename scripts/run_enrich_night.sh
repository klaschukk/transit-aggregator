#!/bin/bash
set -euo pipefail
DIR=/root/klaschuk/transit-aggregator
LOG=$DIR/logs/enrich.log

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

log "Starting nightly enrich..."
cd "$DIR"
source venv/bin/activate

log "Minifying CSS..."
python -u scripts/minify_css.py 2>&1 | tee -a "$LOG" || log "WARN: minify_css failed"

log "Cleaning OG image cache (>7 days)..."
find data/cache/og -name "*.png" -mtime +7 -delete 2>/dev/null || true

log "Scraping Niš stops (Overpass OSM)..."
python -u data/pipelines/scrape_nis_stops.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_nis_stops failed"

log "Enriching stop coordinates..."
python -u data/pipelines/enrich_stops_coords.py 2>&1 | tee -a "$LOG" || log "WARN: enrich_stops_coords failed"

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

log "Rebuilding transit.duckdb..."
python -u data/pipelines/build_db.py 2>&1 | tee -a "$LOG"

# Pair-level affiliate map (app/affiliates/bt4_lineids.json): only departures
# busticket4 actually sells online (purchase_allowed) get a lineId. partners.py
# loads the JSON at import, so the restart below is what ships it.
log "Refreshing BT4 affiliate line ids..."
python -u data/pipelines/refresh_bt4_lineids.py 2>&1 | tee -a "$LOG" || log "WARN: refresh_bt4_lineids failed"

log "Restarting transit (fresh DB + affiliate map)..."
systemctl restart transit
sleep 3
HSTATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://127.0.0.1:8000/health || echo "000")
log "Health after restart: $HSTATUS"
if [ "$HSTATUS" != "200" ]; then
  log "WARN: not healthy after restart, retrying..."
  systemctl restart transit
fi

log "Done!"

# Write last_refresh.json so /health shows nightly status
python3 -c "
import json, time
with open('$DIR/logs/last_refresh.json', 'w') as f:
    json.dump({'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'finished_ts': time.time(), 'status': 'ok'}, f)
"

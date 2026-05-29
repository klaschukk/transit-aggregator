#!/bin/bash
set -euo pipefail
DIR=/root/klaschuk/transit-aggregator
LOG=$DIR/logs/enrich.log

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

log "Starting nightly enrich..."
cd "$DIR"
source venv/bin/activate

log "Scraping Niš stops (Overpass OSM)..."
python -u data/pipelines/scrape_nis_stops.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_nis_stops failed"

log "Enriching stop coordinates..."
python -u data/pipelines/enrich_stops_coords.py 2>&1 | tee -a "$LOG" || log "WARN: enrich_stops_coords failed"

log "Rebuilding transit.duckdb..."
python -u data/pipelines/build_db.py 2>&1 | tee -a "$LOG"

log "Done!"

# Write last_refresh.json so /health shows nightly status
python3 -c "
import json, time
with open('$DIR/logs/last_refresh.json', 'w') as f:
    json.dump({'finished_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'finished_ts': time.time(), 'status': 'ok'}, f)
"

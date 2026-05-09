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
systemctl stop transit
python -u data/pipelines/build_db.py 2>&1 | tee -a "$LOG"
systemctl start transit

log "Done!"

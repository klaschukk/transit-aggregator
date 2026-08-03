#!/bin/bash
# Refresh road-following polylines for the line maps (OSM Overpass).
#
# Why this is not part of run_enrich_night.sh: the scrape takes ~35s per line
# (~5h for Belgrade's 516 alone), and the nightly's DB phase runs with the
# service stopped. Folding it in there would take the site down all night.
#
# Instead the scrape runs against a COPY while the site keeps serving, and the
# result is swapped in with a few seconds of downtime. Losing the table is what
# the Apr 25 incident was about: build_db can only preserve it, never create
# it, so a DB built from scratch has no geometries and every line map silently
# degrades to zig-zag straight lines. /health reports the count and degrades
# when it is empty.
#
# Cron: weekly is plenty — OSM route relations change rarely.
#   30 1 * * 6 cd /home/deploy/transit-aggregator && ./scripts/refresh_line_geometries.sh
#
# Usage: ./scripts/refresh_line_geometries.sh [city ...]   (default: all)
set -o pipefail

DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
LOG=$DIR/logs/line_geometries.log
DB=$DIR/data/dbs/transit.duckdb
WORK=$DIR/data/dbs/.geom_work.duckdb
MAINT_FLAG=$DIR/logs/.maintenance

mkdir -p "$DIR/logs"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }

cd "$DIR" || exit 1
source venv/bin/activate

if [ ! -f "$DB" ]; then
  log "FATAL: $DB missing"
  exit 1
fi

log "Copying DB for offline scrape..."
rm -f "$WORK"
cp "$DB" "$WORK" || { log "FATAL: copy failed"; exit 1; }
trap 'rm -f "$WORK"' EXIT

log "Scraping OSM route geometries (site stays up)..."
GEOM_DB="$WORK" python -u - "$@" >> "$LOG" 2>&1 <<'PY'
import importlib.util
import os
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    'geo', 'data/pipelines/scrape_route_geometries.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.DB = Path(os.environ['GEOM_DB'])
sys.argv = ['scrape_route_geometries.py'] + sys.argv[1:]
raise SystemExit(mod.main())
PY
SCRAPE_STATUS=$?

if [ $SCRAPE_STATUS -ne 0 ]; then
  log "FAIL: scrape exited $SCRAPE_STATUS — keeping current DB untouched"
  exit $SCRAPE_STATUS
fi

# Only swap when the copy actually gained geometries, so a partial or empty
# run can never replace a good DB with a worse one.
COUNT=$(python -c "
import duckdb, sys
try:
    c = duckdb.connect('$WORK', read_only=True)
    print(c.execute('SELECT COUNT(*) FROM line_geometries').fetchone()[0])
except Exception:
    print(0)
")
log "Geometries in scraped copy: $COUNT"
if [ "${COUNT:-0}" -lt 1 ]; then
  log "FAIL: copy has no geometries — not swapping"
  exit 1
fi

log "Swapping DB in (brief downtime)..."
touch "$MAINT_FLAG"
sudo systemctl stop prevozni
sleep 1
cp "$WORK" "$DB" && chown deploy:deploy "$DB"
sudo systemctl start prevozni
rm -f "$MAINT_FLAG"
sleep 3

HSTATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 \
  --unix-socket /run/prevozni/prevozni.sock http://localhost/health || echo "000")
log "Health after swap: $HSTATUS"
if [ "$HSTATUS" != "200" ]; then
  log "WARN: unhealthy after swap, restarting once"
  sudo systemctl restart prevozni
fi

log "Done — $COUNT geometries live"

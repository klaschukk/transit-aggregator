#!/bin/bash
# Nightly data refresh pipeline for Transit Serbia.
# Runs ALL scrapers (city + intercity + trains), rebuilds DB, restarts.
# This is the FULL manual pipeline (~30-60 min, service stopped while
# scraping). The light nightly cron is scripts/run_enrich_night.sh.

set -o pipefail

# Resolve the project root from the script location so the same file
# works on any box (the old hardcoded /home/klaschuk/transit silently
# broke the box where the checkout lives in /root/klaschuk/...).
PROJECT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VENV=$PROJECT/venv/bin/python3
LOG=$PROJECT/logs/nightly_$(date +%Y%m%d).log
STARTED_TS=$(date +%s)

mkdir -p "$PROJECT/logs"
echo "=== START $(date) ===" >> "$LOG"

# Per-scraper exit-code tracking. `run_scraper` increments these so the
# marker can record "lasta failed but intercity succeeded" instead of
# the previous one-bit "all of nightly is ok|fail" signal.
declare -A SCRAPER_STATUS

run_scraper() {
  local name="$1"; shift
  local script="$1"; shift
  if "$VENV" -u "$PROJECT/data/pipelines/$script" "$@" >> "$LOG" 2>&1; then
    SCRAPER_STATUS["$name"]="ok"
  else
    local rc=$?
    SCRAPER_STATUS["$name"]="fail:$rc"
    echo "WARN: $name failed (exit $rc)" >> "$LOG"
  fi
}

# Render SCRAPER_STATUS as JSON object.
render_scrapers_json() {
  local out=""
  for k in "${!SCRAPER_STATUS[@]}"; do
    [[ -n "$out" ]] && out+=","
    out+="\"$k\":\"${SCRAPER_STATUS[$k]}\""
  done
  echo "{$out}"
}

# Write a machine-readable marker for /health. Used by the Flask /health
# endpoint to surface "nightly last ran 8h ago, status=ok".
write_marker() {
  local status="$1"
  local http="${2:-}"
  local now_iso
  now_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local now_ts
  now_ts=$(date +%s)
  local duration=$((now_ts - STARTED_TS))
  local scrapers_json
  scrapers_json=$(render_scrapers_json)
  cat > "$PROJECT/logs/last_refresh.json" <<EOF
{"status":"$status","finished_at":"$now_iso","finished_ts":$now_ts,"duration_s":$duration,"health_http":"$http","scrapers":$scrapers_json}
EOF
}

# Ping Sentry. No-op when SENTRY_DSN is unset; otherwise captures a message
# tagged with job=nightly so alerts can route on that tag.
sentry_ping() {
  "$VENV" "$PROJECT/scripts/sentry_notify.py" "$1" "${2:-error}" job=nightly \
    >> "$LOG" 2>&1 || true
}

# Stop service to release DB lock
sudo systemctl stop prevozni
sleep 2

cd "$PROJECT" || exit 1

# Run scrapers — each is optional, failure is non-fatal. discover_cities
# refreshes the bt4 city catalog that scrape_intercity + scrape_international
# both read from; must run first. Per-scraper exit codes are tracked in
# SCRAPER_STATUS so /health can surface "scrape_lasta failed last night"
# instead of the all-or-nothing top-level status.
run_scraper discover_cities          discover_cities.py
run_scraper scrape_gsp               scrape_gsp.py
run_scraper scrape_intercity         scrape_intercity.py
run_scraper scrape_srbvoz            scrape_srbvoz.py
run_scraper scrape_lasta             scrape_lasta.py
run_scraper scrape_gspns             scrape_gspns.py
run_scraper scrape_gspns_schedule    scrape_gspns_schedule.py
run_scraper scrape_naissus           scrape_naissus.py
run_scraper scrape_international     scrape_international.py

# Rebuild database — this is critical
$VENV -u data/pipelines/build_db.py >> "$LOG" 2>&1
BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
  echo "FATAL: build_db failed (exit $BUILD_STATUS)" >> "$LOG"
  sudo systemctl start prevozni
  echo "FAIL $(date)" > "$PROJECT/logs/last_refresh.txt"
  write_marker "fail"
  sentry_ping "nightly_refresh: build_db failed exit=$BUILD_STATUS" fatal
  echo "=== FAILED $(date) ===" >> "$LOG"
  exit 1
fi

# Post-build: add Novi Sad OSM stops + line links
$VENV -u scripts/enrich_post_build.py >> "$LOG" 2>&1 || true

# Refresh line_geometries (OSM Overpass road polylines for line_detail
# minimaps). build_db.py preserves the table across rebuilds, so this
# only fills gaps + bumps fetched_at; ~30-60 min when Overpass mirrors
# are healthy. Non-fatal — line_detail falls back to straight-line
# polylines when a line has no row, and /health treats line_geometries
# as critical so a permanently-empty table will surface as 503 the
# next morning instead of silently 500ing pages (Apr 25 incident).
$VENV -u data/pipelines/scrape_route_geometries.py >> "$LOG" 2>&1 \
  || echo "WARN: scrape_route_geometries failed ($?)" >> "$LOG"

# Per-entity row-count snapshot. Captures upstream scrape drift the
# file-mtime freshness signal misses. Non-fatal — analytics_db is the
# read path here, transit_db rebuild is what already shipped.
$VENV -u scripts/data_snapshot.py >> "$LOG" 2>&1 || echo "WARN: data_snapshot failed ($?)" >> "$LOG"

# Price-alert snapshot + scan. Non-fatal — an email-send outage must not
# block the nightly refresh. Snapshot must run before scan.
$VENV -u scripts/price_snapshot.py   >> "$LOG" 2>&1 || echo "WARN: price_snapshot failed ($?)" >> "$LOG"
$VENV -u scripts/price_alert_scan.py >> "$LOG" 2>&1 || echo "WARN: price_alert_scan failed ($?)" >> "$LOG"

# Enrich stop coordinates (non-blocking, limit to 50 per night)
$VENV -u data/pipelines/enrich_stops_coords.py enrich --limit 50 >> "$LOG" 2>&1 || true

# Refresh the BT4 pair→line_id affiliate map (reads route pairs from the
# just-rebuilt DB; partners.py loads the JSON at import, so running this
# before the service start below is what actually ships the fresh map).
# A stale line_id 404s the checkout and silently costs sales. Non-fatal:
# the script keeps the old map if API coverage drops below 85%.
$VENV -u data/pipelines/refresh_bt4_lineids.py >> "$LOG" 2>&1 \
  || echo "WARN: refresh_bt4_lineids failed ($?)" >> "$LOG"

# Start service
sudo systemctl start prevozni
sleep 3

# Health check
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --unix-socket /run/prevozni/prevozni.sock http://localhost/health)
echo "Health check: $STATUS" >> "$LOG"

if [ "$STATUS" != "200" ]; then
  echo "WARN: Service not healthy after restart" >> "$LOG"
  sudo systemctl restart prevozni
  sleep 3
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --unix-socket /run/prevozni/prevozni.sock http://localhost/health)
  echo "Retry health check: $STATUS" >> "$LOG"
  if [ "$STATUS" != "200" ]; then
    sentry_ping "nightly_refresh: /health still not 200 after restart (got $STATUS)" error
  fi
fi

echo "=== DONE $(date) ===" >> "$LOG"
echo "$STATUS $(date)" > "$PROJECT/logs/last_refresh.txt"
if [ "$STATUS" = "200" ]; then
  write_marker "ok" "$STATUS"
else
  write_marker "degraded" "$STATUS"
fi

# Cleanup logs older than 14 days
find "$PROJECT/logs" -name "nightly_*.log" -mtime +14 -delete 2>/dev/null || true

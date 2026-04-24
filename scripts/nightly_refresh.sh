#!/bin/bash
# Nightly data refresh pipeline for Transit Serbia.
# Runs all scrapers, rebuilds DB, restarts service.
# Cron: 0 2 * * * /home/klaschuk/transit/scripts/nightly_refresh.sh

set -o pipefail

PROJECT=/home/klaschuk/transit
VENV=$PROJECT/venv/bin/python3
LOG=$PROJECT/logs/nightly_$(date +%Y%m%d).log
STARTED_TS=$(date +%s)

mkdir -p "$PROJECT/logs"
echo "=== START $(date) ===" >> "$LOG"

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
  cat > "$PROJECT/logs/last_refresh.json" <<EOF
{"status":"$status","finished_at":"$now_iso","finished_ts":$now_ts,"duration_s":$duration,"health_http":"$http"}
EOF
}

# Ping Sentry. No-op when SENTRY_DSN is unset; otherwise captures a message
# tagged with job=nightly so alerts can route on that tag.
sentry_ping() {
  "$VENV" "$PROJECT/scripts/sentry_notify.py" "$1" "${2:-error}" job=nightly \
    >> "$LOG" 2>&1 || true
}

# Stop service to release DB lock
sudo systemctl stop transit
sleep 2

cd "$PROJECT" || exit 1

# Run scrapers — each is optional, failure is non-fatal.
# discover_cities refreshes the bt4 city catalog that scrape_intercity +
# scrape_international both read from; must run first.
$VENV -u data/pipelines/discover_cities.py  >> "$LOG" 2>&1 || echo "WARN: discover_cities failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_gsp.py       >> "$LOG" 2>&1 || echo "WARN: scrape_gsp failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_intercity.py  >> "$LOG" 2>&1 || echo "WARN: scrape_intercity failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_srbvoz.py     >> "$LOG" 2>&1 || echo "WARN: scrape_srbvoz failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_lasta.py      >> "$LOG" 2>&1 || echo "WARN: scrape_lasta failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_gspns.py           >> "$LOG" 2>&1 || echo "WARN: scrape_gspns failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_gspns_schedule.py  >> "$LOG" 2>&1 || echo "WARN: scrape_gspns_schedule failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_naissus.py         >> "$LOG" 2>&1 || echo "WARN: scrape_naissus failed ($?)" >> "$LOG"
$VENV -u data/pipelines/scrape_international.py   >> "$LOG" 2>&1 || echo "WARN: scrape_international failed ($?)" >> "$LOG"

# Rebuild database — this is critical
$VENV -u data/pipelines/build_db.py >> "$LOG" 2>&1
BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
  echo "FATAL: build_db failed (exit $BUILD_STATUS)" >> "$LOG"
  sudo systemctl start transit
  echo "FAIL $(date)" > "$PROJECT/logs/last_refresh.txt"
  write_marker "fail"
  sentry_ping "nightly_refresh: build_db failed exit=$BUILD_STATUS" fatal
  echo "=== FAILED $(date) ===" >> "$LOG"
  exit 1
fi

# Post-build: add Novi Sad OSM stops + line links
$VENV -u scripts/enrich_post_build.py >> "$LOG" 2>&1 || true

# Price-alert snapshot + scan. Non-fatal — an email-send outage must not
# block the nightly refresh. Snapshot must run before scan.
$VENV -u scripts/price_snapshot.py   >> "$LOG" 2>&1 || echo "WARN: price_snapshot failed ($?)" >> "$LOG"
$VENV -u scripts/price_alert_scan.py >> "$LOG" 2>&1 || echo "WARN: price_alert_scan failed ($?)" >> "$LOG"

# Enrich stop coordinates (non-blocking, limit to 50 per night)
$VENV -u data/pipelines/enrich_stops_coords.py enrich --limit 50 >> "$LOG" 2>&1 || true

# Start service
sudo systemctl start transit
sleep 3

# Health check
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://127.0.0.1:5000/health)
echo "Health check: $STATUS" >> "$LOG"

if [ "$STATUS" != "200" ]; then
  echo "WARN: Service not healthy after restart" >> "$LOG"
  sudo systemctl restart transit
  sleep 3
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://127.0.0.1:5000/health)
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

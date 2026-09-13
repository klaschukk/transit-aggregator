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
python -u data/pipelines/scrape_nis_stops.py nis 2>&1 | tee -a "$LOG" || log "WARN: scrape_nis_stops nis failed"

# Montenegro city transport (OSM). Self-healing: writes each city's lines.json
# only on a successful fetch, so an Overpass 504 keeps yesterday's data; build_db
# skips any city whose file is absent. Non-fatal.
log "Scraping Montenegro city lines (Overpass OSM)..."
python -u data/pipelines/scrape_montenegro.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_montenegro failed"

log "Scraping Kragujevac city lines (Overpass OSM)..."
python -u data/pipelines/scrape_kragujevac.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_kragujevac failed"

log "Scraping Novi Sad lines (JGSP)..."
python -u data/pipelines/scrape_gspns.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_gspns failed"

# MUST run after scrape_gspns: both write data/raw/novi-sad/lines.json, and
# gspns rewrites it wholesale from JGSP /mreza. With the OSM import first, the
# 490 stops it had just fetched were overwritten by JGSP's name-only list the
# same night. Running it second means OSM enriches the fresh JGSP lines instead.
# Novi Sad's own source ships stop names without coordinates, so its stops come
# from the same OSM importer used for Nis.
log "Scraping Novi Sad stops (Overpass OSM)..."
python -u data/pipelines/scrape_nis_stops.py novi-sad 2>&1 | tee -a "$LOG" || log "WARN: scrape_nis_stops novi-sad failed"

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

log "Scraping ArdaTur (Bulgaria <-> wider Europe/Turkey)..."
python -u data/pipelines/scrape_ardatur.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_ardatur failed"

log "Scraping Union Ivkoni (Bulgaria-domestic + Bulgaria<->Greece)..."
python -u data/pipelines/scrape_ivkoni.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_ivkoni failed"

log "Scraping Srbija Tours (Serbia <-> Germany diaspora coaches)..."
python -u data/pipelines/scrape_srbijatours.py 2>&1 | tee -a "$LOG" || log "WARN: scrape_srbijatours failed"

# ── DB build: runs with the site UP ─────────────────────────────────────────
# build_db writes to transit.duckdb.tmp and finishes with an atomic os.replace,
# so the live DB stays intact and workers keep serving throughout. It used to
# sit inside the maintenance window purely by habit, which cost ~1m51s of 503s
# for nothing.

log "Rebuilding transit.duckdb (site stays up)..."
python -u data/pipelines/build_db.py 2>&1 | tee -a "$LOG"

# Pair-level affiliate map (app/affiliates/bt4_lineids.json): only departures
# busticket4 actually sells online (purchase_allowed) get a lineId. It writes
# JSON, never the DB, so it does not need the service down either — this was
# the biggest slice of the old window at ~3m27s. partners.py loads the JSON at
# import, so the restart below is what ships it.
log "Refreshing BT4 affiliate line ids (site stays up)..."
python -u data/pipelines/refresh_bt4_lineids.py 2>&1 | tee -a "$LOG" || log "WARN: refresh_bt4_lineids failed"

# ── Enrich: on a COPY, so the site never stops ──────────────────────────────
# gunicorn holds a read lock on transit.duckdb and DuckDB allows either one
# writer or many readers, so enrich cannot write to the live file. Stopping the
# service for it cost ~1m37s of 5xx every night — and Google counts those
# against the "Server error (5xx)" validation, which is exactly the report we
# need to pass. 503 is a 5xx like any other.
#
# So: copy, enrich the copy, swap it in atomically, then SIGHUP gunicorn.
# os.replace and a graceful reload are both zero-downtime, so the nightly no
# longer produces a single 5xx.

ENRICH_WORK=$DIR/data/dbs/.enrich_work.duckdb
log "Enriching stop coordinates (on a copy, site stays up)..."
rm -f "$ENRICH_WORK"
if cp "$DIR/data/dbs/transit.duckdb" "$ENRICH_WORK"; then
  if DUCKDB_PATH="$ENRICH_WORK" python -u data/pipelines/enrich_stops_coords.py \
       enrich --limit 200 2>&1 | tee -a "$LOG"; then
    # Only swap when the copy still looks sane — never replace a good DB with
    # a truncated one.
    STOPS=$(python -c "
import duckdb, sys
try:
    c = duckdb.connect('$ENRICH_WORK', read_only=True)
    print(c.execute('SELECT COUNT(*) FROM city_stops').fetchone()[0])
except Exception:
    print(0)
")
    if [ "${STOPS:-0}" -gt 100 ]; then
      mv -f "$ENRICH_WORK" "$DIR/data/dbs/transit.duckdb"
      log "Enriched DB swapped in ($STOPS stops)"
    else
      log "WARN: enriched copy has $STOPS stops — not swapping"
    fi
  else
    log "WARN: enrich_stops_coords failed — keeping current DB"
  fi
  rm -f "$ENRICH_WORK"
fi

# Graceful reload: workers re-exec one at a time, so they pick up the DB that
# build_db and the enrich swap put in place, plus the fresh affiliate map,
# without the socket ever refusing a request.
log "Reloading transit (fresh DB + affiliate map)..."
sudo systemctl reload prevozni
sleep 3
HSTATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 --unix-socket /run/prevozni/prevozni.sock http://localhost/health || echo "000")
log "Health after reload: $HSTATUS"
if [ "$HSTATUS" != "200" ]; then
  log "WARN: not healthy after reload, restarting..."
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

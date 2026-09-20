#!/bin/bash
# Nightly backup of data/dbs/analytics.sqlite — the one file on this box that
# cannot be rebuilt from scrapers (subscribers, reviews, buy-clicks, A/B events,
# composed far-route itineraries). transit.duckdb is rebuilt nightly, so it is
# deliberately NOT backed up here.
# Uses sqlite's online .backup (safe while gunicorn writes in WAL mode), gzips,
# keeps 7 days. Cron (deploy): 20 2 * * *
set -euo pipefail
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DB=$DIR/data/dbs/analytics.sqlite
OUT_DIR=$DIR/data/backups
KEEP_DAYS=7
mkdir -p "$OUT_DIR"
STAMP=$(date +%Y%m%d)
TMP=$OUT_DIR/.analytics-$STAMP.sqlite
sqlite3 "$DB" ".backup '$TMP'"
# refuse to keep a backup that does not open or is empty
rows=$(sqlite3 "$TMP" "SELECT COUNT(*) FROM sqlite_master")
[ "$rows" -gt 5 ] || { rm -f "$TMP"; echo "$(date -u +%FT%TZ) FAIL: backup has $rows schema objects" >&2; exit 1; }
gzip -f "$TMP" && mv -f "$TMP.gz" "$OUT_DIR/analytics-$STAMP.sqlite.gz"
find "$OUT_DIR" -name 'analytics-*.sqlite.gz' -mtime +$KEEP_DAYS -delete
echo "$(date -u +%FT%TZ) OK analytics-$STAMP.sqlite.gz $(du -h "$OUT_DIR/analytics-$STAMP.sqlite.gz" | cut -f1)"

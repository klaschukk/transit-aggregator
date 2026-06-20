#!/bin/bash
# Sunday-evening content + SEO refresh.
#
# 80% of Bookaway clicks come on Mondays — Sunday 22:00 UTC (00:00
# Belgrade) is the latest moment we can ship content updates that will
# be in Google's index by Monday morning. The job:
#
#   1. Ping Google + Bing sitemap so any new pages (country hubs,
#      new routes, fresh schedules) show up in SERPs faster.
#   2. Replay scrapers if the most recent run is older than 24h —
#      keeps trip schedules current for Monday-morning searchers.
#   3. Run the standard weekly SEO digest path (already idempotent).
#
# Cron: 0 22 * * 0 /home/klaschuk/transit/scripts/sunday_content_refresh.sh
#
# All work is logged to logs/sunday_refresh_<date>.log.

set -o pipefail

PROJECT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VENV=$PROJECT/venv/bin/python3
TODAY=$(date -u +%Y-%m-%d)
LOG=$PROJECT/logs/sunday_refresh_${TODAY}.log

mkdir -p "$PROJECT/logs"
echo "=== START $(date -u) ===" >> "$LOG"

cd "$PROJECT" || exit 1

# Step 1: ping search engines.
#
# Google deprecated /ping?sitemap= in 2023 (verified 404 in 2026);
# Bing /ping?sitemap= now 410-Gone. The replacement for Bing/Yandex/
# Naver/Seznam/Yep is IndexNow — submit the urlList in one batched
# POST, indexes within 5-30 minutes for participating engines.
#
# Google honours sitemap-lastmod for re-crawl decisions, so the
# /sitemap-*.xml `<lastmod>` we already emit on every shard is the
# only signal we have left short of the Indexing API (OAuth, out of
# scope until GSC creds land).
if [ -x "$PROJECT/scripts/ping_indexnow.sh" ]; then
  echo "running ping_indexnow..." >> "$LOG"
  "$PROJECT/scripts/ping_indexnow.sh" >> "$LOG" 2>&1
  echo "ping_indexnow exit=$?" >> "$LOG"
fi

# Step 2: refresh scrapers if last enrichment is stale. The nightly
# enrich job runs at 03:00 UTC; if it failed for any reason this is the
# Sunday-evening rescue window before Monday traffic.
ENRICH_MARKER="$PROJECT/data/raw/.last_enrich"
NEEDS_ENRICH=1
if [ -f "$ENRICH_MARKER" ]; then
  AGE_H=$(( ( $(date +%s) - $(stat -c %Y "$ENRICH_MARKER") ) / 3600 ))
  if [ "$AGE_H" -lt 24 ]; then
    NEEDS_ENRICH=0
    echo "skip enrich: last run $AGE_H h ago" >> "$LOG"
  fi
fi
if [ "$NEEDS_ENRICH" -eq 1 ] && [ -x "$PROJECT/scripts/run_enrich_night.sh" ]; then
  echo "running enrich..." >> "$LOG"
  "$PROJECT/scripts/run_enrich_night.sh" >> "$LOG" 2>&1
  ENR_STATUS=$?
  echo "enrich exit=$ENR_STATUS" >> "$LOG"
  [ "$ENR_STATUS" -eq 0 ] && touch "$ENRICH_MARKER"
fi

# Step 3: weekly SEO digest. Idempotent — internally skips if GSC
# credentials are not configured. Reuses the same log structure.
if [ -x "$PROJECT/scripts/weekly_seo.sh" ]; then
  echo "running weekly_seo..." >> "$LOG"
  "$PROJECT/scripts/weekly_seo.sh" >> "$LOG" 2>&1
fi

echo "=== DONE $(date -u) ===" >> "$LOG"

# Cleanup old refresh logs (keep 60 days)
find "$PROJECT/logs" -name "sunday_refresh_*.log" -mtime +60 -delete 2>/dev/null || true

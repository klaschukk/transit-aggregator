#!/bin/bash
# IndexNow ping — submit every URL in our sitemap shards to Bing,
# Yandex, and Naver in one POST. Replaces the dead Google /ping and
# Bing /ping legacy endpoints (deprecated in 2023, returning 404/410
# in 2026 — verified via curl on 2026-04-26).
#
# IndexNow surfaces fresh URLs in 5-30 minutes for participating
# engines (Bing/Yandex/Naver/Seznam.cz/Yep). Google does NOT honour
# IndexNow but does follow the sitemap-lastmod signal we already emit.
#
# Rate limit: IndexNow accepts up to 10K URLs per submit. We're at
# ~3.5K so a single batch covers everything; the chunking loop is
# defensive in case the sitemap grows.
#
# Usage:   bash scripts/ping_indexnow.sh
# Cron:    invoked from sunday_content_refresh.sh post-enrich.
# Exit:    0 if IndexNow returned 2xx; non-zero if anything broke.

set -o pipefail

PROJECT=/home/klaschuk/transit
KEY_FILE=$PROJECT/data/secrets/indexnow.key
LOG=$PROJECT/logs/indexnow.log
HOST=prevozni.com
ENDPOINT=https://api.indexnow.org/indexnow

if [ ! -r "$KEY_FILE" ]; then
  echo "$(date -u +%FT%TZ) FAIL: missing key at $KEY_FILE" >> "$LOG"
  exit 2
fi
KEY=$(tr -d '[:space:]' < "$KEY_FILE")
KEY_LOC="https://${HOST}/${KEY}.txt"

mkdir -p "$PROJECT/logs"
echo "=== $(date -u +%FT%TZ) IndexNow ping start ===" >> "$LOG"

# Step 1: pull every <loc> from the live sitemap shards. Production
# sitemap is what IndexNow's engines will themselves crawl, so we
# submit the same set rather than a separate offline list.
TMP=$(mktemp -t indexnow.XXXXXX.txt)
trap 'rm -f "$TMP" "${TMP}.json"' EXIT

for shard in core routes pairs lines stops; do
  curl -sf "https://${HOST}/sitemap-${shard}.xml" --max-time 30 \
    | grep -oE '<loc>[^<]+</loc>' \
    | sed -E 's#</?loc>##g' \
    >> "$TMP" || echo "warn: shard $shard fetch failed" >> "$LOG"
done

TOTAL=$(wc -l < "$TMP" | tr -d ' ')
echo "collected $TOTAL URLs" >> "$LOG"

if [ "$TOTAL" -eq 0 ]; then
  echo "$(date -u +%FT%TZ) FAIL: empty URL list — sitemap fetch broken?" >> "$LOG"
  exit 3
fi

# Step 2: chunk into batches. IndexNow's published cap is 10K per
# submission; in practice 3457 URLs sometimes 403'd on first run
# (rate-limit during fresh-key validation), so split into 1000-URL
# batches with a brief sleep between them. Slower ramp keeps Bing's
# Cloudflare-style anti-burst quiet.
BATCH=1000
CHUNK_DIR=$(mktemp -d -t indexnow-chunks.XXXXXX)
trap 'rm -rf "$TMP" "${TMP}.json" "$CHUNK_DIR"' EXIT
split -l $BATCH "$TMP" "$CHUNK_DIR/chunk."

OK=0
FAIL=0
for chunk in "$CHUNK_DIR"/chunk.*; do
  # Build the JSON body: jq isn't a hard dep on this host, so do it
  # in python (already in venv path).
  $PROJECT/venv/bin/python3 - "$chunk" "$HOST" "$KEY" "$KEY_LOC" <<'PY' > "${TMP}.json"
import json, sys
chunk_path, host, key, key_loc = sys.argv[1:5]
urls = [line.strip() for line in open(chunk_path) if line.strip()]
print(json.dumps({
    'host': host,
    'key': key,
    'keyLocation': key_loc,
    'urlList': urls,
}))
PY
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 30 \
    -X POST "$ENDPOINT" \
    -H "Content-Type: application/json; charset=utf-8" \
    --data-binary @"${TMP}.json" 2>/dev/null || echo "000")
  # One retry on 403 — fresh-key validation can race with the first
  # submission. Sleep 5 s then resend the same body.
  if [ "$CODE" = "403" ]; then
    sleep 5
    CODE=$(curl -s -o /dev/null -w "%{http_code}" -m 30 \
      -X POST "$ENDPOINT" \
      -H "Content-Type: application/json; charset=utf-8" \
      --data-binary @"${TMP}.json" 2>/dev/null || echo "000")
    echo "chunk $(basename "$chunk") retried 403 → HTTP $CODE" >> "$LOG"
  fi
  N=$(wc -l < "$chunk" | tr -d ' ')
  echo "chunk $(basename "$chunk") urls=$N → HTTP $CODE" >> "$LOG"
  case "$CODE" in
    2*) OK=$((OK+1)) ;;
    *)  FAIL=$((FAIL+1)) ;;
  esac
  # Be a polite client — 1 s between batches.
  sleep 1
done

echo "$(date -u +%FT%TZ) DONE total=$TOTAL ok=$OK fail=$FAIL" >> "$LOG"
echo "" >> "$LOG"

# Cleanup old IndexNow log lines (keep ~6 months of history).
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 5000 ]; then
  tail -n 5000 "$LOG" > "${LOG}.trim" && mv "${LOG}.trim" "$LOG"
fi

[ "$FAIL" -eq 0 ]

#!/bin/bash
# Weekly SEO digest — pulls GSC data, builds markdown report,
# optionally notifies Telegram, auto-commits if docs changed.
#
# Cron: 0 8 * * 0 /home/klaschuk/transit/scripts/weekly_seo.sh
#       (Sunday 08:00 UTC)

set -o pipefail

PROJECT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VENV=$PROJECT/venv/bin/python3
TODAY=$(date -u +%Y-%m-%d)
LOG=$PROJECT/logs/weekly_seo_${TODAY}.log

mkdir -p "$PROJECT/logs" "$PROJECT/data/gsc"
echo "=== START $(date -u) ===" >> "$LOG"

cd "$PROJECT" || exit 1

# Step 1: fetch. Exit code 2 = credentials missing → silent skip.
$VENV -u scripts/gsc_fetch.py --as-of "$TODAY" >> "$LOG" 2>&1
FETCH_STATUS=$?
echo "gsc_fetch exit=$FETCH_STATUS" >> "$LOG"

if [ $FETCH_STATUS -eq 2 ]; then
  echo "SKIP: GSC credentials not configured — see docs/06_tech/gsc-setup.md" >> "$LOG"
  echo "=== SKIPPED $(date -u) ===" >> "$LOG"
  exit 0
fi

if [ $FETCH_STATUS -ne 0 ]; then
  echo "WARN: gsc_fetch returned $FETCH_STATUS — attempting digest on existing data" >> "$LOG"
fi

# Step 2: digest. Non-fatal if it exits 4 (no snapshots yet).
DIGEST_ARGS="--as-of $TODAY"
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
  DIGEST_ARGS="$DIGEST_ARGS --telegram"
fi
$VENV -u scripts/gsc_digest.py $DIGEST_ARGS >> "$LOG" 2>&1
DIGEST_STATUS=$?
echo "gsc_digest exit=$DIGEST_STATUS" >> "$LOG"

# Step 3: auto-commit the digest if git-tracked changes exist.
DIGEST_FILE="docs/00_strategy/weekly-seo-${TODAY}.md"
if [ -f "$DIGEST_FILE" ]; then
  if ! git diff --quiet -- "$DIGEST_FILE" 2>/dev/null || \
     ! git ls-files --error-unmatch "$DIGEST_FILE" >/dev/null 2>&1; then
    git add "$DIGEST_FILE" >> "$LOG" 2>&1
    git -c user.name='seo-bot' -c user.email='seo-bot@prevozni.com' \
        commit -m "docs: weekly SEO digest ${TODAY}" >> "$LOG" 2>&1 || \
        echo "commit skipped (no changes?)" >> "$LOG"
  fi
fi

echo "=== DONE $(date -u) ===" >> "$LOG"

# Cleanup logs older than 30 days
find "$PROJECT/logs" -name "weekly_seo_*.log" -mtime +30 -delete 2>/dev/null || true

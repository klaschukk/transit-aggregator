#!/bin/bash
# Polls GitLab for new commits on main; pulls and restarts if changed.
# Runs via cron every 2 minutes.
set -euo pipefail

DIR=/root/klaschuk/transit-aggregator
LOG=$DIR/logs/autodeploy.log
BRANCH=main

cd "$DIR"

# Always ensure we're on the target branch before comparing/resetting
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  git checkout "$BRANCH" >> "$LOG" 2>&1
fi

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git ls-remote origin "refs/heads/$BRANCH" 2>/dev/null | awk '{print $1}')

if [ -z "$REMOTE" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') ERROR: could not reach remote" >> "$LOG"
  exit 1
fi

if [ "$LOCAL" = "$REMOTE" ]; then
  exit 0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') New commit $REMOTE (was $LOCAL), deploying..." >> "$LOG"

git fetch origin "$BRANCH" >> "$LOG" 2>&1
git reset --hard "origin/$BRANCH" >> "$LOG" 2>&1

# Install new deps if requirements changed
"$DIR/venv/bin/pip" install -r requirements.txt -q >> "$LOG" 2>&1

systemctl restart transit >> "$LOG" 2>&1

# Verify service came up
sleep 3
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/health)
if [ "$STATUS" = "200" ]; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') Deploy OK — $REMOTE" >> "$LOG"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') WARN: health returned $STATUS after deploy" >> "$LOG"
fi

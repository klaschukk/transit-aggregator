#!/bin/bash
# Manual deploy — run ON the server to update to the latest origin/<branch>.
#
# Replaces the old cron autodeploy (transit-autodeploy.sh, every 2 min), which
# reset the working tree to origin/main automatically and repeatedly wiped
# in-progress / uncommitted work. Deploying is now an explicit, on-demand
# action: you run this when you actually want to ship.
#
# Usage:  scripts/deploy.sh [branch]      (default: main)
set -euo pipefail

DIR=/opt/prevozni
BRANCH="${1:-main}"
cd "$DIR"

echo "==> Deploying origin/$BRANCH"
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"

echo "==> Installing deps"
"$DIR/venv/bin/pip" install -r requirements.txt -q

# Rebuild minified CSS into static/css/dist/ (gitignored, not committed) so the
# served, cache-busted CSS matches source. The old autodeploy skipped this, so
# CSS edits silently never shipped.
echo "==> Rebuilding CSS dist"
"$DIR/venv/bin/python" scripts/minify_css.py || echo "WARN: minify_css failed, dist may be stale"

echo "==> Restarting service"
systemctl restart transit
sleep 3

CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/health || echo 000)
if [ "$CODE" = "200" ]; then
  echo "==> Deploy OK ($(git rev-parse --short HEAD))"
else
  echo "==> WARN: /health returned $CODE after deploy"
  exit 1
fi

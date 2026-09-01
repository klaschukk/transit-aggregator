#!/bin/bash
# Performance regression gate — runs in nightly cron.
# Measures gzipped transfer size of key pages and fails (exit 1 + Telegram alert)
# if any exceeds its budget. Budgets are set from docs/90_archive/06_tech/perf-baseline.md with +30%
# headroom so normal content growth doesn't page us.
#
# Note: budgets are GZIPPED bytes (what the client actually downloads), not the
# raw HTML size. Nginx+flask-compress compresses all text/html responses.

set -u
BASE_URL="${PERF_CHECK_BASE:-http://127.0.0.1:5000}"
TG_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TG_CHAT="${TELEGRAM_CHAT_ID:-}"

declare -A BUDGETS=(
  # "/" and "/rute/beograd-novi-sad/" raised 2026-09: route-overview map
  # (markup + intent-gated Mapbox init script — the polyline itself is
  # fetched separately via /api/route-geometry, not inlined) and homepage
  # transport-mode chips. Measured live against prevozni.com post-change:
  # 17571 and 24517 gzipped bytes respectively; budget below adds ~5-8%
  # headroom, not a round-number guess. Tried an SVG <symbol>/<use> sprite
  # to shrink the mode-chip icons first — made every page LARGER (gzip
  # already collapses repeated inline SVG almost for free; the sprite's
  # one-time symbol definitions cost more than they saved) — reverted,
  # documented instead of raising blind.
  ["/"]=18500
  ["/rute/"]=70000
  ["/rute/beograd-novi-sad/"]=25500
  ["/voznja/beograd-do-budva/"]=19500
  ["/gradski/beograd/"]=45000
  ["/gradski/beograd/stajaliste/sajam/"]=20000
)

FAILED=()
for path in "${!BUDGETS[@]}"; do
  budget=${BUDGETS[$path]}
  size=$(curl -s --compressed -H 'Accept-Encoding: gzip' "$BASE_URL$path" -o /dev/null -w '%{size_download}')
  if [ -z "$size" ] || [ "$size" -eq 0 ]; then
    echo "ERR  $path — no response"
    FAILED+=("$path: no response")
    continue
  fi
  if [ "$size" -gt "$budget" ]; then
    echo "FAIL $path — $size bytes > budget $budget"
    FAILED+=("$path: $size > $budget")
  else
    echo "OK   $path — $size / $budget"
  fi
done

if [ ${#FAILED[@]} -gt 0 ]; then
  msg="🚨 Prevozni perf regression:\n$(printf '%s\n' "${FAILED[@]}")"
  if [ -n "$TG_TOKEN" ] && [ -n "$TG_CHAT" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
      --data-urlencode "chat_id=${TG_CHAT}" \
      --data-urlencode "text=${msg}" > /dev/null
  fi
  exit 1
fi
exit 0

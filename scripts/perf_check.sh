#!/bin/bash
# Performance regression gate — runs in nightly cron.
# Measures gzipped transfer size of key pages and fails (exit 1 + Telegram alert)
# if any exceeds its budget. Budgets are set from perf-baseline.md with +30%
# headroom so normal content growth doesn't page us.
#
# Note: budgets are GZIPPED bytes (what the client actually downloads), not the
# raw HTML size. Nginx+flask-compress compresses all text/html responses.

set -u
BASE_URL="${PERF_CHECK_BASE:-http://127.0.0.1:5000}"
TG_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TG_CHAT="${TELEGRAM_CHAT_ID:-}"

declare -A BUDGETS=(
  ["/"]=15000
  ["/rute/"]=70000
  ["/rute/beograd-novi-sad/"]=20000
  ["/voznja/beograd-do-budva/"]=18000
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

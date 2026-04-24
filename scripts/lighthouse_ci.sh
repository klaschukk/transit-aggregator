#!/usr/bin/env bash
# lighthouse_ci.sh — mobile Lighthouse CI wrapper.
#
# Runs Lighthouse with mobile preset (Moto G Power / 4G / 4× CPU throttling)
# on a set of canonical pages and extracts headline numbers (perf score, LCP,
# CLS, TBT, total bytes, requests) into one markdown table. Useful for:
#
#   - Local before/after measurements when touching CSS/JS
#   - Nightly cron regression gate (feed into Telegram via sentry_notify.py)
#   - PR diff checks against a committed baseline
#
# Usage:
#   scripts/lighthouse_ci.sh                 # run against localhost:5000
#   BASE_URL=https://prevozni.com scripts/lighthouse_ci.sh
#   OUTDIR=/tmp/lh scripts/lighthouse_ci.sh  # override report dir
#
# Dependencies: lighthouse (npm -g), jq, a running HTTP server at $BASE_URL.

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:5000}"
OUTDIR="${OUTDIR:-docs/06_tech/lh-baseline}"
TOMORROW="$(date -u -d '+1 day' +%Y-%m-%d)"

PATHS=(
  "/"
  "/pretraga/?od=Beograd&do=Novi+Sad&datum=${TOMORROW}"
  "/rute/beograd-novi-sad/"
  "/voznja/beograd-do-budva/"
  "/gradski/beograd/"
  "/gradski/beograd/stajaliste/sajam/"
)

mkdir -p "$OUTDIR"

# One-liner header for the markdown table
printf '| %s | %s | %s | %s | %s | %s | %s |\n' \
  "Page" "Score" "LCP (s)" "CLS" "TBT (ms)" "KB" "Reqs"
printf '| %s | %s | %s | %s | %s | %s | %s |\n' \
  "----" "----:" "------:" "---:" "-------:" "--:" "---:"

for path in "${PATHS[@]}"; do
  # Derive a filesystem-safe slug
  slug=$(printf '%s' "$path" \
    | sed 's:^/::; s:/$::; s:[^A-Za-z0-9]:-:g; s:--*:-:g; s:^-::; s:-$::')
  [ -z "$slug" ] && slug="home"

  jsonfile="$OUTDIR/${slug}.json"

  lighthouse "${BASE_URL}${path}" \
    --form-factor=mobile \
    --screenEmulation.mobile=true \
    --throttling-method=simulate \
    --only-categories=performance \
    --output=json \
    --output-path="$jsonfile" \
    --chrome-flags="--headless=new --no-sandbox --disable-gpu" \
    --quiet >/dev/null 2>&1 || {
      printf '| `%s` | ERR | — | — | — | — | — |\n' "$path"
      continue
    }

  score=$(jq -r '.categories.performance.score * 100 | floor' "$jsonfile")
  lcp=$(jq -r '.audits["largest-contentful-paint"].numericValue / 1000' "$jsonfile" \
        | awk '{printf "%.2f", $1}')
  cls=$(jq -r '.audits["cumulative-layout-shift"].numericValue' "$jsonfile" \
        | awk '{printf "%.3f", $1}')
  tbt=$(jq -r '.audits["total-blocking-time"].numericValue' "$jsonfile" \
        | awk '{printf "%.0f", $1}')
  kb=$(jq -r '.audits["total-byte-weight"].numericValue / 1024' "$jsonfile" \
        | awk '{printf "%.0f", $1}')
  reqs=$(jq -r '[.audits["network-requests"].details.items[]] | length' "$jsonfile")

  printf '| `%s` | **%s** | %s | %s | %s | %s | %s |\n' \
    "$path" "$score" "$lcp" "$cls" "$tbt" "$kb" "$reqs"
done

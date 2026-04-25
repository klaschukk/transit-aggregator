#!/usr/bin/env bash
# ad_perf_check.sh — CWV regression gate for AdSense placement.
#
# Wraps lighthouse_ci.sh: runs the mobile audit twice — once with
# ADSENSE_ID unset (no ads), once with it set (ads load) — and fails
# loudly if LCP increases by more than the LCP_DELTA_BUDGET_MS budget
# (default 500ms). Use as a pre-deploy guard whenever ad-related
# changes hit the page templates.
#
# Outputs a one-line markdown summary to stdout and a side-by-side
# JSON diff to docs/06_tech/lh-ads-diff.json for archival.
#
# Usage:
#   scripts/ad_perf_check.sh
#   LCP_DELTA_BUDGET_MS=750 scripts/ad_perf_check.sh
#   ADSENSE_ID_TEST=ca-pub-1234 scripts/ad_perf_check.sh
#
# Exits 0 on pass, 1 on regression.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUDGET="${LCP_DELTA_BUDGET_MS:-500}"
TEST_PUBID="${ADSENSE_ID_TEST:-${ADSENSE_ID:-}}"
OUTDIR="${OUTDIR:-${REPO_ROOT}/docs/06_tech/lh-ads-diff}"
mkdir -p "$OUTDIR"

if [ -z "$TEST_PUBID" ]; then
  echo "ad_perf_check: ADSENSE_ID / ADSENSE_ID_TEST is empty — nothing to compare." >&2
  echo "Set ADSENSE_ID_TEST=ca-pub-XXXX to exercise the ads-loaded codepath."
  exit 2
fi

if ! command -v lighthouse >/dev/null 2>&1; then
  echo "ad_perf_check: lighthouse not in PATH (npm i -g lighthouse)." >&2
  exit 2
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "ad_perf_check: jq required." >&2
  exit 2
fi

run_lh() {
  # $1 = scenario name (no-ads / with-ads), $2 = ADSENSE_ID value to use,
  # $3 = output JSON path. Spawns its own dev server so the env is clean.
  local name="$1" pubid="$2" out="$3"
  echo "→ ${name}" >&2

  ADSENSE_ID="$pubid" \
    "$REPO_ROOT/venv/bin/python" "$REPO_ROOT/run.py" >"$OUTDIR/server.${name}.log" 2>&1 &
  local pid=$!
  # Wait until the dev server actually answers — better than a flat sleep,
  # which masks slow boots and produces flaky benchmarks.
  for i in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:5000/health >/dev/null 2>&1; then break; fi
    sleep 0.5
  done

  set +e
  lighthouse "http://127.0.0.1:5000/rute/beograd-novi-sad/" \
    --form-factor=mobile \
    --screenEmulation.mobile=true \
    --throttling-method=simulate \
    --only-categories=performance \
    --output=json \
    --output-path="$out" \
    --chrome-flags="--headless=new --no-sandbox --disable-gpu" \
    --quiet >/dev/null 2>&1
  local status=$?
  set -e

  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  return "$status"
}

run_lh "no-ads"   ""           "$OUTDIR/no-ads.json"
run_lh "with-ads" "$TEST_PUBID" "$OUTDIR/with-ads.json"

lcp_no=$(jq -r '.audits["largest-contentful-paint"].numericValue' "$OUTDIR/no-ads.json")
lcp_yes=$(jq -r '.audits["largest-contentful-paint"].numericValue' "$OUTDIR/with-ads.json")
delta=$(awk -v a="$lcp_yes" -v b="$lcp_no" 'BEGIN { printf "%.0f", a - b }')

cls_no=$(jq -r '.audits["cumulative-layout-shift"].numericValue' "$OUTDIR/no-ads.json")
cls_yes=$(jq -r '.audits["cumulative-layout-shift"].numericValue' "$OUTDIR/with-ads.json")

cat <<EOF
| Scenario | LCP (ms) | CLS |
|----------|---------:|----:|
| No ads   | $(printf '%.0f' "$lcp_no") | $(printf '%.3f' "$cls_no") |
| With ads | $(printf '%.0f' "$lcp_yes") | $(printf '%.3f' "$cls_yes") |
| Δ        | ${delta} | $(awk -v a="$cls_yes" -v b="$cls_no" 'BEGIN{printf "%.3f", a-b}') |

Budget: ${BUDGET}ms LCP increase max.
EOF

# Use awk because /bin/sh-style integer math chokes on negative deltas.
if awk -v d="$delta" -v b="$BUDGET" 'BEGIN { exit !(d > b) }'; then
  echo "❌ FAIL: LCP regression ${delta}ms exceeds budget ${BUDGET}ms"
  exit 1
fi
echo "✓ pass: LCP within budget"
exit 0

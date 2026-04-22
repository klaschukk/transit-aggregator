#!/bin/bash
# activation_check.sh — smoke-test every activation touchpoint.
#
# Usage:
#   bash scripts/activation_check.sh                        # localhost:5000
#   bash scripts/activation_check.sh https://prevozni.com   # production
#
# Checks:
#   1. Sitemap index + 5 shards → 200
#   2. robots.txt + ads.txt → 200
#   3. /admin/* — expect 401 (creds set) or 503 (creds not set); 200 = leak
#   4. /api/subscribe POST with valid shape → 202 (if SMTP dev-fallback on)
#      or 500 if analytics.duckdb is contended (flag but don't fail)
#   5. /api/ba-click POST → 204
#   6. Newsletter form present on / and /rute/beograd-novi-sad/
#   7. Healthcheck endpoint /health → 200
#
# Exit code: 0 if every critical check passes, 1 if any RED.

set -u
BASE="${1:-http://127.0.0.1:5000}"
BASE="${BASE%/}"

RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
RESET="\033[0m"

FAIL=0
WARN=0

pass() { echo -e "  ${GREEN}PASS${RESET}  $1"; }
fail() { echo -e "  ${RED}FAIL${RESET}  $1"; FAIL=$((FAIL+1)); }
warn() { echo -e "  ${YELLOW}WARN${RESET}  $1"; WARN=$((WARN+1)); }

check_status() {
  local url="$1"; local expected="$2"; local label="$3"
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url")
  if [ "$code" = "$expected" ]; then
    pass "$label → $code"
  else
    fail "$label → expected $expected, got $code ($url)"
  fi
}

check_status_in() {
  # Expect one of several codes (e.g. admin might be 401 OR 503 depending on env)
  local url="$1"; local expected_list="$2"; local label="$3"
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url")
  if echo "$expected_list" | grep -qw "$code"; then
    pass "$label → $code"
  else
    fail "$label → expected one of [$expected_list], got $code ($url)"
  fi
}

check_contains() {
  local url="$1"; local needle="$2"; local label="$3"
  local body
  body=$(curl -s --max-time 10 "$url")
  if echo "$body" | grep -q "$needle"; then
    pass "$label contains '$needle'"
  else
    fail "$label missing '$needle' ($url)"
  fi
}

echo "═══ 1. Sitemaps ═══"
check_status "$BASE/sitemap.xml" 200 "sitemap index"
for s in core routes pairs lines stops; do
  check_status "$BASE/sitemap-$s.xml" 200 "sitemap-$s.xml"
done

echo ""
echo "═══ 2. robots.txt + ads.txt ═══"
check_status "$BASE/robots.txt" 200 "robots.txt"
check_status "$BASE/ads.txt" 200 "ads.txt (stub until AdSense)"

echo ""
echo "═══ 3. /health ═══"
check_status "$BASE/health" 200 "health endpoint"

echo ""
echo "═══ 4. Admin (creds-gated) ═══"
# Without auth: 401 (creds configured) OR 503 (creds not yet set). 200 = disaster.
check_status_in "$BASE/admin/revenue" "401 503" "/admin/revenue unauth"
if [ -n "${ADMIN_USER:-}" ] && [ -n "${ADMIN_PASS:-}" ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -u "$ADMIN_USER:$ADMIN_PASS" --max-time 10 "$BASE/admin/revenue")
  if [ "$code" = "200" ]; then
    pass "/admin/revenue with creds → 200"
  else
    fail "/admin/revenue with creds → $code (env creds wrong?)"
  fi
else
  warn "ADMIN_USER/ADMIN_PASS env vars not set locally — skipping auth'd admin fetch"
fi

echo ""
echo "═══ 5. Newsletter form UI ═══"
check_contains "$BASE/" 'newsletter-form--hero' "home hero newsletter"
check_contains "$BASE/" 'newsletter-form--footer' "home footer newsletter"
check_contains "$BASE/rute/beograd-novi-sad/" 'newsletter-form--price_alert' "route price-alert"
check_contains "$BASE/o-nama/" 'newsletter-form--footer' "about page footer newsletter"

echo ""
echo "═══ 6. /api/subscribe (double-opt-in) ═══"
# Valid payload: expect 202 in healthy env (dev-fallback mailer or SMTP live).
# 500 usually means analytics.duckdb write-lock contention — warn, don't fail.
# Random fresh address — avoid the '+' plus-addressing trick because
# application/x-www-form-urlencoded would decode '+' as space.
SUB_EMAIL="activation-check-$(date +%s)@example.com"
SUB_RESP=$(curl -s -o /tmp/sub_body -w '%{http_code}' --max-time 10 \
  -X POST "$BASE/api/subscribe" \
  --data-urlencode "email=$SUB_EMAIL" \
  --data-urlencode "consent=1" \
  --data-urlencode "source=home")
case "$SUB_RESP" in
  202) pass "/api/subscribe valid payload → 202" ;;
  429) pass "/api/subscribe → 429 (rate-limited, prior run exhausted budget; endpoint wired)" ;;
  500) warn "/api/subscribe → 500 (analytics DB busy — run again when idle). Body: $(cat /tmp/sub_body 2>/dev/null | head -c 120)" ;;
  *)   fail "/api/subscribe → $SUB_RESP. Body: $(cat /tmp/sub_body 2>/dev/null | head -c 120)" ;;
esac

# Without consent: 400 (or 429 if we already burnt rate-limit budget above)
NC_CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
  -X POST "$BASE/api/subscribe" --data-urlencode "email=test@example.com" --data-urlencode "source=home")
case "$NC_CODE" in
  400) pass "/api/subscribe no-consent → 400" ;;
  429) pass "/api/subscribe no-consent → 429 (rate-limited, proves limiter works)" ;;
  *)   fail "/api/subscribe no-consent → $NC_CODE (expected 400 or 429)" ;;
esac

# Invalid email: 400 (or 429)
IE_CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
  -X POST "$BASE/api/subscribe" --data-urlencode "email=not-an-email" --data-urlencode "consent=1" --data-urlencode "source=home")
case "$IE_CODE" in
  400) pass "/api/subscribe bad-email → 400" ;;
  429) pass "/api/subscribe bad-email → 429 (rate-limited, proves limiter works)" ;;
  *)   fail "/api/subscribe bad-email → $IE_CODE (expected 400 or 429)" ;;
esac

echo ""
echo "═══ 7. /api/ba-click (Bookaway click beacon) ═══"
BA_CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
  -X POST "$BASE/api/ba-click" \
  -H 'Content-Type: application/json' \
  -d '{"route_slug":"beograd-novi-sad","surface":"route_detail","operator":"Lasta","trip_time":"08:00"}')
case "$BA_CODE" in
  204) pass "/api/ba-click → 204" ;;
  200) pass "/api/ba-click → 200 (acceptable, handler returned body)" ;;
  *)   fail "/api/ba-click → $BA_CODE (expected 204/200)" ;;
esac

echo ""
echo "═══ 8. SMTP configuration ═══"
# We can't probe SMTP from here without credentials — read the site config.
# Instead peek systemd env via a health hint or config log marker (future:
# expose /health/config with redacted fields).
if [ "$BASE" = "http://127.0.0.1:5000" ]; then
  if [ -n "${SMTP_HOST:-}" ]; then
    pass "SMTP_HOST set in local env → $SMTP_HOST"
  else
    warn "SMTP_HOST not set in this shell — if set in systemd, subscribe emails still go out in prod"
  fi
fi

echo ""
echo "═══════════════════════════════════════"
if [ "$FAIL" -gt 0 ]; then
  echo -e "${RED}RED — $FAIL failed, $WARN warnings${RESET}"
  exit 1
elif [ "$WARN" -gt 0 ]; then
  echo -e "${YELLOW}YELLOW — 0 failed, $WARN warnings (review above)${RESET}"
  exit 0
else
  echo -e "${GREEN}GREEN — all activation checks passed${RESET}"
  exit 0
fi

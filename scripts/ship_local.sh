#!/bin/bash
# One command for "I changed something — is it live and healthy?" on this box.
#
#   scripts/ship_local.sh          fix ownership, rebuild css/js, pytest, restart, /health
#   scripts/ship_local.sh --fast   same but skip pytest (docs/CSS-only tweaks)
#
# Replaces the 6-8 separate tool calls (chown, minify_css, minify_js, pytest,
# restart, sleep, curl) the CLAUDE.md discipline used to need, and prints ~8
# lines. Exits non-zero at the first failure and does NOT restart if tests fail.
#
# Ownership: Claude sessions run as root, cron + gunicorn as `deploy`. Root-
# created files are unwritable for cron (nightly scrapers and minify_js died
# with PermissionError on 2026-09-19), so this fixes them every run.
set -uo pipefail
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$DIR" || exit 1
source venv/bin/activate

FAST=0; [ "${1:-}" = "--fast" ] && FAST=1
fail() { echo "FAIL: $*"; exit 1; }

# 1. ownership (root only; venv is skipped — it is big and not written by cron)
if [ "$(id -u)" = 0 ]; then
  n=$(find . -not -path "./venv/*" -user root 2>/dev/null | wc -l)
  find . -not -path "./venv/*" -user root -exec chown deploy:deploy {} + 2>/dev/null
  echo "perms: fixed $n root-owned files"
fi

# 2. assets (dist/ is what production serves; a bare restart does not rebuild it)
python scripts/minify_css.py 2>&1 | tail -1 | sed 's/^/css:   /' || fail "minify_css"
out=$(python scripts/minify_js.py 2>&1); echo "$out" | tail -1 | sed 's/^/js:    /'
echo "$out" | grep -q "^ABORT" && fail "minify_js aborted a file (node --check failed)"
# guard against the 2026-09-14 bug: an unterminated /* swallowed a whole block
python - <<'PY' || fail "dist/app.css lost its :root variables"
c = open('app/static/css/dist/app.css', encoding='utf-8').read()
assert '--mode-bus:' in c and '--color-primary:' in c
PY

# 3. tests
if [ "$FAST" = 0 ]; then
  res=$(python -m pytest -q -p no:warnings -x 2>&1 | tail -3)
  echo "tests: $(echo "$res" | tail -1)"
  echo "$res" | grep -qE "failed|error" && { echo "$res"; fail "tests — not restarting"; }
fi

# 4. restart + health
sudo -n systemctl restart prevozni 2>/dev/null || systemctl restart prevozni || fail "restart"
sleep 3
code=$(curl -s -o /dev/null -w "%{http_code}" --unix-socket /run/prevozni/prevozni.sock http://localhost/health)
[ "$code" = "200" ] || fail "health=$code"
echo "health: 200 | $(git log --oneline -1) | uncommitted: $(git status --short | wc -l)"

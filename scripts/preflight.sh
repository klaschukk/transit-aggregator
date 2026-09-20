#!/bin/bash
# One-screen status of prevozni.com — run this FIRST in a session instead of
# 5-6 exploratory tool calls (health, git, ownership, cron result, A/B, clicks).
#   scripts/preflight.sh
set -uo pipefail
DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$DIR" || exit 1
SOCK=/run/prevozni/prevozni.sock

curl -s --unix-socket $SOCK http://localhost/health | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print('health: UNREACHABLE'); sys.exit()
c = d.get('checks', {}); n = c.get('nightly', {}); t = c.get('transit_db', {})
print(f\"health: {d.get('status')} v{d.get('version')} up {round(d.get('uptime_seconds',0)/3600)}h | db {t.get('age_hours')}h old, {t.get('routes')} routes | disk free {c.get('disk_free_pct')}%\")
print(f\"nightly: {n.get('status')} {n.get('age_hours')}h ago | failed: {n.get('failed_scrapers') or 'none'}\")
for w in n.get('warnings', []): print('  warn:', w)
"
own=$(find . -not -path "./venv/*" -user root 2>/dev/null | wc -l)
echo "git: $(git log --oneline -1) | uncommitted: $(git status --short | wc -l) | root-owned files: $own$([ "$own" != 0 ] && echo ' (run scripts/ship_local.sh)')"
sqlite3 data/dbs/analytics.sqlite "SELECT 'buy-clicks 24h: '||COUNT(*)||' ('||COUNT(DISTINCT ip_hash)||' uniq)' FROM ba_clicks WHERE ts >= strftime('%Y-%m-%dT%H:%M:%SZ','now','-1 day')" 2>/dev/null
sqlite3 data/dbs/analytics.sqlite "SELECT 'subscribers pending confirm: '||SUM(confirmed_at IS NULL AND unsubscribed_at IS NULL)||' (no SMTP => never delivered)' FROM subscribers" 2>/dev/null
grep -qE "^SMTP_HOST=.+|^MAILGUN_API_KEY=.+" .env 2>/dev/null && echo "mail: configured" || echo "mail: NOT configured (no SMTP_HOST/MAILGUN_API_KEY)"
[ -f logs/.maintenance ] && echo "!! maintenance flag present: logs/.maintenance"
exit 0

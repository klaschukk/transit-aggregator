#!/bin/bash
# Healthcheck — checks if transit service responds, restarts if not.
# Cron: */5 * * * *

PROJECT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MAINT_FLAG=$PROJECT/logs/.maintenance
LOG=/var/log/transit-healthcheck.log

# Maintenance window: the data pipelines stop the service on purpose to release
# the DuckDB write lock. Without this gate the healthcheck restarted the service
# mid-run, the fresh gunicorn re-took the read lock, and build_db/enrich died
# with "Conflicting lock is held". A stale flag is ignored after MAX_AGE so a
# crashed pipeline can never disable the healthcheck permanently.
MAX_AGE=7200  # 2h — longer than the full nightly pipeline (~30-60 min)

if [ -f "$MAINT_FLAG" ]; then
  flag_ts=$(stat -c %Y "$MAINT_FLAG" 2>/dev/null || echo 0)
  age=$(( $(date +%s) - flag_ts ))
  if [ "$age" -lt "$MAX_AGE" ]; then
    echo "$(date): maintenance in progress (${age}s), skipping" >> "$LOG"
    exit 0
  fi
  echo "$(date): STALE maintenance flag (${age}s > ${MAX_AGE}s), ignoring" >> "$LOG"
fi

STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 \
  --unix-socket /run/prevozni/prevozni.sock http://localhost/health)

if [ "$STATUS" != "200" ]; then
  echo "$(date): Transit DOWN (status=$STATUS), restarting..." >> "$LOG"
  sudo systemctl restart prevozni.service
else
  echo "$(date): OK" >> "$LOG"
fi

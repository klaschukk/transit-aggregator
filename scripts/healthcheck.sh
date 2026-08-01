#!/bin/bash
# Healthcheck — checks if transit service responds, restarts if not
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --unix-socket /run/prevozni/prevozni.sock http://localhost/health)
if [ "$STATUS" != "200" ]; then
  echo "$(date): Transit DOWN (status=$STATUS), restarting..." >> /var/log/transit-healthcheck.log
  sudo systemctl restart prevozni.service
else
  echo "$(date): OK" >> /var/log/transit-healthcheck.log
fi

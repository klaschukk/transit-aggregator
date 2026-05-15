#!/bin/bash
# Healthcheck — checks if transit service responds, restarts if not
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000/health)
if [ "$STATUS" != "200" ]; then
  echo "$(date): Transit DOWN (status=$STATUS), restarting..." >> /var/log/transit-healthcheck.log
  sudo systemctl restart transit.service
else
  echo "$(date): OK" >> /var/log/transit-healthcheck.log
fi

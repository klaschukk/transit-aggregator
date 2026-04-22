# Price alerts — week {YYYY-WW}

_Template for weekly review. Copy to `price-alerts-YYYY-WW.md` on Monday,
fill from `python scripts/price_alert_scan.py --dry-run` + queries against
analytics.duckdb, commit._

## Scoreboard

| Metric | This week | Prev week | Δ |
|---|---|---|---|
| Snapshots taken | | | |
| Routes qualified (≥10% drop vs 7d min) | | | |
| Emails sent (actual deliveries) | | | |
| Emails failed (SMTP errors) | | | |
| Recipients reached (distinct subscribers) | | | |
| Click-throughs (via ba_clicks utm_medium=price-alert) | | | |
| Unsubscribes within 24h of an alert | | | |
| New subscribers (source=price_alert) | | | |

## Top dropping routes this week

| Route | Baseline (RSD) | Today (RSD) | Drop % | Emails sent |
|---|---|---|---|---|
| | | | | |

## Health signals

- Delivery rate (delivered_ok / total sent): **{X%}** — target >95%
- Unsub rate post-alert (unsub 24h / sent): **{Y%}** — alarm if >5%
  (means we're over-mailing or false-positiving). Over 3 consecutive
  weeks >5% → raise `DROP_THRESHOLD` from 0.90 to 0.85.
- Cooldown saves: **{Z}** alerts skipped due to the 7-day cooldown
  (healthy = low double digits; zero = cooldown might be too strict).

## Queries for the above

```sql
-- Snapshots taken this week
SELECT COUNT(*) FROM price_snapshots
WHERE snapshot_ts >= CURRENT_TIMESTAMP - INTERVAL '7 days';

-- Routes qualified + emails sent
SELECT COUNT(DISTINCT route_slug) AS routes,
       COUNT(*)                   AS emails_sent,
       COUNT(*) FILTER (WHERE delivered_ok) AS delivered,
       COUNT(DISTINCT subscriber_id) AS recipients
FROM price_alerts_sent
WHERE sent_at >= CURRENT_TIMESTAMP - INTERVAL '7 days';

-- Unsub post-alert (health signal)
SELECT COUNT(*)
FROM price_alerts_sent pa
JOIN subscribers s ON s.id = pa.subscriber_id
WHERE pa.sent_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
  AND s.unsubscribed_at IS NOT NULL
  AND s.unsubscribed_at > pa.sent_at
  AND s.unsubscribed_at < pa.sent_at + INTERVAL '24 hours';

-- Clicks from price-alert emails (if Bookaway logging is enabled)
SELECT route_slug, COUNT(*) AS clicks
FROM ba_clicks
WHERE referrer LIKE '%utm_medium=price-alert%'
  AND ts >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY route_slug ORDER BY clicks DESC;
```

## Notes / anomalies

- Track anything non-routine here: a route that fired 5 days in a row
  (scraper glitch?), a spike in unsub rate (template problem?), a
  near-zero-send week (scraper failed? subscribers churned?).

## Next week's tuning (fill only if changing thresholds)

- [ ] No changes — keep DROP_THRESHOLD at 0.90, COOLDOWN_DAYS at 7
- [ ] Raise DROP_THRESHOLD to … because …
- [ ] Lower MAX_EMAILS_PER_RUN to … because …

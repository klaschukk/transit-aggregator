# BusTicket4 sales mirror — Setup Guide

Mirror our BusTicket4 **affiliate sales** (affiliate `735` / prevozni.com)
into the local analytics DB so `/admin/revenue` shows real revenue instead
of zeros. Until this is enabled we are **blind** to whether the affiliate
actually credits our referrals (see `project_bt4_attribution_verified`).

The fetcher is [`scripts/bt4_sales_fetch.py`](../../scripts/bt4_sales_fetch.py):
it logs into the BT4 affiliate panel, pulls the daily sales report for the
current and previous month, and upserts it into the `bt4_sales` table
(one row per day: `ymd`, `tickets`, `value`). Designed for an **hourly** cron.

## What you need

- BT4 affiliate panel credentials (the login for <https://busticket4.me/bus>).
  Same account whose report filters `preduzece=735`.
- Shell access to the prod box (`178.105.76.3`) as the `prevozni` user.

## Step 1 — Add credentials to the prod `.env`

The service reads its environment from `/opt/prevozni/.env` (loaded by the
systemd unit). Add, **without quotes**:

```
BT4_PANEL_USER=<panel login>
BT4_PANEL_PASS=<panel password>
# BT4_AFFILIATE_ID defaults to 735 — only set if it ever changes.
```

Never commit credentials. `.env` is gitignored and lives only on the box.

## Step 2 — Test it once by hand

Run the fetcher manually first so you see the result before wiring cron.
Point `ANALYTICS_DB_PATH` at the **live** analytics DB that the web app
reads (current layout: `/var/lib/prevozni/analytics.sqlite`):

```bash
cd /opt/prevozni
set -a; . ./.env; set +a            # load BT4_PANEL_USER / _PASS
ANALYTICS_DB_PATH=/var/lib/prevozni/analytics.sqlite \
  venv/bin/python scripts/bt4_sales_fetch.py
```

Expected log: `bt4_sales: upserted N day-rows, M tickets total ...`.
Then open `/admin/revenue` — the "BusTicket4 — sales" block should show the
numbers. Zero sales is a valid result (empty report → 0 rows, exit 0).

### Exit codes

| Code | Meaning | Cron action |
|------|---------|-------------|
| `0`  | Success — rows upserted (possibly zero). | nothing |
| `2`  | `BT4_PANEL_USER` / `BT4_PANEL_PASS` not set — safe skip. | check `.env` |
| `3`  | Login / fetch / parse failed after retries. | check logs, panel reachable |

Transient network blips and 5xx responses are retried with exponential
backoff (3 attempts) before exit 3 — a single flaky moment won't lose a run.

## Step 3 — Schedule the hourly cron

As the `prevozni` user (`crontab -e`):

```cron
# BusTicket4 affiliate sales mirror — top of every hour
0 * * * * cd /opt/prevozni && set -a && . ./.env && set +a && ANALYTICS_DB_PATH=/var/lib/prevozni/analytics.sqlite venv/bin/python scripts/bt4_sales_fetch.py >> /var/log/prevozni/bt4_sales.log 2>&1
```

**Hourly, not more often.** Sales change rarely and the script logs into
their panel each run; 24 logins/day is plenty, every-5-min (288/day) risks
their server flagging the account.

Make sure the log dir exists and is writable by `prevozni`:
`mkdir -p /var/log/prevozni`.

## Troubleshooting

- **`/admin/revenue` still shows zeros after a successful run** — confirm the
  cron's `ANALYTICS_DB_PATH` is the *same* file the web app reads. If they
  differ, the data lands in the wrong DB.
- **Exit 3 / "login failed"** — the panel HTML or login flow changed. The
  login/report endpoints are reverse-engineered (documented at the top of
  the script); re-check them against the live panel.
- **Exit 3 / parse error** — the report JSON shape changed. The parser
  expects 3 series (`Dani`, `Broj karata`, `Vrijednost`); see
  `_fetch_month` / `_to_ymd` and the unit tests in
  `tests/test_bt4_sales_fetch.py`.

## Related

- `project_bt4_attribution_verified` — why this matters (we're blind to sales).
- `project_busticket4_affiliate` — the affiliate setup (id 735, 2% commission).
- `docs/06_tech/gsc-setup.md` — same one-time-creds-then-cron pattern.

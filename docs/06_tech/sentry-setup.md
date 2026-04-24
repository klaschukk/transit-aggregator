# Sentry — Setup Guide

Error tracking + light performance profiling for prevozni.com. Free tier
(5K events/mo, 10K perf units/mo) is enough if we keep the beforesend
filter tight — see §6.

## Why

Before Sentry we only learned about 5xx when a user complained (e.g. the
service-worker blank-page incident — a week lost). Sentry catches
unhandled exceptions in Flask, DuckDB query errors, SMTP send failures,
and nightly-refresh build_db failures in real time. It is NOT a
replacement for /health or Umami — it's specifically the "something
broke" channel.

Related plumbing in the repo:

- `app/observability.py` — the thin wrapper every caller goes through.
  No-op when `SENTRY_DSN` is empty, so dev/tests don't phone home.
- `app/__init__.py` — `observability.init_sentry()` runs inside
  `create_app()`.
- `scripts/sentry_notify.py` — fire-and-forget CLI shim used by
  `nightly_refresh.sh` for cron-side failures.
- `/health` — exposes `status`, `checks`, `uptime_seconds`, `version`.
  Good for uptime monitors; not replaced by Sentry.

## Prereqs

- GitHub / Google / email for Sentry signup.
- Access to `/etc/systemd/system/transit.service` on the production box
  (you'll add the DSN as an env var).

## Step 1 — Signup

1. Open <https://sentry.io/signup/>.
2. Create an account (free Developer plan — 5K errors/mo, 10K perf
   units/mo, 1 user).
3. When prompted for a platform, pick **Flask**. Sentry may generate a
   starter snippet — ignore it, we've already wired the SDK.

## Step 2 — Create the project

1. **Projects → Create Project**.
2. Platform: `Python / Flask`.
3. Project name: `prevozni-flask`.
4. Alert frequency: "Alert me on every new issue" for the first two
   weeks (you want to see what's noisy). Tune down after.
5. Team: default.

## Step 3 — Grab the DSN

After the project is created Sentry shows the DSN on the
**Settings → Projects → prevozni-flask → Client Keys (DSN)** page. It
looks like:

```
https://abc123def456@o7654321.ingest.sentry.io/1234567
```

Keep the DSN secret-ish — it's not a password (you can't read events
with it), but it lets anyone send events into our quota.

## Step 4 — Wire it into systemd

Edit `/etc/systemd/system/transit.service` (on the prod box, as root):

```ini
[Service]
# ...existing Environment= lines...
Environment=SENTRY_DSN=https://abc123def456@o7654321.ingest.sentry.io/1234567
Environment=SENTRY_ENV=production
# Optional — defaults to 0.1 (10% perf trace sampling):
# Environment=SENTRY_TRACES_SAMPLE_RATE=0.1
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart transit
```

The nightly cron inherits env from the shell that runs it, so if you
want `scripts/nightly_refresh.sh` to also phone home on failure, add
the same `SENTRY_DSN` / `SENTRY_ENV` to the user's crontab environment:

```crontab
SENTRY_DSN=https://abc123def456@o7654321.ingest.sentry.io/1234567
SENTRY_ENV=production
0 2 * * * /home/klaschuk/transit/scripts/nightly_refresh.sh
```

Without the DSN the nightly script still runs; `sentry_notify.py` just
exits 0.

## Step 5 — Install the SDK

```bash
cd /home/klaschuk/transit
venv/bin/pip install -r requirements.txt
sudo systemctl restart transit
```

`sentry-sdk[flask]==2.17.0` is pinned in `requirements.txt`.

## Step 6 — Verify

### 6a. Trigger a test event

```bash
# From the prod box, with SENTRY_DSN exported:
venv/bin/python scripts/sentry_notify.py "sentry smoke test" info \
    subsystem=smoke
```

Within ~30 seconds you should see the event in **Sentry → Issues**.
Tag filter: `subsystem:smoke`.

### 6b. Trigger a Flask-side event

Hit `/health` first to confirm the app boots with SENTRY_DSN set — the
systemd journal should show `Sentry initialised (env=production
release=<sha> traces=0.10)`.

To confirm Flask integration is wired, temporarily add a
`raise RuntimeError('sentry verify')` to any debug route, hit it, and
check Sentry. Remove immediately.

### 6c. Confirm /health returns structured payload

```bash
curl -s https://prevozni.com/health | jq .
```

Expected shape:

```json
{
  "status": "ok",
  "service": "prevozni",
  "version": "8345547",
  "uptime_seconds": 82800,
  "checks": {
    "transit_db": {"ok": true, "age_hours": 8.2, "routes": 517},
    "analytics_db": {"ok": true, "clicks_total": 1234},
    "logs_writable": true,
    "disk_free_pct": 62.1,
    "nightly": {
      "last_run": "2026-04-24T02:47:12Z",
      "status": "ok",
      "age_hours": 10.1
    }
  }
}
```

`status` transitions:

- `ok` (HTTP 200) — all checks green.
- `degraded` (HTTP 200) — transit_db age > 36h, analytics_db writes
  failing, disk <10% free, or nightly hasn't run in 30h. Does NOT 503
  — degraded shouldn't page.
- `down` (HTTP 503) — transit_db unreadable or logs dir not writable.
  This is what Cloudflare / uptime monitors should alert on.

## Step 7 — What NOT to filter aggressively

The default `before_send` hook in `app/observability.py` drops:

1. 429 rate-limit events (`RateLimitExceeded`) — expected abuse-control
   behaviour, not a server error.
2. Bot-triggered errors (User-Agent matches
   `bot|crawler|spider|slurp|bingpreview|facebookexternalhit|pingdom|uptimerobot|...`).

4xx errors are NOT captured by `FlaskIntegration` — Sentry only picks up
unhandled exceptions, and 404/410 handlers return cleanly. So the
"ignore 4xx" requirement is automatic; we don't need a rule.

Don't extend the ignore list without discussing first — each silenced
class is a future incident we won't find out about.

## Step 8 — Budget watch

5K events/mo ÷ 30 = ~166 events/day. If the error rate blows through
that:

1. **Sentry → Stats → Issues** shows the noisiest issues. Fix them in
   code, don't filter them.
2. Spiky bot that slipped through the UA regex? Add to
   `_BOT_UA_RE` in `app/observability.py`.
3. Known transient (e.g. "DB locked during nightly restart")? Add a
   fragment to `_IGNORED_MESSAGE_FRAGMENTS`.

Monitor the quota bar at **Settings → Subscription**. Sentry sends an
email at 90% and events are dropped at 100% — they don't bill
overage on the free tier, but you lose visibility.

## Step 9 — Release tagging

`release=_ASSET_VERSION` means events are tagged with the short git
SHA at the time the gunicorn worker booted. To attribute an incident
to a specific deploy, filter by the `release` tag in Sentry. No source
map upload is needed — server-side Python stacks resolve locally.

Rolling deploys (`sudo systemctl restart transit`) pick up a new SHA
automatically because `_ASSET_VERSION` is computed at import time.

## Rollback

If Sentry causes issues (perf regression, quota blow-through,
unexpected request-data leak):

1. `Environment=SENTRY_DSN=` (empty) in the systemd unit.
2. `sudo systemctl daemon-reload && sudo systemctl restart transit`.

The SDK `init()` is skipped entirely with an empty DSN — zero overhead
on every request, zero network calls.

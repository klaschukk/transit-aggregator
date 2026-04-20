# Google Search Console API — Setup Guide

One-time setup so `scripts/weekly_seo.sh` can pull organic-search data
from GSC for `prevozni.com` and generate the weekly digest.

## Prereqs

- GSC property `prevozni.com` exists and you are an **Owner**
  (Settings → Users and permissions).
- Google Cloud Console access with project creation rights.

## Step 1 — Create a GCP project

1. Open <https://console.cloud.google.com/>.
2. Top bar → project selector → **New Project**.
   - Name: `prevozni-seo`
   - Organization / billing: any (the GSC API is free).
3. Note the project ID (e.g. `prevozni-seo-424242`).

## Step 2 — Enable the Search Console API

1. In the GCP project, open
   <https://console.cloud.google.com/apis/library/searchconsole.googleapis.com>.
2. Click **Enable**.

## Step 3 — Create a service account

1. <https://console.cloud.google.com/iam-admin/serviceaccounts>
2. **Create service account**:
   - Name: `gsc-digest-bot`
   - Role: _(leave empty — GSC uses its own permission model,
     IAM roles don't apply)_
3. After creation, open the service account → **Keys** tab →
   **Add Key → Create new key → JSON**.
4. A JSON file downloads. Treat it like a password.

## Step 4 — Install the credentials on the server

```bash
# On the server (81.28.248.71):
scp gsc-digest-bot-*.json klaschuk@server:/home/klaschuk/.gsc-credentials.json
ssh klaschuk@server 'chmod 600 /home/klaschuk/.gsc-credentials.json'
```

Never commit this file. `.gitignore` already excludes it by name pattern.

## Step 5 — Grant the service account access in GSC

1. Open the service account JSON and copy the `client_email` field
   (looks like `gsc-digest-bot@prevozni-seo-424242.iam.gserviceaccount.com`).
2. In GSC → Settings → **Users and permissions** → **Add user**.
3. Paste the `client_email`, set permission to **Full** (Owner-equivalent
   for API access).

> If you skip this step, the fetcher returns `403 User does not have
> sufficient permission for site`.

## Step 6 — Verify

```bash
cd /home/klaschuk/transit
source venv/bin/activate
pip install -r requirements.txt
GSC_CREDENTIALS_PATH=/home/klaschuk/.gsc-credentials.json \
  python scripts/gsc_fetch.py --as-of $(date -u +%Y-%m-%d)
ls data/gsc/          # expect one YYYY-MM-DD.json file
python scripts/gsc_digest.py --as-of $(date -u +%Y-%m-%d)
ls docs/00_strategy/  # expect weekly-seo-YYYY-MM-DD.md
```

## Step 7 — Cron

```cron
# Sundays 08:00 UTC
0 8 * * 0 /home/klaschuk/transit/scripts/weekly_seo.sh
```

The script is idempotent; re-running on the same day overwrites the
snapshot and the digest file.

## Env vars

| Var | Default | Purpose |
|-----|---------|---------|
| `GSC_CREDENTIALS_PATH` | `/home/klaschuk/.gsc-credentials.json` | service account JSON |
| `GSC_SITE_URL` | `sc-domain:prevozni.com` | GSC property identifier |
| `TELEGRAM_BOT_TOKEN` | _(unset)_ | reused from contact form; if set, weekly summary is pushed |
| `TELEGRAM_CHAT_ID` | _(unset)_ | see above |

## Property type gotcha

`GSC_SITE_URL` prefix depends on how the property was verified in GSC:

- **Domain property** (verified by DNS TXT): `sc-domain:prevozni.com`
- **URL-prefix property** (verified by file / meta tag):
  `https://prevozni.com/` — trailing slash matters.

The default assumes a domain property. Update the env var if yours
differs, otherwise you get `404 Not Found`.

## Troubleshooting

| Error | Fix |
|-------|-----|
| `FileNotFoundError: .gsc-credentials.json` | Step 4 wasn't done. |
| `403 ... sufficient permission for site` | Step 5 wasn't done, or `GSC_SITE_URL` mismatch. |
| `404 Not Found` | Wrong `GSC_SITE_URL` prefix (see above). |
| Empty JSON / zero rows | GSC has a ~2-day data lag; if the site is brand-new with no traffic, that's expected. |
| `quota exceeded` | Built-in retry with backoff handles transient 429s; persistent failures mean we exceeded the per-minute quota — lower cron frequency. |

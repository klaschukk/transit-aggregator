# AdSense launch checklist (15-minute runbook)

> Run this top-to-bottom the day AdSense approval lands. Every step is
> a hard gate — don't skip the verification line under each one.

## 0 · Pre-conditions (verify before starting)

- [ ] AdSense application status = **Approved** in
      <https://www.google.com/adsense/>
- [ ] `ADSENSE_PUB_ID` from approval email captured (`pub-1234567890`)
- [ ] You have ssh access to the prod box (`81.28.248.71`)
- [ ] You have systemd unit edit rights (`sudo systemctl edit transit.service`)

## 1 · Set the publisher ID + bootstrap (3 min)

In the systemd unit:

```ini
Environment=ADSENSE_ID=ca-pub-1234567890
Environment=ADSENSE_PUB_ID=pub-1234567890
```

Reload + verify:

```bash
sudo systemctl daemon-reload
sudo systemctl restart transit
curl -s https://prevozni.com/ads.txt
# expect: google.com, pub-1234567890, DIRECT, f08c47fec0942fa0
```

In AdSense console: **Sites** → confirm `prevozni.com` shows as
"Ready". This may take 24h — start the rest of the checklist now,
ad units can be created before site verification finishes.

## 2 · Create per-slot ad units in AdSense console (5 min)

Sidebar → **Ads** → **By ad unit** → **Display ads** → for each entry
in the table below, click _Create new ad unit_, paste the suggested
name verbatim, copy the slot ID, paste into the env var.

| Slot key | Suggested name | Format | Env var |
|---|---|---|---|
| `home_top` | Home — top leaderboard | Horizontal | `ADSENSE_SLOT_HOME_TOP` |
| `home_mid` | Home — mid large rect | Square | `ADSENSE_SLOT_HOME_MID` |
| `route_bottom` | Route detail — bottom | Horizontal | `ADSENSE_SLOT_ROUTE_BOTTOM` |
| `city_pair_bottom` | City pair — bottom | Horizontal | `ADSENSE_SLOT_CITY_PAIR_BOTTOM` |
| `city_transport_mid` | City transport — mid | Horizontal | `ADSENSE_SLOT_CITY_TRANSPORT_MID` |
| `catalog_in_feed` | Catalog — bottom | Horizontal | `ADSENSE_SLOT_CATALOG_IN_FEED` |
| `guide_sidebar` | Guide sidebar | Vertical | `ADSENSE_SLOT_GUIDE_SIDEBAR` |
| `mobile_anchor` | Mobile anchor | Anchor (in-page) | `ADSENSE_SLOT_MOBILE_ANCHOR` |

Add to systemd unit:

```ini
Environment=ADSENSE_SLOT_HOME_TOP=1234567890
Environment=ADSENSE_SLOT_ROUTE_BOTTOM=2345678901
Environment=ADSENSE_SLOT_MOBILE_ANCHOR=3456789012
# (start with these three only — see strategy.md "Iteration plan")
```

## 3 · Verify on staging or single page (3 min)

```bash
sudo systemctl daemon-reload && sudo systemctl restart transit

# 1. Fetch a route page with an empty cookie jar — should NOT load
#    adsbygoogle.js (no consent yet) and should render the house ad.
curl -s https://prevozni.com/rute/beograd-novi-sad/ | grep -c 'house-ad'
# expect: ≥1

# 2. Fetch with consent=all — script tag is dynamic, can only verify
#    visually. Open in a real browser, accept the cookie banner, hit
#    F12 → Network → reload, confirm pagead2.googlesyndication.com
#    served and the <ins> filled.
```

## 4 · Wait for first impression (24h)

AdSense takes up to 24h after the first ad-unit creation to begin
serving. If after 24h the slots still show blank in DevTools, recheck:

1. AdSense console → **Sites** → `prevozni.com` row says "Ready", not
   "Requires attention".
2. `ads.txt` is fetchable: `curl -I https://prevozni.com/ads.txt`
   returns 200 with `Content-Type: text/plain`.
3. No `data-ad-status="unfilled"` on `<ins>` (browser DevTools).

## 5 · Confirm CWV is intact (2 min)

```bash
ADSENSE_ID_TEST=ca-pub-1234567890 scripts/ad_perf_check.sh
# expect: ✓ pass: LCP within budget
# fail = roll back ad slots (clear ADSENSE_ID_* env) until you find
# the offending slot
```

## 6 · Wire AdSense reporting to dashboard (1 min)

Add to systemd timer / cron:

```cron
0 3 * * * /home/klaschuk/transit/venv/bin/python \
          /home/klaschuk/transit/scripts/adsense_fetch.py
```

Set `ADSENSE_CREDENTIALS_PATH` (service account JSON, mode `0600`)
OR `ADSENSE_API_KEY`. Both `ADSENSE_ACCOUNT_ID` is required either way.

Without credentials the script writes zero-impression placeholder rows
to `logs/adsense_fetch.log` so the cron run is observable; the
dashboard at `/admin/revenue` shows "No AdSense data yet" gracefully.

## 7 · Day-7 review (1 min, scheduled)

```bash
# Check 7-day RPM by slot — kill any below $0.50:
curl -s -u "${ADMIN_USER}:${ADMIN_PASS}" https://prevozni.com/admin/revenue \
  | grep -A2 'AdSense'
```

If a slot is below threshold, unset its `ADSENSE_SLOT_*` env var
(don't delete the AdSense console unit — Google's auto-optimisation
works better when slots stay registered even if dormant).

## 8 · Roll out remaining slots

Per `adsense-strategy.md` "Iteration plan":

- Day 8–21: enable `home_mid`, `city_pair_bottom`, `city_transport_mid`
- Day 22+: enable `catalog_in_feed`, `guide_sidebar`
- Month 2: turn on Auto-Ads for `/rute/`, `/prevoznici/` index pages

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Slot blank in DevTools, no `<ins>` rendered | Cookie consent ≠ `all`/`essential` | Accept the banner, reload |
| `<ins>` has `data-ad-status="unfilled"` | No fill from Google network for this geo/category | Wait 24–48h; AdSense's auction needs to learn |
| `/ads.txt` returns the placeholder comment | `ADSENSE_PUB_ID` env unset or transit.service didn't reload | `systemctl status transit` → check Environment lines |
| AdSense console shows "Requires attention" → "ads.txt not found" | Cloudflare cache stale | Cloudflare dashboard → Caching → Purge `ads.txt` |
| Mobile anchor never shows | Cookie `ads_anchor_dismissed=1` (you tested dismiss earlier) | DevTools → Application → Cookies → delete |
| `ad_perf_check.sh` fails LCP budget | Top-of-fold ad too aggressive | Switch `home_top` from `leaderboard` to `responsive` |
| `adsense_fetch.py` exits 2 daily | Credentials missing or invalid | Check `logs/adsense_fetch.log` for the auth error |

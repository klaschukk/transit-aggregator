# Deploy Guide — Prevozni

## Current Setup

| Component | Value |
|-----------|-------|
| Server | 81.28.248.71 (Montiko, Podgorica) |
| App | Flask + Gunicorn (4 workers) |
| DB | DuckDB (file-based, read-only at runtime) |
| Service | systemd `transit.service` |
| Port | 5000 (proxied via nginx) |

## 1. Domain Setup

### DNS Records

```
A     prevozni.com      → 81.28.248.71
A     www.prevozni.com  → 81.28.248.71
```

Wait for propagation (check with `dig prevozni.com`).

### nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/transit
```

```nginx
server {
    listen 80;
    server_name prevozni.com www.prevozni.com;

    # Redirect www → non-www
    if ($host = www.prevozni.com) {
        return 301 https://prevozni.com$request_uri;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/klaschuk/transit/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/transit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 2. SSL Certificate

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d prevozni.com -d www.prevozni.com
```

Certbot auto-renews via systemd timer. Verify:
```bash
sudo certbot renew --dry-run
```

## 3. Update Application Config

Edit systemd service to set production environment:

```bash
sudo nano /etc/systemd/system/transit.service
```

Add/update the `Environment` lines:

```ini
[Service]
Environment=FLASK_ENV=production
Environment=BASE_URL=https://prevozni.com
Environment=SECRET_KEY=<generate-a-random-key>
Environment=GA_TRACKING_ID=G-XXXXXXXXXX
Environment=ADSENSE_ID=ca-pub-XXXXXXXXXX
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart transit
```

### Verify

```bash
curl -s https://prevozni.com/health
curl -s https://prevozni.com/sitemap.xml | head -5
curl -s https://prevozni.com/robots.txt
```

## 4. Google Analytics

1. Go to https://analytics.google.com
2. Create property for `prevozni.com`
3. Get Measurement ID (format: `G-XXXXXXXXXX`)
4. Set `GA_TRACKING_ID=G-XXXXXXXXXX` in systemd Environment
5. Restart: `sudo systemctl restart transit`
6. Verify: view source of homepage should contain `gtag.js`

GA code in `base.html` is conditional — only loads when `GA_TRACKING_ID` is set.

## 5. Google Search Console

1. Go to https://search.google.com/search-console/
2. Add property: `https://prevozni.com`
3. Verify ownership via DNS TXT record:
   ```
   TXT  prevozni.com  "google-site-verification=XXXX"
   ```
4. Submit sitemap: `https://prevozni.com/sitemap.xml`
5. Request indexing for homepage
6. Monitor Coverage report — fix any errors within 48h

## 6. Google AdSense

**Prerequisites** (apply after 2-4 weeks of indexed content):
- 2500+ indexed pages
- Original content on every page
- Privacy policy page (add to /o-nama/ or create separate)
- No thin/empty pages in index

**Steps:**
1. Apply at https://adsense.google.com
2. Get Publisher ID (format: `ca-pub-XXXXXXXXXX`)
3. Set `ADSENSE_ID=ca-pub-XXXXXXXXXX` in systemd Environment
4. Restart: `sudo systemctl restart transit`
5. AdSense JS loads automatically via `base.html`
6. Configure ad units in AdSense dashboard

**Recommended ad placements** (add manually later):
- After search results header
- Between trip card groups
- Sidebar on desktop (filter panel area)
- Before footer on content pages

## 7. Data Pipeline

### Nightly Refresh (cron 2:00 AM)

```
scripts/nightly_refresh.sh
├── scrape_gsp.py        — Belgrade city transit (bgprevoz API)
├── scrape_intercity.py  — Intercity buses (busticket4.me + polazak.rs)
├── scrape_srbvoz.py     — Trains (srbijavoz.rs)
├── scrape_lasta.py      — Lasta bus operator
├── scrape_gspns.py      — Novi Sad city transit (gspns.co.rs)
├── scrape_naissus.py    — Niš city transit
├── build_db.py          — Rebuild transit.duckdb from raw data
└── enrich_stops_coords.py — Geocode 50 stops/night (Overpass + Nominatim)
```

### Crontab

```
0 2 * * *   /home/klaschuk/transit/scripts/nightly_refresh.sh
*/5 * * * * /home/klaschuk/transit/scripts/healthcheck.sh
```

### Manual Commands

```bash
# Full refresh
sudo bash scripts/nightly_refresh.sh

# Single scraper
venv/bin/python3 -u data/pipelines/scrape_gsp.py

# Rebuild DB (stop service first)
sudo systemctl stop transit
venv/bin/python3 -u data/pipelines/build_db.py
sudo systemctl start transit

# Last refresh status
cat logs/last_refresh.txt
```

## 8. Monitoring

| What | How | Frequency |
|------|-----|-----------|
| Service health | `scripts/healthcheck.sh` | cron */5 min |
| Data refresh | `scripts/nightly_refresh.sh` | cron 2:00 AM |
| Access logs | `logs/access.log` | continuous |
| Error logs | `logs/error.log` | continuous |
| Refresh logs | `logs/nightly_YYYYMMDD.log` | daily |
| Google Analytics | analytics.google.com | real-time |
| Search Console | search.google.com/search-console | weekly |
| Core Web Vitals | PageSpeed Insights | monthly |

## 9. Troubleshooting

```bash
# Service won't start
sudo journalctl -u transit -n 50

# DB locked error
fuser data/dbs/transit.duckdb
sudo systemctl stop transit  # release lock

# High memory
sudo systemctl restart transit

# Check gunicorn workers
ps aux | grep gunicorn

# Check nginx errors
sudo tail -50 /var/log/nginx/error.log

# SSL certificate issues
sudo certbot certificates
sudo certbot renew --dry-run
```

## 10. Post-Launch Checklist

- [ ] Domain resolves correctly
- [ ] HTTPS works (no mixed content)
- [ ] HTTP redirects to HTTPS
- [ ] www redirects to non-www
- [ ] `config.py` BASE_URL updated to domain
- [ ] sitemap.xml shows domain URLs
- [ ] robots.txt shows domain sitemap
- [ ] Google Search Console property verified
- [ ] Sitemap submitted to GSC
- [ ] Google Analytics tracking live
- [ ] Healthcheck cron active
- [ ] Nightly refresh cron active
- [ ] All 11 page types return 200

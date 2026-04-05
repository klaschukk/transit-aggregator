# Deploy Guide — Transit Serbia

## Current Setup

| Component | Value |
|-----------|-------|
| Server | 81.28.248.71 (Montiko, Podgorica) |
| App | Flask + Gunicorn (4 workers) |
| DB | DuckDB (file-based, read-only at runtime) |
| Service | systemd `transit.service` |
| Port | 5000 |

## Prerequisites for Domain Launch

- [ ] Domain registered (e.g. `transit-serbia.com`)
- [ ] DNS A record: `transit-serbia.com` → `81.28.248.71`
- [ ] DNS A record: `www.transit-serbia.com` → `81.28.248.71`
- [ ] nginx installed: `sudo apt install nginx`

## nginx Configuration

```nginx
server {
    listen 80;
    server_name transit-serbia.com www.transit-serbia.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/klaschuk/transit/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/transit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL (after DNS propagation)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d transit-serbia.com -d www.transit-serbia.com
```

Certbot auto-renews via systemd timer. Verify:
```bash
sudo certbot renew --dry-run
```

## Post-Domain Checklist

- [ ] Update `config.py` — change `BASE_URL` from IP to `https://transit-serbia.com`
- [ ] Restart service: `sudo systemctl restart transit`
- [ ] Verify sitemap: `curl https://transit-serbia.com/sitemap.xml | head`
- [ ] Verify robots.txt: `curl https://transit-serbia.com/robots.txt`

## Google Search Console

1. Go to https://search.google.com/search-console/
2. Add property: `https://transit-serbia.com`
3. Verify via DNS TXT record (recommended) or HTML file
4. Submit sitemap: `https://transit-serbia.com/sitemap.xml`
5. Request indexing for homepage
6. Monitor Coverage report for errors

## Google AdSense (after 2-4 weeks of indexing)

1. Apply at https://adsense.google.com
2. Site must have: original content, privacy policy, sufficient pages
3. Once approved, add ad code to `base.html` (before `</head>`)
4. Recommended placements: between trip cards, after search results, sidebar

## Data Pipeline

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
└── enrich_stops_coords.py — Geocode 50 stops (Overpass + Nominatim)
```

### Manual Commands

```bash
# Run full refresh manually
sudo bash scripts/nightly_refresh.sh

# Run single scraper
venv/bin/python3 -u data/pipelines/scrape_gsp.py

# Rebuild DB only (stop service first!)
sudo systemctl stop transit
venv/bin/python3 -u data/pipelines/build_db.py
sudo systemctl start transit

# Check last refresh status
cat logs/last_refresh.txt
```

## Monitoring

| What | How | Frequency |
|------|-----|-----------|
| Service health | `scripts/healthcheck.sh` | cron */5 min |
| Data refresh | `scripts/nightly_refresh.sh` | cron 2:00 AM |
| Access logs | `logs/access.log` | continuous |
| Error logs | `logs/error.log` | continuous |
| Refresh logs | `logs/nightly_YYYYMMDD.log` | daily |
| Last status | `logs/last_refresh.txt` | after each refresh |

## Troubleshooting

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
```

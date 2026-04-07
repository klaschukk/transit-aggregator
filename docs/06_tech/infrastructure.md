# Инфраструктура

## Сервер

| Параметр | Значение |
|----------|----------|
| Домен | prevozni.com |
| IP | 81.28.248.71 |
| Хост | montiko (Подгорица) |
| OS | Linux 6.8.0 |
| RAM | 32 GB |
| Disk | 157 GB |

## Стек деплоя

```
Client (browser)
    ↓
Cloudflare (DNS, CDN, SSL, WAF)
    ↓
nginx (reverse proxy, static files, security headers)
    ↓
Gunicorn (2 workers, port 5000, localhost only)
    ↓
Flask app (run.py)
    ↓
DuckDB (read-only, file-based)
```

## nginx

```nginx
# /etc/nginx/conf.d/transit.conf
server {
    listen 80;
    server_name prevozni.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 256;

    # Static files (nginx serves directly, 7d cache)
    location /static/ {
        alias /home/klaschuk/transit/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        # Cloudflare-only access
        allow 103.21.244.0/22;
        allow 103.22.200.0/22;
        # ... (full Cloudflare IP list)
        allow 127.0.0.1;
        deny all;

        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30;
    }
}
```

## Cloudflare

- **DNS:** A record → 81.28.248.71 (proxied)
- **SSL:** Full mode (Cloudflare terminates SSL)
- **Cache:** Standard (static assets)
- **WAF:** Managed rules enabled

## systemd service

```ini
# /etc/systemd/system/transit.service
[Service]
User=klaschuk
WorkingDirectory=/home/klaschuk/transit
Environment=PATH=/home/klaschuk/transit/venv/bin
Environment=FLASK_ENV=production
Environment=BASE_URL=https://prevozni.com
ExecStart=gunicorn -w 2 --max-requests 500 --max-requests-jitter 50 --timeout 30
  -b 127.0.0.1:5000
  --access-logfile logs/access.log
  --error-logfile logs/error.log
  run:app
Restart=always
RestartSec=5
```

## Мониторинг

| Что | Как | Когда |
|-----|-----|-------|
| Healthcheck | scripts/healthcheck.sh | cron */5 min |
| Auto-restart | systemd Restart=always | при падении |
| Enrich coords | scripts/run_enrich_night.sh | cron 3:00 AM |
| Access log | logs/access.log | каждый запрос |
| Error log | logs/error.log | ошибки gunicorn |
| Analytics | Umami | real-time |

## Обновление данных

```bash
# Full pipeline
sudo systemctl stop transit

python3 -u data/pipelines/scrape_gsp.py          # Belgrade GSP
python3 -u data/pipelines/scrape_gspns.py         # Novi Sad JGSP
python3 -u data/pipelines/scrape_intercity.py     # busticket4.me (48 cities)
python3 -u data/pipelines/scrape_srbvoz.py        # Srbija Voz trains
python3 -u data/pipelines/scrape_lasta.py         # polazak.rs (302 routes)
python3 -u data/pipelines/build_db.py             # Build DuckDB
python3 -u data/pipelines/enrich_stops_coords.py enrich --limit 500

sudo systemctl start transit
```

## Производительность

| Страница | Req/sec | p95 (ms) |
|----------|---------|----------|
| `/` (главная) | 1,007 | 21 |
| `/rute/` (335 маршрутов) | 122 | 96 |
| `/gradski/beograd/` (514 линий) | 151 | 80 |
| `/rute/beograd-novi-sad/` | 153 | 66 |
| `/gradski/beograd/stajaliste/sajam/` | 113 | 143 |

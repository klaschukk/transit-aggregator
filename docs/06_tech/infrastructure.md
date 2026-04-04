# Инфраструктура

## Сервер

| Параметр | Значение |
|----------|----------|
| IP | 81.28.248.71 |
| Хост | montiko (Подгорица) |
| OS | Linux 6.8.0 |
| RAM | 32 GB |
| Disk | 157 GB (54% used) |

## Стек деплоя

```
Flask app (run.py)
    ↓
Gunicorn (4 workers, port 5000)
    ↓
systemd (transit.service, auto-restart)
    ↓
[TODO: nginx reverse proxy + SSL]
    ↓
[TODO: Cloudflare CDN + WAF]
```

## systemd service

```ini
# /etc/systemd/system/transit.service
[Service]
User=klaschuk
WorkingDirectory=/home/klaschuk/transit
Environment=PATH=/home/klaschuk/transit/venv/bin
Environment=FLASK_ENV=production
Environment=BASE_URL=http://81.28.248.71:5000
ExecStart=gunicorn -w 4 -b 0.0.0.0:5000
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

## Обновление данных

```bash
# 1. Остановить сервер
sudo systemctl stop transit

# 2. Запустить скраперы
python3 -u data/pipelines/scrape_gsp.py
python3 -u data/pipelines/scrape_intercity.py
python3 -u data/pipelines/scrape_srbvoz.py

# 3. Пересобрать БД
python3 -u data/pipelines/build_db.py

# 4. Запустить сервер
sudo systemctl start transit
```

## TODO

- [ ] nginx reverse proxy (порт 80/443)
- [ ] SSL сертификат (Let's Encrypt или Cloudflare)
- [ ] Домен transit-serbia.com
- [ ] Cloudflare CDN
- [ ] Docker image для портативности
- [ ] CI/CD (GitLab → auto deploy по тегам)

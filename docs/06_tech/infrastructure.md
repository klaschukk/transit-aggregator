# Инфраструктура

> **Обновлено 2026-06-12, проверено на живом сервере.**
> Прод — это **178.105.76.3** (hostname `prevozni`), а не montiko. Деплой-бокс и прод — один и тот же сервер.

## 1. Сервер

| Параметр | Значение |
|----------|----------|
| Домен | prevozni.com |
| IP | 178.105.76.3 (eth0, /32) |
| Hostname | `prevozni` |
| ОС | Ubuntu 24.04.3 LTS, kernel 6.8.0, TZ = UTC |
| Железо | 2 vCPU, 3.7 GiB RAM, диск 75 GB (занято ~15 GB / 20%) |
| Рабочая директория | `/root/klaschuk/transit-aggregator` (чекаут main; venv внутри) |
| Python | 3.12.3 (системный и venv) |

Также на боксе крутятся: `proslushka-bot.service` (посторонний TG-бот, root) и два процесса code-server (remote-сессии).

Montiko (81.28.248.71) в обслуживании prevozni.com **не участвует** — фигурировал только в устаревших доках; его текущая роль с прод-бокса не видна.

## 2. Цепочка запроса

```
Браузер
  → Cloudflare (DNS proxied, CDN, SSL-терминация, WAF)
  → nginx :80 (origin принимает ТОЛЬКО HTTP — фактически режим CF Flexible;
                на 443 никто не слушает, certbot не установлен)
  → gunicorn 127.0.0.1:8000 (2 workers)
  → Flask app:create_app() (ProxyFix x_for/x_proto/x_host=1)
  → DuckDB read-only (data/dbs/transit.duckdb, ~292 MB)
    + analytics.sqlite (~77 MB)
```

Масштаб данных (июнь 2026): 569 маршрутов, 3931 рейс, 69 операторов, 661 городская линия, 4 города.

## 3. nginx

Конфиг: `/etc/nginx/sites-available/prevozni` → симлинк в `sites-enabled/prevozni`.

- `listen 80;` `server_name prevozni.com www.prevozni.com;` — www-редиректа в конфиге **нет** (www отдаёт 200 тем же контентом).
- Запрос с `Host=178.105.76.3` (прямой IP) → `return 444`.
- Allowlist всех Cloudflare IPv4+IPv6 диапазонов + `127.0.0.1`, затем `deny all` — на весь server-блок.
- `/static/` → `alias /root/klaschuk/transit-aggregator/app/static/`, `expires 30d`, `Cache-Control "public, max-age=86400"` (без `immutable`).
- `proxy_pass http://127.0.0.1:8000`, заголовки `X-Forwarded-*`, `proxy_read_timeout 30s`.
- Логи nginx пишутся **внутрь репо**: `logs/nginx_access.log`, `logs/nginx_error.log`.

Security-заголовки (HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy) ставит **не nginx, а Flask** в `after_request` (`app/__init__.py`). gzip: `gzip on` в `/etc/nginx/nginx.conf` (http-уровень) + flask-compress в приложении.

## 4. systemd — transit.service

`/etc/systemd/system/transit.service`:

```ini
[Service]
User=root                      # hardening-TODO: до сих пор root
WorkingDirectory=/root/klaschuk/transit-aggregator
EnvironmentFile=/root/klaschuk/transit-aggregator/.env
ExecStart=.../venv/bin/gunicorn -w 2 --max-requests 2000 --max-requests-jitter 200 \
          --timeout 30 --bind 127.0.0.1:8000 "app:create_app()"
Restart=always
RestartSec=5
StandardOutput=append:.../logs/access.log   # фактически пуст: gunicorn access-log не включён
StandardError=append:.../logs/error.log
```

Drop-in `transit.service.d/adsense.conf` содержит закомментированный устаревший `ADSENSE_ID=pub-1417138799653355` — актуальный pub-id живёт в `.env`.

Версии: gunicorn 25.2.0, Flask 3.1.3, duckdb 1.2.1, flask-compress 1.17, flask-wtf 1.2.2, flask-limiter 4.1.1, sentry-sdk[flask] 2.17.0.

## 5. Переменные окружения

Файл: `/root/klaschuk/transit-aggregator/.env` (права 0600, root). Значения секретов здесь не приводим.

**Заданы:**

| Переменная | Значение / назначение |
|------------|----------------------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | задан (обязателен — без него RuntimeError на старте) |
| `DUCKDB_PATH` | `/root/klaschuk/transit-aggregator/data/dbs/transit.duckdb` |
| `GA_TRACKING_ID` | `G-0XPYJTVSSZ` |
| `ADSENSE_ID`, `ADSENSE_PUB_ID` | `ca-pub-9538841764038287` (live; PUB_ID — для `/ads.txt`) |
| `ADMIN_USER` / `ADMIN_PASS` | basic-auth на `/admin/*` |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | контакт-форма → Telegram |
| `BOOKAWAY_AFF_ID` | `4033` (Bookaway, offer_id=34, TUNE-трекер — ТОЛЬКО дальние направления/Азия) |
| `BOOKAWAY_NETWORK_ID` | `bookaway2` |
| `BOOKAWAY_API_KEY` | задан |
| `GROQ_API_KEY` | AI-маршруты дальних направлений |
| `MAPBOX_TOKEN` | задан |
| `ASSET_VERSION` | `hero1` — судя по всему legacy: версия ассетов в рантайме берётся из git SHA |

Партнёрка на обычных маршрутах — **BusTicket4, affiliateId=735** (комиссия 2%); она задаётся не env-переменной, а данными (`refresh_bt4_lineids.py`, см. деплой-гайд). FlixBus убран.

**Поддерживаются кодом, но НЕ заданы (фича выключена / работает дефолт):**

- `SENTRY_DSN` / `SENTRY_ENV` / `SENTRY_TRACES_SAMPLE_RATE` → **Sentry в проде не активен**;
- `SMTP_*` / `MAIL_FROM` → mailer пишет в `logs/mail_dev.log`; `MAILGUN_*`;
- `BASE_URL` (дефолт ProductionConfig = `https://prevozni.com`);
- `IP_HASH_SALT`; `ADSENSE_SLOT_*` (11 слотов); `EUR_RSD_RATE` (дефолт 117);
- `GSC_CREDENTIALS_PATH` / `GSC_SITE_URL`; `YANDEX_VERIFICATION`; `CONTACT_EMAIL`;
- `ANALYTICS_DB_PATH` (дефолт `data/dbs/analytics.sqlite`); `REVIEWS_AUTO_APPROVE_TRUSTED`; `MAIL_PHYSICAL_ADDRESS`.

## 6. Cron (root, время UTC)

Фактический crontab:

```
*/5 * * * * /usr/local/bin/transit-healthcheck.sh
0 3 * * *   /usr/local/bin/transit-enrich-night.sh
```

⚠️ **Обе записи указывают на КОПИИ в /usr/local/bin, а не на скрипты из репо:**

- `transit-healthcheck.sh` — байт-в-байт копия `scripts/healthcheck.sh` (curl `127.0.0.1:8000/health`; не-200 → `systemctl restart transit`; лог `/var/log/transit-healthcheck.log`). Безвредно, но дублирует репо.
- `transit-enrich-night.sh` — **протухшая копия от 15 мая**: делает только scrape_nis_stops → enrich_stops_coords → stop transit → build_db → start → `logs/last_refresh.json`. НЕ скрейпит intercity/international, НЕ обновляет BT4 line_ids, НЕ минифицирует CSS.
- Актуальная репо-версия лёгкого ночного пайплайна — `scripts/run_enrich_night.sh` (состав — в деплой-гайде).
- **Готовый фикс:** `/root/infra-backup-2026-06-12/apply-cron-fix.sh` переключает crontab на репо-скрипты (`scripts/healthcheck.sh`, `scripts/run_enrich_night.sh`) и удаляет копии. На момент аудита **не применён** (бэкапы старого crontab лежат там же).

Чего в кроне **нет**: `nightly_refresh.sh` (это ручной полный пайплайн), `weekly_seo.sh` и `sunday_content_refresh.sh` (хардкодят несуществующий `/home/klaschuk/transit` — на этом боксе нерабочие), `ping_indexnow.sh`, backlinks_*, newsletter_send. Autodeploy-cron (каждые 2 мин) **отключён 2026-06-04** (коммит 136890a; скрипт переименован в `transit-autodeploy.sh.disabled`).

## 7. Мониторинг

| Что | Как |
|-----|-----|
| `/health` (Flask) | всегда JSON; 200 только когда все критические проверки зелёные, иначе **503 + Retry-After** (фикс 9886c0b). Проверяет: transit_db (наличие, возраст, COUNT(*) по критическим таблицам routes/trips/city_lines/city_stops/city_line_stops/operators/line_geometries…), analytics_db (degraded, не 503), logs_writable, disk_free_pct, маркер ночного прогона (`last_refresh.json`), uptime_seconds, `version` = git SHA |
| Cron-healthcheck | */5 мин: авто-restart при не-200, лог `/var/log/transit-healthcheck.log` |
| systemd | `Restart=always` / `RestartSec=5` |
| Аналитика | Umami (cloud.umami.is) + GA4 (`G-0XPYJTVSSZ`) в base.html; собственная `analytics.sqlite` (клики и пр., видна в /health) |
| Sentry | код полностью готов (observability.init_sentry, `scripts/sentry_notify.py`, `docs/06_tech/sentry-setup.md`), но **выключен** — SENTRY_DSN не задан |
| Telegram | уведомления контакт-формы (работает) |
| Админка | `/admin/*` за basic-auth |

Внешнего uptime-мониторинга (UptimeRobot и т.п.) следов на боксе нет.

## 8. Логи и ротация

- logrotate `/etc/logrotate.d/transit`: daily, rotate 14, copytruncate, dateext — для `error.log`, `access.log`, `nginx_access.log`, `nginx_error.log`, `autodeploy.log`, `enrich.log`.
- Намеренно **исключены** из ротации state-логи (читаются обратно как состояние): `backlinks_sent.log`, `price_alerts.log`, `contact_messages.log`.
- `logs/access.log` пуст с 4 мая (gunicorn access-log не включён) — **реальные access-логи смотреть в `logs/nginx_access.log`**.
- `nightly_*.log` чистит сам `nightly_refresh.sh` (старше 14 дней).

## 9. Безопасность

**Сделано (hardening 2026-06-04):**

- ufw active: deny incoming; allow 22, 80, 443 (на 443 никто не слушает — правило «мёртвое»);
- SSH key-only (`/etc/ssh/sshd_config.d/99-hardening.conf`: `PasswordAuthentication no`, `PermitRootLogin prohibit-password`);
- logrotate; ротация GitLab PAT (последняя 2026-06-11);
- nginx CF-only allowlist + `return 444` на прямой IP;
- security headers + CSP на уровне приложения; `.env` 0600.

**НЕ сделано:**

- gunicorn до сих пор работает под **root** (`User=root` в юните);
- CF Authenticated Origin Pulls / Full (strict) — origin вообще без TLS (только :80, фактически Flexible);
- fail2ban установлен, но **inactive**;
- `/root/.git-credentials` — plaintext GitLab PAT (хотя origin уже переведён на SSH).

## 10. Бэкапы

🚩 **Бэкапов нет.** Ни БД, ни offsite-копий.

- `transit.duckdb` (~292 MB) воспроизводим ночной пересборкой из `data/raw` — потеря неприятна, но не фатальна.
- **`analytics.sqlite` (~77 MB, накопленные клики/аналитика) и state-логи невоспроизводимы и ничем не бэкапятся.** Потеря диска = потеря всей собственной аналитики.
- На боксе есть только точечные ручные копии: `/root/infra-backup-2026-06-12` (старый crontab + копии cron-скриптов) и `/root/bt4_lineids.backup.json`.
- Есть ли провайдерские снапшоты VPS — с бокса не видно, не подтверждено.

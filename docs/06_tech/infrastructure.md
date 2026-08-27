# Инфраструктура

> **Обновлено 2026-08-27, проверено на живом сервере.**
> Прод — текущий бокс (см. IP через `curl ifconfig.me` на сервере — не
> фиксируем его в доке, чтобы не protухал снова; спрашивай хостера/DNS,
> если нужен). Старый прод (**178.105.76.3**, `/opt/prevozni`, Ubuntu
> 24.04, TCP :8000) лежал ~месяц (кончилась оплата у хостера) и **больше
> не используется** — переезд на этот бокс произошёл 2026-07-31/08-01.
> Предыдущая версия этого файла (описывала старый сервер) — в
> `docs/90_archive/06_tech/infrastructure-2026-06-12-old-server.md`.

## 1. Сервер

| Параметр | Значение |
|----------|----------|
| Домен | prevozni.com (Cloudflare DNS + proxy) |
| ОС | Debian GNU/Linux 13 (trixie) — не Ubuntu, смена дистрибутива вместе с переездом |
| Железо | 4 vCPU, 7.8 GiB RAM, диск 251 GB (занято ~30 GB / 13%) |
| Прод-чекаут = дев-чекаут | `/home/deploy/transit-aggregator`, владелец — юзер `deploy` (не root). Один и тот же чекаут — отдельного дев/worktree-разделения, в отличие от старого сервера, здесь нет |
| Python | venv в чекауте (`venv/bin/python`) |

**Бокс мультитенантный.** На нём также живут `popaj`, `valocheck` и
`flight-punctuality` — их файлы/сервисы не трогать. С 2026-08-25 на
боксе крутится Docker (демон + `docker-proxy`) — поднят
flight-punctuality под self-hosted Umami (`umami` + `umami-db`, слушают
только `127.0.0.1:3001`). Отдельно стоят нативные PostgreSQL 17 и
Node.js 20 — остатки заброшенной попытки поставить Umami нативно
(откачена, база и юзер удалены), простаивают, можно переиспользовать.
Параллельные Claude-сессии на этом боксе — реальность: координируйся
через `SendMessage`/`ListAgents` перед установкой системного софта.

## 2. Цепочка запроса

```
Браузер
  → Cloudflare (DNS proxied, CDN, SSL-терминация, WAF)
  → nginx :80 (origin принимает ТОЛЬКО HTTP — режим CF Flexible;
                на 443 никто не слушает, certbot не установлен)
  → gunicorn — unix-сокет /run/prevozni/prevozni.sock (2 workers)
  → Flask app:create_app() (ProxyFix x_for/x_proto/x_host=1)
  → DuckDB read-only (data/dbs/transit.duckdb)
    + analytics.sqlite
```

Ключевое отличие от старого сервера: gunicorn слушает **unix-сокет**,
не TCP `127.0.0.1:8000`. Проверка живости — через сокет:

```bash
curl -s -o /dev/null -w '%{http_code}' --unix-socket /run/prevozni/prevozni.sock http://localhost/
```

Масштаб данных — смотри `/health` → `checks.transit_db.tables` (живые
цифры) или таблицу «БД (DuckDB)» в корневом `CLAUDE.md` — здесь не
дублируем, чтобы не расходилось.

## 3. nginx

Конфиг: `/etc/nginx/sites-available/prevozni.com` → симлинк в
`sites-enabled/prevozni.com`. Соседние сайты на боксе (`popaj.me`,
`valocheck.com`, `flightpunctuality.online`, `stats.flightpunctuality.online`)
— отдельные файлы там же, не трогать.

- `server_name prevozni.com www.prevozni.com;` слушает `:80`.
- Cloudflare-only access через `include /etc/nginx/snippets/cloudflare-realip.conf`
  (allowlist CF-диапазонов) — **не трогать эту логику**, origin не должен
  быть достижим напрямую по IP в обход CF WAF/DDoS.
- `error_page 502 504 = @upstream_down` → брендированная 503-страница с
  `Retry-After: 900` и `<meta robots noindex>` — если апстрим падает (например,
  ночной пайплайн держит DuckDB write-lock), Google получает «занят,
  зайду позже» вместо hard-error, который жжёт crawl-бюджет.
- `proxy_pass http://unix:/run/prevozni/prevozni.sock;`
- **Логи общие на весь бокс**, не per-vhost: `access_log /var/log/nginx/access.log;`
  в `nginx.conf` (http-уровень), никакой `access_log`/`error_log`
  директивы внутри `sites-available/prevozni.com`. Это значит лог
  содержит трафик ВСЕХ сайтов на боксе вперемешку (плюс шум от
  ботов-сканеров, бьющих по дефолтному vhost) — при анализе 5xx/404
  фильтровать по prevozni-путям (`/gradski/`, `/rute/`, `/voznja/`,
  `/pretraga/`, `/api/`, `/sitemap`, точный `/ HTTP` для главной), иначе
  цифры будут врать в разы (проверено 2026-08-27: без фильтра 32% "503"
  в общем логе, после фильтра — 0% на реальном трафике prevozni).

Security-заголовки (HSTS, CSP, X-Frame-Options, X-Content-Type-Options,
Referrer-Policy, Permissions-Policy) ставит **Flask**, не nginx
(`app/__init__.py` → `add_security_headers`). gzip: nginx `http`-уровень
+ flask-compress в приложении.

## 4. systemd — prevozni.service

`/etc/systemd/system/prevozni.service`:

```ini
[Service]
User=deploy
Group=deploy
WorkingDirectory=/home/deploy/transit-aggregator
Environment="FLASK_ENV=production"
Environment="BASE_URL=https://prevozni.com"
Environment="ADSENSE_ID=ca-pub-1417138799653355"
Environment="ADSENSE_SLOT_<KEY>=..."   # все 15 слотов, см. CLAUDE.md
Environment="MAPBOX_TOKEN=..."
Environment="GA_TRACKING_ID=G-0XPYJTVSSZ"
# + SECRET_KEY, GROQ_API_KEY — значения не приводим здесь
ExecStart=/home/deploy/transit-aggregator/venv/bin/gunicorn \
          --workers 2 --bind unix:/run/prevozni/prevozni.sock run:app
ExecReload=/bin/kill -HUP $MAINPID   # graceful reload после смены БД —
                                      # обычный restart отдаёт 5xx на пару
                                      # секунд, что Google засчитывает
                                      # против "Server error (5xx)"
Restart=always
RestartSec=3
```

Отличие от старого сервера: секреты/конфиг заданы **прямо в юните**
через `Environment=`, а не в отдельном `EnvironmentFile=`. `.env` в
чекауте существует, но несёт только один ключ, не заданный в юните
(`GROQ_API_KEY` дублируется — фактический источник истины смотри
`systemctl cat prevozni` на боксе, не полагайся на этот файл).

**GA4 (`G-0XPYJTVSSZ`) задан и активен параллельно с Umami** — в CSP
(`app/__init__.py`) домены `google-analytics.com`/`analytics.google.com`
уже разрешены. Корневой `CLAUDE.md` в таблице «Стек» упоминает только
Umami — GA4 не забыт, просто не задокументирован там; если решите
убрать GA4, поправить оба места.

## 5. Переменные окружения

Актуальный список — в корневом `CLAUDE.md` → «Deployment». Не дублируем
здесь во избежание расхождения; при изменении env-переменных обновляй
CLAUDE.md, эта секция — только про **где** они физически живут (юнит,
см. §4).

## 6. Cron

Живёт в `crontab -l -u deploy` (не root — отличие от старого сервера,
где cron был root-овый и указывал на копии в `/usr/local/bin`). Копий
скриптов вне репозитория нет — всё вызывается прямо из
`/home/deploy/transit-aggregator/scripts/`. Актуальный список — в
корневом `CLAUDE.md` → «Cron» (health-check */5 мин, `run_enrich_night.sh`
в 03:00, `ping_indexnow.sh` еженедельно по понедельникам,
`refresh_line_geometries.sh` по субботам). На боксе в том же crontab
есть записи valocheck (`healthcheck.sh`, `backup_sqlite.sh`,
`nightly_refresh.sh`, `poll_tracked.py`, `cache_cleanup.sh`) — не
трогать при правке cron prevozni, добавлять/убирать строки точечно
(`crontab -l | ... | crontab -`), не перезаписывать файл целиком.

`scripts/weekly_seo.sh` (дайджест GSC) в crontab **отсутствует** и не
запустится, даже если добавить — сервис-аккаунт GSC API не установлен
на боксе. Setup: `docs/06_tech/gsc-setup.md`.

## 7. Мониторинг

| Что | Как |
|-----|-----|
| `/health` | JSON; 200 только когда критические проверки зелёные, иначе 503 + Retry-After. Проверяет transit_db (наличие/возраст/COUNT по критическим таблицам), analytics_db (degraded, не 503), logs_writable, disk_free_pct, маркер ночного прогона, uptime, `version` = git SHA |
| Cron-healthcheck | `*/5` мин, `sudo scripts/healthcheck.sh`: не-200 → `systemctl restart prevozni` |
| systemd | `Restart=always` / `RestartSec=3` |
| Аналитика | Umami (cloud.umami.is, миграция на self-hosted в процессе — см. CLAUDE.md) + GA4 (`G-0XPYJTVSSZ`); своя `analytics.sqlite` |
| Sentry | код готов (`docs/06_tech/sentry-setup.md`), статус активности на этом боксе не проверен в рамках этого аудита — сверить `SENTRY_DSN` в юните |
| Внешний uptime-мониторинг | следов на боксе нет (как и на старом сервере) |

## 8. Память и swap

7.8 GiB RAM, из них ~5.2 GiB занято, ~1.2 GiB свободно на момент аудита
(2026-08-27) — бокс работает в притык, особенно после добавления
Docker/Postgres под соседний проект. Swap: 6 ГБ на двух файлах
(`/swapfile` 2 ГБ с 2026-08-03, `/swapfile2` ещё 4 ГБ добавлен
2026-08-25) — до 2026-08-03 swap отсутствовал вовсе, и всплеск памяти
сразу убивал gunicorn-воркер (SIGKILL/OOM, инцидент 2026-08-03 02:13).
`free -h` перед любой новой резидентной службой. **`/tmp` — tmpfs**, не
класть туда рабочие копии `transit.duckdb` (~300 МБ) — см. CLAUDE.md.

## 9. Безопасность

- Cloudflare-only access (nginx allowlist CF-диапазонов + `cloudflare-realip.conf`), origin недостижим по прямому IP;
- SSL: Cloudflare Flexible — TLS терминируется на CF, origin только `:80`;
- Security headers + CSP на уровне Flask (`app/__init__.py`);
- `deploy` — обычный пользователь, не root; systemd-юнит запускается от его имени;
- Детальный текущий аудит fail2ban/ufw/SSH-hardening на ЭТОМ боксе не проводился в рамках этой правки (старая версия файла описывала hardening старого сервера — не переносим как факт, требует отдельной проверки, если важно).

## 10. Бэкапы

Не проверялось в рамках этой правки, требует отдельного аудита при
необходимости — не переносим статус со старого сервера как факт.

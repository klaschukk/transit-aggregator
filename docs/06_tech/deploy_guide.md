# Деплой-гайд — Prevozni

> **Обновлено 2026-06-12, проверено на живом сервере.**
> Прод = деплой-бокс = **178.105.76.3** (root@, hostname `prevozni`). С 2026-06-04 деплой **только ручной** — autodeploy-cron отключён (коммит 136890a). Описание железа/nginx/systemd — в [infrastructure.md](infrastructure.md).

## 1. Деплой кода через GitLab CI (основной путь)

Файл: `.gitlab-ci.yml`. Origin: `git@gitlab.com:klaschukk/transit-aggregator.git` (SSH).

### Stage `test` — автоматически

Запускается на каждый push в `main` и на каждый MR:

- образ `python:3.12-slim`, `FLASK_ENV=testing`, seed-БД `tests/seed.duckdb`;
- `pytest -x` (исключены test_data_quality / test_integration / test_privacy); всего в проекте ~870 тестов;
- `allow_failure: false` — это **гейт**: пока тесты красные, деплоить нельзя.

### Stage `deploy` — РУЧНАЯ кнопка ▶ (`when: manual`, только main)

Что делает джоба по шагам (по SSH на `root@178.105.76.3`, ключ — CI-переменная `DEPLOY_SSH_KEY`, base64):

1. `git fetch && git reset --hard origin/main` — в прод-чекауте `/opt/prevozni` (с 2026-06-13, ad7f68f).
2. `pip install -r requirements.txt` (venv).
3. `python scripts/minify_css.py` — пересборка `app/static/css/dist/` (app.css, app.mobile.css, ads.css, admin.css). **dist/ в gitignore и деплоем НЕ приезжает из репо — он собирается именно на этом шаге.**
4. `systemctl restart transit`.
5. `curl /health` и печать `status` + `version` (фикс a4a31b0: раньше джоба парсила несуществующий ключ и всегда падала).

Порядок работы: изолированный worktree → ветка → MR → merge в `main` → дождаться зелёного `test` → нажать ▶ на джобе `deploy`.

## 2. Локальная альтернатива — scripts/deploy.sh

На самом боксе:

```bash
bash scripts/deploy.sh          # деплой main
bash scripts/deploy.sh <branch> # деплой другой ветки (редко нужно)
```

Делает то же, что CI-джоба: `git reset --hard origin/<branch>` → `pip install` → `minify_css.py` (с warn-fallback) → `systemctl restart transit` → проверка `/health == 200`, при провале `exit 1`.

## 3. Почему деплой ресетит main и зачем worktree

Оба пути деплоя делают `git reset --hard origin/main` в прод-чекауте `/opt/prevozni`.
Дев-чекаут `/root/klaschuk/transit-aggregator` деплоем больше не трогается (с ad7f68f), но
правило прежнее: работать в изолированных worktree и пушить в main сразу — ночной пайплайн
и сборка БД живут именно в дев-чекауте.

Поэтому железное правило: **вся работа — в изолированных worktree** (`/root/klaschuk/.wt/*`, `/root/klaschuk-*-wt` и т.д.), а в main попадаем через rebase + merge/push. Основной чекаут — только для прод-сервиса и деплоя.

## 4. Пайплайны данных

### 4.1 Лёгкий ночной — `scripts/run_enrich_night.sh` (cron 03:00 UTC)

Состав (актуализирован коммитом a4a31b0):

1. `minify_css.py`;
2. чистка OG-кэша (старше 7 дней);
3. `scrape_nis_stops` → `enrich_stops_coords`;
4. `discover_cities` → `scrape_intercity` → `scrape_international`;
5. `build_db.py` (сервис стопится только на время сборки);
6. `refresh_bt4_lineids.py` — карта «пара городов → lineId» для партнёрки BusTicket4 (affiliateId=735, все обычные маршруты);
7. restart transit + проверка `/health` с ретраем;
8. маркер `logs/last_refresh.json`.

⚠️ На момент аудита cron вызывал **протухшую копию** `/usr/local/bin/transit-enrich-night.sh` (от 15 мая, без intercity/international/BT4-шагов). Фикс готов: `/root/infra-backup-2026-06-12/apply-cron-fix.sh` переключает crontab на репо-скрипты — применить и забыть. Подробнее: [infrastructure.md §6](infrastructure.md).

### 4.2 Полный ручной — `scripts/nightly_refresh.sh` (~30–60 мин, сервис остановлен на всё время)

Запускать руками при больших обновлениях данных:

```bash
bash scripts/nightly_refresh.sh
```

Состав:

1. `systemctl stop transit`;
2. 9 скрейперов с пер-скрейперным статусом, падение любого не фатально: `discover_cities` (первым — каталог городов BT4), `scrape_gsp`, `scrape_intercity`, `scrape_srbvoz`, `scrape_lasta`, `scrape_gspns`, `scrape_gspns_schedule`, `scrape_naissus`, `scrape_international`;
3. `build_db.py` — **критичный шаг**: собирает в `transit.duckdb.tmp` и атомарно `os.replace` → `transit.duckdb`; при провале — старт сервиса на старой БД, маркер fail, exit 1. build_db **сам качает GTFS** (фикс a0f2f48 — раньше ребилд стирал расписание Белграда); `import_gtfs.py` руками НЕ запускать;
4. `enrich_post_build.py` (Нови-Сад OSM);
5. `scrape_route_geometries.py` — полилинии линий; `/health` считает `line_geometries` критической таблицей (урок инцидента 25.04);
6. `data_snapshot.py` (срез row-counts), `price_snapshot.py` + `price_alert_scan.py`;
7. `enrich_stops_coords.py --limit 50`;
8. `refresh_bt4_lineids.py` — не фатален: держит старую карту при покрытии <85%;
9. `systemctl start transit` → healthcheck с одним ретраем;
10. маркеры `logs/last_refresh.json` (status/finished_at/duration/scrapers — читается `/health`) и `last_refresh.txt`; чистка `nightly_*.log` старше 14 дней.

Sentry-пинги в пайплайне — no-op, пока SENTRY_DSN не задан.

## 5. Как проверить успешность деплоя

```bash
curl -s https://prevozni.com/health | python3 -m json.tool
```

- `status` должен быть ok, HTTP 200;
- **`version` = git SHA** — сверить с SHA задеплоенного коммита (`git rev-parse --short origin/main`). Если version отстаёт — код смержен, но кнопку ▶ не нажимали (это норма при manual-деплое, прод может отставать от main);
- после дата-пайплайнов: в `/health` смотреть возраст `last_refresh.json` и статусы скрейперов;
- быстрые smoke-проверки: `curl -s https://prevozni.com/sitemap.xml | head -5`, главная, любой `/rute/{slug}/`.

Ориентиры по данным (июнь 2026): 569 маршрутов, 3931 рейс, 69 операторов, 661 городская линия, 4 города. Резкое падение цифр после ребилда — повод откатиться/разбираться.

## 6. Troubleshooting

| Симптом | Что делать |
|---------|-----------|
| **503 во время ребилда БД** | Это штатно: `/health` и сайт отдают 503 + `Retry-After`, пока идёт build_db (фикс 9886c0b — раньше были фантомные 404 в GSC). Дождаться конца ребилда, ничего не рестартить. |
| Сервис не стартует | `journalctl -u transit -n 50`; ошибки gunicorn — в `logs/error.log` (внутри репо). |
| Нужны access-логи | `logs/nginx_access.log` и `logs/nginx_error.log` **в репо** (не `/var/log/nginx/` — site-логи туда не пишутся). `logs/access.log` пуст — gunicorn access-log не включён. |
| «DB locked» | Больше **не проблема**: build_db собирает в `.tmp` и делает атомарный `os.replace`, приложение читает БД read-only. Если что-то держит файл — `fuser data/dbs/transit.duckdb`. |
| Прод отстаёт от main | Норма при manual-деплое — нажать ▶ в GitLab или `bash scripts/deploy.sh`. |
| CSS «сломался» после деплоя | Проверить, что шаг `minify_css.py` прошёл: `dist/` gitignored и собирается только при деплое. Ловушка: minify ломает `+` в `clamp()`/`calc()` — проверять локально до пуша. |
| Сайт лежит, /health не отвечает | cron-healthcheck (*/5 мин) сам рестартит сервис; вручную — `systemctl restart transit`, лог `/var/log/transit-healthcheck.log`. |
| Высокая память | `systemctl restart transit` (workers и так перезапускаются по `--max-requests 2000`). |

## 7. Чего в этом гайде больше нет (и почему)

- **Certbot/SSL на origin** — не используется: TLS терминирует Cloudflare, origin слушает только :80 (CF Flexible).
- **Autodeploy по cron** — отключён 2026-06-04, скрипт лежит как `transit-autodeploy.sh.disabled`.
- **Настройка GA/AdSense с нуля** — давно сделано и live: GA4 `G-0XPYJTVSSZ`, AdSense `ca-pub-9538841764038287` (в `.env`).
- **Bookaway на обычных маршрутах** — убран; Bookaway (offer_id=34, aff_id=4033, TUNE-трекер) только для дальних направлений (Азия). На обычных маршрутах — BusTicket4 (affiliateId=735, комиссия 2%). FlixBus убран совсем.

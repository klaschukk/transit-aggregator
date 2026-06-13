# CLAUDE.md — Prevozni

## Обзор

**Prevozni** — бесплатный агрегатор общественного транспорта Сербии.
Городской (4 города) + межгородские автобусы/поезда. Programmatic SEO.

- **URL:** https://prevozni.com
- **Стек:** Flask + DuckDB + Gunicorn + nginx + Cloudflare
- **Цель:** 4600+ индексируемых страниц, AdSense монетизация

## Язык

- Общение: **русский**
- Код, коммиты, комментарии: **английский**

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Flask (Python 3.12) |
| БД | DuckDB (read-only, file-based) |
| WSGI | Gunicorn (2 workers, max-requests 2000) |
| Reverse proxy | nginx (Cloudflare-only access, только :80) |
| SSL | Cloudflare Flexible (origin TLS нет) |
| Process | systemd (transit.service) |
| Compression | flask-compress (gzip) + nginx gzip |
| Analytics | Umami |
| Данные | Скраперы (bgprevoz, gspns, busticket4.me, srbijavoz, polazak.rs) |

## URL архитектура

```
/                                    — главная (hero + поиск + популярные)
/rute/                               — каталог маршрутов (50 + "Prikaži još")
/rute/{slug}/                        — маршрут (расписание, цены)
/voznja/{from}-do-{to}/              — SEO городская пара + FAQ
/pretraga/?od=X&do=Y                 — результаты поиска
/gradski/{city}/                     — городской транспорт (карта + линии)
/gradski/{city}/linija/{slug}/       — линия (карта + остановки)
/gradski/{city}/stajaliste/{slug}/   — остановка (линии + ETA)
/prevoznici/                         — перевозчики
/autobuske-stanice/                  — станции
/o-nama/                             — о проекте
/kontakt/                            — контакт
/api/cities?q=                       — автокомплит городов
/api/city-stops?sw_lat&sw_lon&ne_lat&ne_lon — остановки на карте (limit 500)
/api/stop-arrivals?slug=             — ETA линий на остановке
/sitemap.xml                         — sitemap index (4 шарда: core, routes, lines, stops)
/robots.txt
/health                              — healthcheck (db status)
```

## Структура проекта

```
transit/
├── CLAUDE.md
├── config.py               ← Config + ProductionConfig (BASE_URL=https://prevozni.com)
├── run.py                   ← dev-сервер
├── requirements.txt         ← Flask, DuckDB, flask-compress, requests, bs4
├── app/
│   ├── __init__.py          ← create_app(), error handlers, gzip, caching
│   ├── db.py                ← query(), query_one(), cached_query(), thread-local conn
│   ├── routes/
│   │   ├── main.py          ← /, /pretraga/, /api/cities, sitemap, robots, health
│   │   ├── intercity.py     ← /rute/, /rute/{slug}/, /voznja/
│   │   ├── city.py          ← /gradski/, /api/city-stops, /api/stop-arrivals
│   │   └── info.py          ← /o-nama/, /kontakt/, /prevoznici/, /autobuske-stanice/
│   ├── templates/
│   │   ├── base.html        ← layout: head, header include, main, footer include
│   │   ├── _partials/       ← _header, _footer, _search_form, _trip_card, _filter_panel,
│   │   │                       _breadcrumb (JSON-LD), _stats_strip, _empty_state
│   │   ├── index.html       ← hero, stats, how-it-works, routes+city duo, benefits
│   │   ├── route_index.html, route_detail.html, city_pair.html, search_results.html
│   │   ├── city_transport.html, line_detail.html, stop_detail.html
│   │   ├── carriers_index.html, stations_index.html
│   │   ├── about.html, contact.html, 404.html, 500.html
│   │   └── 27 шаблонов + 24 partials всего
│   └── static/
│       ├── css/app.css      ← единый CSS, mobile-first, 0 !important
│       └── favicon.svg
├── data/
│   ├── pipelines/
│   │   ├── build_db.py      ← собирает transit.duckdb из raw/ (3 источника + dedup)
│   │   ├── scrape_gsp.py    ← GSP Белград (bgprevoz.rs API)
│   │   ├── scrape_gspns.py  ← JGSP Нови Сад (gspns.co.rs)
│   │   ├── scrape_gspns_schedule.py ← расписание Нови Сад
│   │   ├── scrape_intercity.py ← busticket4.me API (48 городов, 562 пары)
│   │   ├── scrape_srbvoz.py ← srbijavoz.rs (поезда)
│   │   ├── scrape_lasta.py  ← polazak.rs (302 маршрута, 68 операторов)
│   │   ├── scrape_naissus.py ← JGP Ниш (jgpnis.rs + Overpass)
│   │   ├── scrape_kragujevac.py ← Крагуевац (Overpass API)
│   │   ├── enrich_stops_coords.py ← OSM Overpass + Nominatim
│   │   └── import_gtfs.py   ← GTFS feed import (data.gov.rs)
│   ├── dbs/transit.duckdb   ← рабочая БД (gitignored)
│   └── raw/                 ← JSON от скраперов (gitignored)
├── scripts/
│   ├── deploy.sh            ← ручной деплой на боксе (reset --hard origin/main + restart)
│   ├── healthcheck.sh       ← cron */5 min, auto-restart
│   ├── run_enrich_night.sh  ← cron 3:00 AM (лёгкий ночной пайплайн)
│   └── nightly_refresh.sh   ← полный пайплайн, только ВРУЧНУЮ (в cron его нет)
├── logs/                    ← access.log, error.log
└── tests/                   ← pytest (876 тестов)
```

## БД (DuckDB)

Цифры на 2026-06 (живые цифры всегда в `/health` → `checks.transit_db.tables`):

| Таблица | Записей | Описание |
|---------|---------|----------|
| city_lines | 661 | Линии: Белград 521, Нови Сад 61, Ниш 56, Крагуевац 23 |
| city_stops | 2932 | Остановки (94% с координатами) |
| city_line_stops | 13136 | Привязка остановок к линиям |
| line_geometries | 217 | Геометрии линий для карт |
| routes | 569 | Маршруты (domestic + international в одной таблице) |
| trips | 3931 | Рейсы (цены, операторы, BT4 lineId для checkout) |
| operators | 69 | Перевозчики (Lasta, Niš-Ekspres, OZLEM, Srbija Voz и др.) |
| stations | 10 | ЖД станции |
| gtfs_trips | 93991 | GTFS расписание (Белград + Нови Сад) |
| gtfs_stop_times | 2317651 | Времена прибытия |

Отдельной таблицы `international` больше нет — международные рейсы влиты в `routes`/`trips`.

## Deployment

Production environment requires these env vars:

- `FLASK_ENV=production`
- `SECRET_KEY` — **обязателен** (при отсутствии app бросает RuntimeError на старте).
  Сгенерировать: `python -c "import secrets; print(secrets.token_hex(32))"`.
  Хранить в systemd unit (`Environment=`) или `.env` (не коммитить).
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — уведомления контакт-формы
  + weekly SEO digest (переиспользуется).
- `DUCKDB_PATH` — путь к `transit.duckdb` (по умолчанию `data/dbs/transit.duckdb`).
- `GSC_CREDENTIALS_PATH` — service account JSON для Search Console API
  (по умолчанию `/home/klaschuk/.gsc-credentials.json`, mode 0600).
  ⚠️ Дефолтный путь на текущем боксе (178.105.76.3) **мёртвый** — файла нет,
  GSC-скрипты (`weekly_seo.sh` и пр.) не сконфигурированы и не работают.
  Setup: `docs/06_tech/gsc-setup.md`.
- `GSC_SITE_URL` — GSC property identifier
  (по умолчанию `sc-domain:prevozni.com`).
- `SMTP_HOST`, `SMTP_PORT` (587), `SMTP_USER`, `SMTP_PASS`,
  `MAIL_FROM` — outbound email (newsletter confirm/welcome/unsubscribe).
  Без `SMTP_HOST` mailer пишет в `logs/mail_dev.log` — double-opt-in
  работает локально и в тестах без реального mailbox.

## Инфраструктура

```
Домен: prevozni.com (Cloudflare DNS + proxy)
Прод-сервер: 178.105.76.3 (hostname prevozni) — НЕ montiko
Reverse proxy: nginx, только :80, доступ только с IP Cloudflare (прямой заход по IP → 403)
SSL: Cloudflare Flexible — origin TLS НЕТ (CF→origin ходит по HTTP)
Service: systemd transit.service (FLASK_ENV=production)
Workers: gunicorn -w 2 --max-requests 2000 --max-requests-jitter 200 --timeout 30 --bind 127.0.0.1:8000
```

**Прод и рабочий чекаут — один и тот же бокс.** На 178.105.76.3 лежит
рабочий чекаут `/root/klaschuk/transit-aggregator` — это живая инфраструктура:
ночной пайплайн собирает в нём БД, и прод-сервис читает её оттуда
(`DUCKDB_PATH=/root/klaschuk/transit-aggregator/data/dbs/transit.duckdb`).
Сам gunicorn с 2026-06-13 крутится из отдельного прод-чекаута `/opt/prevozni`
под непривилегированным юзером `prevozni` (до этого — прямо из рабочего
чекаута под root). Деплой делает `git reset --hard origin/main` и стирает
всё незакоммиченное, поэтому **ВСЯ работа — только в изолированных worktree**
(`/root/klaschuk/.wt/*`); основной чекаут не трогать, он держится на main.

**Деплой** — только вручную, автодеплой-крона НЕТ (отключён 2026-06-04):

- кнопка ▶ в GitLab CI (stage `deploy`, `when: manual`; test-гейт
  прогоняется автоматически на каждый push в main и MR);
- либо `scripts/deploy.sh` прямо на боксе.

Оба пути: `git reset --hard origin/main` → `pip install` → minify CSS →
`systemctl restart transit` → проверка `/health == 200`.

**Cron:**

- `*/5 min` — healthcheck (`/health` != 200 → авторестарт сервиса);
- `03:00` — `run_enrich_night.sh`, лёгкий ночной пайплайн: minify CSS →
  скрейп Ниш/координаты → BT4-каталог + intercity + international →
  build_db → refresh_bt4_lineids → restart.

`nightly_refresh.sh` — это полный пайплайн, запускается только ВРУЧНУЮ
(в cron его нет, не путать с ночным enrich).

## Конвенции

- Python: PEP 8, type hints, макс 120 символов
- Templates: Jinja2, `{% include %}` для header/footer, `{% macro %}` для trip_card и т.д.
- CSS: семантические переменные (--color-primary), mobile-first, 0 !important
- Git: conventional commits (feat:, fix:, docs:, data:, infra:)
- Inline styles: НОЛЬ (кроме динамического background:color на line-badge)
- Emoji: НОЛЬ (SVG иконки)

## Текущий статус (июнь 2026)

- [x] Flask + DuckDB + 569 маршрутов, 3931 рейс, 69 операторов
- [x] 4 города, 661 городская линия: Белград (521), Нови Сад (61), Ниш (56), Крагуевац (23)
- [x] 2932 остановки (94% GPS), 13136 line-stop links
- [x] Единый CSS дизайн-система (app.css)
- [x] SEO: JSON-LD, OG, BreadcrumbList, FAQ schema, sitemap index (4 шарда)
- [x] Мобильная адаптивность (44px touch targets, focus-visible)
- [x] Скраперы: bgprevoz, gspns, busticket4.me, srbijavoz, polazak.rs, naissus, kragujevac
- [x] Автокомплит городов (API)
- [x] Карта с остановками (Leaflet, limit 500)
- [x] GTFS расписание Белград (87K trips) + Нови Сад (6.5K trips)
- [x] ETA на остановках (GTFS + headway fallback)
- [x] nginx + Cloudflare + gunicorn + gzip + healthcheck
- [x] Connection pooling + TTL cache (0.04s response)
- [x] 876 тестов (pytest)
- [x] Домен prevozni.com + Cloudflare SSL
- [x] Umami analytics
- [x] Telegram bot notifications (контакт-форма)
- [x] 3 языка: sr (default) + en + ru с full i18n
- [x] Международные рейсы (Crna Gora, BiH, HR, TR, SI, MK) — влиты в routes/trips
- [x] BusTicket4 affiliateId=735 — основной партнёр (комиссия 2%), per-trip checkout;
      Bookaway (offer_id=34, aff_id=4033, TUNE-трекер) — ТОЛЬКО дальние направления (Азия);
      FlixBus убран
- [x] Google AdSense — live (ca-pub-9538841764038287)
- [x] Newsletter + price alerts (double-opt-in через SMTP)
- [x] AI-чат с контекстом страниц
- [x] Дальние направления (Азия), фаза 1: AI-составление маршрута (Groq,
      /api/compose-route) + Bookaway CTA
- [x] Гайды /vodici/
- [x] Destinations page (14 топ направлений Балкан)
- [x] hreflang × 3, og:locale:alternate, robots max-image-preview, Organization JSON-LD

## Документация

- `docs/README.md` — оглавление всей документации.
- Самые важные: `docs/06_tech/infrastructure.md` и `docs/06_tech/deploy_guide.md`
  (актуализированы 2026-06-12).
- `docs/90_archive/` — архив, НЕ поддерживается, на него не опираться.

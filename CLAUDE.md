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
| WSGI | Gunicorn (2 workers, max-requests 500) |
| Reverse proxy | nginx (Cloudflare-only access) |
| SSL | Cloudflare (Full mode) |
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
/sitemap.xml                         — 4632 URL
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
│   │   └── 23 шаблона всего
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
│   ├── healthcheck.sh       ← cron */5 min, auto-restart
│   └── run_enrich_night.sh  ← cron 3:00 AM
├── logs/                    ← access.log, error.log
└── tests/                   ← pytest (325 тестов)
```

## БД (DuckDB)

| Таблица | Записей | Описание |
|---------|---------|----------|
| city_lines | 610 | Линии: Белград 514, Нови Сад 61, Ниш 12, Крагуевац 23 |
| city_stops | 3770 | Остановки (97% с координатами) |
| city_line_stops | 14375 | Привязка остановок к линиям |
| routes | 517 | Маршруты: 271 domestic + 246 international/info |
| trips | 2777 | Рейсы (с реальными ценами и операторами) |
| operators | 66 | Перевозчики (Lasta, Niš-Ekspres, OZLEM, Srbija Voz и др.) |
| stations | 10 | ЖД станции |
| gtfs_trips | 93991 | GTFS расписание (Белград + Нови Сад) |
| gtfs_stop_times | 2317651 | Времена прибытия (94% mapped) |
| international | 458 | Международные рейсы (Crna Gora, BiH, HR, TR, SI, MK) |

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
  (по умолчанию `/home/klaschuk/.gsc-credentials.json`, mode 0600). Нужен
  только для `scripts/weekly_seo.sh` (cron). Setup: `docs/06_tech/gsc-setup.md`.
- `GSC_SITE_URL` — GSC property identifier
  (по умолчанию `sc-domain:prevozni.com`).

## Инфраструктура

```
Домен: prevozni.com (Cloudflare DNS + proxy)
Сервер: 81.28.248.71 (montiko, Подгорица)
Reverse proxy: nginx (Cloudflare-only IPs, security headers)
SSL: Cloudflare Full mode
Service: systemd transit.service (FLASK_ENV=production)
Workers: gunicorn -w 2 --max-requests 500 --timeout 30
Logs: logs/access.log, logs/error.log
Healthcheck: cron */5 min → auto-restart
Enrich: cron 3:00 AM
```

## Конвенции

- Python: PEP 8, type hints, макс 120 символов
- Templates: Jinja2, `{% include %}` для header/footer, `{% macro %}` для trip_card и т.д.
- CSS: семантические переменные (--color-primary), mobile-first, 0 !important
- Git: conventional commits (feat:, fix:, docs:, data:, infra:)
- Inline styles: НОЛЬ (кроме динамического background:color на line-badge)
- Emoji: НОЛЬ (SVG иконки)

## Текущий статус (апрель 2026)

- [x] Flask + DuckDB + 335 маршрутов, 2838 рейсов, 70 операторов
- [x] 4 города: Белград (514), Нови Сад (61), Ниш (53), Крагуевац (23 линии)
- [x] 4522 остановки (96% GPS), 22727 line-stop links (98% linked)
- [x] Единый CSS дизайн-система (app.css)
- [x] 23 шаблона + 8 partials
- [x] SEO: JSON-LD, OG, BreadcrumbList, FAQ schema, sitemap (4542 URL)
- [x] Мобильная адаптивность (44px touch targets, focus-visible)
- [x] Скраперы: bgprevoz, gspns, busticket4.me, srbijavoz, polazak.rs, naissus, kragujevac
- [x] Автокомплит городов (API)
- [x] Карта с остановками (Leaflet, limit 500)
- [x] GTFS расписание Белград (87K trips) + Нови Сад (6.5K trips)
- [x] ETA на остановках (GTFS + headway fallback)
- [x] nginx + Cloudflare + gunicorn + gzip + healthcheck
- [x] Connection pooling + TTL cache (0.04s response)
- [x] 325 тестов (pytest)
- [x] Домен prevozni.com + Cloudflare SSL
- [x] Umami analytics
- [x] Telegram bot notifications (контакт-форма)
- [x] 3 языка: sr (default) + en + ru с full i18n
- [x] 458 международных рейсов (Crna Gora, BiH, Hrvatska, Turska, Slovenija)
- [x] Bookaway affiliate (offer_id=34, aff_id=4033) — buy кнопка везде
- [x] Destinations page (14 топ направлений Балкан)
- [x] hreflang × 3, og:locale:alternate, robots max-image-preview, Organization JSON-LD
- [ ] Google AdSense (после 1000+ визитов/мес)

# CLAUDE.md — Prevozni

## Обзор

**Prevozni** — бесплатный агрегатор общественного транспорта Сербии.
Городской (GSP Белград) + межгородские автобусы/поезда. Programmatic SEO.

- **URL:** http://81.28.248.71:5000/ (домен пока нет)
- **Стек:** Flask + DuckDB + Gunicorn + systemd
- **Цель:** 3000+ индексируемых страниц, AdSense монетизация

## Язык

- Общение: **русский**
- Код, коммиты, комментарии: **английский**

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Flask (Python 3.12) |
| БД | DuckDB (read-only, file-based) |
| WSGI | Gunicorn (4 workers) |
| Process | systemd (transit.service) |
| Compression | flask-compress (gzip) |
| Данные | Скраперы (bgprevoz, gspns, busticket4.me, srbijavoz, lasta, polazak) |

## URL архитектура

```
/                                    — главная (hero + поиск + популярные)
/rute/                               — каталог маршрутов
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
/api/city-stops?sw_lat&sw_lon&ne_lat&ne_lon — остановки на карте
/api/stop-arrivals?slug=             — ETA линий на остановке
/sitemap.xml                         — 3304 URL
/robots.txt
/health                              — healthcheck (db status)
```

## Структура проекта

```
transit/
├── CLAUDE.md
├── config.py               ← Config + ProductionConfig (BASE_URL, EUR_RSD_RATE)
├── run.py                   ← dev-сервер
├── requirements.txt         ← Flask, DuckDB, flask-compress, requests, bs4
├── app/
│   ├── __init__.py          ← create_app(), error handlers, gzip, caching
│   ├── db.py                ← query(), query_one(), db_ready()
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
│       ├── css/app.css      ← единый CSS (~1650 строк), mobile-first, 0 !important
│       └── favicon.svg
├── data/
│   ├── pipelines/
│   │   ├── build_db.py      ← собирает transit.duckdb из raw/
│   │   ├── scrape_gsp.py    ← GSP Белград (bgprevoz.rs API)
│   │   ├── scrape_gspns.py  ← JGSP Нови Сад (gspns.co.rs)
│   │   ├── scrape_gspns_schedule.py ← расписание Нови Сад
│   │   ├── scrape_intercity.py ← busticket4.me API
│   │   ├── scrape_srbvoz.py ← srbijavoz.rs
│   │   ├── scrape_lasta.py  ← lasta.rs / polazak.rs
│   │   ├── enrich_stops_coords.py ← OSM Overpass + Nominatim
│   │   └── import_gtfs.py   ← GTFS feed import (data.gov.rs)
│   ├── dbs/transit.duckdb   ← рабочая БД (gitignored)
│   └── raw/                 ← JSON от скраперов (gitignored)
├── scripts/
│   ├── healthcheck.sh       ← cron */5 min, auto-restart
│   └── run_enrich_night.sh  ← cron 3:00 AM
├── logs/                    ← access.log, error.log
└── tests/                   ← pytest (WIP)
```

## БД (DuckDB)

| Таблица | Записей | Описание |
|---------|---------|----------|
| city_lines | 651 | Линии: Белград 514, Нови Сад 61, Ниш 53 + пригород |
| city_stops | 2867 | Остановки (94% с координатами) |
| city_line_stops | 12938 | Привязка остановок к линиям |
| routes | 334 | Межгородские маршруты |
| trips | 2840 | Рейсы (время, цена, оператор) |
| operators | 70 | Перевозчики (Lasta, Niš-Ekspres, Srbija Voz и др.) |
| stations | 10 | ЖД станции |
| gtfs_trips | 93991 | GTFS расписание (Белград + Нови Сад) |
| gtfs_stop_times | 2317651 | Времена прибытия (96% mapped) |

## Инфраструктура

```
Сервер: 81.28.248.71 (montiko, Подгорица)
Service: systemd transit.service (FLASK_ENV=production)
Workers: gunicorn -w 4
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

- [x] Flask + DuckDB + 334 маршрута, 2840 рейсов
- [x] 3 города: Белград (514), Нови Сад (61), Ниш (53 линии)
- [x] Единый CSS дизайн-система (app.css)
- [x] 23 шаблона + 8 partials
- [x] SEO: JSON-LD, OG, BreadcrumbList, FAQ schema, sitemap (3304 URL)
- [x] Мобильная адаптивность (44px touch targets, focus-visible)
- [x] Скраперы: bgprevoz, gspns, busticket4.me, srbijavoz, lasta, polazak
- [x] Автокомплит городов (API)
- [x] Карта с остановками (Leaflet)
- [x] GTFS расписание Белград (87K trips) + Нови Сад (6.5K trips)
- [x] ETA на остановках (GTFS + headway fallback)
- [x] systemd + gunicorn + gzip + healthcheck
- [x] Connection pooling + TTL cache (0.04s response)
- [x] 150+ тестов (pytest)
- [ ] Домен + Cloudflare
- [ ] Google AdSense

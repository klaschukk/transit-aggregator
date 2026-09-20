# История и устаревшие срезы (вынесено из CLAUDE.md 2026-09-21)

Дословно то, что раньше грузилось в контекст каждой сессии, но не нужно для повседневной работы. Актуальные цифры — `scripts/preflight.sh` и `/health`.


## Структура проекта (дерево на июнь 2026)

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
└── tests/                   ← pytest (1116+ тестов)
```


## БД (цифры на 2026-06)

Цифры на 2026-06 (живые цифры всегда в `/health` → `checks.transit_db.tables`):

| Таблица | Записей | Описание |
|---------|---------|----------|
| city_lines | 678 | Белград 516, Нови Сад 71, Ниш 56, Крагуевац 22, Подгорица 7, Будва 4, Херцег-Нови 2 |
| city_stops | 3478 | Остановки (97% с координатами) |
| city_line_stops | 14221 | Привязка остановок к линиям |
| line_geometries | 205 | Геометрии линий для карт (полилинии по дорогам) |
| routes | 577 | Маршруты (domestic + international в одной таблице) |
| trips | 3918 | Рейсы (цены, операторы, BT4 lineId для checkout) |
| operators | 65 | Перевозчики (Lasta, Niš-Ekspres, OZLEM, Srbija Voz и др.) |
| stations | 10 | ЖД станции |
| gtfs_trips | 93504 | GTFS расписание (Белград + Нови Сад) |
| gtfs_stop_times | 2375539 | Времена прибытия |

Города: **7** (4 сербских + 3 черногорских), не 4.

Отдельной таблицы `international` больше нет — международные рейсы влиты в `routes`/`trips`.


## История одного простоя (для контекста, не переоткрывать).** Трафик
рухнул с ~815 кликов/день (26.06) почти до нуля (2/день, 14.07) и
просидел там весь июль — причина: у старого хостера кончилась оплата,
сайт был недоступен ~месяц, из-за чего "Server error (5xx)" в Search
Console вырос до ~19–20K страниц. С переездом на этот бокс (31.07/01.08)
трафик и индексация начали восстанавливаться сами; к 21.08 показы дошли
до ~38K/день (~65% от пика). Это не код-баг и не лечится с этой
стороны — только время + не дать оплате повиснуть на новом хостере.


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
- [x] 1116+ тестов (pytest)
- [x] Домен prevozni.com + Cloudflare SSL
- [x] Umami analytics
- [x] Telegram bot notifications (контакт-форма)
- [x] 3 языка: sr (default) + en + ru с full i18n
- [x] Международные рейсы (Crna Gora, BiH, HR, TR, SI, MK) — влиты в routes/trips
- [x] BusTicket4 affiliateId=735 — основной партнёр (комиссия 2%), per-trip checkout;
      Bookaway (offer_id=34, aff_id=4033, TUNE-трекер) — ТОЛЬКО дальние направления (Азия);
      FlixBus убран
- [x] Google AdSense — live (ca-pub-1417138799653355)
- [x] Newsletter + price alerts (double-opt-in через SMTP)
- [x] AI-чат с контекстом страниц
- [x] Дальние направления (Азия), фаза 1: AI-составление маршрута (Groq,
      /api/compose-route) + Bookaway CTA
- [x] Гайды /vodici/
- [x] Destinations page (14 топ направлений Балкан)
- [x] hreflang × 3, og:locale:alternate, robots max-image-preview, Organization JSON-LD


## Изменения после переезда (август 2026)

- [x] Переезд на текущий бокс 2026-07-31/08-01 (см. «История одного простоя» выше)
- [x] `FLASK_ENV` — был не задан на новом боксе → `create_app()` тихо
      падал на `DevelopmentConfig` (несжатый CSS, без кэша шаблонов, без
      кастомной 500-страницы на неотловленных ошибках). Добавлен
      `FLASK_ENV=production` в systemd unit
- [x] Все 15 слотов AdSense получили реальные `ADSENSE_SLOT_*` (были
      пустые везде кроме `search_mid` — рендерились как Auto Ads hint без
      единого показа с самого запуска монетизации)
- [x] `ads.css` тихо перебивал bottom-stack arbiter из `app.mobile.css` —
      `.mobile-anchor-ad` сидел на `bottom:0`/`z-index:60` вместо
      `var(--m-bnav-h)`/`var(--z-promo)`, перекрывая нижнюю навигацию
- [x] Umami: CSP/i18n ссылались на мёртвый `analytics.farmako.ro` (домен
      до миграции на `cloud.umami.is`) — скрипт и beacon блокировались
      браузером, своя аналитика не собирала ничего с момента миграции
- [x] Поиск `/pretraga/` — diacritic-insensitive matching (`Nis` → `Niš`)
- [x] Кириллица/латиница в номерах линий унифицированы через `|latin`
      Jinja-фильтр (рендер-слой; в БД не лезть — `city_lines.number`
      участвует в `UNIQUE(city, number)`, DuckDB 1.2.1 бросает
      ConstraintException на UPDATE такой колонки, если на строку есть
      FK-ссылка — проверено, не чинить в build_db.py)
- [x] nginx: доступ только с IP Cloudflare (allow/deny), брендированная
      503-страница при полном падении апстрима

**В процессе, не завершено:** self-hosted Umami для prevozni.com —
ждём DNS-запись `stats.flightpunctuality.online` от проекта
flight-punctuality (общий инстанс, см. Инфраструктура); website ID уже
выдан (`0bf85965-824a-4732-914a-d58f97cbb307`), переключение
script-src/connect-src/script-tag — минутное дело, как только домен
зарезолвится (сейчас NXDOMAIN).

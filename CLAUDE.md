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
| Analytics | Umami — cloud.umami.is (website ID `6af0f7f1-e6d7-4d30-b3f0-f47265a83db8`). Self-hosted migration in progress: shared instance on this same box, run by the flight-punctuality project (Docker, `127.0.0.1:3001`), see Инфраструктура. |
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

## Deployment

Production environment requires these env vars:

- `FLASK_ENV=production`
- `SECRET_KEY` — **обязателен** (при отсутствии app бросает RuntimeError на старте).
  Сгенерировать: `python -c "import secrets; print(secrets.token_hex(32))"`.
  Хранить в systemd unit (`Environment=`) или `.env` (не коммитить).
- `ADSENSE_ID` — **обязателен для монетизации** (`ca-pub-1417138799653355`).
  Без него `{% if config.ADSENSE_ID %}` ложно → adsbygoogle.js вообще не
  грузится, ни один слот не рендерится, а `/ads.txt` отдаёт заглушку вместо
  `google.com, pub-…, DIRECT, f08c47fec0942fa0`. Реклама молча не работает.
- `MAPBOX_TOKEN` — **обязателен для карт** (`pk.…`). Без него в шаблон
  подставляется `mapboxgl.accessToken = ''` и карта на `/gradski/…`
  (город, линия, остановка) остаётся пустой. Проверка токена:
  `curl -o /dev/null -w '%{http_code}' "https://api.mapbox.com/styles/v1/mapbox/light-v11?access_token=$MAPBOX_TOKEN"` → 200.
- `GROQ_API_KEY` — **обязателен для AI-чата и дальних направлений** (`gsk_…`).
  Без него `/api/chat` отдаёт 503, а `sitemap-far.xml` пуст: страницы
  `/voznja/<hub>-do-<far>/` индексируются только при наличии готового
  маршрута в кэше `composed_routes`, а наполняет кэш исключительно
  `scripts/pregen_far_routes.py` (обработчик запроса намеренно
  cache-only — Googlebot не должен ждать модель).
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — уведомления контакт-формы
  + weekly SEO digest (переиспользуется).
- `DUCKDB_PATH` — путь к `transit.duckdb` (по умолчанию `data/dbs/transit.duckdb`).
- `GSC_CREDENTIALS_PATH` — service account JSON для Search Console API
  (по умолчанию `/home/klaschuk/.gsc-credentials.json`, mode 0600).
  ⚠️ Не задан и файла нет нигде на текущем боксе (проверено 2026-08-25) —
  `scripts/gsc_fetch.py` не сконфигурирован и не работает; GSC-данные
  для анализа брать через ручной экспорт CSV из Search Console, не через
  этот скрипт. Setup: `docs/06_tech/gsc-setup.md`.
- `GSC_SITE_URL` — GSC property identifier
  (по умолчанию `sc-domain:prevozni.com`).
- `SMTP_HOST`, `SMTP_PORT` (587), `SMTP_USER`, `SMTP_PASS`,
  `MAIL_FROM` — outbound email (newsletter confirm/welcome/unsubscribe).
  Без `SMTP_HOST` mailer пишет в `logs/mail_dev.log` — double-opt-in
  работает локально и в тестах без реального mailbox.
- `ADSENSE_SLOT_*` — 15 отдельных ad-unit ID (все настоящие, живые с
  2026-08-24), ключи см. `config.py` → `ADSENSE_SLOTS`:
  `HOME_TOP`, `HOME_MID`, `MOBILE_ANCHOR`, `ROUTE_BOTTOM`, `ROUTE_MID`,
  `LINE_BOTTOM`, `LINE_MID`, `STOP_BOTTOM`, `STOP_MID`,
  `CITY_PAIR_BOTTOM`, `CITY_PAIR_MID`, `CITY_TRANSPORT_MID`,
  `CATALOG_IN_FEED`, `SEARCH_MID`, `GUIDE_BOTTOM` (+ `GUIDES_BOTTOM` на
  `/vodici/` — тот же физический юнит, что и `GUIDE_BOTTOM`, задан
  отдельной переменной). Без конкретного `ADSENSE_SLOT_<KEY>` слот не
  падает молча — рендерится как Auto Ads placement hint без
  `data-ad-slot` (сайт без `enable_page_level_ads`, так что это ничего
  не показывает). Так было ВЕЗДЕ кроме `search_mid` до 2026-08-24.

## Инфраструктура

> Актуально на 2026-08-01. Всё ниже — текущий бокс; описание старого сервера
> (178.105.76.3, `/opt/prevozni`, `transit.service`, TCP :8000) устарело.

```
Домен: prevozni.com (Cloudflare DNS + proxy)
Чекаут (он же прод): /home/deploy/transit-aggregator, владелец — юзер deploy
Service: systemd prevozni.service (User=deploy)
Workers: gunicorn -w 2 --bind unix:/run/prevozni/prevozni.sock
Reverse proxy: nginx → unix-сокет; 502/504 переписываются в 503 + Retry-After
SSL: Cloudflare Flexible — X-Forwarded-Proto в nginx, НЕ ТРОГАТЬ эту логику
На боксе также живут popaj, valocheck и flight-punctuality — их не трогать
```

**Бокс мульти-тенантный, не только Flask+systemd.** С 2026-08-25 на боксе
также крутится Docker (`docker.service`, демон + `docker-proxy`) — поднят
проектом flight-punctuality под self-hosted Umami (`umami` +
`umami-db`/postgres:16-alpine, слушают только `127.0.0.1:3001`). `docker`
CLI стоит в `/usr/bin/docker`, но большинству сессий это не нужно —
только если работаешь с контейнерами flight-punctuality. Отдельно,
абсолютно не связанные с prevozni, но живут на диске: нативные
PostgreSQL 17 (`systemctl status postgresql`) и Node.js 20 + npm + pnpm —
остались от одной заброшенной попытки поставить self-hosted Umami
нативно (откачена, база `umami`/юзер `umami` удалены), простаивают,
ничего не едят, можно смело переиспользовать под что-то ещё.

Параллельные Claude-сессии на этом боксе — реальность, не гипотеза:
координируйся через `SendMessage`/`ListAgents` перед тем, как ставить
системный софт (Docker, БД, systemd unit) — легко задублировать работу
другой сессии, разбирающей соседний проект на этом же боксе.

Проверка после любого изменения работающего кода:

```bash
sudo systemctl restart prevozni && sleep 3
systemctl is-active prevozni
curl -s -o /dev/null -w '%{http_code}' --unix-socket /run/prevozni/prevozni.sock http://localhost/
```

**`/tmp` — это tmpfs, то есть ОПЕРАТИВНАЯ ПАМЯТЬ.** Не класть туда копии
`transit.duckdb` (~300 МБ) и прочие крупные файлы: они съедают RAM, и
gunicorn-воркер уходит по SIGKILL (OOM) — страница отдаёт 500, в том числе
Googlebot. Так и случилось 2026-08-03 в 02:13 (`Worker was sent SIGKILL`,
`RuntimeError: Query interrupted`, 18 OOM-событий за сутки). Рабочие копии БД
класть на диск, рядом с оригиналом:
`data/dbs/.geom_work.duckdb` — как это делает `refresh_line_geometries.sh`.

Swap: 6 ГБ на двух файлах (`/swapfile` 2 ГБ с 2026-08-03, `/swapfile2` ещё
4 ГБ добавлен 2026-08-25 перед установкой Umami/Postgres — оба
прописаны в `/etc/fstab`, до 2026-08-03 swap отсутствовал вовсе, и
любой всплеск памяти сразу убивал воркер). `free -h` перед любой новой
резидентной службой (БД, Node-процесс) — на боксе уже было тесно.

**Окно обслуживания.** Пайплайнам нужен write-lock DuckDB, поэтому они
останавливают сервис. Хелсчек (cron `*/5`) поднимал его обратно прямо посреди
прогона, новый gunicorn снова забирал read-lock и `build_db`/`enrich` падали с
`Conflicting lock is held`. Теперь на время работ ставится флаг
`logs/.maintenance` — хелсчек его уважает (и игнорирует, если флагу > 2 ч,
чтобы упавший пайплайн не отключил хелсчек навсегда):

```bash
touch logs/.maintenance && sudo systemctl stop prevozni
# … build_db / enrich …
sudo systemctl start prevozni && rm -f logs/.maintenance
```

**Прод и рабочий чекаут — один и тот же бокс, один и тот же чекаут**
(`/home/deploy/transit-aggregator`, юзер `deploy`) — никаких отдельных
worktree не требуется, редактируй файлы прямо здесь и рестартуй сервис.
Этот бокс — не тот, что был раньше: по `git reflog` чекаут склонирован
заново 2026-07-31 15:16, весь `journalctl` начинается с 2026-07-31
14:43 (единственный boot) — переезд на новую машину случился после того,
как старый сервер (178.105.76.3, другие пути, другой юзер) лежал ~месяц
из-за незакрытого счёта у старого хостера (см. «История одного простоя»
ниже). `git reset --hard origin/main` из `deploy.sh`/GitLab CI стирает
незакоммиченное — коммить перед тем, как надолго уходить от бокса, если
не хочешь потерять работу при чужом деплое.

**История одного простоя (для контекста, не переоткрывать).** Трафик
рухнул с ~815 кликов/день (26.06) почти до нуля (2/день, 14.07) и
просидел там весь июль — причина: у старого хостера кончилась оплата,
сайт был недоступен ~месяц, из-за чего "Server error (5xx)" в Search
Console вырос до ~19–20K страниц. С переездом на этот бокс (31.07/01.08)
трафик и индексация начали восстанавливаться сами; к 21.08 показы дошли
до ~38K/день (~65% от пика). Это не код-баг и не лечится с этой
стороны — только время + не дать оплате повиснуть на новом хостере.

**Деплой** — только вручную, автодеплой-крона НЕТ (отключён 2026-06-04):

- `scripts/deploy.sh` прямо на боксе — **единственный рабочий путь сейчас**.
- ⚠️ кнопка ▶ в GitLab CI (stage `deploy`, `when: manual`) НЕ РАБОТАЕТ —
  `.gitlab-ci.yml` всё ещё хардкодит старый мёртвый сервер
  (`DEPLOY_HOST=178.105.76.3`, `root`, `/opt/prevozni`, `systemctl
  restart transit`, health-check по TCP :8000) и CI/CD-переменная
  `DEPLOY_SSH_KEY` не подходит новому боксу (в `authorized_keys`
  деплой-юзера только личный ключ `klaschuk@macbook.local`, не
  CI-ключ). Test-гейт (прогон pytest на каждый push в main/MR) при этом
  исправен и работает — сломан только сам SSH-деплой шаг. Починка
  требует провижининга отдельного CI SSH-ключа — намеренно не сделано
  молча, см. `docs/06_tech/deploy_guide.md` за шагами.

`scripts/deploy.sh`: `git reset --hard origin/main` → `pip install` →
minify CSS → `systemctl restart prevozni` → проверка `/health == 200`
(через unix-сокет). Сам скрипт был сломан на этом боксе тем же способом
(хардкодил `/opt/prevozni`, `transit`, TCP :8000) и не запустился бы
вообще; починен 2026-08-25 под текущие пути — `.gitlab-ci.yml` тогда же
почему-то поправлен не был.

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
- CSS: семантические переменные (--color-primary), mobile-first.
  `!important` — только для kill-switch `prefers-reduced-motion`; в
  app.mobile.css их 19 штук исторически, они не несущие (тот же
  селектор выиграл бы по порядку файлов) — при правках не плодить
- Git: conventional commits (feat:, fix:, docs:, data:, infra:)
- Inline styles: НОЛЬ (кроме динамического background:color на line-badge)
- Emoji: НОЛЬ (SVG иконки). Осталось: `✓`/`✕` в admin/dashboard.html,
  admin/backlinks.html и `✓` как значение stats-strip в stop_detail.html

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

## Документация

- `docs/README.md` — оглавление всей документации.
- Самые важные: `docs/06_tech/infrastructure.md` и `docs/06_tech/deploy_guide.md`
  (переписаны 2026-08-27 под текущий бокс; старые версии, описывавшие
  сервер до переезда, лежат в `docs/90_archive/06_tech/`).
- `docs/90_archive/` — архив, НЕ поддерживается, на него не опираться.
- ⚠️ GitLab CI кнопка ▶ деплоя (см. «Деплой» выше) сейчас нацелена на
  мёртвый старый сервер (178.105.76.3/root/opt-prevozni) и не сработает
  даже после правки хоста — SSH-ключ в CI/CD-переменной тоже устарел.
  Единственный рабочий путь — `scripts/deploy.sh` вручную на боксе.
  Детали и шаги починки: `docs/06_tech/deploy_guide.md`.

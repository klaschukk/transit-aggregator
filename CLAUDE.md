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

## Дисциплина изменений

Одна команда делает пп.1-3 за раз: `scripts/ship_local.sh` (chown → minify css/js → pytest → рестарт → /health).
Перед тем как считать любое изменение готовым, без исключений:

- `pytest` — весь набор зелёный (сейчас 1117+ тестов)
- правка CSS → `scripts/minify_css.py` (прод отдаёт `dist/*.css`, bare
  `systemctl restart` бандл не пересобирает)
- живой health-check после каждого изменения — команды в
  «Инфраструктура» ниже, не считать готовым по логам/статике
- коммит — только локально, с `Co-Authored-By`; **пуш в GitLab/origin
  делает только владелец руками**, сессии не пушат
- другие проекты на этом же боксе (popaj, valocheck, flight-punctuality)
  не трогать — подробности там же, в «Инфраструктура»
- не фабриковать данные расписаний/цен: источник не публикует маршрут —
  пропустить его, не гадать
- реклама: только ручные `ad_slot()`, 1 на страницу; **никогда** Google Auto Ads
  (`enable_page_level_ads`) и липкий anchor без явного «да» владельца после
  скриншотов phone/tablet/desktop (владелец 2026-09-21: «сайтом невозможно
  пользоваться»). Охранник в `base.html` не пускает рекламу в первый экран и ближе
  ~1.5 экранов друг к другу; anchor выключен флагом `ADS_MOBILE_ANCHOR`
- сессии Claude идут от root, а крон/gunicorn — от `deploy`: root-файлы ломают
  ночные скрейперы (PermissionError). `scripts/ship_local.sh` чинит владельца сам

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
| Analytics | Umami self-hosted (с 2026-10-04): `stats.flightpunctuality.online`, website ID `0bf85965-824a-4732-914a-d58f97cbb307`. Общий инстанс проекта flight-punctuality (Docker `umami`/`umami-db`, `127.0.0.1:3001`) — контейнеры не трогать; читать: `docker exec umami-db psql -U umami -d umami`. Грузится только при cookie_consent=all. Старый Cloud-ID `6af0f7f1…` больше не пишет. |
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
/balkan-loop/                        — хаб планировщика маршрута по Балканам (app/planner.py)
/balkan-loop/{slug}/                 — готовый маршрут (planner.PRESETS), индексируется
/balkan-loop/?from&to&days           — результат формы, noindex
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

`app/` — Flask (`__init__.py` create_app, `db.py`, `routes/{main,intercity,city,info,admin}.py`,
`templates/`, `static/`, `i18n.py` — большой плоский словарь: правь через grep+offset, не читай целиком),
`data/pipelines/` — скраперы и `build_db.py`, `scripts/` — деплой/крон/утилиты, `tests/` — pytest,
`docs/` — документация. Полное старое дерево — `docs/06_tech/history-2026.md`.


## БД (DuckDB)

Живые цифры — `scripts/preflight.sh` или `/health` → `checks.transit_db.tables`. Города: **7** (4 сербских +
3 черногорских). Международные рейсы влиты в `routes`/`trips` (отдельной таблицы нет). Пользовательские данные
(подписчики, отзывы, клики, A/B) — в `data/dbs/analytics.sqlite`, бэкап ночью в `data/backups/`.


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

**История простоя июль 2026** (старый хостер не оплачен, ~месяц лежал, GSC «5xx» ~20K) — не переоткрывать,
подробности в `docs/06_tech/history-2026.md`. Трафик восстанавливается сам с переезда 31.07.


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

## Что где (вместо старых чек-листов статуса)

- Статус за 1 вызов: `scripts/preflight.sh`. Изменение → живо и здорово за 1 вызов: `scripts/ship_local.sh` (`--fast` без pytest).
- Новый чат: `scripts/preflight.sh` → `docs/06_tech/handoff-2026-09-21.md` (состояние, блокеры владельца, открытые пункты).
- Что менялось: `git log`. Старые срезы и хронология переезда: `docs/06_tech/history-2026.md`.

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

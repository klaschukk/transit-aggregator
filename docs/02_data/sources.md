# Источники данных

## Городской транспорт

### GSP Beograd (bgprevoz.rs)
- **Данные:** Линии, остановки, расписание
- **Формат:** Веб (bgprevoz.rs API), скрапинг
- **Доступ:** Публичный
- **Приоритет:** ВЫСОКИЙ — основа городского раздела
- **Pipeline:** `data/pipelines/scrape_gsp.py`

### JGSP Novi Sad (gspns.co.rs)
- **Данные:** Линии и расписание Нови Сада
- **Формат:** Веб скрапинг
- **Pipeline:** `data/pipelines/scrape_gspns.py`, `scrape_gspns_schedule.py`

### JGP Niš (jgpnis.rs)
- **Данные:** Линии Ниша (+ остановки из Overpass)
- **Pipeline:** `data/pipelines/scrape_naissus.py`

### Kragujevac
- **Данные:** Линии и остановки из OSM (Overpass API)
- **Pipeline:** `data/pipelines/scrape_kragujevac.py`

### GTFS (data.gov.rs)
- **Данные:** Официальное GTFS-расписание Белграда (trips, stop_times)
- **Доступ:** Открытая лицензия
- **Pipeline:** `build_db.py` сам скачивает GTFS при сборке БД
  (НЕ запускать `import_gtfs.py` вручную)

### OpenStreetMap
- **Данные:** Координаты остановок, геометрия маршрутов
- **Формат:** Overpass API (JSON)
- **Доступ:** Бесплатно, открыто
- **Запрос:** `[out:json]; area["name"="Beograd"]; node["highway"="bus_stop"]; out;`
- **Pipeline:** `data/pipelines/enrich_stops_coords.py`

## Межгородской транспорт

### BusTicket4.me
- **Данные:** Расписания автобусов, цены
- **Формат:** Веб скрапинг (API)
- **Доступ:** Публичный сайт
- **Примечание:** ОСНОВНОЙ affiliate-партнёр (affiliateId=735, комиссия 2%
  с продажи) на всех обычных маршрутах. lineId для чекаута обновляет
  ночной `refresh_bt4_lineids.py`. См. `docs/05_monetization/partners.md`.
- **Pipeline:** `data/pipelines/scrape_intercity.py`

### Srbija Voz (srbvoz.rs)
- **Данные:** Расписание поездов
- **Формат:** Веб скрапинг
- **Доступ:** Публичный сайт
- **Pipeline:** `data/pipelines/scrape_srbvoz.py`

### Lasta и др. операторы — через polazak.rs
- **Данные:** Расписания сотен операторов (Lasta, Niš-Ekspres и др.)
- **Формат:** Веб скрапинг polazak.rs (не lasta.rs)
- **Pipeline:** `data/pipelines/scrape_lasta.py`

### Международные рейсы
- **Данные:** Рейсы Crna Gora, BiH, Hrvatska, Turska, Slovenija, MK
- **Pipeline:** `data/pipelines/scrape_international.py`

### Bookaway — ТОЛЬКО дальние направления
- **Данные/роль:** Не источник расписаний, а affiliate-партнёр
  (offer_id=34, aff_id=4033, через TUNE-трекер) ТОЛЬКО для дальних
  направлений (Азия) с 2026-06-10. Справочник: `app/affiliates/bookaway_far.json`.

## Обновление данных

- Ночной pipeline: `nightly_refresh.sh` по cron в **02:00**
  (скраперы → `build_db.py` → `refresh_bt4_lineids.py`)
- OSM enrichment: отдельный ночной cron

## Pipeline

```
Source (web) → scraper.py → data/raw/*.json → build_db.py → transit.duckdb
```

Flask читает только из transit.duckdb (read-only).

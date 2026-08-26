# CLAUDE.md — data/pipelines/

Наследует корневой `/home/deploy/transit-aggregator/CLAUDE.md` — читай
его первым. Здесь только то, что специфично для пайплайнов.

## DuckDB: не трогай `city_lines.number` в UPDATE

`city_lines` имеет `UNIQUE (city, number)`, и на неё ссылаются FK из
`city_line_stops` и `gtfs_trips`. DuckDB 1.2.1 бросает
`ConstraintException: ... still referenced by a foreign key in a
different table` на **любой** UPDATE, трогающий `number` — даже если
`id` не меняется, даже отдельным `executemany`, даже переставляя
порядок шагов так, чтобы FK-child ещё не существовал. Проверено 4
разными способами в рамках расследования кириллица→латиница для
бейджей линий — не тратить время на повтор, это engine-level
ограничение, не баг в коде. `city_stops.name`/`city_lines.name`
обновлять можно (не под UNIQUE) — этим и пользуется
`_latinise_display_names()`.

Если нужна латиница в `number` — делать на **render-слое** (Jinja
`|latin` фильтр в `app/__init__.py`, уже так и сделано для бейджей),
не в БД. Только НЕ применять фильтр к `data-line`/`data-num`
атрибутам — они матчатся байт-в-байт с `/api/stop-arrivals`.

## Локи и окно обслуживания

Пайплайнам нужен write-lock DuckDB. Если `prevozni.service` жив во
время запуска — падает `Conflicting lock is held`. Всегда:

```bash
touch ../../logs/.maintenance && sudo systemctl stop prevozni
venv/bin/python -u data/pipelines/build_db.py
# … прочие шаги …
sudo systemctl start prevozni && rm -f ../../logs/.maintenance
```

Хелсчек (cron `*/5`) уважает `.maintenance`, но игнорирует его, если
флагу больше 2 часов — не оставлять зависший пайплайн дольше этого.

## `/tmp` — это RAM, не диск

Рабочие копии БД (`.geom_work.duckdb` и т.п.) класть на диск рядом с
`data/dbs/transit.duckdb`, не в `/tmp`. `transit.duckdb` ~300 МБ, в
`/tmp` (tmpfs) это съедает реальную оперативную память и раньше уже
роняло gunicorn-воркер по OOM (2026-08-03).

## Route memory / dedup

`build_db.py` восстанавливает "known routes" между прогонами — если
скрейпер что-то не нашёл в этот раз, но линия была раньше, она не
пропадает молча. Смотри лог-строку `Route memory: N known, restored M
missing this run` после билда — если restored необычно большое число,
что-то у скрейпера сломалось (не в pipeline).

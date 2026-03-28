# Transit Serbia

Сербский агрегатор общественного транспорта. Объединяет городской транспорт (GSP Белград) и межгородские автобусы/поезда в одном месте.

## Стек

- **Backend:** Flask (Python)
- **База данных:** DuckDB (read-only, пересобирается пайплайнами)
- **Инфра:** RKE2/K8s (pumba/simba/timon) + ArgoCD + Cloudflare
- **Аналитика:** Umami (self-hosted)
- **Монетизация:** Google AdSense

## Запуск локально

```bash
# Установить зависимости
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Собрать базу данных
python data/pipelines/build_db.py

# Запустить dev-сервер
python run.py
```

Открыть: http://localhost:5000

## Структура проекта

```
transit/
├── app/
│   ├── routes/          # Flask blueprints
│   ├── templates/       # Jinja2 шаблоны
│   └── static/          # CSS, JS
├── data/
│   ├── pipelines/       # ETL скрипты (скраперы, build_db.py)
│   └── dbs/             # transit.duckdb (gitignored)
└── docs/                # Проектная документация
```

## URL структура

| URL | Описание |
|-----|----------|
| `/` | Главная, поиск |
| `/rute/` | Все маршруты |
| `/rute/{slug}/` | Расписание маршрута |
| `/voznja/{from}-do-{to}/` | SEO-страница городской пары |
| `/gradski/beograd/` | Городской транспорт Белград |
| `/gradski/beograd/linija/{slug}/` | Линия |
| `/sitemap.xml` | Sitemap |

## Документация

Вся документация в папке `docs/` — стратегия, данные, SEO, монетизация, инфра.

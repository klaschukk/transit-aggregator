# CLAUDE.md — Transit Serbia Project Context

## Project Overview

**Transit Serbia** — сербский агрегатор общественного транспорта (programmatic SEO + реальные данные).
Объединяет городской транспорт (GSP Белград) и межгородские автобусы/поезда в одном месте.

- **Стек:** Flask + DuckDB + RKE2/K8s + ArgoCD + Cloudflare
- **Цель:** €500/мес за первые 6 месяцев, €1000+/мес к месяцу 18
- **Масштаб:** 10K–50K индексируемых страниц (городские пары, остановки, маршруты)
- **Фаза:** Foundation (март 2026)
- **Сервер:** montiko (Подгорица), K8s кластер: pumba/simba/timon
- **GitLab:** https://gitlab.com/klaschukk/transit-aggregator

## Язык

- Документация и общение: **русский**
- Код, комментарии, коммиты: **английский**
- Переменные и имена файлов: **английский**

## Стек

| Слой | Технология |
|------|-----------|
| Backend | Flask (Python) |
| База данных | DuckDB (read-only, file-based) |
| Инфра | RKE2/K8s (pumba/simba/timon) |
| Деплой | ArgoCD (GitOps, по тегам) |
| CDN/WAF | Cloudflare |
| Аналитика | Umami (self-hosted) |
| Монетизация | **Google AdSense only** |
| Данные | Веб-скрапинг + GTFS |

## Референсы дизайна и UX

- **Transport Burgas** (Болгария) — мобильное приложение городского транспорта (50K+ загрузок, 3.7★).
  Референс для UX городского транспорта: живые остановки, карта маршрута, список линий.
- **BusTicket4.me** (Черногория/регион) — агрегатор межгородских автобусов.
  Референс для формы поиска, таблицы рейсов, страниц маршрутов.

Принцип: берём лучшее из обоих, адаптируем под веб (не мобильное приложение).

## URL архитектура

```
/                               — главная, форма поиска
/rute/                          — все маршруты
/rute/{slug}/                   — расписание маршрута
/voznja/{from}-do-{to}/         — SEO-страница городской пары
/pretraga/                      — результаты поиска
/gradski/{city}/                — городской транспорт (Белград)
/gradski/{city}/linija/{slug}/  — линия
/gradski/{city}/stajaliste/{slug}/ — остановка
/sitemap.xml
/robots.txt
```

## Структура проекта

```
transit/
├── CLAUDE.md
├── README.md
├── config.py              ← Flask конфиг (DuckDB путь, секреты)
├── run.py                 ← dev-сервер
├── requirements.txt
├── docs/
│   ├── 00_strategy/       ← roadmap.md, competitor_analysis.md
│   ├── 01_brand/          ← brand.md
│   ├── 02_data/           ← sources.md
│   ├── 03_product/        ← page_templates.md
│   ├── 04_seo/            ← seo_strategy.md
│   ├── 05_monetization/   ← monetization_plan.md (AdSense only)
│   ├── 06_tech/           ← infrastructure.md
│   └── 07_legal/          ← legal.md
├── app/
│   ├── __init__.py
│   ├── db.py              ← DuckDB подключение (read-only)
│   ├── routes/
│   │   ├── main.py        ← главная, поиск, sitemap, robots
│   │   ├── intercity.py   ← межгородские маршруты
│   │   └── city.py        ← городской транспорт
│   ├── templates/         ← Jinja2 шаблоны
│   └── static/
│       ├── css/main.css   ← CSS custom properties + BEM
│       └── js/search.js   ← автокомплит городов
├── data/
│   ├── pipelines/
│   │   └── build_db.py    ← собирает transit.duckdb из raw данных
│   ├── dbs/               ← transit.duckdb (gitignored)
│   └── raw/               ← сырые данные (gitignored)
└── scripts/
```

## Ключевые решения

1. **SEO-first** — каждое решение через призму SEO
2. **Программатический контент** — страницы из структурированных данных
3. **DuckDB read-only** — Flask только читает, пайплайны пересобирают
4. **Мобильный приоритет** — 70%+ трафика с мобильных
5. **AdSense only** — единственная монетизация, никакого affiliate
6. **Скрапинг** — публичных API в Сербии нет

## Источники данных

| Источник | Данные | Доступ |
|---------|--------|--------|
| gsp.rs | Линии и остановки GSP Белград | Скрапинг |
| srbijavoz.rs | Расписание поездов | Скрапинг |
| busticket4.me | Межгородские автобусы | Скрапинг |
| lasta.rs | Маршруты Lasta | Скрапинг |
| OpenStreetMap | Координаты остановок | Overpass API (бесплатно) |

## Конкуренты (кратко)

| Сайт | Слабость | Наш ответ |
|------|---------|-----------|
| busticket4.me | Нет городского, платный | Бесплатно + всё в одном |
| gsp.rs | Плохой UX, нет SEO | Современный мобильный UX |
| srbijavoz.rs | SSL ошибки, неудобный | Агрегируем их данные |

## Конвенции кода

- Python: PEP 8, type hints, f-strings, макс 120 символов
- Docstrings: Google style, только публичные функции
- Templates: Jinja2, 2 пробела отступ
- CSS: BEM naming, custom properties (--color-primary, --space-4)
- Git: conventional commits (feat:, fix:, docs:, data:, infra:)
- Ветки: feature/, fix/, data/, docs/

## Текущий статус (март 2026)

- [x] Flask скелет + DuckDB схема + sample data
- [x] Все маршруты: межгородские + городской транспорт Белград
- [x] CSS дизайн система + JS автокомплит
- [x] sitemap.xml + robots.txt
- [x] Документация (стратегия, SEO, монетизация, инфра, легаль, конкуренты)
- [ ] Дизайн через uipro-cli
- [ ] Скраперы (GSP, srbijavoz, busticket4.me)
- [ ] Деплой K8s + ArgoCD
- [ ] Домен + Cloudflare
- [ ] Google AdSense

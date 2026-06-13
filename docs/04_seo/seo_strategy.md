# SEO Стратегия

## Программатические страницы

### 1. Городские пары — главный приоритет
URL: `/voznja/{from}-do-{to}/`

Целевые запросы:
- "beograd novi sad autobus"
- "prevoz beograd nis cena"
- "autobusi beograd subotica red voznje"
- "kako doci od beograda do novog sada"

Потенциал: 50+ пар × 3–5 вариантов = **150–250 ключевых слов**

### 2. Страницы маршрутов
URL: `/rute/{slug}/`

Целевые запросы: конкретные маршруты с расписанием.

### 3. Остановки Белград
URL: `/gradski/beograd/stajaliste/{slug}/`

Целевые запросы: "autobus stajaliste [название]", "gsp stajaliste"
Потенциал: 2000+ остановок GSP = **2000+ страниц**

### 4. Линии
URL: `/gradski/beograd/linija/{num}/`

Целевые запросы: "linija 11 beograd", "gsp linija 25 stajalista"

## Schema Markup

| Страница | Schema |
|---------|--------|
| Главная | `WebSite` + `SearchAction` |
| Маршрут | `ItemList` + `BusTrip`/`TrainTrip` |
| Остановка | `BusStation` |
| Городская пара | `FAQPage` |

## Технический SEO — чеклист (закрыт, июнь 2026)

- [x] `sitemap.xml` (4600+ URL: маршруты + остановки + линии)
- [x] `robots.txt`
- [x] Canonical URLs
- [x] hreflang — все 3 языка live (sr + en + ru)
- [x] Open Graph теги (+ Twitter Cards, og:locale:alternate)
- [x] Core Web Vitals — мониторится, LCP в бюджете
- [x] Mobile-first (44px touch targets)
- [x] Google Search Console подключён (sitemap submitted)

## Актуальные направления (июнь 2026)

- **Генерик «red vožnje autobusa i vozova»** — high-CTR возможность по
  GSC-анализу 2026-06-08 (трафик идёт на городские линии, CTR зажат
  виджетами Google; генерик-запросы — шанс его поднять).
- **Гайды `/vodici/`** — long-form контент под длинный хвост.
- **SEO-страницы дальних направлений** (фаза 2 far destinations,
  Азия + Bookaway-CTA) — ещё НЕ сделаны.

## Контентная стратегия

Каждая страница городской пары генерирует:
- Уникальный H1
- Описание маршрута
- FAQ блок (3–5 вопросов о маршруте)
- Таблица рейсов (динамически из DuckDB)

Всё из структурированных данных — ноль ручного труда.

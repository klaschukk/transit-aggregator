# SEO Стратегия

## Программатические страницы

### 1. Страницы городских пар (приоритет 1)
URL: `/voznja/{from}-do-{to}/`
Примеры: beograd-do-novi-sad, beograd-do-nis, novi-sad-do-nis

**Целевые запросы:**
- "beograd novi sad autobus"
- "prevoz beograd nis cena"
- "autobusi beograd subotica red voznje"

Потенциал: 50+ городских пар × 3–5 вариантов запроса = 150–250 ключевых слов

### 2. Страницы маршрутов (приоритет 2)
URL: `/rute/{slug}/`
Примеры: beograd-novi-sad, beograd-nis

Целевые запросы: конкретные маршруты с расписанием

### 3. Страницы остановок Белград (приоритет 3)
URL: `/gradski/beograd/stajaliste/{slug}/`

Целевые запросы: "autobus stajaliste [название]", "linija [N] stajalista"

### 4. Страницы линий (приоритет 4)
URL: `/gradski/beograd/linija/{num}/`

## Schema Markup

- Главная страница: `WebSite` + `SearchAction`
- Страница маршрута: `ItemList` + `BusTrip`/`TrainTrip`
- Страница остановки: `BusStation`/`TrainStation`
- Городская пара: `FAQPage` (частые вопросы о маршруте)

## Техническое SEO

- [ ] sitemap.xml (все маршруты + остановки)
- [ ] robots.txt
- [ ] canonical URLs
- [ ] hreflang (sr, en потом)
- [ ] Open Graph tags
- [ ] Core Web Vitals оптимизация
- [ ] Мобильная версия (критично — 70%+ трафика с мобильных)

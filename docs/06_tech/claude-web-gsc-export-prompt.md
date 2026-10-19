# Промпт для Claude web: выгрузка Google Search Console (только чтение)

Зачем: API GSC на боксе не настроен, а правки title/сниппетов без данных — вслепую. Нужны запросы и страницы с позициями,
отдельно туристические маршруты и языковые версии (/en/ /ru/ /bg/), чтобы мерить эффект правок от 2026-10-15/19.
Перед запуском владелец входит в Search Console (свойство `sc-domain:prevozni.com`) в этом браузере.
Ответ агента принести в сессию Claude Code.

```
You are helping the owner of prevozni.com (Serbian/Balkan bus timetables). I am logged into Google Search Console in this browser, property "sc-domain:prevozni.com". This is READ-ONLY research.

HARD RULES
- Do not change any setting, do not submit sitemaps, do not request indexing, do not remove URLs, do not add users.
- Only use Performance -> Search results, filters, date ranges and the table views. Copy numbers exactly as shown; if something is missing, say "not shown".
- Search type: Web. Use the "Last 3 months" range unless a step says otherwise.

STEPS
1. Totals for the last 3 months and for the last 28 days: clicks, impressions, average CTR, average position.
2. QUERIES tab, last 3 months, sorted by clicks: the top 150 rows (query, clicks, impressions, CTR, position).
3. PAGES tab, last 3 months, sorted by clicks: the top 150 rows (page, clicks, impressions, CTR, position).
4. Tourist corridors. For each of these words, set a Query filter "contains" and record the top 15 queries (query, clicks, impressions, CTR, position): budva, kotor, podgorica, tivat, herceg, sarajevo, mostar, dubrovnik, tirana, skadar, ohrid. Remove the filter after each one.
5. Language versions. Set a Page filter "URLs containing" and record totals (clicks, impressions, CTR, position) plus the top 20 pages for each: /en/ , /ru/ , /bg/ .
6. Same filter idea for sections, totals only: /gradski/ , /rute/ , /voznja/ , /balkan-loop/ .
7. Compare: date range "Compare last 28 days to previous period". Record the 20 queries with the biggest click LOSS and the 20 with the biggest click GAIN (query, clicks before, clicks after, position before, position after).
8. Countries tab, last 3 months: top 15 countries (clicks, impressions, CTR, position).
9. Devices tab: mobile / desktop / tablet totals.

FINAL REPORT: one section per step, each table as CSV in a code block (header row first). No commentary except a short list of anything that looked broken (e.g. a filter that returned nothing, a tab that would not load).
```

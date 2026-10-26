# Промпт для Claude web: выгрузка GSC, часть 2 (досбор после падения браузера 2026-10-20)

Шаги 1–4 (budva, kotor, podgorica, tivat, herceg) уже есть — сводка в `handoff-2026-09-21.md`, «Апдейт 2026-10-20».
Этот промпт добирает остальное. Владелец входит в Search Console (`sc-domain:prevozni.com`) в этом браузере, ответ несёт в Claude Code.

```
You are helping the owner of prevozni.com (Serbian/Balkan bus timetables). I am logged into Google Search Console in this browser, property "sc-domain:prevozni.com". This is READ-ONLY research. It continues an earlier export that stopped halfway; do ONLY the steps below.

HARD RULES
- Do not change any setting, do not submit sitemaps, do not request indexing, do not remove URLs, do not add users.
- Only use Performance -> Search results, filters, date ranges and the table views. Copy numbers exactly as shown; if something is missing, say "not shown".
- Search type: Web. Use the "Last 3 months" range unless a step says otherwise.
- After every step, output that step's CSV right away (so a browser crash loses nothing), then continue.

STEPS
4. Tourist corridors (rest). For each word, set a Query filter "contains" and record the top 15 queries (query, clicks, impressions, CTR, position): sarajevo, mostar, dubrovnik, tirana, skadar, ohrid. Remove the filter after each one.
5. Language versions. Set a Page filter "URLs containing" and record totals (clicks, impressions, CTR, position) plus the top 20 pages for each: /en/ , /ru/ , /bg/ .
6. Same filter idea for sections, totals only: /gradski/ , /rute/ , /voznja/ , /balkan-loop/ .
7. Remove all filters. Date range "Compare last 28 days to previous period", QUERIES tab. Record the 20 queries with the biggest click LOSS and the 20 with the biggest click GAIN (query, clicks before, clicks after, position before, position after).
8. Back to "Last 3 months", no filters. Countries tab: top 15 countries (country, clicks, impressions, CTR, position).
9. Devices tab, last 3 months, no filters: mobile / desktop / tablet (device, clicks, impressions, CTR, position).

FINAL REPORT: one section per step (4-sarajevo ... 4-ohrid, 5-en, 5-ru, 5-bg, 6, 7-loss, 7-gain, 8, 9), each table as CSV in a code block (header row first). No commentary except a short list of anything that looked broken (e.g. a filter that returned nothing, a tab that would not load).
```

# Промпт для Claude web: AdSense + клики Bookaway + разбор сайтов (только чтение), 2026-10-23

Перед запуском владелец входит в AdSense и в bookaway2.hasoffers.com в этом браузере. Ответ принести в Claude Code:
там он сравнивается с собственным разбором (`docs/06_tech/ads-analysis-2026-10-23.md`).

```
You are helping the owner of three websites on one Google AdSense account (pub-1417138799653355): prevozni.com (Balkan bus timetables), valocheck.com (Valorant stats), flightpunctuality.online (flight delay statistics). I am logged into AdSense and into the Bookaway affiliate panel (bookaway2.hasoffers.com) in this browser. This is READ-ONLY research.

HARD RULES
- Do not change any setting anywhere. Do not click "Request review", do not switch Auto ads on or off, do not create or edit ad units, do not touch payments or tax forms, do not add or remove sites.
- On the websites only read pages: do not submit forms and never click ads or affiliate buttons.
- Copy numbers exactly as shown. If something is missing, write "not shown". Do not guess.

PART A — AdSense
1. Sites page: for each site, approval status, status details, last updated date, and the full text of any explanation shown when you open the site row (read only).
2. Policy center: every issue listed, the affected pages/URLs shown, and dates.
3. Reports, last 28 days, broken down by Site: estimated earnings, page views, page RPM, impressions, clicks, CTR. Then for prevozni.com only, broken down by Ad unit (top 15).
4. Ads -> By site: for each site, is Auto ads ON or OFF? Only read the toggle, do not change it.

PART B — Bookaway clicks (bookaway2.hasoffers.com)
5. Reports -> Performance (or Stats), date range 2026-10-14 to today, grouped by Date and Sub ID 1 (aff_sub): clicks and conversions, top 30 rows by clicks.
6. Same range grouped by Sub ID 2 (aff_sub2).
7. Same range grouped by Country (top 15). If available, also by Browser, Device or Hour for 2026-10-22.
8. Gross vs unique clicks per day, and any "rejected clicks", traffic-quality or fraud notices, if the panel shows them.

PART C — the sites through a reviewer's eyes (read-only browsing, phone width if you can)
9. valocheck.com and flightpunctuality.online: open the home page and 3 random pages of each type (valocheck: agent "a vs b" pages under /agents/, map guides, player pages, pro pages; flightpunctuality: route pages, flight pages, airline pages). For each page: did it load (any error/503), roughly how many words of unique text, does it look near-identical to its siblings, any numbers that look obviously wrong.
10. As an AdSense reviewer: top 5 reasons each of these two sites looks like "low value content", ranked, each with example URLs.
11. For all 3 sites: where would ads fit naturally on each page type (after which block), at most 2 per page, never in the first screen on a phone.

FINAL REPORT: one section per step, tables as CSV in code blocks (header row first). No commentary except a short list of anything broken or suspicious.
```

# Промпт для Claude web (с доступом к браузеру): настройки в AdSense / Search Console / BT4

Вставлять в claude.ai, где владелец залогинен в AdSense (pub-1417138799653355) и Search Console (sc-domain:prevozni.com).
Зачем: то, что не меняется из кода. Результат: отчёт BEFORE → AFTER по каждому пункту.

```
You are helping the owner of prevozni.com (a Serbian public-transport site). I am logged into Google AdSense (pub-1417138799653355) and Google Search Console (property sc-domain:prevozni.com) in this browser. The site's code is already fixed on the server; what remains are dashboard settings that cannot be changed from code.

HARD RULES
- Work read-first: for every setting, record its CURRENT state, then change it, then record the NEW state.
- Change ONLY what is listed below. Never touch Payments, tax info, identity verification, bank details, Account, user access, ads.txt or site verification.
- If a screen differs from what I describe, or a dialog would change anything else, STOP and report instead of guessing.
- Do not click "apply" on any AdSense "Opportunities"/recommendations.

PART A - AdSense
A1. Ads > By site > prevozni.com: turn Auto ads OFF. If it shows per-format options instead, disable ALL of them: Overlay formats (Anchor ads, Side rail ads, Vignette ads) and In-page formats (banner, multiplex, etc.). If an "Ad load" slider is still visible, set it to the lowest ("Fewer ads"). WHY: the owner wants only his own manual ad units (max 1 per page); Auto ads made the site unusable.
A2. Optimization > Experiments (also the yellow banner "One or more Auto optimize experiments are running"): list every running experiment with its type. End/stop any experiment that adds or changes ad formats, ad load, placements or Auto ads. Only report the rest.
A3. Privacy & messaging > European regulations (GDPR) message for prevozni.com: report its current layout/style. On mobile it shows as a full-screen dialog that hides the whole page (schedule and buy buttons) until answered. If a less obstructive layout exists (banner / footer / non-fullscreen), choose the least obstructive that stays compliant and publish it. Keep the default legal text and keep the "Do not consent" and "Manage options" buttons. Do NOT disable the message or GDPR handling.
A4. Privacy & messaging: confirm "Ad blocking recovery" is NOT active; if it is, turn it off.
A5. Ads > Ad units: only REPORT how many manual ad units exist and their names. Do not edit or delete.
A6. Policy center + Sites: report the status of prevozni.com and any warnings.

PART B - Search Console (sc-domain:prevozni.com)
B1. Indexing > Pages: for the issues "Blocked by robots.txt" and "Not found (404)" click "Validate fix" if available (robots.txt was verified fully open for Googlebot on 2026-09-13; the report shows old crawl data). Do NOT try to fix or validate "Excluded by noindex tag" or "Alternate page with proper canonical tag" - they are intentional. Report the new validation state.
B2. Sitemaps: make sure https://prevozni.com/sitemap.xml is submitted with status Success (it lists 5 child sitemaps: core, routes, lines, stops, far). Submit it if missing. Report discovered URLs per child sitemap.
B3. Settings > Crawl stats: report the last 90 days (total requests, average response time, share of 404 / 5xx / blocked). Read-only.
B4. Security & Manual actions: report whether any issue exists.
B5. Performance, last 28 days: give me tables of the top 15 pages and the top 15 queries by impressions, with clicks, CTR and average position. Also state the totals.
B6. Experience > Core Web Vitals: report mobile and desktop status counts.
B7. URL Inspection: inspect https://prevozni.com/ , https://prevozni.com/rute/beograd-novi-sad/ and https://prevozni.com/gradski/beograd/ . If any says "URL is not on Google", click "Request indexing" (only these three). Report each result.

PART C - BusTicket4 affiliate panel (only if I am logged in at busticket4.me; READ-ONLY)
C1. For affiliate ID 735, report daily clicks/orders/sales and commission for the last 90 days and the total. If the panel shows zero orders, say so explicitly.

FINAL REPORT: a short table per item with BEFORE -> AFTER, plus anything you could not do or found unexpected. Nothing beyond the items above.
```

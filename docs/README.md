# docs/ — оглавление

Структура документации Prevozni. Обновлено: 2026-06-12.

Папки идут по номерам: 00 — стратегия, 01–07 — рабочие разделы,
90_archive — исторические снапшоты.

Актуальные факты (на 2026-06-12): партнёрка — BusTicket4 (affiliateId 735,
комиссия 2%) на всех обычных маршрутах; Bookaway (offer_id=34, aff_id=4033,
TUNE-трекер) — только дальние направления (Азия); FlixBus убран; AdSense
live (ca-pub-9538841764038287). База: 569 маршрутов, 3931 рейс,
69 операторов, 661 городская линия, 4 города, 870 тестов.

## 00_strategy/ — стратегия и рост

- `roadmap.md` — роадмап проекта: фазы, таблица статистики, конкуренты.
- `revenue-plan-2026.md` — главный стратегический документ: финмодель, конкурентный анализ (§2 — канонический), 3 фазы роста, риски, бюджет.
- `backlinks-tracker.md` — скорборд backlink-кампании: цели 20/50/100 ссылок, weekly snapshot, правила, недельный воркфлоу.
- `backlinks-targets.csv` — база ~199 outreach-целей со статус-колонками. **Путь захардкожен в коде — не переименовывать и не перемещать.**
- `price-alerts-TEMPLATE.md` — шаблон еженедельного ревью price-alert пайплайна: скорборд, health-сигналы, SQL-запросы.
- `pitch-templates/` — шаблоны outreach-писем. **`*.tpl` рендерятся `app/outreach/templates.py` — пути захардкожены, не перемещать.**
  - `broken-link.md` / `broken_link_en.tpl` — broken-link outreach: гайд + машинный шаблон письма.
  - `expat-forum.md` / `expat_forum_en.tpl` — helpful-reply в Reddit/форумах/FB-группах (гайд + шаблон).
  - `operator-reciprocal.md` / `operator_reciprocal_en.tpl` — reciprocal-link письмо перевозчику (гайд + шаблон).
  - `russian-diaspora.md` / `russian_diaspora_ru.tpl` — outreach в RU-диаспору: Telegram, vc.ru/Habr, FB/VK (гайд + RU-шаблон).
  - `tourism-board.md` / `tourism_board_en.tpl` / `tourism_board_sr.tpl` — письма в туристические организации/госорганы (гайд + EN/SR шаблоны).
  - `travel-blog.md` / `travel_blog_en.tpl` — персонализированный pitch travel-блогерам (гайд + шаблон).
  - `follow_up_en.tpl` — единственный follow-up через 7 дней.
  - `generic_en.tpl` — fallback-шаблон для категорий без специализированного письма.

## 01_brand/ — бренд

- `brand.md` — бренд-бук: название, позиционирование, аудитория, тон, цвета.

## 02_data/ — данные

- `sources.md` — каталог источников данных и схема pipeline (скраперы, GTFS).

## 03_product/ — продукт

- `page_templates.md` — спецификация типов страниц сайта.

## 04_seo/ — SEO

- `seo_strategy.md` — стратегия программатического SEO: типы страниц, schema, контент.

## 05_monetization/ — монетизация

- `partners.md` — сравнение affiliate-партнёров и fallback-цепочка; single source of truth для `app/affiliates/`.
- `adsense-strategy.md` — стратегия размещения AdSense: инвентарь слотов, manual vs auto, CWV-защита, RPM-бенчмарки.
- `adsense-launch-checklist.md` — ранбук дня одобрения AdSense: env-вары, ad units, верификация, отчётность.
- `bookaway_postback.md` — почему у Bookaway нет S2S postback и как вручную сверять комиссии через клик-лог `ba_clicks` и subid.

## 06_tech/ — техдоки (живые)

- `infrastructure.md` — инфраструктура: сервер, nginx, Cloudflare, systemd, мониторинг.
- `deploy_guide.md` — гайд по деплою: DNS, nginx, systemd env, nightly-пайплайн, troubleshooting.
- `gsc-setup.md` — сетап GSC API service account для `scripts/weekly_seo.sh`. **На файл ссылаются CLAUDE.md и weekly_seo.sh — не перемещать.**
- `sentry-setup.md` — сетап Sentry: DSN, observability.py, sentry_notify.py для cron, /health-контракт.
- `ab-process.md` — процессный гайд по A/B-экспериментам: гипотезы, sample size, вердикты, анти-паттерны.
- `email-deliverability.md` — доставляемость email: SPF/DKIM/DMARC, Mailgun, warm-up, suppression.
- `og-images-2026-04-26.md` — дизайн-док системы динамических OG-карточек (`app/og.py`): 6 типов, кэширование, тесты.
- `og-samples/` — 6 эталонных PNG OG-карточек — референс для визуальной регрессии при изменении layout `og.py`.
- `sitemap-freshness-2026-04-27.md` — дизайн-док per-URL lastmod в sitemap + статус follow-up'ов (что живо, что deferred).
- `incident-2026-04-25-line-geometries.md` — RCA инцидента: nightly стирал `line_geometries`; фиксы — preserve при rebuild + /health probes.

## 07_legal/ — юридическое

- `legal.md` — юридические требования: disclaimer, Privacy Policy, GDPR, скрапинг.

## 90_archive/ — исторические снапшоты, не поддерживаются

Разовые отчёты, выполненные ранбуки и устаревшие планы. Лежат как есть,
факты в них соответствуют своей дате и **не обновляются** — не читать как
актуальное состояние. Подпапка = откуда файл переехал.

- `03_product/` — скриншоты сдачи фичи отзывов (май 2026): форма, блок на маршруте, админка модерации.
- `04_seo/`
  - `seo_checklist.md` — pre-launch SEO-чеклист (выполнен; запуск давно состоялся).
  - `stop_prose_samples.md` — before/after примеры SEO-прозы остановок (фича живёт в `app/content/stop_prose.py`).
  - `gsc_setup.md` — ручное подключение GSC/Bing/Yandex (выполнено; не путать с живым `06_tech/gsc-setup.md` про API).
- `05_monetization/`
  - `monetization_plan.md` — апрельский план «только AdSense, никакого affiliate» — противоречит текущей реальности, заменён `00_strategy/revenue-plan-2026.md`.
  - `dashboard-2026-04.png` — скриншот /admin/revenue эпохи Bookaway (апрель).
- `06_tech/`
  - `activation-checklist.md` — разовый ранбук активации апреля (GSC, AdSense, SMTP) — выполнен.
  - `domain_switch.md` — разовый ранбук переключения на prevozni.com — выполнен.
  - `perf-baseline.md` + `perf-before-route.png` — перф-отчёт 2026-04-20 (budgets в `scripts/perf_check.sh` выставлены от него).
  - `perf-baseline-mobile.md` + `perf-mobile-rute-before.jpg` — мобильный перф-проход 2026-04-24 (after-скриншот утерян — был дублем before).
  - `p28-mobile-polish-plan.md` — план мобильной полировки P28 — отработан и перекрыт.
  - `chrome-parity-final-2026-04-26.md` — отчёт о закрытии chrome-parity гэпов.
  - `hub-parity-2026-04-26.md` — отчёт о подтяжке 4 hub-страниц до паритета.
  - `hub-indexing-2026-04-27.md` — аудит «Discovered not indexed» + внедрение `_browse_hubs.html`.
  - `link-audit-2026-04-26.md` — аудит внутренних ссылок до/после (повторяем через `scripts/audit_links.py`).
  - `sitemap-audit-2026-04-26.md` — аудит sitemap на soft-404 (вырезаны операторы без priced trips).
  - `sitemap-thin-routes-cut-2026-04-26.md` — **decision record в силе**: маршруты по trip-count НЕ резать.
  - `sitemap-freshness-followup-2026-04-27.md` — детали follow-up'ов freshness (выжимка влита в живой `06_tech/sitemap-freshness-2026-04-27.md`).
  - `qa-2026-04-26.md` — end-of-day QA-свип по 19 страницам.
  - `lighthouse-2026-04-26.md` — Lighthouse-прогон 6 топ-страниц + фикс Leaflet на /gradski/.
  - `template-parity-2026-04-26.md` — отчёт о подтяжке stop_detail/line_detail до паритета.

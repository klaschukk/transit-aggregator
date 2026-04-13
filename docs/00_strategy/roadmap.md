# Roadmap — Prevozni

## Цель

Бесплатный агрегатор общественного транспорта Сербии и Балкан с реальными данными,
3 языка, монетизация через Bookaway affiliate.

**URL:** https://prevozni.com
**Статус:** В продакшне, автономный

---

## ✅ Фаза 1: Фундамент (готово)

- [x] Flask + DuckDB + Gunicorn + nginx + Cloudflare
- [x] Sitemap (3600+ URL), robots.txt, hreflang теги
- [x] Документация (план, данные, SEO, монетизация)
- [x] UI/UX дизайн (teal/white minimal, mobile-first)
- [x] CSS дизайн-система (1300+ строк, 0 !important)
- [x] 23 шаблона + 8 partials

---

## ✅ Фаза 2: Данные (готово)

- [x] Скрапер GSP Belgrade (bgprevoz.rs) — 514 линий, 4002 остановки
- [x] Скрапер JGSP Novi Sad (gspns.co.rs) — 61 линия + 825 OSM остановок
- [x] Скрапер межгородских (busticket4.me) — 220+ маршрутов
- [x] Скрапер международных (busticket4.me intl) — 116 маршрутов, 458 рейсов
- [x] Скрапер Srbija Voz (srbvoz.rs) — 88 поездов
- [x] Скрапер Lasta/polazak.rs — 1896 рейсов
- [x] Скрапер Niš (jgpnis.rs)
- [x] Скрапер Kragujevac
- [x] OSM enrichment — 96% остановок с GPS
- [x] GTFS импорт data.gov.rs (Belgrade) — 87K trips, 2.3M stop_times
- [x] GTFS Novi Sad из расписания GSPNS — 6.5K trips
- [x] Nightly cron pipeline (2:00) — auto-refresh

---

## ✅ Фаза 3: Продукт (готово)

- [x] 23 шаблона: home, route_index, route_detail, city_pair,
      city_transport, line_detail, stop_detail, search_results,
      destinations, carriers, stations, about, contact, 404, 500
- [x] Mobile-first, 44px touch targets, focus-visible
- [x] SEO: JSON-LD (WebSite, Organization, BreadcrumbList, FAQ, ItemList)
- [x] Open Graph + Twitter Cards + hreflang × 3
- [x] Performance: connection pooling + TTL cache (0.02-0.10s)
- [x] 325 pytest тестов passing
- [x] 100% SEO clean на 3600+ страницах

---

## ✅ Фаза 4: Деплой (готово)

- [x] Домен prevozni.com + Cloudflare (Full SSL)
- [x] systemd transit.service + gunicorn 4 workers
- [x] nginx reverse proxy (Cloudflare-only IPs, security headers)
- [x] Healthcheck cron (*/5 min, auto-restart)
- [x] Nightly refresh cron (02:00) — full data pipeline
- [x] Umami analytics
- [x] Google Search Console — sitemap submitted
- [x] Yandex verification meta tag support
- [x] Telegram bot для контакт-формы
- [x] 3 языка: sr (default), en, ru — full i18n

---

## ✅ Фаза 5: Монетизация (готово)

- [x] Bookaway affiliate registered (offer_id=34, aff_id=4033)
- [x] Buy ticket button на каждом маршруте (Bookaway)
- [x] Country mapping для правильных URL (Montenegro, Bosnia, Croatia...)
- [x] AdSense placeholder в config (готов к подключению)

---

## 📊 Текущая статистика

| Метрика | Значение |
|---------|----------|
| Маршрутов | 517 (271 domestic + 246 international/info) |
| С реальными данными | 336 |
| Городских линий | 610 (Beograd 514, Novi Sad 61, Niš 12, Kragujevac 23) |
| Городских остановок | 3770 (97% GPS) |
| Trips (intercity) | 2777 |
| GTFS trips | 93,991 |
| GTFS stop_times | 2.3M (94% mapped) |
| Sitemap URLs | 3600+ |
| Языков | 3 (sr, en, ru) |
| Тестов | 325 passing |
| Response time | 0.02-0.10s |
| SEO score | 100% clean |

---

## 🔮 Будущее (опционально)

- [ ] AdSense заявка (после 1000+ визитов/месяц)
- [ ] Real-time vehicle tracking (если найдём API)
- [ ] Push notifications для задержек
- [ ] iOS/Android приложение (PWA уже работает)
- [ ] Расширение на другие Балканы (Албания, Греция)
- [ ] Партнёрства с Lasta, Niš-Ekspres напрямую (50-100€/мес)
- [ ] Перенос на Hetzner VPS (5€/мес вместо 100€)

---

## Конкуренты

| Сайт | Что хорошо | Что плохо |
|------|-----------|-----------|
| busticket4.me | Покупка билетов | Нет городского транспорта |
| srbvoz.rs | Официальный | Ужасный UX, нет SEO |
| bgprevoz.rs | Официальный | Только Белград |
| polazak.rs | Широкий охват | Только сербские |
| getbybus.com | International | Очень дорого |

**Наше преимущество:** Городской + межгородской + международный в одном месте,
3 языка, современный UX, бесплатно, SEO-оптимизировано, реальные данные ночного refresh.

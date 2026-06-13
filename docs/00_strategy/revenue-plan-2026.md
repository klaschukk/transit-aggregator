# Revenue Plan 2026 — Prevozni

**Автор:** Strategy review, апрель 2026
**Горизонт:** 12 месяцев (апрель 2026 → апрель 2027)
**Цель:** €1000-5000/мес recurring revenue к месяцу 12
**Стартовая точка:** ~60 визитов/день, 872 indexed, 2 канала монетизации (Bookaway + AdSense placeholder)

---

## ⚠️ Ревизия: июнь 2026 (2026-06-12)

Майская ревизия не делалась. Ключевые изменения относительно апрельской версии:

1. **Партнёрка перевёрнута.** Основной affiliate-канал теперь **BusTicket4**
   (affiliateId=735, комиссия 2%) на ВСЕХ обычных маршрутах. Bookaway
   (offer_id=34, aff_id=4033, TUNE-трекер) с 2026-06-10 оставлен ТОЛЬКО для
   дальних направлений (Азия). FlixBus убран. Вся финмодель §1 построена на
   Bookaway 8% — **требует рекалибровки под BT4 2%**; дашборд BT4 показывает
   **0 продаж за апрель–июнь**, реальный EPC пока неизвестен.
2. **AdSense уже live** (ca-pub-9538841764038287, слоты активированы) —
   Приоритет 1 Фазы 2 выполнен раньше плана.
3. **Инсайт GSC (2026-06-08):** фактический трафик — городские линии, а не
   межгород. Приоритеты Фазы 1 (city-pair контент) надо пересмотреть в пользу
   городских страниц; генерик «red vožnje autobusa i vozova» — high-CTR
   возможность.
4. **Риск 5.3** («busticket4 блокирует скрапер») смягчён: теперь официальное
   affiliate-партнёрство.

Конкурентный анализ §2 остаётся каноническим (в §2.8 влит ранний
`competitor_analysis.md`).

---

## 0. Тезис документа

Prevozni — programmatic SEO play на транспортном нишевом рынке Сербии/Балкан, где конкуренты либо государственные сайты с ужасным UX (gsp.rs, srbvoz.rs), либо платные билетные агрегаторы (busticket4.me, getbybus.com). Окно возможностей: 12-18 месяцев пока Google ещё индексирует programmatic-контент, пока AI Overviews не съели search intent для "расписание автобусов". Один выиграшный канал дохода — affiliate + AdSense в пропорции ~60/40. Данные — главный moat.

---

## 1. Финмодель

### 1.1 Допущения и источники

**CTR на affiliate CTA:**
- Benchmark travel aggregators: 2-5% от visits кликают на "Buy ticket" (source: Awin travel vertical benchmarks, 2024; own estimate validated via Rome2Rio case study на Medium 2023)
- Prevozni без A/B тестинга CTA — принимаем **2%** как базу

**EPC (earnings per click) Bookaway / 12Go-style:**

> _Ревизия июнь 2026: расчёт ниже относится к Bookaway, который теперь
> работает только на дальних направлениях. Для основного канала (BusTicket4,
> комиссия 2%) EPC надо мерить заново — пока 0 подтверждённых продаж._
- Bookaway public affiliate rate: 8% commission от ticket price (source: bookaway.com/affiliate-program-partners landing page)
- Avg Serbia bus ticket: €8-20 (busticket4.me pricing check, апрель 2026)
- Conversion rate click → booking: **1-3%** (source: Awin 2024 Travel Benchmarks Report — "Search & Aggregator" category)
- Итого EPC: €0.08 × €12 avg × 2% conv = **€0.20-0.60 EPC реалистично для Сербии** (ниже типичного €0.50-1.50 travel EPC т.к. low ticket price)

**AdSense RPM (Serbia travel content):**
- Serbia GDP per capita ~€9K = Tier 3 AdSense market
- Travel vertical RPM globally: €3-8 (source: Ezoic Big Data public reports 2024)
- Tier 3 adjustment: ~40% of Tier 1 = **€1.20-3.20 RPM realistic**
- Russian/English visitors лучше монетизируются — если достанем 30% EU/US traffic, RPM подрастает до €2-4 blended

**Pageviews per visit:** 3.0 (sitemap 4632 URLs, interlinking развит, принимаем 3 — консервативно для SEO-трафика где многие landing-and-bounce).

### 1.2 Таблица доходов

| Visits/day | Visits/mo | PV/mo | Bookaway clicks (2%) | Bookaway rev (EPC €0.30-0.60) | AdSense (RPM €2 mid) | **Total/mo** |
|-----------:|----------:|------:|---------------------:|------------------------------:|--------------------:|-------------:|
| 100        | 3,000     | 9K    | 60                   | €18-36                        | €18                  | **€36-54**   |
| 500        | 15,000    | 45K   | 300                  | €90-180                       | €90                  | **€180-270** |
| 2,000      | 60,000    | 180K  | 1,200                | €360-720                      | €360 (RPM €2)        | **€720-1,080** |
| 10,000     | 300,000   | 900K  | 6,000                | €1,800-3,600                  | €2,700 (Ezoic RPM €3)| **€4,500-6,300** |

**Честная калибровка:**
- Нижняя граница = pessimistic EPC €0.30, базовая RPM €2. Если EPC реально €0.15 (low-ticket, Балканы) — делите affiliate на 2.
- Верхняя граница возможна только если 30%+ трафика из EU (ru/en версии) и pageviews per visit >3.5.
- При 10K/day — реально Mediavine/Raptive даст RPM €5-8 (но они требуют 50K-100K sessions, у нас это 1.5M pv/mo — проходит с запасом).

**Break-even для hosting+tools (€120/mo при €30 VPS + €90 Ahrefs):** ~700 visits/day при conservative EPC.

### 1.3 Что именно я не знаю (honest)

- **Фактический Bookaway EPC для Сербии** — unknown, нужно 30 дней данных из параллельного analytics-агента. Research план: трекать clicks в Umami → matches Bookaway dashboard → calculate EPC real. Pivot после месяца 2.
- **AdSense RPM для Serbian travel niche** — unknown до approval. Research: запустить placeholder и смотреть после 30 дней live impressions.
- **Реальная conversion rate click→booking на Bookaway для Balkan routes** — Bookaway не публикует niche-specific numbers, обычно 1-3% overall, но для low-demand маршрутов может быть 0.3%.

---

## 2. Конкурентный анализ

Числа — public estimates на базе SimilarWeb free tier + Ahrefs free Domain Rating checker (https://ahrefs.com/backlink-checker). Точность ±30%, достаточно для стратегии.

### 2.1 busticket4.me

- **Трафик:** ~300-500K visits/mo (SimilarWeb estimate, апрель 2026)
- **DR (Ahrefs):** ~50-55
- **Монетизация:** Commission с продажи билетов (они market-maker, не только affiliate). 5-10% от ticket price.
- **Контент:** Динамический каталог маршрутов, 14 языков, schema.org BusReservation. Но — **нулевой long-form content**, нет guides, нет блога.
- **Backlinks:** Немного travel-блогов, немного каталогов. Не SEO-first, growth через бренд/прямой трафик.
- **Что у них работает:** Онлайн-оплата, широкая Европа, 14 языков.
- **Что мы делаем лучше:** Городской транспорт (их нет), FAQ schema, real GTFS data, long-form guides.
- **Пробел:** Они не зарабатывают на information search intent — только на transactional. Вся SEO-поляна "расписание X-Y" наша.

### 2.2 srbvoz.rs (Srbija Voz)

- **Трафик:** ~200-400K visits/mo (official gov site, direct traffic dominant)
- **DR:** ~40 (старый домен, .rs TLD boost)
- **Монетизация:** ticket sales, нет рекламы
- **Контент:** Только официальное расписание, ужасный UX, SSL ошибки (апрель 2026 — проверить).
- **Что работает:** Authority как государственный сайт, direct brand traffic.
- **Что лучше у нас:** UX, mobile, интеграция с автобусами, interlinking, 3 языка.
- **Пробел:** User searches "beograd novi sad voz" — их страница unusable → возможность перехватить intent.

### 2.3 polazak.rs

- **Трафик:** ~50-150K visits/mo (SimilarWeb low end)
- **DR:** ~25-30
- **Монетизация:** Bus ticket resale commission
- **Контент:** Минимальный, слабое SEO, нет hreflang, нет schema markup.
- **Что лучше у нас:** Практически всё — мы SEO-first с первого дня.
- **Пробел:** Нет содержательных страниц, нет international.

### 2.4 getbybus.com

- **Трафик:** ~150-300K visits/mo globally
- **DR:** ~48
- **Монетизация:** High commission ticket broker (markup ~20-30% vs partner price — пользователи жалуются на Reddit)
- **Контент:** Хорошие long-form guides ("how to get from X to Y"), schema markup, multiple languages.
- **Backlinks:** Широкий профиль из travel blogs (Nomadic Matt-style), TripAdvisor mentions.
- **Что у них работает:** SEO content play — именно то что мы пытаемся повторить. Изучать их top pages через SimilarWeb/Ahrefs.
- **Что лучше у нас:** Бесплатно (они с markup), нишевой фокус Balkan, городской транспорт.
- **Action:** взять их top-20 pages по organic traffic (Ahrefs Site Explorer trial 7 days) и скопировать keyword set.

### 2.5 omio.com

- **Трафик:** 30-50M visits/mo globally
- **DR:** ~85 (huge)
- **Монетизация:** Ticket broker с markup + commissions
- **Контент:** Programmatic на миллионы страниц, contents team из 30+ писателей.
- **Наш вывод:** не соревноваться head-on. Omio доминирует на головных запросах ("bus berlin munich"). Наша ниша — Serbian-specific long-tail ("kako doci od Beograda do Zlatibora autobusom 2026") где они слабее в локализации.

### 2.6 12go.asia

- **Трафик:** 5-10M visits/mo
- **DR:** ~70
- **Монетизация:** Ticket broker commission
- **Используем как playbook reference:** 12Go начинали как SEA aggregator, сейчас доминируют. Их growth engine — programmatic city-pair pages + Pinterest-driven content. **Это наш будущий образец**, если говорим об exit в €50K+ ARR.
- **Что у них работает:** massive city-pair pages, unique content per pair, aggressive ads budget.

### 2.7 Сравнительная сводка

| Сайт           | Traffic/mo | DR  | Main moat           | Наш угол атаки                 |
|----------------|-----------:|----:|---------------------|--------------------------------|
| busticket4.me  | 300-500K   | 50+ | Ticket sales        | City transport + guides         |
| srbvoz.rs      | 200-400K   | 40  | Official authority  | UX, aggregation                |
| polazak.rs     | 50-150K    | 25  | Low moat            | Beat on SEO quality            |
| getbybus.com   | 150-300K   | 48  | Guides + international | Free + local nuance             |
| omio.com       | 30M+       | 85  | Scale               | Don't compete; long-tail Balkan |
| 12go.asia      | 5-10M      | 70  | Asia dominance      | Replicate their playbook locally|

**Главный инсайт:** ни один конкурент не закрывает одновременно (city + intercity + train + 3 языка + free + long-form content). Это дефендабельный позиционинг. Окно — 12 месяцев до того как busticket4.me или omio может добавить локальный контент-слой.

### 2.8 Локальные «официальные» сайты (из раннего обзора, март 2026)

Перенесено из `competitor_analysis.md` (мартовский одностраничник, упразднён) — уникальные наблюдения, которых нет выше.

**gsp.rs (GSP Beograd)** — официальный сайт городского транспорта Белграда.

| Плюсы | Минусы |
|-------|--------|
| Официальный источник данных | Устаревший дизайн (2010-е) |
| Полная база линий | Нет адаптивной мобильной версии |
| Приложение для Android | Нет поиска по маршрутам |
| | Сломанные javascript-ссылки |
| | Нулевое SEO (нет meta, нет schema) |
| | Нет реального расписания онлайн |

Наш ответ: берём их данные, делаем нормальный UX — «GSP с человеческим лицом».

**prevoz.org** — поиск попутчиков (carpooling), популярен в Словении. Не прямой конкурент — другая ниша (carpool, не расписание). Игнорируем.

**Что копируем у конкурентов:**

- **busticket4.me:** чистый дизайн формы поиска (Откуда / Куда / Дата); Schema.org BusReservation/BusTrip разметка. (С июня 2026 busticket4.me ещё и наш affiliate-партнёр, affiliateId 735 — см. `docs/05_monetization/partners.md`.)
- **GSP:** структура данных по линиям (номер, маршрут, остановки).

---

## 3. Growth strategy — 3 фазы

### Фаза 1 (месяцы 1-3): Foundation → 500 visits/day

Текущее состояние: 872 indexed / 3346 "Discovered not indexed". Это главная проблема — **crawl budget gap**. Google считает страницы low-value.

**Приоритет 1: Unlock indexing (impact: 5-10x организики за 60 дней)**

Что делать конкретно:
1. **Усилить уникальность programmatic-страниц** — текущие city-pair страницы, вероятно, шаблонные. Добавить в каждую:
   - 200-400 слов уникального content (LLM-generated из данных, но с real numbers: "Автобус Белград — Ниш стоит в среднем €11, идёт 3ч 15мин, 8 отправлений в день, оператор Niš-Ekspres")
   - Price/duration stats block (из trips таблицы)
   - "Popular departure times" chart (из gtfs_stop_times)
   - 3-5 user-intent FAQs, уникальные per pair
2. **Internal linking** — каждая маршрутная страница линкует на 5-10 related (same city hub, similar distance, same operator). Snowball effect для crawl.
3. **Удалить thin content** — если pair имеет <2 trips и нет schedule, либо noindex, либо merge в hub-страницу "все маршруты из X".
4. **Request indexing в GSC** — submit top 50 city pairs manually, бустит crawl rate.

**Expected lift:** indexed pages 872 → 2500-3500 за 60 дней; organic traffic 60 → 200-300 visits/day при тех же impressions.

**Приоритет 2: Content factory (длинный хвост)**

- **4 long-form guides/неделю** в `/vodici/` — уже есть такая структура судя по последнему коммиту `c6aa2bb feat(content): /vodici/ guides section`.
- Keyword research (без paid Ahrefs): Google Keyword Planner (free через Google Ads account), keywordtool.io free tier, Google Autocomplete + "People also ask" manual scraping.
- Target queries (validate каждый через Google search + [serbia] geo):
  - "autobus beograd [grad] cijena" × 50 городов
  - "kako doci od [grad] do [grad]" × 100 пар
  - "red voznje gsp linija [N] beograd" × 50 линий
  - "[grad] autobuska stanica kontakt" × 30 станций
  - "beograd zlatibor autobus 2026" (seasonal, actively ранжируется)
- **Native Serbian writer:** €50-75 за 1500-word guide, 4/week = €200-300/mo. Найти через upwork.com filtering by Serbian location + Linkedin groups "Serbia copywriters".
- Альтернатива если нет бюджета: LLM-drafts + личная редактура + local terms check. Меньше качества, но можно тестить.

**Expected lift:** +100-200 visits/day из новых длинных страниц к месяцу 3.

**Приоритет 3: Backlinks (10-20 ссылок за 90 дней)**

Конкретные цели:
1. **Wikipedia SR:** редактировать статьи "Javni prevoz u Beogradu", "GSP Beograd", "Srbija Voz" — добавить ссылку на соответствующую страницу Prevozni как external reference (нужен real value-add, не спам — например, интерактивная карта остановок). DR boost = большой.
2. **Reddit:** r/serbia, r/beograd, r/travel — не дропать ссылки в комменты (банят), а сделать useful post "I built a free transit aggregator for Serbia, feedback welcome". Цель: 2-3 organic threads.
3. **Expat forums:** expatrio.com Serbia page, serbianflyer.com forum, internations.org Belgrade group — posts about "how to navigate Belgrade transport" с ссылкой на наш city guide.
4. **Travel blogs:** pitch 10-15 бalkan travel bloggers (ссылки через BuzzStream free list или ручной поиск "Serbia travel blog 2025"). Предлагать им бесплатный embed нашей карты/расписания на их страницу "Belgrade transport" в обмен на link.
5. **Local news outlets:** blic.rs, 021.rs (Novi Sad), juznevesti.com (Niš) — pitch press release "Ruski developer запустил бесплатный аналог gsp.rs с интерактивной картой". Success rate <10%, но один hit на major outlet = DR 60+ backlink.
6. **data.gov.rs:** если используем их GTFS данные (подтверждено в roadmap), просим их добавить Prevozni в "projects using this dataset" раздел. Government backlink.
7. **HARO (helpareporter.com) / Qwoted:** sign up, respond to Serbia travel или EU transit queries. 2-3 ответов/неделю, 1-2 links/месяц.

**Expected lift:** DR 0 → DR 15-20 к месяцу 3. Критично для индексации и ранжирования.

**Milestone месяц 3:** 500 visits/day, 2500 indexed, 10+ DR, 10-15 quality backlinks.

### Фаза 2 (месяцы 4-6): Scale → 2000 visits/day

**Priority 1: AdSense approval — ✅ СДЕЛАНО (июнь 2026, раньше плана)**

AdSense подключён и крутится: ca-pub-9538841764038287, слоты активированы.
Дальше — следить за RPM (см. `docs/05_monetization/adsense-strategy.md`).
Исходные требования оставлены для истории:

AdSense требования (точно из support.google.com/adsense/answer/9724):
- Unique quality content (у нас есть — programmatic + guides)
- Navigation (есть)
- Privacy policy, About, Contact (есть — проверить /o-nama, /kontakt)
- Domain age 6+ months (мы в требованиях, если домен куплен осенью 2025)
- Policy compliance — нет copyrighted content, нет adult, нет scraping без attribution

**Риск:** могут отклонить из-за "Insufficient original content" — programmatic pages часто получают этот флаг. Mitigation: ensure guides section `/vodici/` имеет минимум 15-20 long-form original articles к моменту подачи.

**Action:** подавать конец месяца 4, когда 1500+ daily visitors и 20+ guides. Approval занимает 1-4 недели.

**Priority 2: Direct affiliate partnerships**

Email pitch template для операторов:

```
Тема: Besplatni trafik за Lasta — 10000 pretraga mesečno na prevozni.com

Pozdrav [imeContact],

Prevozni.com je agregator putničkog transporta Srbije (4632 stranica, 15000 posetilaca/mes u aprilu 2026).
Vaše rute se već prikazuju u našim rezultatima pretrage.

Predlažem affiliate partnerstvo:
- Mi šaljemo topla lead-ova (korisnik tražio tačno Vašu rutu)
- Vi plaćate 5-10% komisije od prodaje, ili fiksnu naknadu €0.50-1.50 po klikanju
- Dodatna prednost: bolje pozicioniranje Vaših ruta na našem sajtu

Spreman sam da uradim test 30 dana.
```

Targets: Lasta (lasta.rs), Niš-Ekspres, AS Beograd, BusPlus. Industry standard commission: 5-15% от сделки или €0.30-1.50/click. Start с одним (например Lasta — largest). Skip if no budget для ops work (takes ~10 часов/deal).

Честно: direct deals работают только при 5K+ visits/day. До того — focus на Bookaway.

**Priority 3: Language expansion**

Текущий split (3 языка) — sr default, en, ru. Приоритеты:
1. **EN** — дисеминатор. Expat traffic + travel SEO globally. Boost с guides на EN.
2. **RU** — Balkan tourism Russian-speakers, плюс подрастающая российская диаспора в Сербии. Low competition для русских запросов про сербский транспорт.
3. **DE** — unknown, need research. German tourism в Балканы растёт, CPC на немецкий AdSense 3-5x sr. **Add в месяце 5-6 если bandwidth позволяет**.

**Priority 4: Paid ads — skip пока**

Не рекомендую до месяца 6+. Причина: Google Ads на transit keywords для Сербии имеет CPC €0.10-0.40 (Keyword Planner benchmark). При EPC €0.30-0.60 break-even marginal. Органик — 10x лучше ROI для этой ниши.

Исключение: **reservation-intent keywords** типа "autobus beograd budva karta". CPC €0.30, конверсия click→Bookaway 5%+ = ROI 3-5x. Test с €100 budget в месяце 5 после установки conversion tracking.

**Milestone месяц 6:** 2000 visits/day, AdSense approved and earning €150-300/mo, Bookaway €400-800/mo, 1 direct deal signed, DE launched.

### Фаза 3 (месяцы 7-12): Monetize → 10K visits/day, €1-5K/mo

**Priority 1: Upgrade ad network**

Thresholds (точные, current апрель 2026):
- **Ezoic:** 10K visits/mo (мы уже на 60K). Test между месяцами 7-8.
- **Mediavine:** 50K sessions/mo (достижимо к месяцу 8-9). RPM benchmark 1.5-3x AdSense.
- **Raptive (AdThrive):** 100K pageviews/mo (к месяцу 9-10). Лучшие RPMs, €5-10 в travel niche.

Не менять AdSense на Ezoic слишком рано — Ezoic более aggressive с ads, может повредить UX и organic rankings (Google E-E-A-T). Test A/B: половина трафика на Ezoic, половина на AdSense, сравнить RPM + Core Web Vitals + bounce rate 30 дней.

**Priority 2: Data licensing (speculative)**

Кто может платить за наши данные:
- Insurance companies (travel insurance upsells) — €100-500/mo за API access
- Tourism boards — unlikely unless PR deal
- Research/academic — pennies
- **Main target:** maps/navigation companies (Yandex Maps, HERE) — но они уже имеют GTFS. Likely No.

Честно: data licensing — low probability, high optionality. Один потенциал — продать OSM-enriched stops dataset на marketplace. Unclear, не планировать как revenue line до месяца 10.

**Priority 3: Sponsored content**

После 50K visits/mo можно питчить:
- Taxi apps (CarGo, Yandex Go Serbia) — sponsored "how to get from airport" guide, €200-500/pack
- Travel insurance — affiliate referral
- Car rental (Rentalcars.com affiliate, EPC €3-8) — add "alternatives" section на intercity страницы, вероятный lift €100-300/mo

**Priority 4: Mobile apps — NO если web < €1000/mo**

Apps = 200+ часов разработки + €100/year Apple dev + €25 Google Play. ROI отрицательный до 5K DAU. PWA уже покрывает 80% кейсов (есть из роадмапа). Skip до месяца 12+ или пока не будет revenue для hire dev help.

**Milestone месяц 12:** 10K visits/day, €1500-3500/mo total revenue (ads €1000-2000, Bookaway €500-1500).

---

## 4. Quick wins — next 30 days

Ranked by ROI (impact/effort). Каждый — исполнимо за 1 неделю max.

| # | Действие | Effort (hrs) | Expected impact | Why now |
|---|----------|-------------:|-----------------|---------|
| 1 | **Fix "Discovered not indexed" — добавить 300-400 слов unique content на top-50 city-pair страниц** | 8 | 500-1000 indexed → 2000-3000 organic visits/week | 3346 страниц лежат мёртвым грузом; unlock = compound effect |
| 2 | **Wikipedia SR edits** — добавить Prevozni в 3-5 статей (Gradski prevoz Beograd, Autobuska stanica Beograd, Srbija Voz) | 4 | DR +3-5, autority boost | Highest-leverage backlink за 1 вечер |
| 3 | **Submit top 100 URLs в GSC вручную для re-indexing** | 2 | 20-40% of них re-indexed за 7 дней | Free crawl budget boost |
| 4 | **Conversion tracking на Bookaway CTAs через Umami custom events** | 3 | Знать реальный EPC в течение 14 дней | Блокирует все дальнейшие решения |
| 5 | **Написать 4 cornerstone long-form guides** (Belgrade → Novi Sad, Belgrade → Niš, airport → city, GSP bus for tourists) на sr + en + ru | 20 | +50-100 visits/day to tier-1 pages за 30 дней | Foundational для DA + AdSense approval |
| 6 | **Reddit post в r/serbia + r/travel** с ссылкой "I built free Serbian transport aggregator" | 2 | 200-500 burst visits + 1-3 natural backlinks | Zero-cost, один вечер |
| 7 | **Add breadcrumb + "related routes" блок внизу каждой маршрутной страницы** | 4 | Internal linking boost → crawl + rankings | Pages already built — just UI work |
| 8 | **AdSense applicability pre-check** — audit privacy policy, about, contact; fix any gaps | 3 | Готов к подаче в месяце 3-4 | Prevent rejection later |
| 9 | **Competitor top-pages analysis** — SimilarWeb free или Ahrefs 7-day trial, выгрузить top-50 pages getbybus.com и busticket4.me, увидеть их keyword set | 3 | Найдём 30-50 keywords которые мы упускаем | One-time research, high leverage |
| 10 | **Set up weekly GSC + Umami review** — Saturday mornings, 30 min, заполнять metrics dashboard (см. раздел 6) | 0.5/week | Early warning для regressions, discipline | Without it all остальное guesswork |

**Total effort: ~50 часов = 10 hrs/week × 5 weeks.** Realistic for solo dev.

---

## 5. Risks + mitigation

### 5.1 Google algorithm update (Helpful Content / AI Overviews)

- **Risk:** Major update (как HCU Sep 2023, March 2024) может срезать programmatic pages на 40-80%. AI Overviews уже съедают click-through на "расписание автобусов" типе запросов.
- **Mitigation:**
  - Diversify content: не только programmatic, но и 50+ reallong-form guides которые Google не может легко AI-summarize (live data, comparisons, personal angle).
  - Build brand search (people Google "prevozni" directly) через social + PR. Brand traffic immune к algo updates.
  - Backup traffic: email list (см. раздел 6), Telegram channel, iOS/Android app к месяцу 12.
  - Monitor weekly: любой drop >20% на topic "Serbia bus" → full SEO audit в течение 48 часов.

### 5.2 Bookaway меняет commission или terms

- **Risk:** Commission cut с 8% до 4% = half revenue. Or terms change blocks our traffic.
- **Mitigation:**
  - Не монетизировать только одним партнёром. После месяца 4 — intro 12go.asia Europe affiliate (если есть), getbybus.com affiliate, Lasta direct deal.
  - Diversify: AdSense + affiliate + (eventually) direct ads. Single-channel risk неприемлем.
  - Ежемесячно проверять dashboard Bookaway. При изменениях — iterate quickly.

### 5.3 busticket4.me блокирует scraper

> _Ревизия июнь 2026: риск резко снижен — с busticket4.me заключено
> официальное affiliate-партнёрство (affiliateId=735), мы им приводим
> покупателей. Fallback-опция из mitigation фактически реализована._

- **Risk:** Cloudflare challenge, IP ban, legal letter. Потеря 40-50% data coverage (intercity routes).
- **Mitigation:**
  - Уже используем multiple sources (polazak.rs, srbvoz.rs, GTFS data.gov.rs). Redundancy built in.
  - Респект rate limits: 1 req/sec max, legitimate User-Agent, cache aggressively.
  - **Fallback option:** официальный партнёрский API. Написать в BusLogic (родительская компания busticket4.me) — предложить partnership где мы forwarding traffic к ним, они дают legit API access. Win-win если grown enough.
  - **Legal position:** scraping публичных расписаний в EU допустимо (public data, no DB rights violation если не копируем структуру). Не копировать их HTML 1:1. Всегда transform data.

### 5.4 Правовые (right публиковать данные перевозчиков)

- **Risk:** Srbija Voz, Lasta могут отправить takedown letter. В Сербии нет chi strong precedent, но possible.
- **Mitigation:**
  - GTFS data.gov.rs — официально open license (CC-BY), можем использовать. **Документировать source на каждой странице**.
  - Для scraped data (busticket4.me, polazak) — это публичная информация о рейсах, факт не копирайтный. Мы transform (aggregate, re-present). Safe.
  - Добавить footer "Данные собраны из открытых источников: [links]. Для покупки билетов — перейти на официальные сайты перевозчиков."
  - Подготовить standard response на takedown: "We aggregate public transport data for consumer benefit under EU open data principles. Happy to add attribution or direct booking link to your platform."
  - Avoid копирования descriptions, only facts (schedule, stops, prices).
  - **If threatened:** respond professionally, propose partnership instead of confrontation.

### 5.5 Solo dev burnout

- **Risk:** Самый серьёзный риск. Единственная точка отказа — ты.
- **Mitigation:**
  - **Hard rule:** 1 day/week off from Prevozni. No exceptions.
  - **Documentation discipline:** всё что делается — фиксируется в `/docs`. Если нужно передать/вернуться после месяца отпуска — можно.
  - **Automate everything что скрапится:** ночной cron уже есть. Добавить auto-fix для common скрейпер breaks (retries, alerting в Telegram).
  - **Revenue milestone = motivation:** как только €500/mo стабильно, это 1 weekend/mo compensation. €2K/mo = part-time income.
  - **Seek help при €1000/mo:** нанять part-time Serbian writer (€200/mo) и SEO audit раз в квартал (€300). Free up твоё время для strategy.
  - **Community:** join IndieHackers Serbia, Balkan solopreneurs Discord. Loneliness = burnout accelerator.

### 5.6 Risk priority

| Risk | Probability | Impact | Combined | Monitor |
|------|:-----------:|:------:|:--------:|---------|
| Solo burnout | High | Catastrophic | **1** | Weekly self-check |
| Google algo | Medium | High | **2** | GSC daily |
| Bookaway changes | Medium | Medium | **3** | Monthly dashboard |
| Scraper blocks | Medium | Medium | **4** | Daily cron health |
| Legal | Low | High | **5** | Quarterly review |

---

## 6. Metrics dashboard — еженедельно

**Cadence:** Суббота 10:00, 30 минут. Заполнять в простой spreadsheet (Google Sheets, колонки = weeks, строки = metrics).

| Metric | Source | Why |
|--------|--------|-----|
| Visitors (last 7d) + sources (organic/direct/social/referral) | Umami | Core north star |
| Indexed pages (total) | Google Search Console | Tracking crawl budget unlock |
| "Discovered, not indexed" count | GSC > Pages > Why not indexed | Early warning signal |
| Bookaway clicks + conversions + revenue | Umami custom events + Bookaway dashboard | Revenue truth |
| AdSense revenue + RPM + CTR | AdSense dashboard (after approval) | Ad revenue truth |
| Email list size (newsletter signups) | Self-hosted or ConvertKit free tier | Diversification |
| Top 10 queries by clicks + positions | GSC > Performance > Queries | What's working |
| Avg position для 20 tracked keywords | GSC или SERPstat free tier | Ranking trends |
| Number of backlinks (referring domains) | Ahrefs free backlink checker | DR growth proxy |
| Site health: 4xx/5xx rate, LCP, CLS | nginx logs + PageSpeed Insights API weekly | Technical health |
| Revenue/visitor (€/1000 visits) | calc from above | Economic efficiency |

**Red flags, которые требуют immediate action:**
- Visitors ↓ >20% week-over-week
- "Discovered, not indexed" ↑ >10%
- Bookaway EPC < €0.15 для 2 недель подряд (= что-то сломано или ниша unviable)
- AdSense account flag or policy warning

**Monthly review** (последнее воскресенье месяца, 2 часа): пересмотреть Phase, recalibrate projections, update этот документ.

---

## 7. Budget

### Текущие расходы

- Hosting: **€0** (montiko donated)
- Domain prevozni.com: ~€10/year amortized = **€1/mo**
- Telegram bot API, Cloudflare free tier, Umami self-hosted: **€0**
- **Total: ~€1/mo**

### Phase 1 (месяцы 1-3) — lean

| Item | Cost/mo | Purpose |
|------|--------:|---------|
| Domain | €1 | — |
| Hosting (stay on montiko) | €0 | — |
| Ahrefs / SEMrush: skip, use free tier | €0 | — |
| Content writing (optional) | €0-200 | 4 guides/week if hire |
| **Phase 1 total** | **€1-201/mo** | Break-even при 50 visits/day with Bookaway |

### Phase 2 (месяцы 4-6) — invest в tools

| Item | Cost/mo | Purpose |
|------|--------:|---------|
| Hosting (migrate to Hetzner CX22 €5/mo if needed) | €0-5 | Scale insurance |
| Content writing | €200-300 | 4 posts/week professional |
| Ahrefs Lite | €89 | Keyword research + backlink monitoring |
| Paid ads test | €100 | 1 campaign на reservation-intent keywords |
| Email service (Brevo free до 300 emails/day) | €0 | List building |
| **Phase 2 total** | **€389-494/mo** | Break-even при 1500 visits/day |

### Phase 3 (месяцы 7-12) — scale

| Item | Cost/mo | Purpose |
|------|--------:|---------|
| Hosting (Hetzner CX32) | €15 | Scale capacity |
| Content | €400-600 | 6-8 posts/week + video/diagrams |
| SEO tools (Ahrefs Standard) | €199 | Advanced analysis |
| Paid ads | €500-1500 | Scale winning campaigns |
| Freelance dev help (ad hoc) | €200-500 | Bug fixes, feature work |
| Legal consult (1-time) | €0-300 | Scraping legal opinion |
| **Phase 3 total** | **€1314-3114/mo** | Break-even при 8K visits/day |

### Break-even targets

| Phase | Budget | Break-even visits/day (conservative EPC €0.30, RPM €1.5) |
|-------|-------:|--------------------------------------:|
| 1 | €200/mo | 400 visits/day |
| 2 | €450/mo | 1400 visits/day |
| 3 | €2000/mo | 4000 visits/day |

Если Phase 1 не достигает 500 visits/day к концу месяца 3 — **не масштабировать бюджет**. Stay lean, iterate на Phase 1 tactics до result.

---

## 8. "One thing" — ranked monthly focus

Если можешь сделать **только одно** в месяц, вот приоритет (in execution order):

| Месяц | Single focus | Why this, not that |
|------:|--------------|--------------------|
| 1 | **Unlock "Discovered, not indexed" — add 300-word unique content block + internal linking to top 300 programmatic pages** | 3346 мёртвых страниц = dormant traffic. Ничто не даст больше leverage. |
| 2 | **Write & publish 15 long-form guides (~2500 words each) in sr + en + ru** | Foundation для long-tail + AdSense approval + DA boost |
| 3 | **Backlinks campaign: Wikipedia + Reddit + 5 pitched placements** | DR unlock = compound на всё дальше |
| 4 | **Instrument conversion tracking + run 30-day Bookaway EPC measurement** | Можно скейлить только то что измеряется |
| 5 | **AdSense application + ads placement optimization** | Второй revenue stream = de-risk |
| 6 | **Launch DE language + Balkan neighbors (ME, BA, HR) routes expansion** | Market expansion = new keyword universes |
| 7 | **Paid ads test (€200 budget) на reservation-intent keywords** | Identify profitable paid channels |
| 8 | **Migrate to Ezoic/Mediavine если approved; RPM A/B test** | Ad revenue optimization |
| 9 | **Direct affiliate deal (Lasta preferred) negotiation + contract** | Diversification + higher commission tier |
| 10 | **Email list + newsletter (weekly transport news Serbia)** | Own audience = algo-proof revenue |
| 11 | **Sponsored content pilot (taxi app or travel insurance)** | Test new revenue line |
| 12 | **Retrospective + strategy re-write for year 2** | Compound learning |

**Single most important month is 1.** If indexing doesn't unlock, everything else downstream fails.

---

## TL;DR (читать поздно вечером)

1. **Главный рычаг — unlock indexing.** 3346 "Discovered, not indexed" → это твой reservoir. Добавь 300-400 слов уникального content на top-500 programmatic страниц + internal linking. Месяц 1 = всё остальное downstream.
2. **Монетизация двухканальная.** Bookaway сейчас (~€20-50/mo при 100 visits/day), AdSense с месяца 4 (+€150-300/mo). К месяцу 12: €1000-3500/mo реалистично.
3. **Conversion tracking — блокер для всего.** Пока не меряешь EPC, любая стратегия гадание. Неделя work, critical.
4. **Контент-фабрика — 4 guide/неделю.** Native Serbian writer €200/mo или LLM-drafts + твоя редактура. Без long-form ты не получишь AdSense и не перебьёшь getbybus.com.
5. **Backlinks: Wikipedia первым.** Один вечер, DR +3-5. Потом Reddit + expat forums + press pitch. Цель: 15 quality links за 90 дней.
6. **Конкурентов не бояться.** busticket4.me, srbvoz.rs — все слабы на content/SEO. Окно 12-18 мес.
7. **Риск №1 — твой burnout.** 1 day off/week. Неделя отпуска/квартал. Без этого проект мёртв к месяцу 6.
8. **Не масштабировать бюджет до результата.** Phase 1 — €1/mo. Phase 2 только при 500+ visits/day. Phase 3 только при €500+/mo revenue.
9. **Окупаемость hosting: ~400 visits/day.** Сейчас 60. Цель месяц 3.
10. **Единственная метрика которая имеет значение — revenue/visitor.** Всё остальное — прокси.

---

*Документ living, пересматривать каждый месяц после monthly review (раздел 6). Последняя ревизия: июнь 2026 (блок «⚠️ Ревизия» в начале). Следующая: июль 2026.*

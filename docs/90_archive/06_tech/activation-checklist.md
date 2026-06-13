# Activation Checklist — Prevozni

Runbook: всё что построено в коде, но ещё не обслуживает живой трафик.
Цель — один час работы solo dev'а, каждый пункт verifiable.

**Перед началом:** прогони `bash scripts/activation_check.sh https://prevozni.com`
и зафиксируй какие пункты уже done (some are, e.g. sitemaps). Чеклист ниже
покрывает pure-ops задачи + outreach.

---

## A. Admin dashboards (15 мин)

### A1. Сгенерируй admin credentials

```bash
ADMIN_USER=kirill
ADMIN_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
echo "USER=$ADMIN_USER"
echo "PASS=$ADMIN_PASS"
# Сохрани пароль в 1Password/BitWarden. ЭТОТ ВЫВОД — единственный раз.
```

### A2. Добавь в systemd unit

```bash
sudo systemctl edit --full transit.service
# В секции [Service] добавь две строки:
#   Environment=ADMIN_USER=kirill
#   Environment=ADMIN_PASS=<твой_токен>
# Сохрани, затем:
sudo systemctl daemon-reload
sudo systemctl restart transit
```

### A3. Проверка

```bash
# Без auth — должно быть 401 (а не 503)
curl -o /dev/null -w '%{http_code}\n' https://prevozni.com/admin/revenue
# Ожидаемо: 401

# С auth — 200 + HTML
curl -u "$ADMIN_USER:$ADMIN_PASS" https://prevozni.com/admin/revenue \
  | head -20
# Ожидаемо: HTML с заголовком Revenue Dashboard
```

### A4. Rollback

Если что-то сломалось, откатись:
```bash
sudo systemctl edit --full transit.service  # убери обе Environment=
sudo systemctl daemon-reload && sudo systemctl restart transit
# /admin/* вернётся к 503 (safe default) — сайт живой.
```

---

## B. Email SMTP (20 мин)

Сейчас `app/mailer.py` без `SMTP_HOST` пишет в `logs/mail_dev.log` — double-opt-in
работает локально, но юзеры писем не получают.

### B1. Выбор провайдера

| Провайдер | Free tier | Setup | Рекомендация |
|-----------|-----------|-------|--------------|
| **Resend** | 3K/mo, 100/day | 5 мин | **✅ первый выбор** (простейший) |
| Mailgun | 5K/mo (3 мес), потом $35 | 20 мин (DNS verify) | если нужен объём |
| Brevo | 300/day forever | 10 мин | fallback |
| Amazon SES | $0.10/1K | ~2 недели approval | позже, для scale |

### B2. Resend setup (рекомендовано)

1. Зарегистрируйся на https://resend.com/signup
2. **Domains → Add Domain → prevozni.com**
3. Скопируй 3 DNS записи (SPF + DKIM + return-path CNAME) и добавь в Cloudflare
   DNS для prevozni.com:
   - `prevozni.com` TXT: `v=spf1 include:_spf.resend.com ~all`
   - `resend._domainkey.prevozni.com` TXT: `<DKIM key из UI>`
   - `send.prevozni.com` CNAME: `feedback-smtp.us-east-1.amazonses.com`
4. В UI дождись "Verified" (обычно 1-5 мин после Cloudflare propagation)
5. **API Keys → Create API Key** — скопируй. Формат `re_XXX`.

### B3. Добавь SMTP env vars в systemd

```bash
sudo systemctl edit --full transit.service
# Добавь в [Service]:
#   Environment=SMTP_HOST=smtp.resend.com
#   Environment=SMTP_PORT=587
#   Environment=SMTP_USER=resend
#   Environment=SMTP_PASS=re_XXXXXXXXXXXX
#   Environment=MAIL_FROM=hello@prevozni.com
sudo systemctl daemon-reload && sudo systemctl restart transit
```

### B4. Проверка

```bash
# Реальный email (твой личный, не prevozni.com):
curl -X POST https://prevozni.com/api/subscribe \
  -d 'email=klaschukk@gmail.com&consent=1&source=home'
# Ожидаемо: HTTP 202 + JSON {"ok": true, "status": "pending_confirm"}

# Проверь inbox klaschukk@gmail.com — должно прийти письмо с
# темой "Potvrdite pretplatu na Prevozni newsletter" + линк.
# Кликни линк → landing "subscription confirmed" + welcome letter.
```

### B5. Rollback

Удали SMTP_* env vars, daemon-reload, restart. Mailer автоматически вернётся
к dev-log fallback. Никаких пользовательских данных не теряется.

---

## C. Search Console + sitemaps (10 мин)

### C1. Google Search Console (если не сделано)

1. https://search.google.com/search-console → Add property
2. `Domain` → `prevozni.com` → Next
3. Verify via Cloudflare DNS TXT (GSC даст запись, Cloudflare → Add TXT)
4. **Sitemaps → Add sitemap** — добавь **каждый** shard отдельно:
   - `sitemap.xml` (index)
   - `sitemap-core.xml`
   - `sitemap-routes.xml`
   - `sitemap-pairs.xml`
   - `sitemap-lines.xml`
   - `sitemap-stops.xml`

Почему отдельно: GSC показывает **per-sitemap** индексацию, так быстрее
видно где "Discovered, not indexed" залипло.

### C2. Bing Webmaster Tools

1. https://www.bing.com/webmasters → Add site → Import from GSC
   (один клик, если GSC уже настроен — самый быстрый путь)
2. Или вручную: Add a site → `https://prevozni.com` → verify via DNS
3. **Sitemaps → Submit sitemap** — `https://prevozni.com/sitemap.xml`
4. Bing также индексирует DuckDuckGo, Ecosia — free traffic.

### C3. Yandex Webmaster

Критично для RU трафика (наш 3-й язык).

1. https://webmaster.yandex.com/ → Add site → `prevozni.com`
2. Verify via DNS TXT или meta tag (есть `YANDEX_VERIFICATION` env var —
   только прописать token если нужен meta-based verify).
3. **Indexing → Sitemap files → Add** `https://prevozni.com/sitemap.xml`
4. Yandex медленнее Google на 2-4 недели — подай сейчас, увидишь в мае.

### C4. Проверка

В каждом из 3 инструментов: **Sitemaps** page shows "Success" и число URLs.
Числа должны совпадать (±1%) с:

```bash
for s in sitemap-core sitemap-routes sitemap-pairs sitemap-lines sitemap-stops; do
  n=$(curl -s "https://prevozni.com/$s.xml" | grep -c '<url>')
  echo "$s: $n urls"
done
```

---

## D. AdSense заявка (5 мин + 2-4 недели ожидание)

### D1. Pre-check

```bash
# /ads.txt — serves text/plain 200 (pending-comment теперь)
curl -sI https://prevozni.com/ads.txt | head -2

# Privacy policy page existenece
curl -o /dev/null -w '%{http_code}\n' https://prevozni.com/privatnost/

# /kontakt/, /o-nama/ existence
curl -o /dev/null -w '%{http_code}\n' https://prevozni.com/o-nama/
curl -o /dev/null -w '%{http_code}\n' https://prevozni.com/kontakt/

# Enough indexed content (в GSC)
# Должно быть >20 indexed pages и no "Manual Actions" warnings.
```

### D2. Submit

1. https://www.google.com/adsense/start/ → Get started
2. Website: `https://prevozni.com`
3. Country: Serbia
4. Payments: Wise или local RS bank account
5. Auto-ads: **опция — включать после approval**, не до.
6. После submit: Google выдаст **publisher ID** (`pub-XXXXXXXXXXX`).
7. **Добавь ADSENSE_ID в systemd env:**
   ```
   Environment=ADSENSE_ID=pub-XXXXXXXXXXX
   ```
   После рестарта `/ads.txt` автоматически отдаст корректную запись
   (код в `app/routes/main.py::ads_txt`).

### D3. Ожидание

Review 1-4 недели. Google может отклонить с причинами:
- "Insufficient content" — у нас 4632 URL, редко возникает
- "Site not ready" — нужно >30 дней домена, у нас ОК
- "Policy violation" — adult/copyrighted — у нас нет

Если отклонили — fix + re-apply (бесплатно).

### D4. После approval

1. В AdSense UI → Ads → **Auto ads** — включи для `prevozni.com`
2. Alternative: manual ad units в template. Скрипт уже подключен через
   `ADSENSE_ID` env var в `base.html:51-53`, async. Добавить `<ins>` slots
   в route_detail / route_index / city_transport.

---

## E. Nightly GSC digest cron (5 мин)

### E1. Check prereq

GSC service account credentials должны лежать на сервере
(см. `docs/06_tech/gsc-setup.md`). Проверка:

```bash
ls -la /home/klaschuk/.gsc-credentials.json
# Expect: -rw------- (0600) и owner klaschuk
```

Если файла нет — сначала пройди gsc-setup.md (~15 мин), потом вернись сюда.

### E2. Добавь в crontab

```bash
crontab -e
# Append:
0 8 * * 0 cd /home/klaschuk/transit && bash scripts/weekly_seo.sh \
  >> /home/klaschuk/transit/logs/weekly-seo.log 2>&1
# Воскресенье 08:00 местного времени.
```

### E3. Smoke-test

```bash
# Запусти вручную — проверить что не падает
cd /home/klaschuk/transit && bash scripts/weekly_seo.sh
# Ожидаемо: docs/00_strategy/weekly-seo-YYYY-MM-DD.md создан
# + Telegram notification, если TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID set.
```

### E4. Rollback

`crontab -e`, удали строку. Dailies восстановятся без этого.

---

## F. Backlinks outreach — первая волна (30 мин)

### F1. Выбери 10 targets

```bash
cd /home/klaschuk/transit
# Filter CSV по приоритету: tourism boards + expat forums, DA>40
python3 -c "
import csv
rows = [r for r in csv.DictReader(open('docs/00_strategy/backlinks-targets.csv'))
        if r['status'] == 'todo'
        and r['category'] in ('serbian_tourism', 'expat_forum', 'city_tourism')
        and int(r['DA_estimate'] or 0) >= 40]
rows.sort(key=lambda r: -int(r['DA_estimate']))
for r in rows[:10]:
    print(f\"{r['DA_estimate']}  {r['domain']:30} {r['url']} ({r['category']})\")"
```

### F2. Персонализируй email каждому

Шаблоны в [docs/00_strategy/pitch-templates/](../00_strategy/pitch-templates/):
- `tourism-board.md` — tob.rs, serbia.travel, novisad.travel
- `expat-forum.md` — expat.com, serbia forum boards
- `russian-diaspora.md` — RU-language communities в Сербии
- `travel-blog.md` — Balkan travel bloggers

**Rule:** НЕ массово copy-paste. Каждый email:
1. Прочитай 1 статью на их сайте (≥ 2 мин).
2. Первый параграф = конкретный reference ("Вашу статью про X прочитал, и…")
3. Упомяни конкретный page на prevozni.com который им полезен.
4. Конкретный ask: "Можно ли добавить ссылку в секцию X вашей страницы Y?"

### F3. Send & track

1. Отправь **вручную** через gmail (не SMTP нашего сайта — чтобы у тебя
   reply-to был личный). < 10 в день, иначе Gmail spam-filter triggers.
2. В `backlinks-targets.csv` для каждого отправленного:
   ```
   status=contacted
   contacted_at=YYYY-MM-DD
   notes=<о чём письмо>
   ```
3. Git commit CSV — pipeline `scripts/backlinks_digest.py` будет отслеживать
   follow-up timing.

### F4. Follow-up schedule

- Day 0: initial pitch
- Day 7: follow-up если no reply (одно, не больше)
- Day 30: close as "no_response"

`scripts/backlinks_digest.py` генерит еженедельный reminder через Telegram
(воскресенье — уже в cron после E2).

---

## G. UI-форма email subscribe — уже в коде ✅

**Сделано в этой задаче** (commit `feat(ui): newsletter forms …`):

- [app/templates/_partials/_newsletter_form.html](../../app/templates/_partials/_newsletter_form.html)
  — macro с 3 variants: footer / hero / price_alert
- [app/templates/_partials/_footer.html](../../app/templates/_partials/_footer.html)
  — footer column `brand` теперь содержит newsletter form
- [app/templates/index.html](../../app/templates/index.html) — hero-variant
  между hero и stats (`.home-newsletter`)
- [app/templates/route_detail.html](../../app/templates/route_detail.html)
  — price-alert variant между trip list и partners-block
- [app/static/css/app.css](../../app/static/css/app.css) — `.newsletter-form*`
  стили, `.visually-hidden` utility
- [app/i18n.py](../../app/i18n.py) — 13 новых ключей (`newsletter.*`, `price_alert.*`)
  × 3 языка = 39 строк
- JS handler в base.html — fetch POST + in-place success/error message,
  Umami `newsletter_signup` event на 202

Проверки:
```bash
curl -s http://localhost:5000/ | grep -c '<form class="newsletter-form'
# 2  (home hero + footer)
curl -s http://localhost:5000/rute/beograd-novi-sad/ | grep -c '<form class="newsletter-form'
# 2  (price-alert + footer)
curl -s http://localhost:5000/o-nama/ | grep -c '<form class="newsletter-form'
# 1  (footer only)
```

Тесты: `tests/test_activation.py` (12 tests, все passing).

**Что осталось:** только SMTP (шаг B) чтобы конверсии реально приходили в inbox.

---

## H. Monitoring (5 мин)

### H1. Cloudflare Analytics

1. https://dash.cloudflare.com → prevozni.com → Analytics
2. Убедись что "Requests" > 0 за последние 24h (если сайт в проде).
3. **Analytics → Edit Notifications → Add:**
   - Event: `5xx Error Code`
   - Threshold: `> 10 per minute`
   - Channel: email klaschukk@gmail.com

### H2. Umami

1. https://analytics.farmako.ro/ (проверь у себя URL)
2. Website `prevozni.com` → **Current Visitors** > 0 (если трафик есть)
3. Events → `ba_click`, `search_submit`, `newsletter_signup`, `scroll_depth`
   — все должны появляться. Если `newsletter_signup` отсутствует после
   первого живого submit — проверь что Umami script загрузился (блокеры?).

### H3. Healthcheck cron — already running

```bash
# Должно быть:
crontab -l | grep healthcheck
# */5 * * * * /home/klaschuk/transit/scripts/healthcheck.sh
# Если нет — добавь.
```

### H4. Logs — быстрый sanity check

```bash
tail -200 /home/klaschuk/transit/logs/error.log | grep -vE '^$' | head -20
# Ожидаемо: 0 stack traces за последний час.
# Если видишь "Conflicting lock" на analytics.duckdb — гипотеза для отдельной задачи,
# не блокирует activation.
```

---

## Порядок выполнения (recommended)

**Sprint 1 (сегодня, 60 мин):**
1. A. Admin creds + systemd (15)
2. B. Resend SMTP + DNS (20)
3. C. GSC + Bing + Yandex (10)
4. E. GSC cron (5)
5. H. Monitoring alerts (5)
6. Run `scripts/activation_check.sh https://prevozni.com` — зелёный отчёт.

**Sprint 2 (завтра):**
7. D. AdSense submit (5 мин) — ждёшь 2-4 недели.
8. F. Backlinks wave 1 (30 мин) — 10 писем.

**Sprint 3 (через месяц):**
9. F repeats — 10 новых backlinks/неделя.
10. D follow-up — если AdSense approved, Auto-ads включить.

---

## Rollback master

Если всё пошло не так:

```bash
# Убрать все env vars, вернуться к до-activation состоянию
sudo systemctl edit --full transit.service
# Удали все добавленные Environment= строки.
sudo systemctl daemon-reload && sudo systemctl restart transit
# Сайт живёт, admin — 503, mailer — dev-log fallback, sitemap — serving.
# Ничего не теряется; просто activation не активна.
```

User action blocked items не коммитятся в git — credentials в systemd unit
(вне репо). Безопасно.

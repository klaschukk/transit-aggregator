# Door-to-door блок (трансфер / аренда авто) — как включить

Код готов (`app/affiliates/transfers.py`, `_partials/_transfer_offer.html`), **на проде спит**: без ссылок ничего не рисуется.

## Почему это главный рычаг
За 30 дней (2026-08-22..09-21): 721 клик «Buy», все на BusTicket4 (комиссия ~2%); 55% с английских страниц; топ-маршруты —
туристические коридоры (Podgorica–Kotor, Budva–Kotor, Mostar–Kotor, Budva–Podgorica, Mostar–Budva). Туристам там нужны
трансфер и авто; такие программы платят за одну бронь на порядок больше, чем 2% с автобусного билета. Реальные продажи BT4 не видны
(`bt4_sales` пуст), поэтому цифру дохода обещать нельзя — сначала смотрим CTR блока.

## Что сделать владельцу (10–15 минут)
1. Зарегистрироваться в Travelpayouts, добавить сайт prevozni.com (если попросят вставить верификационный код в `<head>` — сказать сессии, вставим за минуту).
2. Подать заявки: трансферы (Kiwitaxi / Welcome Pickups) и аренда авто (Discover Cars / Localrent / EconomyBookings); дождаться одобрения.
3. В генераторе ссылок взять партнёрские ссылки (только `https://`).
4. `cp data/affiliates.local.json.example data/affiliates.local.json`, вписать `AFF_TRANSFER_URL` / `AFF_CARS_URL` (+ `*_NAME`, если хотите видеть бренд на кнопке).
   Плейсхолдеры в URL, если партнёр поддерживает глубокие ссылки: `{from} {to} {from_name} {to_name}` (кодируются сами).
5. `sudo systemctl restart prevozni` (или `scripts/ship_local.sh --fast`).

Переменные окружения с теми же именами приоритетнее файла. Файл вне git.

## Где показывается и как смотреть результат
- Только страницы маршрутов, где оба города из `TOURIST_CITIES` (список в `transfers.py`; Белград—Будва и подобное сознательно не включены).
- Один спокойный блок между списком рейсов и подпиской на цену, ссылки `rel="sponsored nofollow noopener"`, с пометкой о комиссии.
- Клики пишутся в `ba_clicks` с `partner = transfer | cars` — видны в админке рядом с BT4 и в SQL:
  `select route_slug, partner, count(*) from ba_clicks where partner in ('transfer','cars') group by 1,2 order by 3 desc;`
- Рекламные правила не менялись: авто-реклама и липкий anchor по-прежнему выключены.

## Balkan Loop планировщик (`/balkan-loop/`, с 2026-10-14)

Страница строит маршрут «старт, финиш, N дней» из прямых автобусов между 13 городами кольца (`app/planner.py`, список `STOPS`).
Работает и без партнёрок: каждая deonica ведёт на `/rute/<slug>/`, где уже стоит кнопка BusTicket4.

Четыре спящих слота (`app/affiliates/trip_extras.py`), тот же файл `data/affiliates.local.json`:

| Ключ | Где показывается | Плейсхолдер |
|------|------------------|-------------|
| `AFF_STAY_URL` / `AFF_STAY_NAME` | под каждым городом (жильё) | `{city}` |
| `AFF_TOURS_URL` / `AFF_TOURS_NAME` | под каждым городом (туры) | `{city}` |
| `AFF_ESIM_URL` / `AFF_ESIM_NAME` | один раз под маршрутом | нет |
| `AFF_INSURANCE_URL` / `AFF_INSURANCE_NAME` | один раз под маршрутом | нет |

Только `https://`. После правки файла: `scripts/ship_local.sh --fast`. Клики пишутся в `ba_clicks` с `surface = planner`
и `partner = stay | tours | esim | insurance`:
`select partner, route_slug, count(*) from ba_clicks where surface='planner' group by 1,2 order by 3 desc;`

### SEO-устройство (2026-10-14)

- `/balkan-loop/` — хаб: форма, карточки готовых маршрутов, индекс всех прямых автобусов между городами кольца. Индексируется.
- `/balkan-loop/<slug>/` — 7 готовых маршрутов (`planner.PRESETS`), у каждого свои title/description/H1, вводка и FAQ из данных,
  разметка `TouristTrip` + `FAQPage`, своя OG-картинка (`/og/balkan-loop/<slug>.png`). Если расписание перестало складываться
  в цепочку, страница отдаёт 404 и сама пропадает из `sitemap-core.xml`.
- `/balkan-loop/?from=&to=&days=` — результат формы: `noindex, follow`. Если параметры совпали с готовым маршрутом, 301 на его адрес.
- Новый готовый маршрут = одна строка в `PRESETS`; тексты и разметка соберутся сами. Не добавлять зеркальные (A→B и B→A)
  и почти одинаковые маршруты: это дубли, а не новые страницы.
- Качество цепочки настраивается константами в `app/planner.py`: `HOUR_TAX`, `STOP_COST`, `TURN_COST`.
- Запросы под title подбирались без данных Search Console (API на боксе не настроен). Через 3–4 недели сверить с реальными
  запросами в GSC и поправить `planner.title` / `planner.p_title` в `app/i18n.py`.

Стоп-условие, о котором договорились 2026-10-14: если к 15 декабря `/en/balkan-loop/` не набирает показов в Search Console,
дальше в планировщик не вкладываемся.

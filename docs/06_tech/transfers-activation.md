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

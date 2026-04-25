"""Seed three pre-baked campaign drafts on app boot if they don't exist.

This file owns the *content* of the welcome / weekly / seasonal templates
in three languages. Editing here and re-running upsert refreshes the
draft without losing the campaign id (so analytics already collected
against the campaign survive a content tweak).

Why files-not-DB-fixtures: the templates themselves are versioned in git
so we can review/revert content changes through normal PR review. The
DB row is just a working-copy reflection of the latest template.
"""
from __future__ import annotations

import logging

from app.newsletter import campaigns as cmp_mod

logger = logging.getLogger(__name__)


# ── Campaign 1: Welcome (auto-trigger on confirm + 2h) ─────────────────

WELCOME = {
    'slug': 'welcome-confirmed',
    'template_kind': 'welcome',
    'subjects': {
        'sr': 'Dobrodošli! 5 najpopularnijih ruta na Prevozni',
        'en': 'Welcome! 5 most popular bus routes in Serbia',
        'ru': 'Добро пожаловать! 5 популярных автобусных маршрутов',
    },
    'preheaders': {
        'sr': 'Pretraga, raspored, cene — sve na jednom mestu.',
        'en': 'Search, schedules, prices — all in one place.',
        'ru': 'Поиск, расписания, цены — всё в одном месте.',
    },
    'bodies': {
        'sr': """# Dobrodošli na Prevozni!

Hvala što ste se pridružili — sad ćete dobijati obaveštenja o nižim cenama
i novim rutama u Srbiji i susednim zemljama.

## 5 najpopularnijih ruta

- [Beograd → Novi Sad](https://prevozni.com/voznja/beograd-do-novi-sad/) — više od 80 polazaka dnevno
- [Beograd → Niš](https://prevozni.com/voznja/beograd-do-nis/) — 5 časova autoputem
- [Beograd → Subotica](https://prevozni.com/voznja/beograd-do-subotica/) — direktno do mađarske granice
- [Beograd → Sarajevo](https://prevozni.com/voznja/beograd-do-sarajevo/) — najjeftinija veza ka Bosni
- [Beograd → Budva](https://prevozni.com/voznja/beograd-do-budva/) — letnja klasika za Crnu Goru

## Šta još imamo?

- **462 međugradskih ruta** sa pravim cenama i vremenima polaska
- **Gradski prevoz** za Beograd, Novi Sad, Niš i Kragujevac
- **Tri jezika** — sr/en/ru, biraćemo automatski po vašem
- **Bez registracije** — samo pretražite i krenite

Idite na [prevozni.com](https://prevozni.com) i probajte sami.

— Tim Prevozni
""",
        'en': """# Welcome to Prevozni!

Thanks for joining — you'll now get alerts on price drops and new routes
across Serbia and the Balkans.

## Top 5 routes

- [Belgrade → Novi Sad](https://prevozni.com/voznja/beograd-do-novi-sad/) — 80+ daily departures
- [Belgrade → Niš](https://prevozni.com/voznja/beograd-do-nis/) — 5 hours via highway
- [Belgrade → Subotica](https://prevozni.com/voznja/beograd-do-subotica/) — direct to Hungary border
- [Belgrade → Sarajevo](https://prevozni.com/voznja/beograd-do-sarajevo/) — cheapest link to Bosnia
- [Belgrade → Budva](https://prevozni.com/voznja/beograd-do-budva/) — classic summer ride to Montenegro

## What else?

- **462 intercity routes** with real prices and departure times
- **City transport** for Belgrade, Novi Sad, Niš, Kragujevac
- **Three languages** — sr/en/ru, auto-detected
- **No signup** — just search and go

Visit [prevozni.com](https://prevozni.com) and try it.

— The Prevozni team
""",
        'ru': """# Добро пожаловать на Prevozni!

Спасибо, что присоединились — теперь вы будете получать уведомления о
снижении цен и новых маршрутах по Сербии и Балканам.

## Топ-5 маршрутов

- [Белград → Нови-Сад](https://prevozni.com/voznja/beograd-do-novi-sad/) — 80+ рейсов ежедневно
- [Белград → Ниш](https://prevozni.com/voznja/beograd-do-nis/) — 5 часов по автомагистрали
- [Белград → Суботица](https://prevozni.com/voznja/beograd-do-subotica/) — до венгерской границы
- [Белград → Сараево](https://prevozni.com/voznja/beograd-do-sarajevo/) — самый дешёвый рейс в Боснию
- [Белград → Будва](https://prevozni.com/voznja/beograd-do-budva/) — классический летний рейс в Черногорию

## Что ещё?

- **462 междугородних маршрута** с реальными ценами и временем отправления
- **Городской транспорт** Белграда, Нови-Сада, Ниша, Крагуеваца
- **Три языка** — sr/en/ru, автоопределение
- **Без регистрации** — просто ищите и поезжайте

Заходите на [prevozni.com](https://prevozni.com).

— Команда Prevozni
""",
    },
    'audience_filter': {
        'min_days_old': 0,
        'max_days_old': 14,
    },
    'status': 'draft',
}


# ── Campaign 2: Weekly digest ──────────────────────────────────────────

WEEKLY = {
    'slug': 'weekly-digest-template',
    'template_kind': 'weekly',
    'subjects': {
        'sr': 'Ova nedelja na Prevozni: nove rute i niže cene',
        'en': 'This week on Prevozni: new routes and price drops',
        'ru': 'Эта неделя на Prevozni: новые маршруты и снижение цен',
    },
    'preheaders': {
        'sr': 'Sažetak — 30 sekundi čitanja.',
        'en': '30-second weekly recap.',
        'ru': 'Краткий итог — 30 секунд.',
    },
    'bodies': {
        'sr': """# Ova nedelja na Prevozni

## Novi pravci

Ove nedelje smo dodali **{{new_routes_count}}** novih međugradskih ruta —
najznačajnije su {{top_new_routes}}.

## Najtraženije rute

Putnici su najviše puta otvarali ove rute:

1. [Beograd → Budva](https://prevozni.com/voznja/beograd-do-budva/)
2. [Beograd → Novi Sad](https://prevozni.com/voznja/beograd-do-novi-sad/)
3. [Beograd → Sarajevo](https://prevozni.com/voznja/beograd-do-sarajevo/)

## Vodič nedelje

[Kako kupiti autobusku kartu u Srbiji 2026](https://prevozni.com/vodici/kupovina-karte/)
— sve o online + kasama + pravilima za prtljag.

## Akcija od partnera

Provera cena uživo ide preko [Bookaway](https://prevozni.com/?utm_source=newsletter&utm_medium=weekly).
Ako nađete jeftinije, javite nam — naš index ćemo ažurirati sledeće nedelje.

— Vidimo se sledeće nedelje.
""",
        'en': """# This week on Prevozni

## New routes

We added **{{new_routes_count}}** intercity routes this week — most notable:
{{top_new_routes}}.

## Most-searched

Travellers opened these routes most:

1. [Belgrade → Budva](https://prevozni.com/voznja/beograd-do-budva/)
2. [Belgrade → Novi Sad](https://prevozni.com/voznja/beograd-do-novi-sad/)
3. [Belgrade → Sarajevo](https://prevozni.com/voznja/beograd-do-sarajevo/)

## Guide of the week

[How to buy a Serbian bus ticket in 2026](https://prevozni.com/en/vodici/kupovina-karte/)
— online vs. counter, baggage rules, payment options.

## Partner deal

Live ticketing runs through [Bookaway](https://prevozni.com/?utm_source=newsletter&utm_medium=weekly).
Found a cheaper price somewhere? Tell us — we'll update next week.

— See you next week.
""",
        'ru': """# Эта неделя на Prevozni

## Новые маршруты

На этой неделе мы добавили **{{new_routes_count}}** междугородних маршрутов
— наиболее важные: {{top_new_routes}}.

## Самые искомые

Путешественники чаще всего смотрели:

1. [Белград → Будва](https://prevozni.com/voznja/beograd-do-budva/)
2. [Белград → Нови-Сад](https://prevozni.com/voznja/beograd-do-novi-sad/)
3. [Белград → Сараево](https://prevozni.com/voznja/beograd-do-sarajevo/)

## Гид недели

[Как купить билет на автобус в Сербии в 2026](https://prevozni.com/ru/vodici/kupovina-karte/)
— онлайн vs касса, багаж, способы оплаты.

## Партнёрское предложение

Реальное бронирование через [Bookaway](https://prevozni.com/?utm_source=newsletter&utm_medium=weekly).
Нашли дешевле? Напишите — обновим на следующей неделе.

— До встречи через неделю.
""",
    },
    'audience_filter': {
        'route_slug': None,  # generic newsletter only — exclude price-alerts
        'min_days_old': 1,
    },
    'status': 'draft',
}


# ── Campaign 3: Seasonal travel (manual trigger) ───────────────────────

SEASONAL_SUMMER = {
    'slug': 'seasonal-summer',
    'template_kind': 'seasonal',
    'subjects': {
        'sr': 'Letnja sezona — autobus do mora po najnižoj ceni',
        'en': 'Summer is here — bus to the Adriatic at lowest prices',
        'ru': 'Лето — автобусы на море по лучшей цене',
    },
    'preheaders': {
        'sr': 'Top 7 ruta ka Crnoj Gori i Hrvatskoj.',
        'en': 'Top 7 routes to Montenegro and Croatia.',
        'ru': 'Топ-7 маршрутов в Черногорию и Хорватию.',
    },
    'bodies': {
        'sr': """# Letnja sezona je počela

Ako planirate godišnji odmor na moru, provera cena autobusa pre
rezervacije šedi vam 30–60% u poređenju sa avionom + transferom.

## Najtraženije letnje rute

- [Beograd → Budva](https://prevozni.com/voznja/beograd-do-budva/) — direktno, ~12 sati
- [Beograd → Bar](https://prevozni.com/voznja/beograd-do-bar/) — alternativa
- [Beograd → Tivat](https://prevozni.com/voznja/beograd-do-tivat/) — najbliže Bokokotorskoj
- [Beograd → Split](https://prevozni.com/voznja/beograd-do-split/) — u Hrvatsku
- [Beograd → Dubrovnik](https://prevozni.com/voznja/beograd-do-dubrovnik/)
- [Novi Sad → Budva](https://prevozni.com/voznja/novi-sad-do-budva/)
- [Niš → Budva](https://prevozni.com/voznja/nis-do-budva/)

## Saveti za rezervaciju

- **Knjižite 2–3 nedelje unapred** — cene rastu posle 7 dana pre polaska
- **Noćna polazna** štedi vam jednu noć smeštaja
- **Prtljag do 20 kg** je obično uključen u cenu

Sve cene + raspored su uživo na [prevozni.com](https://prevozni.com).

Ugodno more.
— Prevozni
""",
        'en': """# Summer is here

If you're heading to the Adriatic this season, checking bus prices
before booking saves 30–60% versus flight + transfer.

## Top summer routes

- [Belgrade → Budva](https://prevozni.com/voznja/beograd-do-budva/) — direct, ~12h
- [Belgrade → Bar](https://prevozni.com/voznja/beograd-do-bar/) — alternative
- [Belgrade → Tivat](https://prevozni.com/voznja/beograd-do-tivat/) — closest to Boka
- [Belgrade → Split](https://prevozni.com/voznja/beograd-do-split/) — into Croatia
- [Belgrade → Dubrovnik](https://prevozni.com/voznja/beograd-do-dubrovnik/)
- [Novi Sad → Budva](https://prevozni.com/voznja/novi-sad-do-budva/)
- [Niš → Budva](https://prevozni.com/voznja/nis-do-budva/)

## Booking tips

- **Book 2–3 weeks ahead** — prices climb sharply inside 7 days
- **Night departures** save one hotel night
- **20 kg luggage** is usually included

All prices + schedules live on [prevozni.com](https://prevozni.com).

Enjoy the sea.
— Prevozni
""",
        'ru': """# Летний сезон начался

Если в этом году едете на Адриатику, проверка цен на автобусы перед
бронированием экономит 30–60% по сравнению с самолётом + трансфер.

## Топ летних маршрутов

- [Белград → Будва](https://prevozni.com/voznja/beograd-do-budva/) — напрямую, ~12 ч
- [Белград → Бар](https://prevozni.com/voznja/beograd-do-bar/) — альтернатива
- [Белград → Тиват](https://prevozni.com/voznja/beograd-do-tivat/) — ближе всего к Бока-Которской
- [Белград → Сплит](https://prevozni.com/voznja/beograd-do-split/) — в Хорватию
- [Белград → Дубровник](https://prevozni.com/voznja/beograd-do-dubrovnik/)
- [Нови-Сад → Будва](https://prevozni.com/voznja/novi-sad-do-budva/)
- [Ниш → Будва](https://prevozni.com/voznja/nis-do-budva/)

## Советы по бронированию

- **Покупайте за 2–3 недели** — цены резко растут за 7 дней до
- **Ночные рейсы** экономят одну ночёвку в отеле
- **20 кг багажа** обычно включены

Цены + расписание уживо на [prevozni.com](https://prevozni.com).

Хорошего моря.
— Prevozni
""",
    },
    'audience_filter': {
        'route_slug': None,
    },
    'status': 'draft',
}


_DRAFTS = (WELCOME, WEEKLY, SEASONAL_SUMMER)


def seed() -> list[int]:
    """Idempotent — refreshes existing drafts to current template, creates
    missing ones. Returns the list of campaign ids."""
    ids: list[int] = []
    for d in _DRAFTS:
        cid = cmp_mod.upsert_campaign(
            slug=d['slug'],
            template_kind=d['template_kind'],
            subjects=d['subjects'],
            preheaders=d['preheaders'],
            bodies=d['bodies'],
            audience_filter=d['audience_filter'],
            status=d['status'],
        )
        ids.append(cid)
    logger.info('seeded %d newsletter drafts', len(ids))
    return ids

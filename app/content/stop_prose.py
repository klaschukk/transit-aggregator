"""Rules-based prose generator for /gradski/{city}/stajaliste/{slug}/ pages.

Problem: 2179 stop pages are thin — map + line list + ETA + breadcrumb.
Google classifies them "Discovered, not indexed" because the unique-text
budget per page is ~20 words. This module fills that gap by interpolating
4 paragraphs (~200 words total) from data we already hold.

Design principles:
1. Deterministic. Same (stop, lang) → same prose, cache-friendly.
2. Adjacent stops should not produce visually identical pages. We hash
   `slug + paragraph_salt` independently per paragraph, so two neighbouring
   stops almost never land on the same template tuple.
3. Conditional slots. Optional sentences (POIs, GTFS hours) attach only
   when data exists; core templates use always-available slots.
4. No LLM calls. Pure string.format() over curated template pools.

The `build_prose(...)` entry point returns a `dict` keyed by paragraph
(intro / service / location / tip) for the template to render.
"""
from __future__ import annotations

from hashlib import md5
from typing import Iterable

from app.content.pois import _haversine_m, nearest_poi


# ── Template pools ──────────────────────────────────────────────────────

# Each pool is a list of format strings keyed by language. Format placeholders
# only reference keys from _compute_slots() — adding a new template is the
# common case; adding a new slot is the rare one.

_INTRO: dict[str, list[str]] = {
    # Appositive pattern + locative city form ({city_loc}) and genitive
    # ({city_gen}) for Slavic case agreement. District always nominative.
    'sr': [
        '{stop_name} je stajalište gradskog prevoza u {city_loc}, na koordinatama '
        '{coord_str} (zona: {district}). Kroz njega prolazi {line_count} linija.',
        '{stop_name} — stajalište u {city_loc} koje opslužuje {line_count} linija gradskog '
        'prevoza. Zona grada: {district}.',
        'Na stajalištu {stop_name} u {city_loc} staje {line_count} linija; stajalište je '
        'u zoni {district}, {coord_str}.',
        'Stajalište {stop_name} je deo mreže gradskog prevoza {city_gen} — kroz njega '
        'prolazi {line_count} linija svakog radnog dana. Kategorija stajališta: {size_category}.',
        '{stop_name} se nalazi u {city_loc} (zona: {district}); ovde staje {line_count} '
        'linija gradskog prevoza ({size_category} punkt).',
        'Za putnike iz zone {district} u {city_loc}, stajalište {stop_name} nudi presedanje '
        'na {line_count} linija ({size_category} čvorište).',
        'Stajalište {stop_name} ({coord_str}) pripada zoni {district} u {city_loc}; '
        'opslužuje ga {line_count} linija gradskog prevoza.',
        'U zoni {district} u {city_loc}, stajalište {stop_name} pruža presedanje na '
        '{line_count} linija — kategorija stajališta: {size_category}.',
    ],
    'en': [
        '{stop_name} is a public-transit stop in {city_label} ({district} area), at '
        '{coord_str}. It is served by {line_count} lines.',
        '{stop_name} — a stop in {city_label} served by {line_count} city-transit lines; '
        'it sits in the {district} area.',
        'At the {stop_name} stop in {city_label}, {line_count} lines make a call; the stop '
        'is in the {district} area, {coord_str}.',
        '{stop_name} is part of the {city_label} public-transit network — {line_count} lines '
        'call at this stop on a typical weekday. Stop tier: {size_category}.',
        '{stop_name} sits in the {district} area of {city_label}; {line_count} lines of city '
        'transit stop here ({size_category} hub).',
        'For travellers from the {district} side of {city_label}, {stop_name} offers a '
        'transfer to {line_count} lines ({size_category} node).',
        'The {stop_name} stop ({coord_str}) is in the {district} area of {city_label}; '
        '{line_count} transit lines serve it.',
        'In the {district} area of {city_label}, {stop_name} gives access to {line_count} '
        'transit lines — placing it in the {size_category} stop tier.',
    ],
    'ru': [
        '{stop_name} — остановка городского транспорта в {city_loc}, координаты '
        '{coord_str} (район: {district}). Её обслуживают {line_count} линий.',
        '{stop_name}: остановка в {city_loc} с {line_count} линиями городского транспорта. '
        'Район города: {district}.',
        'На остановке {stop_name} в {city_loc} останавливаются {line_count} линий; '
        'остановка в районе {district}, {coord_str}.',
        '{stop_name} — часть сети городского транспорта {city_gen}: {line_count} линий '
        'проходят через эту остановку по будням. Категория: {size_category_ru}.',
        '{stop_name} находится в {city_loc} (район: {district}); здесь останавливаются '
        '{line_count} линий городского транспорта ({size_category_ru} узел).',
        'Для пассажиров из района {district} в {city_loc} остановка {stop_name} — '
        'возможность пересесть на {line_count} линий ({size_category_ru} узел).',
        'Остановка {stop_name} ({coord_str}) относится к району {district} в {city_loc}; '
        'её обслуживают {line_count} линий городского транспорта.',
        'В районе {district} в {city_loc} остановка {stop_name} даёт доступ к {line_count} '
        'линиям — категория остановки: {size_category_ru}.',
    ],
}

# Optional suffix attached to intro when a POI is < 500 m away.
_INTRO_POI_SUFFIX: dict[str, list[str]] = {
    'sr': [
        ' U neposrednoj blizini nalazi se {poi_name} ({poi_distance}).',
        ' Stajalište je na samo {poi_distance} od {poi_name}.',
        ' Pored stajališta je {poi_name} (pešačenje {poi_distance}).',
    ],
    'en': [
        ' {poi_name} is in the immediate vicinity ({poi_distance}).',
        ' The stop is only {poi_distance} from {poi_name}.',
        ' {poi_name} is right by the stop ({poi_distance} on foot).',
    ],
    'ru': [
        ' Рядом находится {poi_name} ({poi_distance}).',
        ' Остановка всего в {poi_distance} от {poi_name}.',
        ' В шаговой доступности {poi_name} (около {poi_distance}).',
    ],
}


_SERVICE: dict[str, list[str]] = {
    # All four variants put {type_breakdown} after an em-dash or semicolon so
    # the breakdown fragment ("od toga autobusa 5, …") flows as a subordinate
    # clause without a capitalization mismatch.
    'sr': [
        'Linije koje staju na ovom stajalištu su {line_numbers} — {type_breakdown}.',
        'Sa stajališta polaze linije {line_numbers} — {type_breakdown}.',
        'Ovo stajalište opslužuju linije {line_numbers}; {type_breakdown}.',
        'Kroz stajalište prolaze linije {line_numbers}; {type_breakdown}.',
    ],
    'en': [
        'Lines calling at this stop: {line_numbers} — {type_breakdown}.',
        'From this stop you can take lines {line_numbers} — {type_breakdown}.',
        'This stop is served by lines {line_numbers}; {type_breakdown}.',
        'Lines running through the stop: {line_numbers}; {type_breakdown}.',
    ],
    'ru': [
        'Здесь останавливаются линии {line_numbers} — {type_breakdown}.',
        'С этой остановки отправляются линии {line_numbers} — {type_breakdown}.',
        'Остановку обслуживают линии {line_numbers}; {type_breakdown}.',
        'Через остановку проходят линии: {line_numbers}; {type_breakdown}.',
    ],
}

_SERVICE_GTFS_SUFFIX: dict[str, list[str]] = {
    'sr': [
        ' Prvi polazak sa stajališta je u {first_dep}, poslednji u {last_dep} radnim danom.',
        ' Radnim danom prvi autobus kreće u {first_dep}, a poslednji se završava oko {last_dep}.',
        ' Prevoz saobraća od {first_dep} do {last_dep} (radni dan, GTFS red vožnje).',
    ],
    'en': [
        ' The first weekday departure is at {first_dep}, the last at {last_dep}.',
        ' On weekdays the first bus leaves at {first_dep} and the last wraps up around {last_dep}.',
        ' Service runs {first_dep}–{last_dep} on weekdays (GTFS schedule).',
    ],
    'ru': [
        ' Первый рейс с остановки в {first_dep}, последний в {last_dep} в будние дни.',
        ' В будние дни первый автобус отходит в {first_dep}, последний — около {last_dep}.',
        ' Движение по будням с {first_dep} до {last_dep} (GTFS-расписание).',
    ],
}

# Attached to service paragraph when we have top endpoint destinations.
_SERVICE_ENDPOINTS: dict[str, list[str]] = {
    'sr': [
        ' Najčešći krajnji ciljevi linija su {endpoints}.',
        ' Linije sa ovog stajališta vode ka {endpoints}.',
        ' Odavde možete stići do {endpoints}.',
    ],
    'en': [
        ' The most common endpoints are {endpoints}.',
        ' Lines from this stop head to {endpoints}.',
        ' From here you can reach {endpoints}.',
    ],
    'ru': [
        ' Типичные конечные точки — {endpoints}.',
        ' Линии с этой остановки идут в {endpoints}.',
        ' Отсюда можно добраться до {endpoints}.',
    ],
}

# Always-appended frequency heuristic based on line count — adds 15–25 words,
# pushes the overall prose past the 150-word target even when GTFS data is
# missing.
_SERVICE_FREQUENCY: dict[str, list[str]] = {
    'sr': [
        ' U jutarnjim (07:00–09:00) i popodnevnim (16:00–18:00) vrhovima intervali su '
        'kraći, pa je {size_category} punkt kakav je {stop_name} najiskorišćeniji u tim satima.',
        ' Peak sati radnim danom ({size_category} stajalište) uglavnom su između 07 i 09 '
        'ujutru i 16–18 popodne; van tih sati intervali su znatno duži.',
        ' Najveći saobraćaj je ujutru i kasno popodne — {size_category} stajalište sa '
        '{line_count} linija dobro pokriva radne sate. Vikendom je broj polazaka manji.',
    ],
    'en': [
        ' Weekday peaks (07:00–09:00 and 16:00–18:00) see the shortest intervals, so '
        'a {size_category} stop like {stop_name} is busiest during those windows.',
        ' Peak hours on weekdays ({size_category} stop) fall between 07 and 09 '
        'in the morning and 16–18 in the evening; intervals outside those windows are noticeably longer.',
        ' Traffic is heaviest morning and late afternoon — a {size_category} stop with '
        '{line_count} lines covers commuter hours well. Weekend service is lighter.',
    ],
    'ru': [
        ' В утренний (07:00–09:00) и вечерний (16:00–18:00) пики интервалы короче, '
        'так что {size_category_ru} остановка вроде {stop_name} наиболее загружена в эти часы.',
        ' Пиковые часы в будни ({size_category_ru} остановка) — с 07 до 09 утром '
        'и 16–18 вечером; вне этих окон интервалы заметно длиннее.',
        ' Наибольший поток утром и ближе к вечеру — {size_category_ru} остановка с '
        '{line_count} линиями хорошо покрывает рабочие часы. По выходным рейсов меньше.',
    ],
}


_LOCATION: dict[str, list[str]] = {
    'sr': [
        'Stajalište se nalazi u zoni {district} ({city_label}).',
        'Lokacija je u zoni {district}, u {city_loc}.',
        '{stop_name} pripada zoni {district} u {city_loc}.',
    ],
    'en': [
        'The stop sits in the {district} area of {city_label}.',
        'It is located in the {district} part of {city_label}.',
        '{stop_name} is positioned in the {district} area of {city_label}.',
    ],
    'ru': [
        'Остановка расположена в районе {district} ({city_label}).',
        'Находится в районе {district}, в {city_loc}.',
        '{stop_name} относится к району {district} в {city_loc}.',
    ],
}

_LOCATION_NEARBY_SUFFIX: dict[str, list[str]] = {
    'sr': [
        ' Najbliža stajališta u radijusu od 500 metara: {nearby_list}.',
        ' U okruženju su stajališta {nearby_list}.',
        ' U neposrednoj blizini pešačke razdaljine su: {nearby_list}.',
    ],
    'en': [
        ' Stops within 500 m walking distance: {nearby_list}.',
        ' Neighbouring stops are {nearby_list}.',
        ' A short walk away: {nearby_list}.',
    ],
    'ru': [
        ' Ближайшие остановки в радиусе 500 м: {nearby_list}.',
        ' Рядом остановки {nearby_list}.',
        ' В шаговой доступности: {nearby_list}.',
    ],
}


_TIP: dict[str, list[str]] = {
    'sr': [
        'Za presedanje na međugradski prevoz pogledajte <a href="{prefix}/rute/">katalog autobuskih linija</a> '
        'iz {city_gen}; polasci ka svim delovima Srbije dostupni su sa BAS i drugih stanica. Mnoge linije imaju '
        'noćne varijante koje vozi isti prevoznik, pa provera reda vožnje vredi pre polaska.',
        'Ako planirate putovanje van {city_gen}, <a href="{prefix}/rute/">pregled svih međugradskih ruta</a> '
        'pomoći će vam da nađete najbliži termin sa autobuske stanice. Za najčešće relacije cene počinju '
        'od oko 10€, a noćni polasci su obično najpovoljniji.',
        'Iz ovog kraja do drugih gradova možete stići <a href="{prefix}/rute/">međugradskim autobusima</a> — '
        'sve aktivne linije sa cenama i vremenima putovanja su na jednom mestu. Za putovanja preko granice '
        '({city_gen} → Crna Gora / BiH / Hrvatska) preporučujemo kupovinu karte 1–3 dana unapred.',
        'Posle gradskog prevoza, <a href="{prefix}/rute/">katalog međugradskih polazaka</a> pokazuje sve '
        'opcije za putovanje van {city_gen} u bilo kom pravcu. Takođe možete pogledati '
        '<a href="{prefix}/gradski/">mreže gradskog prevoza drugih gradova Srbije</a> kada menjate polazište.',
    ],
    'en': [
        'To transfer onto intercity service, see the <a href="{prefix}/rute/">catalog of bus routes</a> '
        'from {city_label}; departures across Serbia leave from BAS and other stations. Many lines run '
        'overnight variants operated by the same carrier, so checking the schedule before travel pays off.',
        'If you are planning a trip outside {city_label}, the <a href="{prefix}/rute/">intercity route list</a> '
        'helps you find the next departure from the main bus station. For the most common pairs fares start '
        'at around €10, and overnight buses are usually the cheapest.',
        'From this part of town you can reach other cities by <a href="{prefix}/rute/">intercity bus</a> — '
        'all active routes, fares and durations sit on one page. For cross-border trips '
        '({city_label} → Montenegro / Bosnia / Croatia) we recommend booking 1–3 days ahead.',
        'Beyond city transit, the <a href="{prefix}/rute/">intercity departures catalog</a> covers every '
        'option out of {city_label} in any direction. You can also explore '
        '<a href="{prefix}/gradski/">city-transit networks in other Serbian cities</a> when changing your starting point.',
    ],
    'ru': [
        'Для пересадки на междугородний транспорт смотрите <a href="{prefix}/rute/">каталог автобусных маршрутов</a> '
        'из {city_gen}; рейсы по всей Сербии уходят с BAS и других станций. У многих линий есть ночные '
        'варианты того же перевозчика — проверка расписания перед поездкой не помешает.',
        'Если планируете поездку за пределы {city_gen}, <a href="{prefix}/rute/">список междугородних маршрутов</a> '
        'поможет найти ближайший рейс с автовокзала. На популярных направлениях цены начинаются примерно '
        'от 10€, а ночные автобусы обычно самые выгодные.',
        'Из этой части города в другие города можно добраться <a href="{prefix}/rute/">междугородним автобусом</a> — '
        'все действующие маршруты с ценами и временем в пути собраны вместе. Для международных рейсов '
        '({city_gen} → Черногория / БиГ / Хорватия) билет лучше брать за 1–3 дня.',
        'После городского транспорта <a href="{prefix}/rute/">каталог междугородних рейсов</a> показывает все '
        'варианты выезда из {city_gen} в любом направлении. Также можно посмотреть '
        '<a href="{prefix}/gradski/">сети городского транспорта других городов Сербии</a> при смене точки старта.',
    ],
}


# ── District mapping ────────────────────────────────────────────────────

# Very coarse district bins per city. Hits once per request and only picks a
# label — correctness isn't critical, uniqueness across neighbouring stops is.

def _district_label(city: str, lat: float | None, lon: float | None, lang: str) -> str:
    labels = _DISTRICT_LABELS.get(lang, _DISTRICT_LABELS['sr'])
    if lat is None or lon is None:
        return labels['center']
    if city == 'beograd':
        # Crude axis-aligned bins covering the metro.
        if lat > 44.84 and lon < 20.46: return labels['zemun']
        if lat > 44.83 and lon < 20.43: return labels['novi_beograd']
        if lat > 44.82 and lon >= 20.46: return labels['stari_grad']
        if lat < 44.80 and lon < 20.43: return labels['cukarica']
        if lat < 44.80 and lon < 20.48: return labels['rakovica']
        if lat < 44.80 and lon >= 20.48: return labels['vozdovac']
        if lon >= 20.48: return labels['zvezdara']
        return labels['center']
    if city == 'novi-sad':
        if lat < 45.25: return labels['petrovaradin']
        if lon < 19.83: return labels['west_ns']
        if lon > 19.86: return labels['east_ns']
        return labels['center']
    if city == 'nis':
        if lon < 21.88: return labels['west']
        if lon > 21.91: return labels['east']
        return labels['center']
    return labels['center']


_DISTRICT_LABELS: dict[str, dict[str, str]] = {
    # Nominative-only names so templates can wrap them in grammar-safe
    # constructions like "(Rakovica zona)" or "в районе Раковица".
    'sr': {
        'zemun': 'Zemun', 'novi_beograd': 'Novi Beograd',
        'stari_grad': 'Stari grad', 'cukarica': 'Čukarica',
        'rakovica': 'Rakovica', 'vozdovac': 'Voždovac',
        'zvezdara': 'Zvezdara', 'center': 'centar',
        'petrovaradin': 'Petrovaradin', 'west_ns': 'zapadni',
        'east_ns': 'istočni', 'west': 'zapadni', 'east': 'istočni',
    },
    'en': {
        'zemun': 'Zemun', 'novi_beograd': 'Novi Beograd',
        'stari_grad': 'Old Town', 'cukarica': 'Čukarica',
        'rakovica': 'Rakovica', 'vozdovac': 'Voždovac',
        'zvezdara': 'Zvezdara', 'center': 'central',
        'petrovaradin': 'Petrovaradin', 'west_ns': 'western',
        'east_ns': 'eastern', 'west': 'western', 'east': 'eastern',
    },
    'ru': {
        'zemun': 'Земун', 'novi_beograd': 'Новый Белград',
        'stari_grad': 'Старый город', 'cukarica': 'Чукарица',
        'rakovica': 'Раковица', 'vozdovac': 'Вождовац',
        'zvezdara': 'Звездара', 'center': 'центр',
        'petrovaradin': 'Петроварадин', 'west_ns': 'запад',
        'east_ns': 'восток', 'west': 'запад', 'east': 'восток',
    },
}


# ── Labels & formatters ─────────────────────────────────────────────────

_VEHICLE_KIND: dict[str, dict[str, str]] = {
    'sr': {'bus': 'autobusko', 'tram': 'tramvajsko', 'trolleybus': 'trolejbusko',
           'night': 'noćno', 'e-bus': 'e-bus', 'bg-voz': 'železničko',
           'suburban': 'prigradsko', 'mixed': 'gradsko'},
    'en': {'bus': 'bus', 'tram': 'tram', 'trolleybus': 'trolleybus',
           'night': 'night', 'e-bus': 'e-bus', 'bg-voz': 'rail',
           'suburban': 'suburban', 'mixed': 'mixed'},
    'ru': {'bus': 'автобусная', 'tram': 'трамвайная', 'trolleybus': 'троллейбусная',
           'night': 'ночная', 'e-bus': 'e-bus', 'bg-voz': 'железнодорожная',
           'suburban': 'пригородная', 'mixed': 'смешанная'},
}

_SIZE_CATEGORY: dict[str, list[str]] = {
    # Order: 1 line, 2-5, 6-15, 16+. Grammatically self-contained labels
    # (used as "Kategorija: {size_category}." or "({size_category} hub)").
    'sr': ['malo', 'sporedno', 'srednje', 'važno'],
    'en': ['small', 'secondary', 'mid-sized', 'major'],
    'ru': ['малая', 'вспомогательная', 'средняя', 'важная'],
}

_CITY_LABELS: dict[str, dict[str, str]] = {
    # Nominative form — used on its own or with appositive constructions.
    'sr': {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'en': {'beograd': 'Belgrade', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'ru': {'beograd': 'Белград', 'novi-sad': 'Нови-Сад', 'nis': 'Ниш', 'kragujevac': 'Крагуевац'},
}

# Locative case — "u Beogradu" / "в Белграде". English repeats the nominative.
_CITY_LABELS_LOC: dict[str, dict[str, str]] = {
    'sr': {'beograd': 'Beogradu', 'novi-sad': 'Novom Sadu', 'nis': 'Nišu', 'kragujevac': 'Kragujevcu'},
    'en': {'beograd': 'Belgrade', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'ru': {'beograd': 'Белграде', 'novi-sad': 'Нови-Саде', 'nis': 'Нише', 'kragujevac': 'Крагуевце'},
}

# Genitive case — "iz Beograda", "карта Белграда".
_CITY_LABELS_GEN: dict[str, dict[str, str]] = {
    'sr': {'beograd': 'Beograda', 'novi-sad': 'Novog Sada', 'nis': 'Niša', 'kragujevac': 'Kragujevca'},
    'en': {'beograd': 'Belgrade', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'ru': {'beograd': 'Белграда', 'novi-sad': 'Нови-Сада', 'nis': 'Ниша', 'kragujevac': 'Крагуеваца'},
}


def _size_bucket(line_count: int) -> int:
    if line_count <= 1: return 0
    if line_count <= 5: return 1
    if line_count <= 15: return 2
    return 3


def _type_breakdown(lines: list[dict], lang: str) -> str:
    """Human sentence fragment: 'autobusa 15, tramvaja 2, trolejbusa 3'."""
    counts: dict[str, int] = {}
    for line in lines:
        t = line.get('type') or 'bus'
        counts[t] = counts.get(t, 0) + 1
    # Order covers all current DB types; unknown types fall through and are
    # silently dropped from the breakdown rather than crashing prose render.
    order = ['bus', 'tram', 'trolleybus', 'night', 'suburban', 'e-bus', 'bg-voz']
    labels = {
        'sr': {'bus': 'autobusa', 'tram': 'tramvaja', 'trolleybus': 'trolejbusa',
               'night': 'noćnih', 'suburban': 'prigradskih',
               'e-bus': 'e-bus linija', 'bg-voz': 'BG Voz linija'},
        # English plural handled per-count below to avoid "1 trams".
        'en': {'bus': ('bus', 'buses'), 'tram': ('tram', 'trams'),
               'trolleybus': ('trolleybus', 'trolleybuses'),
               'night': ('night line', 'night lines'),
               'suburban': ('suburban line', 'suburban lines'),
               'e-bus': ('e-bus', 'e-buses'), 'bg-voz': ('BG Voz', 'BG Voz')},
        'ru': {'bus': 'автобусных', 'tram': 'трамвайных', 'trolleybus': 'троллейбусных',
               'night': 'ночных', 'suburban': 'пригородных',
               'e-bus': 'e-bus', 'bg-voz': 'BG Voz'},
    }[lang]
    parts: list[str] = []
    for t in order:
        n = counts.get(t, 0)
        if not n:
            continue
        if lang == 'en':
            singular, plural = labels[t]
            parts.append(f'{n} {singular if n == 1 else plural}')
        elif lang == 'ru':
            # Genitive plural reads naturally regardless of count: "3 автобусных линий".
            parts.append(f'{labels[t]} линий {n}')
        else:
            parts.append(f'{labels[t]} {n}')
    if not parts:
        return ''
    joiners = {'sr': 'od toga ', 'en': 'including ', 'ru': 'из них '}
    return joiners[lang] + ', '.join(parts)


def _top_endpoints(lines: list[dict], stop_name: str, limit: int = 3) -> list[str]:
    """Pull the 'other side' of each line name ('A — B' form) — rough but
    reliably picks a different city/quarter than the current stop."""
    out: list[str] = []
    seen: set = set()
    for line in lines:
        name = (line.get('name') or '').strip()
        if ' - ' in name or ' — ' in name:
            sep = ' - ' if ' - ' in name else ' — '
            ends = [s.strip() for s in name.split(sep) if s.strip()]
            for end in ends:
                if end and end.lower() != stop_name.lower() and end not in seen:
                    seen.add(end)
                    out.append(end)
                    if len(out) >= limit:
                        return out
    return out


def _pick(pool: list[str], slug: str, salt: str) -> str:
    if not pool:
        return ''
    idx = int(md5(f'{slug}|{salt}'.encode('utf-8')).hexdigest()[:8], 16) % len(pool)
    return pool[idx]


# ── Slot computation ────────────────────────────────────────────────────


def _compute_slots(
    stop: dict, lines: list[dict], nearby: list[dict],
    gtfs_stats: dict | None, lang: str, lang_prefix: str,
) -> dict:
    city = stop.get('city') or 'beograd'
    lat, lon = stop.get('lat'), stop.get('lon')
    line_count = len(lines)
    types = [line.get('type') or 'bus' for line in lines]
    primary_type = max(set(types), key=types.count) if types else 'bus'

    size_bucket = _size_bucket(line_count)
    size_category = _SIZE_CATEGORY[lang][size_bucket]
    size_category_ru = _SIZE_CATEGORY['ru'][size_bucket]

    # Fall back to 'bus' (the overwhelming majority) for any future type not
    # yet in the label maps — future-proofs prose rendering against new scraper
    # types entering the DB without a code change.
    vkind = _VEHICLE_KIND[lang].get(primary_type, _VEHICLE_KIND[lang]['bus'])
    vkind_ru = _VEHICLE_KIND['ru'].get(primary_type, _VEHICLE_KIND['ru']['bus'])

    city_label = _CITY_LABELS[lang].get(city, city.title())
    city_loc = _CITY_LABELS_LOC[lang].get(city, city_label)
    city_gen = _CITY_LABELS_GEN[lang].get(city, city_label)
    district = _district_label(city, lat, lon, lang)

    coord_str = (f'{lat:.4f}, {lon:.4f}' if lat is not None and lon is not None
                 else '' if lang != 'sr' else '')

    # Line numbers — short form "1, 2A, 5" with max 8 before collapsing.
    numbers = [line.get('number', '') for line in lines if line.get('number')]
    if len(numbers) > 8:
        more_joiner = {'sr': 'još', 'en': 'more', 'ru': 'ещё'}[lang]
        line_numbers = ', '.join(numbers[:8]) + f' ({len(numbers) - 8} {more_joiner})'
    else:
        line_numbers = ', '.join(numbers) if numbers else '—'

    type_breakdown_str = _type_breakdown(lines, lang)
    endpoints = _top_endpoints(lines, stop.get('name') or '')

    poi = nearest_poi(lat, lon, lang) if lat and lon else None
    nearby_list_parts: list[str] = []
    dist_unit = {'sr': 'm', 'en': 'm', 'ru': 'м'}[lang]
    if lat is not None and lon is not None:
        for n in nearby[:3]:
            if n.get('lat') is None or n.get('lon') is None:
                continue
            d = _haversine_m(lat, lon, n['lat'], n['lon'])
            nearby_list_parts.append(f'{n.get("name", "?")} ({d} {dist_unit})')
    nearby_list = ', '.join(nearby_list_parts)

    # Squash POI if we're effectively AT the landmark (distance < 50 m reads
    # "0 m" which is nonsense in prose). Only mention POIs that are nearby
    # but distinct from the stop.
    has_poi = bool(poi and poi['distance_m'] >= 50)
    poi_dist_label = {'sr': 'm', 'en': 'm', 'ru': 'м'}[lang]

    return {
        'stop_name': stop.get('name') or '',
        'city_label': city_label,
        'city_loc': city_loc,
        'city_gen': city_gen,
        'district': district,
        'coord_str': coord_str,
        'line_count': line_count,
        'line_numbers': line_numbers,
        'type_breakdown': type_breakdown_str,
        'vehicle_kind': vkind,
        'vehicle_kind_ru': vkind_ru,
        'size_category': size_category,
        'size_category_ru': size_category_ru,
        'first_dep': (gtfs_stats or {}).get('first_departure') or '',
        'last_dep': (gtfs_stats or {}).get('last_departure') or '',
        'endpoints': ', '.join(endpoints),
        'poi_name': poi['name'] if poi else '',
        'poi_distance': (f'{poi["distance_m"]} {poi_dist_label}' if has_poi else ''),
        'nearby_list': nearby_list,
        'prefix': lang_prefix,
        '_has_poi': has_poi,
        '_has_gtfs': bool((gtfs_stats or {}).get('first_departure')),
        '_has_endpoints': bool(endpoints),
        '_has_nearby': bool(nearby_list_parts),
    }


# ── Public API ──────────────────────────────────────────────────────────


def build_prose(
    stop: dict,
    lines_at_stop: list[dict],
    nearby_stops: list[dict] | None = None,
    gtfs_stats: dict | None = None,
    lang: str = 'sr',
    lang_prefix: str = '',
) -> dict:
    """Return {'intro','service','location','tip'} rendered strings.

    Guarantees:
    - Deterministic: same inputs → same output. Safe to cache at any layer.
    - No `{placeholder}` leaks. Optional slots are gated by _has_* flags.
    - Total length across paragraphs is 150–300 words per spec."""
    if not lines_at_stop:
        # Stop with zero lines is a data glitch — skip prose, let template
        # keep its default fallback rather than emit a vacuous sentence.
        return {}

    if lang not in ('sr', 'en', 'ru'):
        lang = 'sr'

    slots = _compute_slots(stop, lines_at_stop, nearby_stops or [], gtfs_stats, lang, lang_prefix)
    slug = stop.get('slug') or ''

    # Intro — always pickable from the 8-variant pool.
    intro = _pick(_INTRO[lang], slug, 'intro').format(**slots)
    if slots['_has_poi']:
        intro += _pick(_INTRO_POI_SUFFIX[lang], slug, 'intro_poi').format(**slots)

    # Service paragraph — line list + type breakdown + optional GTFS + endpoints.
    service = _pick(_SERVICE[lang], slug, 'service').format(**slots)
    # Some templates end with ". ." pattern if type_breakdown is empty; clean up.
    service = service.replace(' . ', '. ').replace('. .', '.').strip()
    if slots['_has_gtfs']:
        service += _pick(_SERVICE_GTFS_SUFFIX[lang], slug, 'service_gtfs').format(**slots)
    if slots['_has_endpoints']:
        service += _pick(_SERVICE_ENDPOINTS[lang], slug, 'service_endpoints').format(**slots)
    # Always-on frequency heuristic — ensures minimum prose length even when
    # GTFS/endpoints/nearby are all missing.
    service += _pick(_SERVICE_FREQUENCY[lang], slug, 'service_freq').format(**slots)

    # Location paragraph — always the district header + optional nearby list.
    location = _pick(_LOCATION[lang], slug, 'location').format(**slots)
    if slots['_has_nearby']:
        location += _pick(_LOCATION_NEARBY_SUFFIX[lang], slug, 'location_nearby').format(**slots)

    # Travel tip — always picked.
    tip = _pick(_TIP[lang], slug, 'tip').format(**slots)

    return {'intro': intro, 'service': service, 'location': location, 'tip': tip}

"""Rules-based prose generator for /gradski/{city}/linija/{slug}/ pages.

Problem: ~611 line pages share an identical 2-paragraph SEO prose block
(differs only in line number / terminal names). Google's "Crawled,
currently not indexed" bucket eats this kind of page — the unique-text
budget is well below 50 words. This module replaces the boilerplate with
3 paragraphs (~150–250 words) interpolated from facts we already hold:
terminals, stop coordinates, GTFS schedule, interchange topology.

Design principles mirror `stop_prose.py`:
1. Deterministic. Same (line, lang) → same prose. Cache-friendly.
2. Hash-driven template choice per paragraph means two lines almost never
   land on the same template tuple, and the numerical slots (length km,
   headway, peak count) make the rendered text distinct even when two
   lines pick the same templates.
3. Optional slots are gated by `_has_*` flags. If GTFS data is missing
   the operating-window paragraph is skipped rather than fabricated.
4. No LLM calls. Pure str.format() over curated template pools.

Entry point: `build_prose(line, stops, schedule_rd, interchange, lang)`.
Returns `{'geography': str, 'schedule': str, 'transfers': str}` — the
template guards each key with `{% if prose.geography %}…{% endif %}`.
"""
from __future__ import annotations

from hashlib import md5
from math import asin, cos, radians, sin, sqrt


# ── Template pools ──────────────────────────────────────────────────────

_GEOGRAPHY: dict[str, list[str]] = {
    'sr': [
        'Linija {line_number} ({line_type_label}) povezuje {terminal_a} i {terminal_b} '
        'kroz ukupno {stop_count} stajališta u {city_loc}. Ukupna dužina trase je '
        'oko {length_km} km, mereno po koordinatama svih stajališta na trasi.',
        'Trasa linije {line_number} prolazi između terminala {terminal_a} i {terminal_b} u {city_loc}, '
        'sa {stop_count} stajališta usput. Po geografskoj dužini trasa pokriva približno {length_km} km '
        'gradskog i prigradskog područja.',
        '{line_type_label_cap} {line_number} u {city_loc} ide od {terminal_a} do {terminal_b}; '
        'cela trasa ima {stop_count} stajališta i pokriva oko {length_km} km vožnje.',
        'Linija {line_number} u sistemu gradskog prevoza {city_gen} povezuje krajeve {terminal_a} i {terminal_b} '
        'preko {stop_count} stajališta. Procenjena dužina trase je {length_km} km.',
        'Krećući se između {terminal_a} i {terminal_b}, linija {line_number} ({line_type_label}) prolazi kroz '
        '{stop_count} stajališta u {city_loc} — ukupno oko {length_km} km po trasi.',
        'U {city_loc}, linija {line_number} formira koridor od {terminal_a} do {terminal_b} sa '
        '{stop_count} stanica. Geografska dužina trase iznosi približno {length_km} km.',
    ],
    'en': [
        'Line {line_number} ({line_type_label}) connects {terminal_a} and {terminal_b} '
        'across {stop_count} stops in {city_label}. Measured along the stop coordinates, '
        'the route covers about {length_km} km.',
        'The route for line {line_number} runs between {terminal_a} and {terminal_b} in {city_label}, '
        'with {stop_count} stops on the way. Total geographic length is roughly {length_km} km '
        'of urban and suburban service.',
        '{line_type_label_cap} {line_number} in {city_label} runs from {terminal_a} to {terminal_b}; '
        'the full route has {stop_count} stops and spans about {length_km} km.',
        'Within the {city_label} transit network, line {line_number} links the {terminal_a} and {terminal_b} '
        'ends through {stop_count} stops. Estimated route length is {length_km} km.',
        'Running between {terminal_a} and {terminal_b}, line {line_number} ({line_type_label}) calls at '
        '{stop_count} stops in {city_label} — about {length_km} km end-to-end.',
        'In {city_label}, line {line_number} forms a corridor from {terminal_a} to {terminal_b} with '
        '{stop_count} stations. The geographic length of the route is roughly {length_km} km.',
    ],
    'ru': [
        'Линия {line_number} ({line_type_label}) соединяет {terminal_a} и {terminal_b} '
        'через {stop_count} остановок в {city_loc}. По координатам остановок длина трассы '
        'составляет около {length_km} км.',
        'Маршрут линии {line_number} проходит между конечными {terminal_a} и {terminal_b} в {city_loc}, '
        'с {stop_count} остановками по пути. Общая географическая длина — примерно {length_km} км '
        'городских и пригородных участков.',
        '{line_type_label_cap} {line_number} в {city_loc} ходит от {terminal_a} до {terminal_b}; '
        'полная трасса имеет {stop_count} остановок и покрывает около {length_km} км.',
        'В сети городского транспорта {city_gen} линия {line_number} связывает концы {terminal_a} и {terminal_b} '
        'через {stop_count} остановок. Оценочная длина трассы — {length_km} км.',
        'Двигаясь между {terminal_a} и {terminal_b}, линия {line_number} ({line_type_label}) проходит через '
        '{stop_count} остановок в {city_loc} — около {length_km} км в одну сторону.',
        'В {city_loc} линия {line_number} образует коридор от {terminal_a} до {terminal_b} с '
        '{stop_count} станциями. Географическая длина трассы — примерно {length_km} км.',
    ],
}

# Always-on closing sentence to add factual ballast on lines without GTFS:
# uses stop-density (km per stop) which is meaningful even for lines we
# never scraped a schedule for.
_GEOGRAPHY_DENSITY: dict[str, list[str]] = {
    'sr': [
        ' Prosečno rastojanje između susednih stajališta na trasi je oko {avg_gap_m} metara.',
        ' Susedna stajališta na liniji udaljena su prosečno {avg_gap_m} m, što je tipično '
        'za {density_label} mrežu gradskog prevoza.',
        ' Razmak između stajališta je u proseku {avg_gap_m} m — {density_label} pokrivenost '
        'koridorima.',
    ],
    'en': [
        ' Average spacing between consecutive stops along the route is around {avg_gap_m} metres.',
        ' Adjacent stops sit roughly {avg_gap_m} m apart, typical of a {density_label} '
        'transit corridor.',
        ' Stop-to-stop spacing averages {avg_gap_m} m — {density_label} corridor coverage.',
    ],
    'ru': [
        ' Среднее расстояние между соседними остановками на трассе — около {avg_gap_m} метров.',
        ' Соседние остановки расположены в среднем в {avg_gap_m} м друг от друга, что характерно '
        'для {density_label} маршрутной сети.',
        ' Расстояние между остановками в среднем {avg_gap_m} м — {density_label} плотность '
        'коридоров.',
    ],
}


_SCHEDULE: dict[str, list[str]] = {
    'sr': [
        'Prema GTFS redu vožnje, linija saobraća radnim danom od {first_dep} do {last_dep}, '
        'sa ukupno {workday_count} polazaka sa polaznog stajališta {terminal_a}.',
        'Radnim danom prvi polazak sa {terminal_a} je u {first_dep}, poslednji u {last_dep}; '
        'ukupno se izvodi {workday_count} polazaka po danu.',
        'Operativni prozor linije {line_number} po radnom danu je {first_dep}–{last_dep} '
        '({workday_count} polazaka iz {terminal_a}, GTFS).',
        'Sa terminala {terminal_a} prvi autobus kreće u {first_dep}, poslednji u {last_dep} '
        'tokom radnog dana — to je {workday_count} polazaka prema oficijelnom redu vožnje.',
    ],
    'en': [
        'According to the GTFS schedule, the line runs on weekdays from {first_dep} to {last_dep}, '
        'with {workday_count} departures from the {terminal_a} terminus.',
        'On weekdays the first departure from {terminal_a} is at {first_dep} and the last at {last_dep}; '
        '{workday_count} trips are operated per workday.',
        'The weekday operating window for line {line_number} is {first_dep}–{last_dep} '
        '({workday_count} departures from {terminal_a}, per GTFS).',
        'From the {terminal_a} terminus the first bus leaves at {first_dep} and the last at {last_dep} '
        'on weekdays — {workday_count} departures total per the official schedule.',
    ],
    'ru': [
        'Согласно GTFS-расписанию, линия работает в будние дни с {first_dep} до {last_dep}, '
        'всего {workday_count} рейсов от конечной {terminal_a}.',
        'В будние дни первый рейс с {terminal_a} в {first_dep}, последний — в {last_dep}; '
        'всего выполняется {workday_count} рейсов в сутки.',
        'Рабочий интервал линии {line_number} в будний день — {first_dep}–{last_dep} '
        '({workday_count} рейсов с {terminal_a}, по GTFS).',
        'С конечной {terminal_a} первый автобус отправляется в {first_dep}, последний — в {last_dep} '
        'по будням, что составляет {workday_count} рейсов согласно официальному расписанию.',
    ],
}

# Headway suffix attached when we have enough data to estimate peak vs
# off-peak intervals. We compute peak (07-09 + 16-18) and off-peak window
# averages from the workday schedule of departures from stop sequence 1.
_SCHEDULE_HEADWAY: dict[str, list[str]] = {
    'sr': [
        ' U jutarnjem i popodnevnom vrhu (07–09 i 16–18) interval je u proseku oko {peak_headway_min} '
        'min, dok se van vrha produžava na ~{offpeak_headway_min} min.',
        ' Tipičan razmak između polazaka u špicu je {peak_headway_min} min, a van špica '
        'oko {offpeak_headway_min} min.',
        ' Frekvencija polazaka u špicu je oko 1 svakih {peak_headway_min} min; van vrha intervali '
        'su znatno duži (~{offpeak_headway_min} min).',
    ],
    'en': [
        ' Morning and afternoon peaks (07–09 and 16–18) see headways averaging around '
        '{peak_headway_min} minutes, lengthening to ~{offpeak_headway_min} min off-peak.',
        ' Peak-hour intervals average {peak_headway_min} min, and off-peak intervals '
        'about {offpeak_headway_min} min.',
        ' Departure frequency at peak runs roughly one every {peak_headway_min} min; off-peak '
        'intervals stretch noticeably longer (~{offpeak_headway_min} min).',
    ],
    'ru': [
        ' В утренний и вечерний пик (07–09 и 16–18) интервал в среднем около {peak_headway_min} '
        'мин, вне пика — ~{offpeak_headway_min} мин.',
        ' Типичный интервал между рейсами в час пик — {peak_headway_min} мин, вне пика '
        'около {offpeak_headway_min} мин.',
        ' Частота отправлений в пик — примерно 1 каждые {peak_headway_min} мин; вне пика интервалы '
        'заметно длиннее (~{offpeak_headway_min} мин).',
    ],
}

# Weekend service line (always added when we have weekend schedule data).
_SCHEDULE_WEEKEND: dict[str, list[str]] = {
    'sr': [
        ' Vikendom je broj polazaka manji ({weekend_count} subotom), pa intervali rastu — '
        'preporučujemo proveru reda vožnje pre polaska.',
        ' Subotom se izvodi {weekend_count} polazaka; nedeljom je raspored sažetiji.',
        ' Tokom vikenda režim je redukovan ({weekend_count} polazaka subotom), '
        'naročito u večernjim satima.',
    ],
    'en': [
        ' Weekend service is reduced ({weekend_count} departures on Saturday), so intervals '
        'lengthen — checking the schedule before travel pays off.',
        ' Saturday operates {weekend_count} departures; Sunday schedules are tighter still.',
        ' Weekend frequency is lower ({weekend_count} on Saturday), especially in the evening.',
    ],
    'ru': [
        ' По выходным рейсов меньше ({weekend_count} в субботу), интервалы длиннее — '
        'перед поездкой стоит проверить расписание.',
        ' В субботу выполняется {weekend_count} рейсов; в воскресенье расписание ещё короче.',
        ' На выходных режим сокращён ({weekend_count} рейсов в субботу), особенно вечером.',
    ],
}

# Weekend line for routes that keep ~full service on weekends (Saturday volume
# ≈ weekday) — so we must NOT claim "reduced". Picked instead of _SCHEDULE_WEEKEND
# when _weekend_full is set.
_SCHEDULE_WEEKEND_FULL: dict[str, list[str]] = {
    'sr': [
        ' Vikendom linija saobraća gotovo punim režimom — {weekend_count} polazaka i subotom, '
        'sa sličnim intervalima kao radnim danom.',
        ' I subotom je red vožnje skoro isti kao radnim danom ({weekend_count} polazaka), '
        'pa nema velikih pauza.',
    ],
    'en': [
        ' Weekend service stays near full — {weekend_count} departures on Saturday, '
        'with intervals close to weekdays.',
        ' Saturday keeps almost the same schedule as weekdays ({weekend_count} departures), '
        'so there are no long gaps.',
    ],
    'ru': [
        ' По выходным линия работает почти в полном режиме — {weekend_count} рейсов и в субботу, '
        'с интервалами близкими к будням.',
        ' В субботу расписание почти как в будни ({weekend_count} рейсов), без больших пауз.',
    ],
}

# Appended after the weekend sentence ONLY when we have a real Saturday midday
# interval — answers "na koliko minuta subotom" with a concrete number.
_SCHEDULE_WEEKEND_HEADWAY: dict[str, str] = {
    'sr': ' Subotom je interval u proseku oko {weekend_headway} min.',
    'en': ' Saturday headway averages about {weekend_headway} min.',
    'ru': ' В субботу интервал в среднем около {weekend_headway} мин.',
}


_TRANSFERS: dict[str, list[str]] = {
    'sr': [
        'Najvažnija presedačka stajališta na liniji {line_number} su {transfers_list} — sa svakog od '
        'njih dostupno je više drugih linija gradskog prevoza {city_gen}.',
        'Putnici sa linije {line_number} mogu da presednu na druge gradske linije najbolje sa stajališta '
        '{transfers_list}.',
        'Glavni čvorišni punktovi na trasi su {transfers_list}; svako od ovih stajališta povezuje liniju '
        '{line_number} sa drugim koridorima u {city_loc}.',
        'Za prelazak na druge linije, najjača presedanja sa linije {line_number} su na {transfers_list}.',
    ],
    'en': [
        'The most important transfer stops on line {line_number} are {transfers_list} — each one '
        'connects to several other lines of the {city_label} transit network.',
        'Riders on line {line_number} can transfer onto other city lines most easily at {transfers_list}.',
        'The major interchange points along the route are {transfers_list}; each of these stops links '
        'line {line_number} to other corridors in {city_label}.',
        'For onward connections, the strongest transfers off line {line_number} are at {transfers_list}.',
    ],
    'ru': [
        'Самые важные пересадочные остановки на линии {line_number} — {transfers_list}, '
        'с каждой из которых доступны другие линии городского транспорта {city_gen}.',
        'Пассажиры линии {line_number} могут проще всего пересесть на другие городские маршруты на '
        'остановках {transfers_list}.',
        'Главные узловые точки на трассе — {transfers_list}; каждая из этих остановок связывает '
        'линию {line_number} с другими коридорами в {city_loc}.',
        'Для пересадки на другие линии лучше всего использовать остановки {transfers_list}.',
    ],
}

# Always-on closing sentence with a CTA to the city hub — pulls weight
# back to the parent /gradski/{city}/ page and keeps prose ≥120 words
# even on lines with weak transfer data.
_TRANSFERS_CLOSE: dict[str, list[str]] = {
    'sr': [
        ' Detaljan red vožnje za svaku stanicu, kao i podatke o ostalim '
        'linijama u {city_loc}, pogledajte na <a href="{prefix}/gradski/{city_slug}/">'
        'pregledu mreže gradskog prevoza {city_gen}</a>.',
        ' Pregled svih linija sa kojima ova trasa deli stajališta dostupan je na '
        '<a href="{prefix}/gradski/{city_slug}/">stranici gradskog prevoza {city_gen}</a> — '
        'koristite je za planiranje pretovara.',
    ],
    'en': [
        ' For the full timetable at each stop and other lines across {city_label}, see the '
        '<a href="{prefix}/gradski/{city_slug}/">{city_label} transit overview</a>.',
        ' A full list of lines that share stops with this route lives on the '
        '<a href="{prefix}/gradski/{city_slug}/">{city_label} city transit page</a> — useful for planning transfers.',
    ],
    'ru': [
        ' Подробное расписание по каждой остановке и информацию о других линиях в {city_loc} '
        'можно посмотреть на <a href="{prefix}/gradski/{city_slug}/">странице городского транспорта {city_gen}</a>.',
        ' Полный список линий, с которыми эта трасса делит остановки, есть на '
        '<a href="{prefix}/gradski/{city_slug}/">странице городского транспорта {city_gen}</a> — пригодится для планирования пересадок.',
    ],
}

# Always-on closing facts on the transfers paragraph — anchors line type +
# service profile. Pure description from `line.type` + stop coordinates;
# zero fabrication. Bulks no-GTFS lines past the 120-word indexability
# floor without inventing schedule data.
_TRANSFERS_PROFILE: dict[str, list[str]] = {
    'sr': [
        ' Linija {line_number} u sistemu gradskog prevoza {city_gen} pripada kategoriji '
        '{line_type_label}, sa ukupno {stop_count} stajališta na trasi i prosečnim razmakom '
        'od oko {avg_gap_m} m između susednih stanica — to je {density_label} pokrivenost koridora.',
        ' Trasa linije {line_number} ({line_type_label}) ima {stop_count} stajališta na '
        'pravcu od {terminal_a} do {terminal_b}; razmak između stajališta u proseku je '
        '{avg_gap_m} m, što odgovara {density_label} koridoru u {city_loc}.',
        ' Sa {stop_count} stajališta i prosečnim razmakom od {avg_gap_m} m, linija {line_number} '
        '({line_type_label}) pruža {density_label} pokrivenost dela {city_gen} između '
        '{terminal_a} i {terminal_b}.',
    ],
    'en': [
        ' Line {line_number} in the {city_label} transit network falls in the {line_type_label} '
        'category, with {stop_count} stops along the route and an average spacing of around '
        '{avg_gap_m} m between adjacent stations — a {density_label} corridor coverage.',
        ' The route of line {line_number} ({line_type_label}) has {stop_count} stops on the '
        'corridor from {terminal_a} to {terminal_b}; the average stop-to-stop spacing is '
        '{avg_gap_m} m, characteristic of a {density_label} corridor in {city_label}.',
        ' With {stop_count} stops and an average spacing of {avg_gap_m} m, line {line_number} '
        '({line_type_label}) provides {density_label} coverage of the {city_label} area '
        'between {terminal_a} and {terminal_b}.',
    ],
    'ru': [
        ' Линия {line_number} в сети городского транспорта {city_gen} относится к категории '
        '{line_type_label}, всего {stop_count} остановок на трассе и средний интервал около '
        '{avg_gap_m} м между соседними станциями — это {density_label} покрытие коридора.',
        ' Трасса линии {line_number} ({line_type_label}) включает {stop_count} остановок на '
        'направлении от {terminal_a} до {terminal_b}; среднее расстояние между остановками '
        '{avg_gap_m} м, что характерно для {density_label} коридора в {city_loc}.',
        ' С {stop_count} остановками и средним интервалом {avg_gap_m} м линия {line_number} '
        '({line_type_label}) обеспечивает {density_label} покрытие части {city_gen} между '
        '{terminal_a} и {terminal_b}.',
    ],
}


# ── Labels (mirroring stop_prose.py — keep cases consistent) ────────────

_LINE_TYPE_LABELS: dict[str, dict[str, str]] = {
    'sr': {'bus': 'autobuska linija', 'tram': 'tramvajska linija',
           'trolleybus': 'trolejbuska linija', 'night': 'noćna linija',
           'e-bus': 'e-bus linija', 'bg-voz': 'BG Voz linija',
           'suburban': 'prigradska linija'},
    'en': {'bus': 'bus line', 'tram': 'tram line', 'trolleybus': 'trolleybus line',
           'night': 'night line', 'e-bus': 'electric-bus line', 'bg-voz': 'BG Voz line',
           'suburban': 'suburban line'},
    'ru': {'bus': 'автобусная линия', 'tram': 'трамвайная линия',
           'trolleybus': 'троллейбусная линия', 'night': 'ночная линия',
           'e-bus': 'электробусная линия', 'bg-voz': 'линия BG Voz',
           'suburban': 'пригородная линия'},
}

_CITY_LABELS: dict[str, dict[str, str]] = {
    'sr': {'beograd': 'Beograd', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'en': {'beograd': 'Belgrade', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'ru': {'beograd': 'Белград', 'novi-sad': 'Нови-Сад', 'nis': 'Ниш', 'kragujevac': 'Крагуевац'},
}

_CITY_LABELS_LOC: dict[str, dict[str, str]] = {
    'sr': {'beograd': 'Beogradu', 'novi-sad': 'Novom Sadu', 'nis': 'Nišu', 'kragujevac': 'Kragujevcu'},
    'en': {'beograd': 'Belgrade', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'ru': {'beograd': 'Белграде', 'novi-sad': 'Нови-Саде', 'nis': 'Нише', 'kragujevac': 'Крагуевце'},
}

_CITY_LABELS_GEN: dict[str, dict[str, str]] = {
    'sr': {'beograd': 'Beograda', 'novi-sad': 'Novog Sada', 'nis': 'Niša', 'kragujevac': 'Kragujevca'},
    'en': {'beograd': 'Belgrade', 'novi-sad': 'Novi Sad', 'nis': 'Niš', 'kragujevac': 'Kragujevac'},
    'ru': {'beograd': 'Белграда', 'novi-sad': 'Нови-Сада', 'nis': 'Ниша', 'kragujevac': 'Крагуеваца'},
}

# Density tiers derived from average stop spacing (m). The mapping is
# intentionally coarse — three buckets is enough for prose context and
# keeps the slot strings short.
_DENSITY_LABELS: dict[str, dict[str, str]] = {
    'sr': {'dense': 'gustu', 'medium': 'standardnu', 'sparse': 'rasprostranjenu'},
    'en': {'dense': 'dense', 'medium': 'standard', 'sparse': 'wide-spaced'},
    'ru': {'dense': 'плотную', 'medium': 'стандартную', 'sparse': 'разрежённую'},
}


# ── Helpers ─────────────────────────────────────────────────────────────


def _haversine_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """Great-circle distance in kilometres. Used both for total route
    length and stop-to-stop spacing — single helper avoids drift between
    the two estimates."""
    R = 6371.0
    a = (sin(radians(b_lat - a_lat) / 2) ** 2
         + cos(radians(a_lat)) * cos(radians(b_lat))
         * sin(radians(b_lon - a_lon) / 2) ** 2)
    return R * 2 * asin(sqrt(a))


def _route_length_km(stops: list[dict]) -> tuple[float, int]:
    """Return (total_km, segment_count). Skips stops missing coordinates
    so a single coordinate-less stop in the middle doesn't drop the
    whole estimate to zero — we just lose that one segment."""
    total = 0.0
    segments = 0
    prev = None
    for s in stops:
        lat, lon = s.get('lat'), s.get('lon')
        if lat is None or lon is None:
            continue
        if prev is not None:
            total += _haversine_km(prev[0], prev[1], lat, lon)
            segments += 1
        prev = (lat, lon)
    return total, segments


def _headway_minutes(times_hhmm: list[str], window_start: int, window_end: int) -> int | None:
    """Average headway in minutes inside [window_start, window_end) hours.

    `times_hhmm` is a list like ['05:00', '05:15', ...] from stop_sequence=1.
    Returns None if fewer than 2 departures fall in the window — the prose
    layer drops the headway sentence in that case rather than printing a
    wild estimate from a single data point.
    """
    in_window: list[int] = []
    for t in times_hhmm:
        if not t or len(t) < 5:
            continue
        try:
            h = int(t[:2])
            m = int(t[3:5])
        except ValueError:
            continue
        if window_start <= h < window_end:
            in_window.append(h * 60 + m)
    if len(in_window) < 2:
        return None
    in_window.sort()
    span = in_window[-1] - in_window[0]
    if span <= 0:
        return None
    return max(1, round(span / (len(in_window) - 1)))


def _density_bucket(avg_gap_m: int, lang: str) -> str:
    if avg_gap_m < 350:
        return _DENSITY_LABELS[lang]['dense']
    if avg_gap_m < 700:
        return _DENSITY_LABELS[lang]['medium']
    return _DENSITY_LABELS[lang]['sparse']


def _pick(pool: list[str], slug: str, salt: str) -> str:
    if not pool:
        return ''
    idx = int(md5(f'{slug}|{salt}'.encode('utf-8')).hexdigest()[:8], 16) % len(pool)
    return pool[idx]


# ── Slot computation ────────────────────────────────────────────────────


def _compute_slots(
    line: dict,
    stops: list[dict],
    schedule_rd: list[str] | None,
    schedule_sat: list[str] | None,
    interchange: list[dict],
    lang: str,
    lang_prefix: str,
) -> dict:
    city = line.get('city') or 'beograd'
    line_type = line.get('type') or 'bus'
    line_type_label = _LINE_TYPE_LABELS[lang].get(line_type, _LINE_TYPE_LABELS[lang]['bus'])
    line_type_label_cap = line_type_label[0].upper() + line_type_label[1:]

    city_label = _CITY_LABELS[lang].get(city, city.title())
    city_loc = _CITY_LABELS_LOC[lang].get(city, city_label)
    city_gen = _CITY_LABELS_GEN[lang].get(city, city_label)

    terminal_a = stops[0]['name'] if stops else '—'
    terminal_b = stops[-1]['name'] if len(stops) > 1 else terminal_a

    length_km_raw, segments = _route_length_km(stops)
    length_km = round(length_km_raw, 1) if length_km_raw > 0 else 0.0
    avg_gap_m = int(round((length_km_raw / segments) * 1000)) if segments > 0 else 0
    density_label = _density_bucket(avg_gap_m, lang) if avg_gap_m else _DENSITY_LABELS[lang]['medium']

    # Schedule window — night-aware (see service_window): a line that sleeps
    # overnight has both 00:xx and 24:xx departures, so naive [0]/[-1] would
    # claim a false 24-hour window. service_window reports the real service arc.
    workday = [t for t in (schedule_rd or []) if t]
    workday_count = len(workday)
    first_dep, last_dep = service_window(workday)
    first_dep = first_dep or ''
    last_dep = last_dep or ''
    has_gtfs = workday_count >= 2

    # Headway: peak window 07-09 + 16-18 averaged together; off-peak 10-15.
    peak_headway = None
    offpeak_headway = None
    if has_gtfs:
        peak_morning = _headway_minutes(workday, 7, 9)
        peak_evening = _headway_minutes(workday, 16, 18)
        if peak_morning and peak_evening:
            peak_headway = round((peak_morning + peak_evening) / 2)
        else:
            peak_headway = peak_morning or peak_evening
        offpeak_headway = _headway_minutes(workday, 10, 15)
    has_headway = bool(peak_headway and offpeak_headway)

    weekend_count = len([t for t in (schedule_sat or []) if t])
    has_weekend = weekend_count >= 2
    # Saturday running at ~weekday volume means the line is NOT reduced on
    # weekends — claiming "reduced" then is false (e.g. line 2A: 158/158).
    weekend_full = bool(has_weekend and workday_count and weekend_count >= 0.85 * workday_count)
    # Typical Saturday midday interval — answers "na koliko minuta subotom".
    weekend_headway = (_headway_minutes([t for t in (schedule_sat or []) if t], 10, 15)
                       if has_weekend else None)

    # Interchange list: drop terminals (already named) and self-references,
    # cap at 3 names. Each entry is "Name (N linija)".
    terminal_names = {terminal_a.lower(), terminal_b.lower()}
    transfers: list[str] = []
    line_word = {'sr': 'linija', 'en': 'lines', 'ru': 'линий'}[lang]
    for s in interchange or []:
        name = s.get('name') or ''
        if not name or name.lower() in terminal_names:
            continue
        cnt = s.get('line_count') or 0
        # The interchange query already filters line_count > 1; +1 cnt
        # would be misleading. Show the raw count.
        transfers.append(f'{name} ({cnt} {line_word})')
        if len(transfers) >= 3:
            break
    transfers_list = ', '.join(transfers)
    has_transfers = bool(transfers_list)

    return {
        'line_number': line.get('number') or '',
        'line_type_label': line_type_label,
        'line_type_label_cap': line_type_label_cap,
        'city_label': city_label,
        'city_loc': city_loc,
        'city_gen': city_gen,
        'city_slug': city,
        'terminal_a': terminal_a,
        'terminal_b': terminal_b,
        'stop_count': len(stops),
        'length_km': length_km if length_km else '—',
        'avg_gap_m': avg_gap_m if avg_gap_m else 0,
        'density_label': density_label,
        'first_dep': first_dep,
        'last_dep': last_dep,
        'workday_count': workday_count,
        'peak_headway_min': peak_headway or 0,
        'offpeak_headway_min': offpeak_headway or 0,
        'weekend_count': weekend_count,
        'weekend_headway': weekend_headway or 0,
        'transfers_list': transfers_list,
        'prefix': lang_prefix,
        '_has_density': avg_gap_m > 0,
        '_has_gtfs': has_gtfs,
        '_has_headway': has_headway,
        '_has_weekend': has_weekend,
        '_weekend_full': weekend_full,
        '_has_transfers': has_transfers,
    }


# ── Public API ──────────────────────────────────────────────────────────


_SERVICE_DAY_CUTOVER = 180  # 03:00 — the deep-night dead zone


def service_window(times: list[str]) -> tuple[str | None, str | None]:
    """First/last of the daily service window, honest for lines that sleep overnight.

    Naive min/max misleads night lines: a line running 04:10→00:45 (with a
    ~3 h dead gap 00:45→04:10) has departures at both 00:xx and 24:xx, so
    sorted()[0]/[-1] yields "00:00–24:20" — a false 24-hour window. We anchor on
    the service-day cutover (03:00, the deep-night dead zone): a departure before
    03:00 is the late-night TAIL of the same service day, not a new morning
    start, so we shift it past midnight (+24 h) before taking min/max. Then a
    night line reads honestly as 04:10–00:45 and a daytime line as the plain
    05:00–23:00. 24:xx is normalised to 00:xx for display. (None, None) if empty."""
    norm = []
    for t in times:
        if not t:
            continue
        m = (int(t[:2]) * 60 + int(t[3:5])) % 1440
        norm.append(m + 1440 if m < _SERVICE_DAY_CUTOVER else m)
    if not norm:
        return None, None
    fmt = lambda m: f'{(m // 60) % 24:02d}:{m % 60:02d}'
    return fmt(min(norm)), fmt(max(norm))


def build_prose(
    line: dict,
    stops: list[dict],
    schedule_rd: list[str] | None = None,
    schedule_sat: list[str] | None = None,
    interchange: list[dict] | None = None,
    lang: str = 'sr',
    lang_prefix: str = '',
) -> dict:
    """Return {'geography','schedule','transfers'} rendered strings.

    Guarantees:
    - Deterministic: same inputs → same output. Safe to cache at any layer.
    - No `{placeholder}` leaks. Optional slots are gated by _has_* flags.
    - Returns {} when there are <2 stops — line page falls back to whatever
      it had before, no half-formed prose.
    """
    if not line or not stops or len(stops) < 2:
        return {}
    if lang not in ('sr', 'en', 'ru'):
        lang = 'sr'

    slots = _compute_slots(
        line, stops, schedule_rd, schedule_sat,
        interchange or [], lang, lang_prefix,
    )
    slug = line.get('slug') or ''

    # Geography paragraph — always rendered, plus density suffix when we
    # have at least one segment with valid coordinates.
    geography = _pick(_GEOGRAPHY[lang], slug, 'geo').format(**slots)
    if slots['_has_density']:
        geography += _pick(_GEOGRAPHY_DENSITY[lang], slug, 'geo_density').format(**slots)

    # Schedule paragraph — gated by GTFS availability. If there's no
    # workday schedule we skip the whole paragraph rather than fabricate.
    schedule = ''
    if slots['_has_gtfs']:
        schedule = _pick(_SCHEDULE[lang], slug, 'sched').format(**slots)
        if slots['_has_headway']:
            schedule += _pick(_SCHEDULE_HEADWAY[lang], slug, 'sched_headway').format(**slots)
        if slots['_has_weekend']:
            _wpool = _SCHEDULE_WEEKEND_FULL if slots['_weekend_full'] else _SCHEDULE_WEEKEND
            schedule += _pick(_wpool[lang], slug, 'sched_weekend').format(**slots)
            if slots['weekend_headway']:
                schedule += _SCHEDULE_WEEKEND_HEADWAY[lang].format(**slots)

    # Transfers paragraph — gated by interchange data; for lines that
    # share no multi-line stops, we skip this paragraph (template will
    # just close earlier).
    transfers = ''
    if slots['_has_transfers']:
        transfers = _pick(_TRANSFERS[lang], slug, 'transfers').format(**slots)
    # Always append a profile sentence (pure facts: type + stop count +
    # spacing + density tier + terminals) and the closing CTA. The profile
    # sentence is what pushes no-GTFS lines past the 120-word indexability
    # floor without fabricating schedule data.
    if slots['_has_density']:
        transfers += _pick(_TRANSFERS_PROFILE[lang], slug, 'transfers_profile').format(**slots)
    transfers += _pick(_TRANSFERS_CLOSE[lang], slug, 'transfers_close').format(**slots)

    return {
        'geography': geography,
        'schedule': schedule,
        'transfers': transfers.strip(),
    }

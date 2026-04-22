"""Static POI map — 20 Belgrade landmarks + handful for the other cities.

Lives in-module (not DB) because the list is small, stable, and we need
it for prose generation without a round-trip. When Overpass/OSM enrichment
lands the loader can swap to DB-backed.

Coords are WGS84 decimal degrees, taken from Wikipedia / OSM in 2026. The
`name` fields are keyed by language so the prose generator can drop the
right one directly into the output.
"""
from math import asin, cos, radians, sin, sqrt
from typing import Iterable

# Each entry: (lat, lon, {lang: display name}, optional_tag).
# Tag is used to pick a locative preposition ("kod" landmark vs "na" plaza).
_POIS: tuple[tuple[float, float, dict, str], ...] = (
    # Beograd — historic / commercial heart
    (44.8225, 20.4515, {'sr': 'Kalemegdan', 'en': 'Kalemegdan Fortress', 'ru': 'Калемегдан'}, 'landmark'),
    (44.8175, 20.4658, {'sr': 'Skadarlija', 'en': 'Skadarlija', 'ru': 'Скадарлия'}, 'district'),
    (44.8178, 20.4590, {'sr': 'Trg Republike', 'en': 'Republic Square', 'ru': 'площадь Республики'}, 'plaza'),
    (44.8150, 20.4603, {'sr': 'Terazije', 'en': 'Terazije', 'ru': 'Теразие'}, 'plaza'),
    (44.8180, 20.4566, {'sr': 'Knez Mihailova', 'en': 'Knez Mihailova Street', 'ru': 'улица Князя Михаила'}, 'landmark'),
    (44.8023, 20.4660, {'sr': 'Slavija', 'en': 'Slavija Square', 'ru': 'площадь Славия'}, 'plaza'),
    (44.7985, 20.4690, {'sr': 'Hram Svetog Save', 'en': 'Saint Sava Cathedral', 'ru': 'храм Святого Саввы'}, 'landmark'),
    (44.8120, 20.4621, {'sr': 'Beograđanka', 'en': 'Beogradjanka Tower', 'ru': 'Белградянка'}, 'landmark'),
    # Beograd — transport / events
    (44.8133, 20.4475, {'sr': 'BAS autobuska stanica', 'en': 'BAS Belgrade Bus Station', 'ru': 'автовокзал BAS'}, 'transport'),
    (44.8135, 20.4572, {'sr': 'Beograd Centar (Prokop)', 'en': 'Belgrade Centar (Prokop)', 'ru': 'вокзал Прокоп'}, 'transport'),
    (44.8091, 20.4164, {'sr': 'Štark Arena', 'en': 'Štark Arena', 'ru': 'Штарк Арена'}, 'landmark'),
    (44.7965, 20.4426, {'sr': 'Beogradski sajam', 'en': 'Belgrade Fair', 'ru': 'Белградская ярмарка'}, 'landmark'),
    (44.7858, 20.4028, {'sr': 'Ada Ciganlija', 'en': 'Ada Ciganlija', 'ru': 'Ада Циганлия'}, 'park'),
    (44.8037, 20.3937, {'sr': 'Delta City', 'en': 'Delta City', 'ru': 'Delta City'}, 'landmark'),
    # Beograd — municipalities
    (44.8469, 20.4036, {'sr': 'Zemun kej', 'en': 'Zemun Quay', 'ru': 'набережная Земуна'}, 'district'),
    (44.8230, 20.4700, {'sr': 'Dorćol', 'en': 'Dorćol', 'ru': 'Дорчол'}, 'district'),
    (44.7830, 20.4086, {'sr': 'Hipodrom Beograd', 'en': 'Belgrade Hippodrome', 'ru': 'Белградский ипподром'}, 'landmark'),
    (44.7854, 20.4844, {'sr': 'stadion Voždovac', 'en': 'Voždovac Stadium', 'ru': 'стадион Вождовац'}, 'landmark'),
    (44.7970, 20.4761, {'sr': 'Vračar', 'en': 'Vračar', 'ru': 'Врачар'}, 'district'),
    (44.8184, 20.3091, {'sr': 'aerodrom Nikola Tesla', 'en': 'Nikola Tesla Airport', 'ru': 'аэропорт Никола Тесла'}, 'transport'),
    # Novi Sad — a couple of anchors
    (45.2551, 19.8450, {'sr': 'Petrovaradinska tvrđava', 'en': 'Petrovaradin Fortress', 'ru': 'Петроварадинская крепость'}, 'landmark'),
    (45.2554, 19.8425, {'sr': 'Dunavski park', 'en': 'Danube Park', 'ru': 'Дунайский парк'}, 'park'),
    (45.2551, 19.8351, {'sr': 'Trg slobode', 'en': 'Liberty Square', 'ru': 'площадь Свободы'}, 'plaza'),
    # Niš
    (43.3209, 21.8958, {'sr': 'Niška tvrđava', 'en': 'Niš Fortress', 'ru': 'Нишская крепость'}, 'landmark'),
    (43.3124, 21.8920, {'sr': 'Čegar', 'en': 'Čegar Memorial', 'ru': 'Чегар'}, 'landmark'),
    # Kragujevac
    (44.0128, 20.9114, {'sr': 'Šumarice Memorial Park', 'en': 'Šumarice Memorial Park', 'ru': 'мемориал Шумарице'}, 'park'),
)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Great-circle distance in metres. Good to ~0.3% for distances <50 km."""
    r = 6371000.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return int(2 * r * asin(sqrt(a)))


def nearest_poi(lat: float, lon: float, lang: str = 'sr', max_m: int = 500) -> dict | None:
    """Return {'name', 'distance_m', 'tag'} for the closest POI within max_m,
    or None when nothing matches. lang falls back to sr if missing."""
    if lat is None or lon is None:
        return None
    best: tuple[int, dict, str] | None = None
    for plat, plon, names, tag in _POIS:
        d = _haversine_m(lat, lon, plat, plon)
        if d > max_m:
            continue
        if best is None or d < best[0]:
            best = (d, names, tag)
    if best is None:
        return None
    d, names, tag = best
    return {'name': names.get(lang) or names['sr'], 'distance_m': d, 'tag': tag}

"""City centroid coordinates for rendering the route-overview map on
/rute/<slug>/ (two pins + a line between the origin and destination city).

Duplicated from data/pipelines/build_db.py's CITY_COORDS (used there to
estimate distance_km via haversine) rather than imported from it — the
pipeline module is a standalone script, not meant to be imported by the
live web app at request time. Keep the two in sync if a city is added or
a centroid is corrected; neither is a live source of truth for the other.
"""

CITY_COORDS: dict[str, tuple[float, float]] = {
    'Ada': (45.80, 20.13), 'Apatin': (45.67, 18.98), 'Aranđelovac': (44.31, 20.56),
    'Atina': (37.98, 23.73), 'Banja Luka': (44.77, 17.19), 'Bar': (42.10, 19.10),
    'Bačka Palanka': (45.25, 19.39), 'Beograd': (44.79, 20.45), 'Bečej': (45.62, 20.04),
    'Bitolj': (41.03, 21.34), 'Bor': (44.07, 22.10), 'Budimpešta': (47.50, 19.04),
    'Budva': (42.29, 18.84), 'Drač': (41.32, 19.45), 'Dubrovnik': (42.65, 18.09),
    'Gornji Milanovac': (44.02, 20.46), 'Herceg Novi': (42.45, 18.54), 'Inđija': (45.05, 20.08),
    'Ivanjica': (43.58, 20.23), 'Jagodina': (43.98, 21.26), 'Kanjiža': (46.07, 20.05),
    'Kikinda': (45.83, 20.46), 'Kotor': (42.42, 18.77), 'Kragujevac': (44.01, 20.92),
    'Kraljevo': (43.72, 20.69), 'Kruševac': (43.58, 21.33), 'Lazarevac': (44.39, 20.26),
    'Leskovac': (42.99, 21.95), 'Ljubljana': (46.06, 14.51), 'Loznica': (44.53, 19.22),
    'Mladenovac': (44.43, 20.70), 'Mostar': (43.34, 17.81), 'Negotin': (44.23, 22.53),
    'Nikšić': (42.77, 18.94), 'Niš': (43.32, 21.90), 'Novi Pazar': (43.14, 20.51),
    'Novi Sad': (45.25, 19.84), 'Obrenovac': (44.65, 20.20), 'Ohrid': (41.12, 20.80),
    'Osijek': (45.55, 18.69), 'Pančevo': (44.87, 20.64), 'Pirot': (43.15, 22.59),
    'Podgorica': (42.44, 19.26), 'Požarevac': (44.62, 21.19), 'Priboj': (43.58, 19.53),
    'Pula': (44.87, 13.85), 'Rijeka': (45.33, 14.44), 'Ruma': (45.01, 19.82),
    'Sarajevo': (43.86, 18.41), 'Senta': (45.93, 20.09), 'Skoplje': (41.99, 21.43),
    'Smederevo': (44.66, 20.93), 'Smederevska Palanka': (44.37, 20.96), 'Sofija': (42.70, 23.32),
    'Solun': (40.64, 22.94), 'Sombor': (45.77, 19.11), 'Split': (43.51, 16.44),
    'Sremska Mitrovica': (44.98, 19.61), 'Stara Pazova': (44.99, 20.16), 'Subotica': (46.10, 19.67),
    'Temerin': (45.41, 19.89), 'Tetovo': (42.01, 20.97), 'Tirana': (41.33, 19.82),
    'Tivat': (42.43, 18.70), 'Trebinje': (42.71, 18.34), 'Tuzla': (44.54, 18.68),
    'Užice': (43.86, 19.84), 'Valjevo': (44.27, 19.89), 'Vranje': (42.55, 21.90),
    'Vrbas': (45.57, 19.64), 'Vrsac': (45.12, 21.30), 'Zadar': (44.12, 15.23),
    'Zagreb': (45.81, 15.98), 'Zaječar': (43.90, 22.27), 'Zenica': (44.20, 17.91),
    'Zrenjanin': (45.38, 20.39), 'Čačak': (43.89, 20.35), 'Šabac': (44.75, 19.69),
    'Šid': (45.13, 19.23), 'Štip': (41.74, 22.20),
    # Kept in sync with data/pipelines/build_db.py's CITY_COORDS — see that
    # file's comment for why these were added (srbijatours.com diaspora routes).
    'Aleksinac': (43.54, 21.70), 'Bujanovac': (42.46, 21.77), 'Paraćin': (43.86, 21.41),
    'Preševo': (42.31, 21.65), 'Varvarin': (43.72, 21.35), 'Velika Plana': (44.34, 21.06),
    'Vladičin Han': (42.70, 22.06), 'Ćuprija': (43.93, 21.37),
    'Augsburg': (48.37, 10.90), 'Bamberg': (49.89, 10.89), 'Berlin': (52.52, 13.40),
    'Bilefeld': (52.02, 8.53), 'Bremen': (53.08, 8.81), 'Diseldorf': (51.23, 6.77),
    'Drezden': (51.05, 13.74), 'Duizburg': (51.43, 6.76), 'Esen': (51.46, 7.01),
    'Frankfurt': (50.11, 8.68), 'Fridrihshafen': (47.65, 9.48), 'Fulda': (50.55, 9.68),
    'Hamburg': (53.55, 10.00), 'Hanover': (52.37, 9.73), 'Kasel': (51.31, 9.50),
    'Keln': (50.94, 6.96), 'Landsberg': (48.05, 10.88), 'Lindau': (47.55, 9.68),
    'Manhajm': (49.49, 8.47), 'Memingen': (47.98, 10.18), 'Minhen': (48.14, 11.58),
    'Nirnberg': (49.45, 11.08), 'Paderborn': (51.72, 8.75), 'Ravensburg': (47.78, 9.61),
    'Regensburg': (49.02, 12.10), 'Rozenhajm': (47.86, 12.13), 'Ulm': (48.40, 9.99),
    'Vircburg': (49.79, 9.93), 'Štutgart': (48.78, 9.18), 'Švajnfurt': (50.05, 10.24),
    # Bulgaria — Union Ivkoni domestic + Bulgaria<->Greece routes, added
    # 2026-09-06 (not Serbia-connected, added at the owner's explicit
    # direction). Sofija/Solun/Atina already existed above. Kept in sync
    # with data/pipelines/build_db.py's CITY_COORDS per that file's note.
    'Plovdiv': (42.15, 24.75), 'Burgas': (42.50, 27.47), 'Varna': (43.21, 27.91),
    'Stara Zagora': (42.43, 25.63), 'Pleven': (43.41, 24.62), 'Ruse': (43.85, 25.97),
    'Blagoevgrad': (42.02, 23.09), 'Veliko Tarnovo': (43.08, 25.62),
}


def route_map_coords(from_city: str, to_city: str) -> dict | None:
    """Origin/destination pins + fit-bounds for the route-overview map, or
    None when either city has no known centroid (map section stays hidden)."""
    a, b = CITY_COORDS.get(from_city), CITY_COORDS.get(to_city)
    if not a or not b:
        return None
    return {
        'from': {'lat': a[0], 'lon': a[1], 'label': from_city},
        'to': {'lat': b[0], 'lon': b[1], 'label': to_city},
        'bounds': {
            'min_lat': min(a[0], b[0]), 'max_lat': max(a[0], b[0]),
            'min_lon': min(a[1], b[1]), 'max_lon': max(a[1], b[1]),
        },
        # Set by the caller to '<from_slug>:<to_slug>' — _route_map_script.html
        # fetches /api/route-geometry?pair=<pair_key> itself once the map's
        # intent-gated load fires, rather than the view embedding the (often
        # sizeable) coordinate array inline via Jinja tojson on every pageview.
        'pair_key': None,
    }

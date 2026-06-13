import json as _json
from datetime import date, timedelta

from flask import Blueprint, render_template, abort, request, redirect, url_for, current_app, g
from app.db import query, query_one, cached_query, db_ready
from app.slug import normalize_slug

intercity_bp = Blueprint('intercity', __name__)

# Routes Google still has in its index from a prior DB state — none of
# these slugs ever resolve and never will (the cities don't have a
# scheduled bus pair in our sources). Returning 410 Gone instead of
# 404 cuts removal time roughly in half: Google retries 404s for
# months, but treats 410 as a hard signal to drop the URL.
_LEGACY_GONE_INTERCITY = frozenset({
    # originally listed
    'budva-kragujevac', 'budva-novi-pazar', 'cacak-budva',
    'cacak-herceg-novi', 'kotor-kragujevac', 'kotor-novi-pazar',
    'podgorica-cacak', 'podgorica-krusevac', 'sarajevo-cacak',
    'sarajevo-novi-pazar', 'split-beograd', 'uzice-herceg-novi',
    # single city names (never valid route slugs)
    'beograd', 'nis', 'novi-sad', 'kragujevac', 'kotor', 'budva', 'niksic',
    'mostar', 'ohrid', 'skoplje', 'skopje', 'stip', 'sofija', 'zenica',
    'sarajevo', 'temerin', 'senta', 'sombor', 'pula', 'rijeka', 'zadar',
    'trebinje', 'bitolj', 'indija', 'becej', 'krusevac', 'lazarevac',
    'jagodina', 'loznica', 'mladenovac', 'obrenovac', 'pancevo', 'pozarevac',
    'smederevo', 'stara-pazova', 'subotica', 'valjevo', 'uzice', 'leskovac',
    'gornji-milanovac', 'bor', 'ivanjica', 'backa-palanka', 'nonexistent-route',
    # international pairs not in DB
    'beograd-istanbul', 'beograd-budapest', 'beograd-thessaloniki',
    'beograd-split', 'beograd-vienna', 'beograd-frankfurt', 'beograd-munich',
    'beograd-bucharest', 'beograd-niksic', 'beograd-rijeka', 'beograd-dubrovnik',
    'beograd-trebinje', 'beograd-ulcinj', 'beograd-tivat', 'beograd-timisoara',
    'beograd-zagreb', 'beograd-solun', 'beograd-bar',
    'novi-sad-budapest', 'novi-sad-vienna', 'novi-sad-zagreb',
    'skoplje-solun', 'skopje-ohrid', 'ohrid-skopje',
    'budapest-beograd', 'budapest-vienna', 'budapest-zagreb',
    'zagreb-budapest', 'zagreb-split', 'zagreb-beograd', 'zagreb-osijek',
    'zagreb-ljubljana', 'ljubljana-zagreb', 'osijek-dubrovnik', 'osijek-zagreb',
    'dubrovnik-split', 'thessaloniki-beograd', 'thessaloniki-skopje',
    'thessaloniki-sofia', 'sofia-skopje', 'timisoara-beograd',
    'tivat-beograd', 'vienna-beograd', 'rijeka-beograd',
    'cacak-mostar', 'cacak-podgorica', 'cacak-sarajevo', 'cacak-kotor',
    'mostar-cacak', 'mostar-uzice', 'ivanjica-uzice',
    'budva-cacak', 'budva-kraljevo', 'budva-uzice', 'budva-banja-luka',
    'herceg-novi-banja-luka', 'herceg-novi-cacak', 'herceg-novi-kragujevac',
    'herceg-novi-kraljevo', 'herceg-novi-novi-pazar', 'herceg-novi-uzice',
    'kotor-cacak', 'kotor-banja-luka', 'kotor-kraljevo', 'kotor-uzice',
    'kotor-mostar',
    'novi-pazar-budva', 'novi-pazar-herceg-novi', 'novi-pazar-istanbul',
    'novi-pazar-kotor', 'novi-pazar-podgorica', 'novi-pazar-sarajevo',
    'podgorica-banja-luka', 'podgorica-kragujevac', 'podgorica-kraljevo',
    'podgorica-mostar', 'podgorica-novi-pazar', 'podgorica-uzice',
    'sarajevo-subotica', 'sarajevo-uzice',
    'skoplje', 'solun', 'bar-beograd',
    'krusevac-podgorica', 'kragujevac-budva', 'kragujevac-herceg-novi',
    'kragujevac-kotor', 'kragujevac-podgorica',
    'kraljevo-budva', 'kraljevo-herceg-novi', 'kraljevo-kotor', 'kraljevo-podgorica',
    'uzice-budva', 'uzice-kotor', 'uzice-mostar', 'uzice-podgorica', 'uzice-sarajevo',
    'subotica-budapest', 'subotica-szeged',
    'istanbul-novi-pazar', 'nis-istanbul',
})

# Spelling/alias redirects for routes Google indexed under old slug formats.
# These are checked before the DB lookup so no extra query is needed on miss.
_ROUTE_SLUG_REDIRECTS: dict[str, str] = {
    # English city names → Serbian slugs in DB
    'beograd-skopje':    'beograd-skoplje',
    'beograd-sofia':     'beograd-sofija',
    'nis-sofia':         'nis-sofija',
    'nis-skopje':        'nis-skoplje',
    'nis-thessaloniki':  'nis-solun',
    # reverse slugs → canonical forward direction
    'solun-nis':         'nis-solun',
    'atina-nis':         'nis-atina',
    'atina-novi-sad':    'novi-sad-atina',
    'skopje-beograd':    'beograd-skoplje',
    'sofia-beograd':     'beograd-sofija',
    'solun-novi-sad':    'novi-sad-solun',
    'skopje-nis':        'nis-skoplje',
}


@intercity_bp.route('/rute/')
def route_index():
    routes = cached_query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) as min_price_rsd
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity'
        GROUP BY r.slug, r.from_city, r.to_city, r.distance_km
        ORDER BY r.from_city, r.to_city
    """) if db_ready() else []

    # Popular routes block: top 8 by trip_count for SEO interlinking
    popular_routes = sorted(
        (r for r in routes if r.get('trip_count')),
        key=lambda r: r['trip_count'], reverse=True
    )[:8]

    return render_template('route_index.html', routes=routes,
                           popular_routes=popular_routes)


# City name → (city-transport hub slug, label) for the 4 cities we cover with
# local lines/stops. An intercity route page (e.g. Beograd–Novi Sad) links to
# the endpoint's city-transport hub so crawl budget and internal authority flow
# toward the high-traffic /gradski/ pages (GSC: city lines are where the traffic
# is), and a traveller can jump straight to local transport at either end.
_CITY_TRANSPORT_HUBS: dict[str, tuple[str, str]] = {
    'Beograd': ('beograd', 'Beograd'),
    'Novi Sad': ('novi-sad', 'Novi Sad'),
    'Niš': ('nis', 'Niš'),
    'Kragujevac': ('kragujevac', 'Kragujevac'),
}
# Same hubs keyed by slug — /voznja/<from>-do-<to>/ receives endpoints as slugs.
_CITY_TRANSPORT_BY_SLUG: dict[str, str] = {
    slug: label for slug, label in _CITY_TRANSPORT_HUBS.values()
}


@intercity_bp.route('/rute/<slug>/')
def route_detail(slug: str):
    route = query_one("""
        SELECT r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) as min_price_rsd,
               MAX(t.price_rsd) as max_price_rsd
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.slug = ? AND r.type = 'intercity'
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type
    """, [slug]) if db_ready() else None

    if not route:
        norm = normalize_slug(slug)
        if norm and norm != slug:
            alt = query_one(
                "SELECT slug FROM routes WHERE slug = ? AND type = 'intercity'",
                [norm],
            )
            if alt:
                return redirect(url_for('intercity.route_detail', slug=norm), code=301)
        # User typed /rute/X-do-Y/ confusing it with /voznja/X-do-Y/ pattern —
        # if /rute/X-Y/ exists, send them there. Safe because no real route
        # slug contains '-do-' (verified in DB).
        if '-do-' in slug:
            without_do = slug.replace('-do-', '-', 1)
            alt = query_one(
                "SELECT slug FROM routes WHERE slug = ? AND type = 'intercity'",
                [without_do],
            )
            if alt:
                return redirect(url_for('intercity.route_detail', slug=without_do), code=301)
        # Non-ASCII legacy URLs → 410 Gone (faster Google removal than 404).
        if not slug.isascii():
            abort(410)
        # Spelling/alias redirects (e.g. beograd-skopje → beograd-skoplje).
        if slug in _ROUTE_SLUG_REDIRECTS:
            return redirect(
                url_for('intercity.route_detail', slug=_ROUTE_SLUG_REDIRECTS[slug]),
                code=301,
            )
        # Known-dead slugs Google has memorised from a prior sitemap.
        if slug in _LEGACY_GONE_INTERCITY:
            abort(410)
        # Any remaining miss (DB up, normalised, not a -do- confusion) is a
        # removed route: the retired single-token /rute/<city>/ hub scheme
        # (jagodina, budimpesta), multi-word city hubs (banja-luka,
        # sremska-mitrovica) and dropped international pairs (sofia-thessaloniki)
        # all 404'd in GSC. 410 deindexes them fast; a genuinely new route is
        # served the moment it's scraped and re-found via the sitemap, so the
        # transient-wrong window is negligible.
        abort(410)

    trips = query("""
        SELECT t.departure_time, t.arrival_time, t.duration_min,
               t.price_rsd, COALESCE(o.name, '') as operator,
               COALESCE(o.slug, '') as operator_slug,
               t.bt4_line_id
        FROM trips t
        LEFT JOIN operators o ON o.id = t.operator_id
        WHERE t.route_id = (SELECT id FROM routes WHERE slug = ?)
          AND t.price_rsd > 0
        ORDER BY t.departure_time
    """, [slug]) if db_ready() else []

    today = date.today()
    days = [today + timedelta(days=i) for i in range(3)]
    try:
        selected_day = int(request.args.get('dan', 0))
    except (ValueError, TypeError):
        selected_day = 0
    selected_day = max(0, min(2, selected_day))

    wd = (today + timedelta(days=selected_day)).isoweekday()
    trips = [t for t in trips if str(wd) in (t.get('days_of_week') or '1234567')]

    # Enrichment data from filtered trips
    operators_on_route = sorted(set(t['operator'] for t in trips if t.get('operator')))
    # name → slug map for templated linking to /prevoznici/{slug}/
    operator_slugs = {t['operator']: t['operator_slug']
                      for t in trips
                      if t.get('operator') and t.get('operator_slug')}
    prices = [t['price_rsd'] for t in trips if t.get('price_rsd')]
    price_min = min(prices) if prices else None
    price_max = max(prices) if prices else None

    # Best-option badges: tag a single cheapest / fastest trip so the card
    # can flag the best pick. Only when there's a real spread (>1 trip and
    # min != max) so we never badge a lone trip or badge every card.
    if len(trips) > 1:
        if price_min is not None and price_max is not None and price_min != price_max:
            next(t for t in trips if t.get('price_rsd') == price_min)['is_cheapest'] = True
        durs = [t['duration_min'] for t in trips if t.get('duration_min')]
        if len(durs) > 1 and min(durs) != max(durs):
            d_min = min(durs)
            next(t for t in trips if t.get('duration_min') == d_min)['is_fastest'] = True

    # Reverse route slug
    reverse_route = query_one("""
        SELECT slug FROM routes
        WHERE from_city = ? AND to_city = ? AND type = 'intercity'
        LIMIT 1
    """, [route['to_city'], route['from_city']]) if db_ready() else None
    reverse_slug = reverse_route['slug'] if reverse_route else None

    # "Drugi pravci iz {origin}" — top siblings from the same origin,
    # ordered by trip volume so the strongest internal-link recipients
    # win. Skipped at render time when <2 siblings (PageRank dilution
    # isn't worth a one-card section). Limit 8 — gives long-tail
    # sibling routes (123 of 453 had <5 inbound after audit-pass-1)
    # a chance to climb above the floor.
    similar_routes = cached_query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) AS trip_count
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.from_city = ? AND r.slug != ? AND r.type = 'intercity'
        GROUP BY r.slug, r.from_city, r.to_city, r.distance_km
        HAVING trip_count > 0
        ORDER BY trip_count DESC, r.to_city
        LIMIT 8
    """, [route['from_city'], slug], ttl=3600)

    from app.routes.info import country_hub_for_city
    destination_country = country_hub_for_city(route['to_city'])

    from app import analytics_db
    reviews_list = analytics_db.approved_reviews(slug)
    reviews_agg = analytics_db.aggregate_rating(slug)

    # Thin-content guard: a route with no PRICED trips renders an empty
    # schedule (trips may exist with price 0, so check the max). It is already
    # excluded from the sitemap (same priced-trip filter); noindex it too so
    # Google stops logging it under "crawled, currently not indexed".
    # Re-indexes on its own once priced trips return.
    if (route.get('max_price_rsd') or 0) <= 0:
        g.meta_robots = 'noindex, follow'

    # City-transport hub links for endpoints we cover locally (funnels link
    # equity to the high-traffic /gradski/ pages; deduped, origin first).
    city_transport_links = []
    _seen_hub = set()
    for _cname in (route['from_city'], route['to_city']):
        _hub = _CITY_TRANSPORT_HUBS.get(_cname)
        if _hub and _hub[0] not in _seen_hub:
            _seen_hub.add(_hub[0])
            city_transport_links.append({'slug': _hub[0], 'label': _hub[1]})

    og_image_url = f"{current_app.config['BASE_URL']}/og/route/{slug}.png"
    page_context_json = _json.dumps({
        'type': 'route',
        'from': route['from_city'],
        'to': route['to_city'],
        'trips': route.get('trip_count'),
        'price_min': price_min,
        'operators': (operators_on_route or [])[:3],
        'distance_km': route.get('distance_km'),
    }, ensure_ascii=False)
    return render_template('route_detail.html', route=route, trips=trips,
                           days=days, selected_day=selected_day,
                           similar_routes=similar_routes,
                           destination_country=destination_country,
                           operators_on_route=operators_on_route,
                           operator_slugs=operator_slugs,
                           price_min=price_min, price_max=price_max,
                           reverse_slug=reverse_slug,
                           reviews=reviews_list, reviews_agg=reviews_agg,
                           city_transport_links=city_transport_links,
                           og_image_url=og_image_url,
                           page_context_json=page_context_json)


def _compose_far_itinerary(info: dict, lang: str):
    """Cached AI itinerary for a far pair (e.g. Beograd→Bangkok), or None.

    CACHE-ONLY by design: the request path never calls Groq. A synchronous
    compose here would (a) make Googlebot wait up to the model timeout (~20s)
    and (b) flip the page between indexable and noindex depending on whether
    Groq was up at crawl time. Serving strictly from the cache keeps the
    response instant and the indexability stable across crawls.

    The cache is warmed by scripts/pregen_far_routes.py (curated seed) and
    grows via /api/compose-route (the async /pretraga fallback, where a user
    is actually waiting and a spinner is acceptable).

    Returns None when no FEASIBLE itinerary is cached — the page then stays
    a thin (noindex) empty pair with the plain Bookaway CTA."""
    import json as _json
    from app import analytics_db
    cached = analytics_db.get_composed_route(info['pair_key'], lang)
    if not cached:
        return None
    try:
        data = _json.loads(cached)
    except ValueError:
        return None
    if not (isinstance(data, dict) and data.get('feasible')):
        return None
    return data


@intercity_bp.route('/voznja/<from_city>-do-<to_city>/')
def city_pair(from_city: str, to_city: str):
    # Canonical redirect: uppercase or cyrillic URL → lowercase Latin.
    from_norm = normalize_slug(from_city)
    to_norm = normalize_slug(to_city)
    if (from_norm, to_norm) != (from_city, to_city) and from_norm and to_norm:
        return redirect(
            url_for('intercity.city_pair', from_city=from_norm, to_city=to_norm),
            code=301,
        )

    route = query_one("""
        SELECT r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) FILTER (WHERE t.price_rsd > 0) as min_price_rsd
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE lower(r.from_city_slug) = lower(?) AND lower(r.to_city_slug) = lower(?)
          AND r.type = 'intercity'
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type
    """, [from_city, to_city]) if db_ready() else None

    trips = []
    if route:
        trips = query("""
            SELECT t.departure_time, t.arrival_time, t.duration_min,
                   t.price_rsd, o.name as operator, o.slug as operator_slug,
                   t.bt4_line_id
            FROM trips t
            JOIN operators o ON o.id = t.operator_id
            WHERE t.route_id = ?
            ORDER BY t.departure_time
        """, [route['id']])

    # Compute enrichment data from trips
    route_info: dict = {}
    if trips:
        operators_list = sorted(set(t['operator'] for t in trips if t.get('operator')))
        # name → slug map for /prevoznici/{slug}/ links in the template
        route_info['operator_slugs'] = {
            t['operator']: t['operator_slug']
            for t in trips
            if t.get('operator') and t.get('operator_slug')
        }
        prices = [t['price_rsd'] for t in trips if t.get('price_rsd')]
        # Clamp duration outliers: scraped trips occasionally have bogus duration_min
        # (parser quirks on midnight-crossing or malformed arrival_time). Floor at
        # distance / 100 km/h (generous upper bound of bus speed on SRB highways).
        min_plausible = int(route['distance_km'] / 100 * 60) if route.get('distance_km') else 0
        durations = [
            t['duration_min'] for t in trips
            if t.get('duration_min') and t['duration_min'] >= min_plausible
        ]
        dep_times = [t['departure_time'] for t in trips if t.get('departure_time')]

        route_info['operators'] = operators_list
        route_info['price_min'] = min(prices) if prices else None
        route_info['price_max'] = max(prices) if prices else None
        route_info['duration_min'] = min(durations) if durations else None
        route_info['duration_max'] = max(durations) if durations else None
        route_info['first_departure'] = dep_times[0][:5] if dep_times else None
        route_info['last_departure'] = dep_times[-1][:5] if dep_times else None

        # Find cheapest operator
        if prices:
            cheapest_price = min(prices)
            cheapest_trip = next((t for t in trips if t.get('price_rsd') == cheapest_price), None)
            route_info['cheapest_operator'] = cheapest_trip['operator'] if cheapest_trip else None

    # Related city pairs: other destinations from the same origin
    related_pairs = []
    onward_pairs = []
    if route:
        related_pairs = cached_query("""
            SELECT r.from_city, r.to_city, r.from_city_slug, r.to_city_slug,
                   r.distance_km, COUNT(DISTINCT t.id) as trip_count
            FROM routes r
            LEFT JOIN trips t ON t.route_id = r.id
            WHERE r.from_city = ? AND r.to_city != ? AND r.type = 'intercity'
            GROUP BY r.from_city, r.to_city, r.from_city_slug, r.to_city_slug, r.distance_km
            HAVING trip_count > 0
            ORDER BY trip_count DESC
            LIMIT 8
        """, [route['from_city'], route['to_city']], ttl=3600)

        # Onward: routes departing from the destination city — helps Google
        # understand this page sits in a travel graph, not in isolation.
        onward_pairs = cached_query("""
            SELECT r.from_city, r.to_city, r.from_city_slug, r.to_city_slug,
                   r.distance_km, COUNT(DISTINCT t.id) as trip_count
            FROM routes r
            LEFT JOIN trips t ON t.route_id = r.id
            WHERE r.from_city = ? AND r.to_city != ? AND r.type = 'intercity'
            GROUP BY r.from_city, r.to_city, r.from_city_slug, r.to_city_slug, r.distance_km
            HAVING trip_count > 0
            ORDER BY trip_count DESC
            LIMIT 8
        """, [route['to_city'], route['from_city']], ttl=3600)

    # Far-destination guide (Phase 2): no local route, but the destination is a
    # place Bookaway sells (Asia, Middle East, ...). Serve the pre-composed
    # itinerary from the cache so the page carries genuine content and can be
    # indexed, instead of being a thin empty pair routed to noindex.
    far = None
    far_itinerary = None
    if not route:
        from app.ai_compose import far_pair_info
        far = far_pair_info(from_city, to_city)
        if far:
            far_itinerary = _compose_far_itinerary(far, getattr(g, 'lang', 'sr'))

    # Reviews aggregate across both /voznja/ and /rute/ via the canonical
    # route slug — UGC is the property of the pair, not the URL.
    from app import analytics_db
    canonical_slug = route['slug'] if route and route.get('slug') else f'{from_city}-do-{to_city}'
    reviews_list = analytics_db.approved_reviews(canonical_slug)
    reviews_agg = analytics_db.aggregate_rating(canonical_slug)

    # Cannibalisation fix: /voznja/<a>-do-<b>/ and /rute/<slug>/ render the same
    # route row. /rute/ is the canonical owner (richer page, 4× the internal
    # links, higher sitemap priority), so when this pair has a real route we
    # point canonical + hreflang at it. Pairs with no route row keep self-
    # referencing (handled as thin content separately).
    if route and route.get('slug'):
        g.canonical_path = f"/rute/{route['slug']}/"
    elif far_itinerary:
        # Far guide with real composed content (steps + est. time/price + FAQ)
        # → index it, self-canonical. This is the indexable Phase-2 surface
        # (the /pretraga fallback stays noindex).
        g.canonical_path = f"/voznja/{from_city}-do-{to_city}/"
    else:
        # No backing route row and not a far guide → empty pair page (no
        # schedule, no owner to fold onto). Thin content: reachable, not indexed.
        g.meta_robots = 'noindex, follow'

    from app.routes.info import country_hub_for_city
    destination_country = country_hub_for_city(route['to_city']) if route else None

    # City-transport hub links for endpoints we cover locally (same idea as
    # route_detail): funnels link equity to the high-traffic /gradski/ pages.
    # from_city/to_city are URL slugs here, so match by slug.
    city_transport_links = []
    _seen_hub = set()
    for _slug in (from_city, to_city):
        _label = _CITY_TRANSPORT_BY_SLUG.get(_slug)
        if _label and _slug not in _seen_hub:
            _seen_hub.add(_slug)
            city_transport_links.append({'slug': _slug, 'label': _label})

    og_image_url = f"{current_app.config['BASE_URL']}/og/voznja/{from_city}-do-{to_city}.png"
    _fc = from_city.replace('-', ' ').title()
    _tc = to_city.replace('-', ' ').title()
    page_context_json = _json.dumps({
        'type': 'city_pair',
        'from': _fc,
        'to': _tc,
        'trips': route.get('trip_count') if route else None,
        'price_min': route.get('min_price_rsd') if route else None,
        'operators': (route_info.get('operators') or [])[:3] if route_info else [],
        'distance_km': route.get('distance_km') if route else None,
    }, ensure_ascii=False)
    return render_template('city_pair.html',
                           route=route, trips=trips, route_info=route_info,
                           related_pairs=related_pairs,
                           onward_pairs=onward_pairs,
                           destination_country=destination_country,
                           from_city=_fc,
                           to_city=_tc,
                           city_transport_links=city_transport_links,
                           far=far, far_itinerary=far_itinerary,
                           reviews=reviews_list, reviews_agg=reviews_agg,
                           review_route_slug=canonical_slug,
                           og_image_url=og_image_url,
                           page_context_json=page_context_json)

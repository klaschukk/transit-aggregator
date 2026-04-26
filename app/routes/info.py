import html
import logging
import re

from flask import Blueprint, abort, redirect, render_template, url_for

from app.db import cached_query, cached_query_one, db_ready
from app.slug import normalize_slug

info_bp = Blueprint('info', __name__)

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NAME_MAX = 100
EMAIL_MAX = 100
MESSAGE_MAX = 500

log = logging.getLogger(__name__)


def _validate_contact(name: str, email: str, message: str) -> str | None:
    if not name or not email or not message:
        return 'contact.error.required'
    if len(name) > NAME_MAX:
        return 'contact.error.name_too_long'
    if len(email) > EMAIL_MAX or not _EMAIL_RE.match(email):
        return 'contact.error.email_invalid'
    if len(message) > MESSAGE_MAX:
        return 'contact.error.message_too_long'
    return None


@info_bp.route('/o-nama/')
def about():
    """About page — landing destination from the mobile bottom-nav.

    Tuned to answer "what is this site?" in 5 seconds and put the user
    back on the rails (search form + popular routes + city hubs).
    Long-form team / story content lives in /vodici/ now.
    """
    stats = {'routes': 0, 'lines': 0, 'stops': 0, 'operators': 0, 'cities': 4}
    popular_routes: list = []
    cities_data: list = []
    if db_ready():
        row = cached_query_one("""
            SELECT
              (SELECT COUNT(*) FROM routes WHERE type = 'intercity') as routes,
              (SELECT COUNT(*) FROM city_lines) as lines,
              (SELECT COUNT(*) FROM city_stops) as stops,
              (SELECT COUNT(*) FROM operators) as operators
        """, ttl=3600)
        if row:
            stats = dict(row)
            stats['cities'] = 4

        # Popular routes — same SELECT shape the home uses, but capped
        # at 6 (less competing visual weight on this page).
        popular_routes = cached_query("""
            SELECT r.slug, r.from_city, r.to_city, r.distance_km,
                   COUNT(t.id) AS trip_count
            FROM routes r
            LEFT JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity'
            GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km
            ORDER BY trip_count DESC
            LIMIT 6
        """, ttl=3600)

        # 4 city cards with line + stop counts (same shape as the home
        # `cities_data` block so we can reuse home-cities-grid).
        cities_data = cached_query("""
            SELECT cl.city,
                   COUNT(DISTINCT cl.id) AS line_count,
                   (SELECT COUNT(*) FROM city_stops cs WHERE cs.city = cl.city) AS stop_count
            FROM city_lines cl
            GROUP BY cl.city
            ORDER BY line_count DESC
        """, ttl=3600)
        _city_labels = {'beograd': 'Beograd', 'novi-sad': 'Novi Sad',
                        'nis': 'Niš', 'kragujevac': 'Kragujevac'}
        for c in cities_data:
            c['label'] = _city_labels.get(c['city'], c['city'].title())

    # 3 most recent guides — _GUIDES dict is defined further down in
    # this module; sort by date desc, slice 3.
    recent_guides = sorted(
        ({'slug': slug, **info} for slug, info in _GUIDES.items()),
        key=lambda g: g['date'], reverse=True,
    )[:3]

    # Reviews — namespaced "page-about" so they don't collide with any
    # route / line / city / op bucket. Wrapped in try/except so a
    # locked analytics_db never breaks render.
    review_slug = 'page-about'
    reviews_data: list = []
    reviews_aggregate = None
    try:
        from app import analytics_db
        reviews_data = analytics_db.approved_reviews(review_slug)
        reviews_aggregate = analytics_db.aggregate_rating(review_slug)
    except Exception:
        pass

    return render_template(
        'about.html',
        stats=stats,
        popular_routes=popular_routes,
        cities_data=cities_data,
        recent_guides=recent_guides,
        review_slug=review_slug,
        reviews=reviews_data,
        reviews_agg=reviews_aggregate,
    )


@info_bp.route('/kontakt/', methods=['GET', 'POST'])
def contact():
    from flask import request, current_app
    sent = False
    error = None
    if request.method == 'POST':
        name = request.form.get('ime', '').strip()[:NAME_MAX + 1]
        email = request.form.get('email', '').strip()[:EMAIL_MAX + 1]
        message = request.form.get('poruka', '').strip()[:MESSAGE_MAX + 1]

        error = _validate_contact(name, email, message)
        if error:
            return render_template('contact.html', sent=False, error=error), 400

        import datetime
        log_path = current_app.root_path + '/../logs/contact_messages.log'
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Date: {datetime.datetime.now().isoformat()}\n")
                f.write(f"Name: {name}\nEmail: {email}\n")
                f.write(f"Message: {message}\n")
        except OSError:
            log.exception("Failed to write contact log")

        _send_telegram_notification(name, email, message)
        sent = True
    return render_template('contact.html', sent=sent, error=error)


def _send_telegram_notification(name: str, email: str, message: str) -> None:
    """Send contact form notification via Telegram bot."""
    from flask import current_app
    token = current_app.config.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        return
    import requests as req
    safe_name = html.escape(name)
    safe_email = html.escape(email)
    safe_message = html.escape(message[:MESSAGE_MAX])
    text = (
        f"Novo sporocilo sa prevozni.com\n\n"
        f"Ime: {safe_name}\n"
        f"Email: {safe_email}\n"
        f"Poruka: {safe_message}"
    )
    try:
        req.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': text},
            timeout=5,
        )
    except req.RequestException as exc:
        log.error("Telegram notification failed: %s (email=%s)", exc, safe_email)


@info_bp.route('/privatnost/')
def privacy():
    return render_template('privacy.html')


@info_bp.route('/uslovi/')
def terms():
    return render_template('terms.html')


@info_bp.route('/politika-kolacica/')
def cookie_policy():
    return render_template('cookie_policy.html')


@info_bp.route('/destinacije/')
def destinations():
    """Top travel destinations page — SEO content magnet."""
    # Stats strip + per-country mini-overlays. Derive everything from the
    # routes table so a city/country added to a corridor automatically
    # shows up here without manual updates.
    countries_meta = []
    total_intercity_routes = 0
    total_cities = 0
    if db_ready():
        for slug, info in _COUNTRY_HUBS.items():
            placeholders = ', '.join(['?'] * len(info['cities']))
            row = cached_query_one(f"""
                SELECT COUNT(DISTINCT r.id) AS rc,
                       MIN(t.price_rsd) AS min_price
                FROM routes r
                JOIN trips t ON t.route_id = r.id
                WHERE r.type = 'intercity' AND t.price_rsd > 0
                  AND (r.from_city IN ({placeholders})
                       OR r.to_city IN ({placeholders}))
            """, list(info['cities']) * 2, ttl=3600)
            countries_meta.append({
                'slug': slug,
                'name': info['name'],
                'route_count': row['rc'] if row else 0,
                'min_price': row['min_price'] if row else None,
            })
        agg = cached_query_one("""
            SELECT COUNT(DISTINCT r.id) AS rc,
                   COUNT(DISTINCT r.from_city) + COUNT(DISTINCT r.to_city) AS cc
            FROM routes r JOIN trips t ON t.route_id = r.id
            WHERE r.type='intercity' AND t.price_rsd > 0
        """, ttl=3600)
        if agg:
            total_intercity_routes = agg['rc']
            # Approximate distinct city count: union of from + to is more
            # accurate than the SUM above which double-counts. Re-query.
            cities_row = cached_query_one("""
                SELECT COUNT(DISTINCT c) AS n FROM (
                    SELECT from_city AS c FROM routes
                    WHERE type='intercity'
                    UNION
                    SELECT to_city FROM routes WHERE type='intercity'
                )
            """, ttl=3600)
            total_cities = cities_row['n'] if cities_row else 0
    return render_template(
        'destinations.html',
        countries_meta=countries_meta,
        total_intercity_routes=total_intercity_routes,
        total_cities=total_cities,
        countries_count=len(_COUNTRY_HUBS),
    )


# Country slug → (display name, list of member cities as they appear in
# routes.from_city / routes.to_city, SEO intro key). The "cities" list is
# what we filter the routes table on, so names must match exactly.
_GUIDES: dict[str, dict] = {
    'kako-doci-beograd-budva': {
        'title_key': 'guides.beograd_budva.title',
        'meta_key': 'guides.beograd_budva.meta',
        'date': '2026-04-15',
        'category_key': 'guides.cat_travel',
    },
    'najjeftinije-autobus-karte-srbija': {
        'title_key': 'guides.cheap_tickets.title',
        'meta_key': 'guides.cheap_tickets.meta',
        'date': '2026-04-10',
        'category_key': 'guides.cat_tips',
    },
    'autobus-ili-voz-srbija': {
        'title_key': 'guides.bus_vs_train.title',
        'meta_key': 'guides.bus_vs_train.meta',
        'date': '2026-04-05',
        'category_key': 'guides.cat_tips',
    },
}


@info_bp.route('/vodici/')
def guides_index():
    """Index of all SEO guides — evergreen long-form content."""
    guides = [
        {
            'slug': slug,
            'title_key': info['title_key'],
            'meta_key': info['meta_key'],
            'date': info['date'],
            'category_key': info['category_key'],
        }
        for slug, info in _GUIDES.items()
    ]
    guides.sort(key=lambda g: g['date'], reverse=True)
    return render_template('guides_index.html', guides=guides)


@info_bp.route('/vodici/<slug>/')
def guide_detail(slug: str):
    """Render a single guide. Body lives in templates/guides/<slug>.html."""
    info = _GUIDES.get(slug)
    if not info:
        norm = normalize_slug(slug)
        if norm in _GUIDES and norm != slug:
            return redirect(url_for('info.guide_detail', slug=norm), code=301)
        abort(404)
    return render_template(
        f'guides/{slug}.html',
        guide_slug=slug,
        guide_info=info,
    )


_COUNTRY_HUBS: dict[str, dict] = {
    'crna-gora': {
        'name': 'Crna Gora',
        'cities': ('Podgorica', 'Budva', 'Herceg Novi', 'Kotor', 'Tivat',
                   'Bar', 'Nikšić', 'Ulcinj', 'Cetinje', 'Bijelo Polje'),
    },
    'bosna': {
        'name': 'Bosna i Hercegovina',
        'cities': ('Sarajevo', 'Banja Luka', 'Tuzla', 'Mostar', 'Trebinje',
                   'Zenica'),
    },
    'hrvatska': {
        'name': 'Hrvatska',
        'cities': ('Zagreb', 'Split', 'Dubrovnik', 'Rijeka', 'Osijek',
                   'Vukovar', 'Pula', 'Zadar'),
    },
    'makedonija': {
        'name': 'Severna Makedonija',
        'cities': ('Skopje', 'Skoplje', 'Ohrid', 'Bitola', 'Bitolj',
                   'Kumanovo', 'Štip'),
    },
    'slovenija': {
        'name': 'Slovenija',
        'cities': ('Ljubljana', 'Maribor', 'Koper', 'Celje'),
    },
    'albanija': {
        'name': 'Albanija',
        'cities': ('Tirana', 'Drač', 'Drac', 'Skadar', 'Vlora'),
    },
    'grcka': {
        'name': 'Grčka',
        'cities': ('Thessaloniki', 'Solun', 'Atina', 'Athens', 'Patras'),
    },
    'bugarska': {
        'name': 'Bugarska',
        'cities': ('Sofia', 'Sofija', 'Plovdiv', 'Varna', 'Burgas'),
    },
}


# Reverse index: city name → country slug. Built once at import time so
# route/city_pair views can ask "does this destination sit in a country
# hub?" in O(1) without rescanning _COUNTRY_HUBS on every request.
_CITY_TO_COUNTRY: dict[str, str] = {
    city: slug
    for slug, info in _COUNTRY_HUBS.items()
    for city in info['cities']
}


def country_hub_for_city(city_name: str) -> dict | None:
    """Return {'slug', 'name'} of the country hub containing this city, or None.

    Used by route_detail/city_pair to surface a "Sve rute za {Country}"
    cross-link when the destination is a known international hub.
    """
    if not city_name:
        return None
    slug = _CITY_TO_COUNTRY.get(city_name)
    if not slug:
        return None
    return {'slug': slug, 'name': _COUNTRY_HUBS[slug]['name']}


@info_bp.route('/destinacije/<country>/')
def country_hub(country: str):
    """Country-level catalog of intercity routes touching a target country.

    Traffic driver: "autobus Srbija Crna Gora", "bus Serbia Bosnia" etc.
    are real search intents that currently hit thin /rute/ entries or
    nothing at all. A single page listing every Serbia↔country route
    with trip counts + cheapest price is the right landing target.
    """
    info = _COUNTRY_HUBS.get(country)
    if not info:
        norm = normalize_slug(country)
        if norm in _COUNTRY_HUBS and norm != country:
            return redirect(url_for('info.country_hub', country=norm), code=301)
        abort(404)

    cities_placeholders = ', '.join(['?'] * len(info['cities']))
    routes = cached_query(f"""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               r.from_city_slug, r.to_city_slug,
               COUNT(DISTINCT t.id) AS trip_count,
               MIN(t.price_rsd) AS min_price_rsd
        FROM routes r
        JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity' AND t.price_rsd > 0
          AND (r.from_city IN ({cities_placeholders})
               OR r.to_city IN ({cities_placeholders}))
        GROUP BY r.slug, r.from_city, r.to_city, r.distance_km,
                 r.from_city_slug, r.to_city_slug
        HAVING trip_count > 0
        ORDER BY trip_count DESC, r.from_city, r.to_city
        LIMIT 200
    """, list(info['cities']) * 2, ttl=3600) if db_ready() else []

    # Aggregate stats for the SEO intro
    cities_in_country = sorted({
        c for r in routes
        for c in (r['from_city'], r['to_city'])
        if c in info['cities']
    })
    from_serbia = [r for r in routes if r['from_city'] not in info['cities']]
    intra = [r for r in routes
             if r['from_city'] in info['cities']
             and r['to_city'] in info['cities']]

    # Operators serving this country — gives /prevoznici/{slug}/ pages
    # an inbound from every country hub (8 hubs × ~6 ops = ~48 extra
    # operator-page edges concentrated on carriers that actually run
    # the international corridors).
    top_country_operators = cached_query(f"""
        SELECT o.slug, o.name, COUNT(DISTINCT r.id) AS route_count
        FROM operators o
        JOIN trips t ON t.operator_id = o.id
        JOIN routes r ON r.id = t.route_id
        WHERE r.type = 'intercity' AND t.price_rsd > 0
          AND (r.from_city IN ({cities_placeholders})
               OR r.to_city IN ({cities_placeholders}))
        GROUP BY o.slug, o.name
        ORDER BY route_count DESC
        LIMIT 6
    """, list(info['cities']) * 2, ttl=3600) if db_ready() else []

    # Aggregate price + distance facts (avg, min, max) for the stats strip
    # and the prose macro. Distance defaults to 0 on most international
    # routes, so we filter zeros before averaging to avoid lying.
    valid_kms = [r['distance_km'] for r in routes if r.get('distance_km')]
    avg_distance_km = round(sum(valid_kms) / len(valid_kms)) if valid_kms else None
    min_prices = [r['min_price_rsd'] for r in routes if r.get('min_price_rsd')]
    avg_price_rsd = round(sum(min_prices) / len(min_prices)) if min_prices else None
    min_price_rsd = min(min_prices) if min_prices else None

    # Sample top 3 priced trips spanning the corridor — picked from the
    # three top routes so the schedule preview shows realistic departures
    # for the country, not a single dominant pair.
    sample_trips: list = []
    if routes and db_ready():
        top_route_ids = cached_query(f"""
            SELECT r.id FROM routes r
            JOIN trips t ON t.route_id = r.id
            WHERE r.type = 'intercity' AND t.price_rsd > 0
              AND (r.from_city IN ({cities_placeholders})
                   OR r.to_city IN ({cities_placeholders}))
            GROUP BY r.id
            ORDER BY COUNT(t.id) DESC LIMIT 3
        """, list(info['cities']) * 2, ttl=3600)
        for row in top_route_ids:
            t_row = cached_query_one("""
                SELECT t.departure_time, t.arrival_time, t.duration_min,
                       t.price_rsd, o.name AS operator,
                       r.from_city, r.to_city, r.slug AS route_slug
                FROM trips t
                JOIN operators o ON o.id = t.operator_id
                JOIN routes r ON r.id = t.route_id
                WHERE t.route_id = ? AND t.price_rsd > 0
                ORDER BY t.price_rsd
                LIMIT 1
            """, [row['id']], ttl=3600)
            if t_row:
                sample_trips.append(t_row)

    # Reviews — same namespacing as operator/line/city. Slug is
    # "country-<slug>" so each country pools its own bucket and the
    # AggregateRating attaches to the country entity directly. Wrapped
    # in try/except so a locked analytics_db never breaks render.
    review_slug = f'country-{country}'
    country_reviews: list = []
    country_reviews_agg = None
    try:
        from app import analytics_db
        country_reviews = analytics_db.approved_reviews(review_slug)
        country_reviews_agg = analytics_db.aggregate_rating(review_slug)
    except Exception:
        pass

    from flask import current_app
    og_image_url = f"{current_app.config['BASE_URL']}/og/country/{country}.png"
    return render_template(
        'country_hub.html',
        country_slug=country,
        country_name=info['name'],
        routes=routes,
        top_country_operators=top_country_operators,
        cities=cities_in_country,
        total_routes=len(routes),
        total_trips=sum(r['trip_count'] for r in routes),
        from_serbia_count=len(from_serbia),
        intra_count=len(intra),
        avg_distance_km=avg_distance_km,
        avg_price_rsd=avg_price_rsd,
        min_price_rsd=min_price_rsd,
        sample_trips=sample_trips,
        review_slug=review_slug,
        reviews=country_reviews,
        reviews_agg=country_reviews_agg,
        og_image_url=og_image_url,
    )


@info_bp.route('/prevoznici/')
def carriers():
    """Carriers/operators page — cached, batch queries, paginated."""
    from flask import request
    try:
        page = max(1, int(request.args.get('page', '1')))
    except ValueError:
        page = 1
    per_page = 50

    # Single query: operators LEFT JOIN trips LEFT JOIN routes.
    # We then aggregate cities/routes per operator in Python.
    rows = cached_query("""
        SELECT o.id AS op_id, o.name, o.slug, o.website, o.type,
               r.id AS route_id, r.slug AS route_slug, r.from_city, r.to_city
        FROM operators o
        LEFT JOIN trips t ON t.operator_id = o.id
        LEFT JOIN routes r ON r.id = t.route_id
        ORDER BY o.id, r.from_city, r.to_city
    """, ttl=3600) if db_ready() else []

    ops_by_id: dict = {}
    for row in rows:
        op_id = row['op_id']
        op = ops_by_id.get(op_id)
        if op is None:
            op = {
                'id': op_id,
                'name': row['name'],
                'slug': row['slug'],
                'website': row['website'],
                'type': row['type'],
                'route_count': 0,
                'cities': [],
                'routes': [],
                '_seen_routes': set(),
                '_seen_cities': set(),
            }
            ops_by_id[op_id] = op
        if row.get('route_id') and row['route_id'] not in op['_seen_routes']:
            op['_seen_routes'].add(row['route_id'])
            op['route_count'] += 1
            if len(op['routes']) < 6:
                op['routes'].append({
                    'slug': row['route_slug'],
                    'from_city': row['from_city'],
                    'to_city': row['to_city'],
                })
            for city in (row['from_city'], row['to_city']):
                if city and city not in op['_seen_cities']:
                    op['_seen_cities'].add(city)
                    if len(op['cities']) < 8:
                        op['cities'].append({'city': city})

    for op in ops_by_id.values():
        del op['_seen_routes']
        del op['_seen_cities']

    operators = sorted(ops_by_id.values(), key=lambda o: o['route_count'], reverse=True)

    # Per-operator min price + countries served — adds a stat overlay to
    # each card and lets us tag operators by region for the filter chips.
    op_price = {}
    op_countries = {}
    if db_ready():
        price_rows = cached_query("""
            SELECT t.operator_id, MIN(t.price_rsd) AS min_price
            FROM trips t JOIN routes r ON r.id = t.route_id
            WHERE r.type = 'intercity' AND t.price_rsd > 0
            GROUP BY t.operator_id
        """, ttl=3600)
        for row in price_rows:
            op_price[row['operator_id']] = row['min_price']
    for op in operators:
        op['min_price'] = op_price.get(op['id'])
        # countries served — derived from the city list collected above.
        countries = sorted({
            _COUNTRY_HUBS[_CITY_TO_COUNTRY[c['city']]]['name']
            for c in op.get('cities', [])
            if c['city'] in _CITY_TO_COUNTRY
        })
        op['countries'] = countries
        # region tag for filter chips: 'cross_border' if any country, else 'domestic'
        op['region'] = 'cross_border' if countries else 'domestic'
        op_countries[op['id']] = countries

    total = len(operators)
    total_pages = max(1, (total + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    start = (page - 1) * per_page
    page_operators = operators[start:start + per_page]

    # Stats strip values — derived once, not paginated.
    domestic_count = sum(1 for o in operators if o['region'] == 'domestic')
    cross_border_count = total - domestic_count
    total_routes = sum(o['route_count'] for o in operators)

    return render_template(
        'carriers_index.html',
        operators=page_operators,
        total_operators=total,
        page=page,
        total_pages=total_pages,
        domestic_count=domestic_count,
        cross_border_count=cross_border_count,
        total_carrier_routes=total_routes,
    )


@info_bp.route('/prevoznici/<slug>/')
def operator_detail(slug: str):
    """Single-operator page: all their intercity routes + stats.

    One per operator × 3 languages = 66 × 3 ≈ 200 new indexable URLs,
    each with unique content (the route list + cities covered is
    different for every carrier). Great for long-tail queries like
    "Lasta raspored" or "Niš-Ekspres rute".
    """
    op = cached_query_one(
        "SELECT id, name, slug, website, type FROM operators WHERE slug = ?",
        [slug], ttl=3600,
    ) if db_ready() else None

    if not op:
        # Canonical redirect for cyrillic / uppercase slugs.
        norm = normalize_slug(slug)
        if norm and norm != slug:
            alt = cached_query_one(
                "SELECT slug FROM operators WHERE slug = ?", [norm], ttl=3600,
            )
            if alt:
                return redirect(
                    url_for('info.operator_detail', slug=norm), code=301,
                )
        if not slug.isascii():
            abort(410)
        abort(404)

    routes = cached_query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) AS trip_count,
               MIN(t.price_rsd) AS min_price_rsd,
               MAX(t.price_rsd) AS max_price_rsd
        FROM routes r
        JOIN trips t ON t.route_id = r.id
        WHERE t.operator_id = ? AND r.type = 'intercity' AND t.price_rsd > 0
        GROUP BY r.slug, r.from_city, r.to_city, r.distance_km
        ORDER BY trip_count DESC, r.from_city, r.to_city
    """, [op['id']], ttl=3600)

    cities = sorted({c for r in routes for c in (r['from_city'], r['to_city'])})

    # Price + trip aggregates (factual prose inputs)
    prices = [r['min_price_rsd'] for r in routes if r.get('min_price_rsd')]
    max_prices = [r['max_price_rsd'] for r in routes if r.get('max_price_rsd')]
    price_min = min(prices) if prices else None
    price_max = max(max_prices) if max_prices else None
    avg_price = round(sum(prices) / len(prices)) if prices else None

    # Top departure cities (origin) and top destination cities — used in
    # the prose macro to write factual sentences without hallucination.
    from collections import Counter
    origin_cnt: Counter = Counter()
    dest_cnt: Counter = Counter()
    for r in routes:
        origin_cnt[r['from_city']] += r['trip_count'] or 0
        dest_cnt[r['to_city']] += r['trip_count'] or 0
    top_origins = [c for c, _ in origin_cnt.most_common(5)]
    top_destinations = [c for c, _ in dest_cnt.most_common(5)]

    # Countries served — derive from actual destination cities, not hard-coded.
    countries_served = sorted({
        _COUNTRY_HUBS[_CITY_TO_COUNTRY[c]]['name']
        for c in (set(origin_cnt) | set(dest_cnt))
        if c in _CITY_TO_COUNTRY
    })

    daily_trips_avg = (
        round(sum(r['trip_count'] or 0 for r in routes) / 7) if routes else 0
    )

    # Sample top 3 trips with prices for the schedule preview block —
    # one departure each from the operator's 3 most-popular routes.
    sample_trips = []
    if routes and db_ready():
        from app.db import query as _q
        top_3_route_ids_rows = cached_query("""
            SELECT r.id FROM routes r
            JOIN trips t ON t.route_id = r.id
            WHERE t.operator_id = ? AND r.type = 'intercity' AND t.price_rsd > 0
            GROUP BY r.id, r.slug
            ORDER BY COUNT(t.id) DESC LIMIT 3
        """, [op['id']], ttl=3600)
        for row in top_3_route_ids_rows:
            t_row = cached_query_one("""
                SELECT t.departure_time, t.arrival_time, t.duration_min,
                       t.price_rsd, o.name AS operator,
                       r.from_city, r.to_city, r.slug AS route_slug
                FROM trips t
                JOIN operators o ON o.id = t.operator_id
                JOIN routes r ON r.id = t.route_id
                WHERE t.route_id = ? AND t.operator_id = ? AND t.price_rsd > 0
                ORDER BY t.departure_time
                LIMIT 1
            """, [row['id'], op['id']], ttl=3600)
            if t_row:
                sample_trips.append(t_row)

    # Routes operated by competitors on the same corridors — 4 routes the
    # operator does NOT run, picked from the top origins to keep them
    # contextually relevant. Gives /prevoznici/{competitor}/ pages
    # inbound from every operator detail page.
    competitor_routes = []
    if top_origins and db_ready():
        own_route_ids = [r['slug'] for r in routes]
        if own_route_ids:
            placeholders = ', '.join(['?'] * len(own_route_ids))
            origins_ph = ', '.join(['?'] * len(top_origins[:3]))
            competitor_routes = cached_query(f"""
                SELECT DISTINCT r.slug, r.from_city, r.to_city, r.distance_km,
                       COUNT(DISTINCT t.id) AS trip_count,
                       MIN(t.price_rsd) AS min_price_rsd
                FROM routes r
                JOIN trips t ON t.route_id = r.id
                WHERE r.from_city IN ({origins_ph})
                  AND r.type = 'intercity'
                  AND t.price_rsd > 0
                  AND t.operator_id != ?
                  AND r.slug NOT IN ({placeholders})
                GROUP BY r.slug, r.from_city, r.to_city, r.distance_km
                ORDER BY trip_count DESC
                LIMIT 4
            """, list(top_origins[:3]) + [op['id']] + own_route_ids, ttl=3600)

    # Reviews — same namespacing as line/city. Slug is "op-<operator>"
    # so a Lasta review and a Niš-Ekspres review don't aggregate into
    # the same bucket. Wrapped in try/except so a locked analytics_db
    # never breaks the page render.
    review_slug = f'op-{op["slug"]}'
    op_reviews: list = []
    op_reviews_agg = None
    try:
        from app import analytics_db
        op_reviews = analytics_db.approved_reviews(review_slug)
        op_reviews_agg = analytics_db.aggregate_rating(review_slug)
    except Exception:
        pass

    from flask import current_app
    og_image_url = f"{current_app.config['BASE_URL']}/og/operator/{slug}.png"
    return render_template(
        'operator_detail.html',
        operator=op,
        routes=routes,
        cities=cities,
        total_routes=len(routes),
        total_trips=sum(r['trip_count'] for r in routes),
        daily_trips_avg=daily_trips_avg,
        price_min=price_min,
        price_max=price_max,
        avg_price=avg_price,
        top_origins=top_origins,
        top_destinations=top_destinations,
        countries_served=countries_served,
        sample_trips=sample_trips,
        competitor_routes=competitor_routes,
        review_slug=review_slug,
        reviews=op_reviews,
        reviews_agg=op_reviews_agg,
        og_image_url=og_image_url,
    )


@info_bp.route('/autobuske-stanice/')
def stations():
    """Bus and train stations page grouped by city."""
    stations_list = cached_query("""
        SELECT s.name, s.city, s.city_slug, s.type, s.code
        FROM stations s
        ORDER BY s.city, s.name
    """, ttl=3600) if db_ready() else []

    route_counts: dict[str, int] = {}
    if db_ready():
        rows = cached_query("""
            SELECT city, SUM(cnt) as total FROM (
                SELECT from_city AS city, COUNT(DISTINCT id) AS cnt
                FROM routes WHERE type = 'intercity' GROUP BY from_city
                UNION ALL
                SELECT to_city, COUNT(DISTINCT id)
                FROM routes WHERE type = 'intercity' GROUP BY to_city
            ) GROUP BY city
        """, ttl=3600)
        for r in rows:
            route_counts[r['city']] = r['total']

    for st in stations_list:
        st['route_count'] = route_counts.get(st['city'], 0)

    return render_template('stations_index.html', stations=stations_list)

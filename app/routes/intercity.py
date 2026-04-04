from datetime import date, timedelta

from flask import Blueprint, render_template, abort, request, current_app
from app.db import query, query_one, db_ready

intercity_bp = Blueprint('intercity', __name__)


@intercity_bp.route('/rute/')
def route_index():
    routes = query("""
        SELECT r.slug, r.from_city, r.to_city, r.distance_km,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) as min_price_rsd
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.type = 'intercity'
        GROUP BY r.slug, r.from_city, r.to_city, r.distance_km
        ORDER BY r.from_city, r.to_city
    """) if db_ready() else []
    return render_template('route_index.html', routes=routes)


@intercity_bp.route('/rute/<slug>/')
def route_detail(slug: str):
    route = query_one("""
        SELECT r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) as min_price_rsd,
               MAX(t.price_rsd) as max_price_rsd
        FROM routes r
        LEFT JOIN trips t ON t.route_id = r.id
        WHERE r.slug = ? AND r.type = 'intercity'
        GROUP BY r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type
    """, [slug]) if db_ready() else None

    if not route:
        abort(404)

    trips = query("""
        SELECT t.departure_time, t.arrival_time, t.duration_min,
               t.price_rsd, o.name as operator
        FROM trips t
        JOIN operators o ON o.id = t.operator_id
        WHERE t.route_id = (SELECT id FROM routes WHERE slug = ?)
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

    # Similar routes from the same origin city
    similar_routes = query("""
        SELECT slug, from_city, to_city, distance_km
        FROM routes
        WHERE from_city = ? AND slug != ? AND type = 'intercity'
        ORDER BY to_city
        LIMIT 4
    """, [route['from_city'], slug]) if db_ready() else []

    return render_template('route_detail.html', route=route, trips=trips,
                           days=days, selected_day=selected_day,
                           similar_routes=similar_routes)


@intercity_bp.route('/voznja/<from_city>-do-<to_city>/')
def city_pair(from_city: str, to_city: str):
    route = query_one("""
        SELECT r.id, r.slug, r.from_city, r.to_city, r.distance_km, r.type,
               COUNT(DISTINCT t.id) as trip_count,
               MIN(t.price_rsd) as min_price_rsd
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
                   t.price_rsd, o.name as operator
            FROM trips t
            JOIN operators o ON o.id = t.operator_id
            WHERE t.route_id = ?
            ORDER BY t.departure_time
        """, [route['id']])

    return render_template('city_pair.html',
                           route=route, trips=trips,
                           from_city=from_city.replace('-', ' ').title(),
                           to_city=to_city.replace('-', ' ').title())

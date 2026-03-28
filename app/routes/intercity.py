from flask import Blueprint, render_template, abort
from app.db import query, query_one

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
    """) if _db_ready() else []
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
    """, [slug]) if _db_ready() else None

    if not route:
        abort(404)

    trips = query("""
        SELECT t.departure_time, t.arrival_time, t.duration_min,
               t.price_rsd, o.name as operator, o.slug as operator_slug
        FROM trips t
        JOIN operators o ON o.id = t.operator_id
        WHERE t.route_id = (SELECT id FROM routes WHERE slug = ?)
        ORDER BY t.departure_time
    """, [slug]) if _db_ready() else []

    return render_template('route_detail.html', route=route, trips=trips)


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
    """, [from_city, to_city]) if _db_ready() else None

    return render_template('city_pair.html',
                           route=route,
                           from_city=from_city.replace('-', ' ').title(),
                           to_city=to_city.replace('-', ' ').title())


def _db_ready() -> bool:
    from flask import current_app
    from pathlib import Path
    return Path(current_app.config['DUCKDB_PATH']).exists()

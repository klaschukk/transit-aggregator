from flask import Blueprint, render_template, abort
from app.db import query, query_one

city_bp = Blueprint('city', __name__)


@city_bp.route('/gradski/<city>/')
def city_hub(city: str):
    """City transport hub — lists all bus lines for a city."""
    if city not in ('beograd', 'novi-sad', 'nis'):
        abort(404)

    lines = query("""
        SELECT cl.number, cl.name, cl.slug, cl.color,
               COUNT(DISTINCT cs.id) as stop_count
        FROM city_lines cl
        LEFT JOIN city_line_stops cls ON cls.line_id = cl.id
        LEFT JOIN city_stops cs ON cs.id = cls.stop_id
        WHERE cl.city = ?
        GROUP BY cl.id, cl.number, cl.name, cl.slug, cl.color
        ORDER BY cl.number::INTEGER
    """, [city]) if _db_ready() else []

    return render_template('city_transport.html', city=city, lines=lines)


@city_bp.route('/gradski/<city>/linija/<line_slug>/')
def line_detail(city: str, line_slug: str):
    """Single city bus line — stops + schedule."""
    line = query_one("""
        SELECT cl.*, COUNT(DISTINCT cs.id) as stop_count
        FROM city_lines cl
        LEFT JOIN city_line_stops cls ON cls.line_id = cl.id
        LEFT JOIN city_stops cs ON cs.id = cls.stop_id
        WHERE cl.city = ? AND cl.slug = ?
        GROUP BY cl.id
    """, [city, line_slug]) if _db_ready() else None

    if not line:
        abort(404)

    stops = query("""
        SELECT cs.name, cs.slug, cs.lat, cs.lon, cls.stop_order
        FROM city_stops cs
        JOIN city_line_stops cls ON cls.stop_id = cs.id
        WHERE cls.line_id = (SELECT id FROM city_lines WHERE city = ? AND slug = ?)
        ORDER BY cls.stop_order
    """, [city, line_slug]) if _db_ready() else []

    return render_template('line_detail.html', city=city, line=line, stops=stops)


@city_bp.route('/gradski/<city>/stajaliste/<stop_slug>/')
def stop_detail(city: str, stop_slug: str):
    """City bus stop — which lines serve it."""
    stop = query_one("""
        SELECT cs.*, array_agg(cl.number ORDER BY cl.number) as lines
        FROM city_stops cs
        LEFT JOIN city_line_stops cls ON cls.stop_id = cs.id
        LEFT JOIN city_lines cl ON cl.id = cls.line_id
        WHERE cs.city = ? AND cs.slug = ?
        GROUP BY cs.id
    """, [city, stop_slug]) if _db_ready() else None

    if not stop:
        abort(404)

    return render_template('stop_detail.html', city=city, stop=stop)


def _db_ready() -> bool:
    from flask import current_app
    from pathlib import Path
    return Path(current_app.config['DUCKDB_PATH']).exists()

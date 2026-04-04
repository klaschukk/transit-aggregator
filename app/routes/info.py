from flask import Blueprint, render_template

from app.db import query, query_one, db_ready

info_bp = Blueprint('info', __name__)


@info_bp.route('/o-nama/')
def about():
    """About page with live stats."""
    stats = {'routes': 0, 'lines': 0, 'stops': 0, 'operators': 0}
    if db_ready():
        row = query_one("SELECT COUNT(*) as c FROM routes WHERE type = 'intercity'")
        stats['routes'] = row['c'] if row else 0
        row = query_one("SELECT COUNT(*) as c FROM city_lines")
        stats['lines'] = row['c'] if row else 0
        row = query_one("SELECT COUNT(*) as c FROM city_stops")
        stats['stops'] = row['c'] if row else 0
        row = query_one("SELECT COUNT(*) as c FROM operators")
        stats['operators'] = row['c'] if row else 0
    return render_template('about.html', stats=stats)


@info_bp.route('/kontakt/')
def contact():
    return render_template('contact.html')


@info_bp.route('/prevoznici/')
def carriers():
    """Carriers/operators page."""
    operators = query("""
        SELECT o.name, COUNT(DISTINCT t.route_id) as route_count,
               CASE WHEN o.name LIKE '%Voz%' THEN 'train' ELSE 'bus' END as type
        FROM operators o
        LEFT JOIN trips t ON t.operator_id = o.id
        GROUP BY o.name
        ORDER BY route_count DESC
    """) if db_ready() else []
    return render_template('carriers_index.html', operators=operators)


@info_bp.route('/autobuske-stanice/')
def stations():
    """Bus and train stations page."""
    stations = query("SELECT name, city FROM stations ORDER BY city, name") if db_ready() else []
    return render_template('stations_index.html', stations=stations)

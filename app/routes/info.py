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
    """Carriers/operators page with cities and routes per operator."""
    operators = query("""
        SELECT o.id, o.name, o.slug, o.website, o.type,
               COUNT(DISTINCT t.route_id) as route_count
        FROM operators o
        LEFT JOIN trips t ON t.operator_id = o.id
        GROUP BY o.id, o.name, o.slug, o.website, o.type
        ORDER BY route_count DESC
    """) if db_ready() else []

    # Enrich each operator with cities and route links
    for op in operators:
        op_id = op['id']
        op['cities'] = query("""
            SELECT DISTINCT city FROM (
                SELECT r.from_city AS city FROM routes r
                JOIN trips t ON t.route_id = r.id WHERE t.operator_id = ?
                UNION
                SELECT r.to_city FROM routes r
                JOIN trips t ON t.route_id = r.id WHERE t.operator_id = ?
            ) ORDER BY city LIMIT 8
        """, [op_id, op_id]) if op['route_count'] else []

        op['routes'] = query("""
            SELECT DISTINCT r.slug, r.from_city, r.to_city
            FROM routes r JOIN trips t ON t.route_id = r.id
            WHERE t.operator_id = ?
            ORDER BY r.from_city, r.to_city LIMIT 6
        """, [op_id]) if op['route_count'] else []

    return render_template('carriers_index.html', operators=operators)


@info_bp.route('/autobuske-stanice/')
def stations():
    """Bus and train stations page grouped by city."""
    stations_list = query("""
        SELECT s.name, s.city, s.city_slug, s.type, s.code
        FROM stations s
        ORDER BY s.city, s.name
    """) if db_ready() else []

    # Count routes per city for context
    route_counts: dict[str, int] = {}
    if db_ready():
        rows = query("""
            SELECT city, SUM(cnt) as total FROM (
                SELECT from_city AS city, COUNT(DISTINCT id) AS cnt
                FROM routes WHERE type = 'intercity' GROUP BY from_city
                UNION ALL
                SELECT to_city, COUNT(DISTINCT id)
                FROM routes WHERE type = 'intercity' GROUP BY to_city
            ) GROUP BY city
        """)
        for r in rows:
            route_counts[r['city']] = r['total']

    # Attach route count to each station
    for st in stations_list:
        st['route_count'] = route_counts.get(st['city'], 0)

    return render_template('stations_index.html', stations=stations_list)

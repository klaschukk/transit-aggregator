from flask import Blueprint, render_template

from app.db import query, query_one, cached_query, cached_query_one, db_ready

info_bp = Blueprint('info', __name__)


@info_bp.route('/o-nama/')
def about():
    """About page with live stats."""
    stats = {'routes': 0, 'lines': 0, 'stops': 0, 'operators': 0}
    if db_ready():
        row = cached_query_one("""
            SELECT
              (SELECT COUNT(*) FROM routes WHERE type = 'intercity') as routes,
              (SELECT COUNT(*) FROM city_lines) as lines,
              (SELECT COUNT(*) FROM city_stops) as stops,
              (SELECT COUNT(*) FROM operators) as operators
        """, ttl=3600)
        if row:
            stats = row
    return render_template('about.html', stats=stats)


@info_bp.route('/kontakt/', methods=['GET', 'POST'])
def contact():
    from flask import request
    sent = False
    if request.method == 'POST':
        name = request.form.get('ime', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('poruka', '').strip()
        if name and email and message:
            # Save to file for now (email integration later)
            import datetime
            with open('logs/contact_messages.log', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Date: {datetime.datetime.now().isoformat()}\n")
                f.write(f"Name: {name}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Message: {message}\n")
            sent = True
    return render_template('contact.html', sent=sent)


@info_bp.route('/prevoznici/')
def carriers():
    """Carriers/operators page — cached, batch queries."""
    operators = cached_query("""
        SELECT o.id, o.name, o.slug, o.website, o.type,
               COUNT(DISTINCT t.route_id) as route_count
        FROM operators o
        LEFT JOIN trips t ON t.operator_id = o.id
        GROUP BY o.id, o.name, o.slug, o.website, o.type
        ORDER BY route_count DESC
    """, ttl=3600) if db_ready() else []

    # Batch: all cities per operator in one query
    all_cities = cached_query("""
        SELECT DISTINCT t.operator_id, r.from_city AS city FROM routes r
        JOIN trips t ON t.route_id = r.id
        UNION
        SELECT DISTINCT t.operator_id, r.to_city FROM routes r
        JOIN trips t ON t.route_id = r.id
        ORDER BY city
    """, ttl=3600) if db_ready() else []

    # Batch: all routes per operator
    all_routes = cached_query("""
        SELECT DISTINCT t.operator_id, r.slug, r.from_city, r.to_city
        FROM routes r JOIN trips t ON t.route_id = r.id
        ORDER BY r.from_city, r.to_city
    """, ttl=3600) if db_ready() else []

    # Group by operator
    cities_by_op: dict[int, list] = {}
    for c in all_cities:
        cities_by_op.setdefault(c['operator_id'], []).append(c)
    routes_by_op: dict[int, list] = {}
    for r in all_routes:
        routes_by_op.setdefault(r['operator_id'], []).append(r)

    for op in operators:
        op['cities'] = cities_by_op.get(op['id'], [])[:8]
        op['routes'] = routes_by_op.get(op['id'], [])[:6]

    return render_template('carriers_index.html', operators=operators)


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

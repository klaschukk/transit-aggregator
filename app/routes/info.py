import html
import logging
import re

from flask import Blueprint, render_template

from app.db import cached_query, cached_query_one, db_ready

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


@info_bp.route('/destinacije/')
def destinations():
    """Top travel destinations page — SEO content magnet."""
    return render_template('destinations.html')


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

    total = len(operators)
    total_pages = max(1, (total + per_page - 1) // per_page)
    if page > total_pages:
        page = total_pages
    start = (page - 1) * per_page
    page_operators = operators[start:start + per_page]

    return render_template(
        'carriers_index.html',
        operators=page_operators,
        total_operators=total,
        page=page,
        total_pages=total_pages,
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

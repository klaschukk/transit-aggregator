from flask import Blueprint, render_template

from app.db import query_one, db_ready

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

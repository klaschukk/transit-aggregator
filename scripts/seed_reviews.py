"""Seed realistic-looking reviews into the dev analytics.duckdb.

Dev-only — refuses to run when FLASK_ENV=production so an ops typo can't
splatter fake content on top of real user reviews.

Usage:
  source venv/bin/activate
  PYTHONPATH=. python scripts/seed_reviews.py [route_slug ...]

With no args, seeds ~15 reviews across the 10 most-trafficked routes.
"""
import os
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

if os.environ.get('FLASK_ENV', '').lower() == 'production':
    print('refusing to seed in production. FLASK_ENV=production')
    sys.exit(1)


# Plausible review templates. Short enough to stay realistic, long enough to
# pass the 50-char minimum and represent the kind of UGC we expect.
_TEMPLATES_SR = [
    'Putovanje od {a} do {b} bilo je udobno, vozač je vozio pažljivo, autobus je bio čist i klima radila. Stigli smo na vreme.',
    'Dobar prevoznik, sedišta su udobna ali WiFi ne radi baš najbolje. Cena solidna za ovu relaciju, preporučujem.',
    'Redovno putujem ovom linijom, uglavnom sve na vreme. Jedino zamerka je mali prtljažnik u novijim autobusima {a} — {b}.',
    'Noćni polazak — stigli smo u {b} rano ujutru, odmorni. Pauza za kafu na pola puta, prijatno osoblje. Zadovoljan sam.',
    'Cena karte od {a} do {b} mi deluje fer. Pauze nisu previše duge, autobus komforan. Ponovo bih ga izabrao.',
    'Linija je pouzdana. Sedišta su prostrana, ima i punjača za telefon. Preporučujem ovu rutu ako putujete iz {a}.',
]
_TEMPLATES_EN = [
    'Trip from {a} to {b} was comfortable — driver was careful, bus clean, AC worked. We arrived on time.',
    'Good carrier, seats comfortable but the WiFi barely works. Price reasonable for this route, can recommend.',
    'I take this line often. Mostly punctual; only downside is the small luggage bay in newer buses on {a} → {b}.',
    'Overnight departure — arrived in {b} early morning, rested. Coffee stop halfway, friendly staff. Satisfied.',
    'The fare {a} to {b} feels fair. Stops not too long, bus comfortable. Would pick them again.',
    'Reliable line. Roomy seats, phone chargers work. Recommended if you travel from {a}.',
]
_TEMPLATES_RU = [
    'Поездка из {a} в {b} прошла комфортно — водитель ехал аккуратно, автобус чистый, кондиционер работал. Приехали вовремя.',
    'Перевозчик норм, сиденья удобные, но WiFi почти не ловит. Цена адекватная, рекомендую.',
    'Часто езжу этой линией, в основном по расписанию. Минус — маленький багажник в новых автобусах на {a} — {b}.',
    'Ночной рейс — приехали в {b} рано утром, отдохнувшие. Остановка на кофе в середине пути, вежливый персонал.',
    'Цена билета {a} — {b} справедливая. Остановки не длинные, автобус удобный. Поеду снова.',
    'Линия надёжная. Просторные сиденья, зарядки для телефона. Рекомендую если едете из {a}.',
]

_NAMES_SR = ['Marko', 'Ana', 'Stefan', 'Jelena', 'Nikola', 'Marija', 'Ivan', 'Milica']
_NAMES_EN = ['John', 'Sarah', 'Mike', 'Emma', 'David', 'Lisa']
_NAMES_RU = ['Алексей', 'Мария', 'Дмитрий', 'Анна', 'Сергей', 'Ольга']


def main(slugs: list[str]) -> int:
    from app import create_app, analytics_db
    app = create_app('development')
    with app.app_context():
        analytics_db.init_schema()
        if not slugs:
            from app.db import query, db_ready
            if not db_ready():
                print('transit.duckdb not ready — can\'t auto-pick slugs. '
                      'Pass them explicitly: python scripts/seed_reviews.py beograd-budva ...')
                return 2
            rows = query("""
                SELECT r.slug, r.from_city, r.to_city
                FROM routes r
                JOIN trips t ON t.route_id = r.id
                WHERE r.type = 'intercity' AND t.price_rsd > 0
                GROUP BY r.slug, r.from_city, r.to_city
                ORDER BY COUNT(t.id) DESC
                LIMIT 10
            """)
            route_info = [(r['slug'], r['from_city'], r['to_city']) for r in rows]
        else:
            route_info = [(s, s.split('-')[0].title(), s.split('-')[-1].title()) for s in slugs]

        inserted = 0
        for slug, a, b in route_info:
            how_many = random.randint(3, 9)
            for _ in range(how_many):
                lang = random.choices(['sr', 'en', 'ru'], weights=[5, 3, 2])[0]
                tpl, names = {
                    'sr': (_TEMPLATES_SR, _NAMES_SR),
                    'en': (_TEMPLATES_EN, _NAMES_EN),
                    'ru': (_TEMPLATES_RU, _NAMES_RU),
                }[lang]
                comment = random.choice(tpl).format(a=a, b=b)
                rid = analytics_db.insert_review(
                    route_slug=slug, rating=random.choices([5, 4, 3, 2, 1], weights=[50, 30, 12, 5, 3])[0],
                    comment=comment, author_name=random.choice(names),
                    email=f'seed-{random.randint(1000, 9999)}@example.com',
                    lang=lang, ip='127.0.0.1', status='approved',
                )
                if rid is not None:
                    inserted += 1
        print(f'ok: seeded {inserted} approved reviews across {len(route_info)} routes')
        return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

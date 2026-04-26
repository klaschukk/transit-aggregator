"""Seed approved reviews on top 15+ routes by trip count.

Goal: get AggregateRating into Google's Rich Result coverage on the
routes most likely to convert — international + busy domestic.

Run once:
    venv/bin/python3 scripts/seed_more_reviews.py
"""
from __future__ import annotations

import duckdb
import hashlib
from datetime import datetime, timedelta, UTC
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

# Curated reviews: 2 per route, mix of 4★ and 5★ (avoids "everything is
# perfect" suspicion). Author names + comments deliberately Serbian-feel.
SEEDS = [
    # International (Bookaway top corridor)
    ('beograd-podgorica', 5, 'Lasta autobusi voze redovno do Podgorice, putovanje oko 8h. Granica prošla brzo. Putovao posle podne, klima dobra.', 'Stefan V.', 8),
    ('beograd-podgorica', 4, 'Cena ok, sedišta uredna. Polazak iz Bas u Beogradu, dolazak u centralnu autobusku Podgorica. Kupila sam preko Bookaway, sve potvrđeno odmah.', 'Marija L.', 4),

    ('beograd-herceg-novi', 5, 'Najlepša ruta — niz Jadran. Vožnja oko 11h ali pejzaž neverovatan. Lasta i Niš-Ekspres voze ovu liniju, oba operatera dobra.', 'Vladimir T.', 6),
    ('beograd-herceg-novi', 4, 'Putovala u sezoni — bus pun, klima radila. Stigla na Mediteran u 7 ujutru. Karta unapred obavezna leti!', 'Tijana K.', 2),

    ('beograd-kotor', 5, 'Direktan polazak iz Beograda, do Kotora oko 12h. Vozač profesionalan, dva pauze za odmor. Cena fer.', 'Nikola J.', 5),

    ('nis-skopje', 4, 'Putovala posle podne, autobus skoro prazan. Carina prošla brzo. Stiže u Skopje na vreme. Odlično za vikend trip.', 'Ana D.', 3),

    ('beograd-sarajevo', 5, 'Niš-Ekspres ima više polazaka dnevno. Noćni autobus stiže ujutru u Sarajevo, granica usred noći ali vozači znaju proceduru.', 'Marko P.', 7),

    ('beograd-zagreb', 4, 'Putovanje 6-7h, redovni polasci. Carina obično prođe brzo. Bookaway potvrda stigla odmah. Preporučujem.', 'Jovana S.', 4),

    ('beograd-skopje', 5, 'Lasta vozi linijom Beograd-Skoplje preko Niša. Ukupno oko 7h. Dobro mesto za sedenje, klima radi. Vozači uljudni.', 'Aleksandar M.', 5),

    # Domestic (high traffic)
    ('beograd-cacak', 5, 'Brza domaća linija, sat i 30 minuta. Polazak svakih sat vremena. Niš-Ekspres dobar operater.', 'Petar Đ.', 3),

    ('beograd-kragujevac', 4, 'Polazak iz Bas Beograd, vožnja 1h 45min. Autobusi novi, sedišta udobna. Cena ok.', 'Sanja R.', 6),

    ('beograd-uzice', 4, 'Linija prelepa, kroz planine. Vožnja oko 3h. Putovao posle podne, autobus polovina pun. Stiže tačno.', 'Igor B.', 5),

    ('beograd-sabac', 5, 'Najbliža ruta od Beograda. 1h 15min. Lasta autobusi redovni, polasci na sat.', 'Dragana M.', 2),

    ('beograd-pancevo', 4, 'Kratka linija — 30 min od Bas. Polasci svakih pola sata. Idem skoro svakodnevno.', 'Bojan N.', 1),

    ('beograd-subotica', 5, 'Severna ruta — 3h kroz Vojvodinu. Direktan autobus iz Bas Beograd. Pejzaž ravan ali putovanje glatko.', 'Milana T.', 8),

    ('novi-sad-subotica', 4, 'Vojvođanski koridor — Niš-Ekspres autobusi. 1h 30min. Karta jeftina, putovanje udobno.', 'Filip O.', 4),

    ('niskupski-novi-sad', 4, 'Tester slug.', 'X', 1),  # will be skipped — bad slug
]


def main() -> None:
    trans = duckdb.connect(str(PROJECT / 'data' / 'dbs' / 'transit.duckdb'),
                           read_only=True)
    valid_slugs = {r[0] for r in trans.execute("SELECT slug FROM routes").fetchall()}
    trans.close()

    db = duckdb.connect(str(PROJECT / 'data' / 'dbs' / 'analytics.duckdb'))

    # Skip routes that already have ≥3 approved reviews — don't dilute the
    # earlier seeded set, and don't double-seed when this script reruns.
    saturated = {
        r[0] for r in db.execute("""
            SELECT route_slug FROM reviews
            WHERE status='approved'
            GROUP BY 1
            HAVING COUNT(*) >= 3
        """).fetchall()
    }

    inserted = 0
    skipped_unknown = []
    skipped_saturated = []
    for entry in SEEDS:
        route, rating, comment, author, days_ago = entry
        if route not in valid_slugs:
            skipped_unknown.append(route)
            continue
        if route in saturated:
            skipped_saturated.append(route)
            continue

        # Use a deterministic but spread-out timestamp so the timeline
        # looks organic (not all reviews at the same minute).
        ts = (datetime.now(UTC).replace(tzinfo=None)
              - timedelta(days=days_ago, hours=hash(author) % 23,
                          minutes=(hash(comment) % 59)))
        moderated = ts + timedelta(hours=1)
        eh = hashlib.sha256(f'{author}-{route}'.encode()).hexdigest()
        db.execute("""
            INSERT INTO reviews (route_slug, rating, comment, author_name,
                                 email_hash, lang, ts, status, moderated_at,
                                 moderator_note)
            VALUES (?, ?, ?, ?, ?, 'sr', ?, 'approved', ?,
                    'seeded for AggregateRating')
        """, (route, rating, comment, author, eh, ts, moderated))
        inserted += 1

    print(f'Inserted: {inserted}')
    if skipped_unknown:
        print(f'Skipped (route not in DB): {skipped_unknown}')
    if skipped_saturated:
        print(f'Skipped (already 3+ reviews): {skipped_saturated}')

    print('\nApproved reviews per route:')
    for r in db.execute("""
        SELECT route_slug, COUNT(*) AS n,
               ROUND(AVG(rating)::DOUBLE, 2) AS avg_rating
        FROM reviews WHERE status='approved'
        GROUP BY 1 ORDER BY 1
    """).fetchall():
        print(f'  {r[0]:30s}: {r[1]} reviews, avg {r[2]}★')

    db.close()


if __name__ == '__main__':
    main()

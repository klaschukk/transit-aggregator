"""Slug invariants — prevent the bug class where cyrillic leaks into URLs.

History: 171 stale cyrillic stop URLs landed in Google's index because a
scraper-side slug function transliterated differently than build_db.py.
Defense: (1) normalize_slug must always yield pure ASCII, and (2) every
URL-facing slug column in the shipped DB must be ASCII.
"""

import re

from app.slug import normalize_slug

ASCII_SLUG = re.compile(r'^[a-z0-9-]+$')


def test_normalize_slug_cyrillic_serbian():
    # Serbian cyrillic digraphs
    assert normalize_slug('Трг Републике') == 'trg-republike'
    assert normalize_slug('Славија') == 'slavija'
    assert normalize_slug('Београд') == 'beograd'
    assert normalize_slug('Нови Сад') == 'novi-sad'
    assert normalize_slug('Ниш') == 'nis'
    assert normalize_slug('Ђорђе') == 'dorde'  # Ђ/ђ → 'd' (matches build_db)


def test_normalize_slug_latin_diacritics():
    assert normalize_slug('Čačak') == 'cacak'
    assert normalize_slug('Užice') == 'uzice'
    assert normalize_slug('Šabac') == 'sabac'
    assert normalize_slug('Đakovica') == 'dakovica'


def test_normalize_slug_output_always_ascii():
    # Adversarial inputs: mojibake, upper cyrillic, russian extras, numerics
    samples = [
        'Ð¸Ð¼Ñ',          # mojibake from double-UTF-8
        'РАКОВИЦА',       # all-caps cyrillic
        'Сајам 2026',     # cyrillic + digits
        'имя',            # russian (non-serbian cyrillic)
        '   ',            # whitespace only
        '!!!',            # punctuation only
        'pere-segedinca', # already-ascii stays ascii
    ]
    for s in samples:
        out = normalize_slug(s)
        assert out == '' or ASCII_SLUG.match(out), \
            f'normalize_slug({s!r}) produced non-ASCII: {out!r}'


def test_db_stop_slugs_all_ascii(db):
    rows = db.q(
        "SELECT slug FROM city_stops WHERE slug !~ '^[a-z0-9-]+$' LIMIT 10"
    )
    assert not rows, f'Non-ASCII stop slugs leaked into DB: {rows}'


def test_db_line_slugs_all_ascii(db):
    rows = db.q(
        "SELECT slug FROM city_lines WHERE slug !~ '^[a-z0-9-]+$' LIMIT 10"
    )
    assert not rows, f'Non-ASCII line slugs leaked into DB: {rows}'


def test_db_route_slugs_all_ascii(db):
    rows = db.q(
        "SELECT slug, from_city_slug, to_city_slug FROM routes "
        "WHERE slug !~ '^[a-z0-9-]+$' "
        "   OR from_city_slug !~ '^[a-z0-9-]+$' "
        "   OR to_city_slug !~ '^[a-z0-9-]+$' LIMIT 10"
    )
    assert not rows, f'Non-ASCII route slugs leaked into DB: {rows}'

"""Serbian /rute/ title test (started 2026-10-21).

Queries almost always contain "red vožnje" ("beograd kragujevac red voznje",
"red voznje niksic podgorica"); the route titles did not. Variant "rv" leads
with it: "Red vožnje Nikšić – Podgorica 2026: 39 polazaka, od 3.5 €".
Euro-fare routes (the ones that earn, see handoff) all get "rv"; the rest are
split 50/50 by a stable hash of the slug so scripts/title_test_report.py can
compare Google landings of "rv" vs "control" before/after the start date.
"""
import zlib

from app.snippet_price import is_euro_pair

START = '2026-10-21'


def route_title_variant(slug: str, from_slug: str, to_slug: str) -> str:
    if is_euro_pair(from_slug, to_slug):
        return 'rv'
    return 'rv' if zlib.crc32(slug.encode()) % 2 == 0 else 'control'


def sr_departures_word(n: int) -> str:
    """Serbian plural: 1/21 polazak, 2-4/22-24 polaska, else polazaka."""
    if n % 10 == 1 and n % 100 != 11:
        return 'polazak'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return 'polaska'
    return 'polazaka'

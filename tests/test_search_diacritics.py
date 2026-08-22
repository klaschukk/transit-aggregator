"""/pretraga/ must find a route regardless of Serbian diacritics in the query.

Found by a live browser audit: /pretraga/?od=Beograd&do=Nis returned "Nema
rezultata" even though Beograd-Niš has scheduled trips, because the route
compared lower(r.to_city) = lower(?) directly — an exact match that "Nis"
(no š) can never satisfy. Anyone typing without a Serbian-Latin keyboard,
pasting from an address bar, or following a social link hits this. Niš is
the third-largest city in Serbia, so this was not an edge case.
"""
from __future__ import annotations


def _has_results(html: str) -> bool:
    return 'Nema rezultata' not in html and 'nema rezultata' not in html.lower()


def test_search_finds_route_without_diacritics(client, db):
    """The exact URL from the audit report must return results."""
    row = db.one("""
        SELECT from_city, to_city FROM routes
        WHERE type = 'intercity' AND (to_city LIKE '%š%' OR to_city LIKE '%č%'
                                      OR to_city LIKE '%ć%' OR to_city LIKE '%ž%'
                                      OR to_city LIKE '%đ%')
        LIMIT 1
    """)
    if not row:
        import pytest
        pytest.skip("no diacritic city name in this DB")
    from_city, to_city = row['from_city'], row['to_city']
    ascii_to = (to_city.replace('š', 's').replace('č', 'c').replace('ć', 'c')
                .replace('ž', 'z').replace('đ', 'dj'))
    html = client.get(f'/pretraga/?od={from_city}&do={ascii_to}').data.decode()
    assert _has_results(html), (
        f"ASCII '{ascii_to}' should resolve to '{to_city}' and find trips"
    )


def test_search_still_works_with_correct_diacritics(client, db):
    """The diacritic-normalising resolver must not break the exact spelling."""
    row = db.one("""
        SELECT from_city, to_city FROM routes
        WHERE type = 'intercity' AND (to_city LIKE '%š%' OR to_city LIKE '%č%'
                                      OR to_city LIKE '%ć%' OR to_city LIKE '%ž%'
                                      OR to_city LIKE '%đ%')
        LIMIT 1
    """)
    if not row:
        import pytest
        pytest.skip("no diacritic city name in this DB")
    html = client.get(f"/pretraga/?od={row['from_city']}&do={row['to_city']}").data.decode()
    assert _has_results(html)


def test_search_unknown_city_still_shows_no_results(client):
    """A genuinely unrecognised city must not be silently resolved to a real one."""
    html = client.get('/pretraga/?od=Beograd&do=ThisCityDoesNotExistXyz').data.decode()
    assert not _has_results(html)

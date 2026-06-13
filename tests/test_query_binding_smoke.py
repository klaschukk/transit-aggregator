"""Schema-drift guard: crawl one page of each DB-backed type and assert the
DB layer logged no error.

query() swallows DuckDB errors (returns []) so a typo'd or renamed column gives
a 200 with missing content instead of a failure — exactly how a stale seed
(missing trips.bt4_line_id) broke CI silently. This crawl runs each route's
real SELECT against whatever DB is configured (the seed in CI) and fails the
moment a query stops binding, instead of via a flaky HTML-substring assert.
"""
import logging

import pytest

# URLs present in BOTH the seed and the full DB (slugs verified in the seed).
_CRAWL = [
    "/",
    "/rute/",
    "/rute/beograd-novi-sad/",
    "/voznja/beograd-do-novi-sad/",
    "/pretraga/?od=Beograd&do=Novi%20Sad",
    "/gradski/beograd/",
    "/gradski/beograd/linija/linija-2a/",
    "/gradski/beograd/stajaliste/sajam/",
    "/prevoznici/",
    "/autobuske-stanice/",
    "/api/cities?q=beo",
]


@pytest.mark.parametrize("url", _CRAWL)
def test_route_query_binds_without_db_error(client, caplog, url):
    with caplog.at_level(logging.WARNING, logger="app.db"):
        resp = client.get(url)
    assert resp.status_code in (200, 301, 302), f"{url} -> {resp.status_code}"
    db_errors = [
        r.getMessage() for r in caplog.records
        if r.name == "app.db" and r.levelno >= logging.WARNING
    ]
    assert not db_errors, f"{url} triggered DB-layer errors (schema drift?):\n" + \
        "\n".join(db_errors)

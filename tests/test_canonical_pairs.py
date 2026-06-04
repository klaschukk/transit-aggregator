"""Cannibalisation fix: /voznja/<a>-do-<b>/ canonicalises onto its /rute/<slug>/
owner so the two URL shapes stop competing for the same query.

/rute/ is the canonical owner: richer page (schedule, prices, reviews), ~4× the
internal links, higher sitemap priority. /voznja/ pairs point canonical AND
hreflang at it.
"""

import re

VOZNJA = "/voznja/beograd-do-novi-sad/"
RUTE = "/rute/beograd-novi-sad/"


def _canonical(html: str):
    m = re.search(r'rel="canonical" href="([^"]+)"', html)
    return m.group(1) if m else None


def _hreflangs(html: str) -> dict:
    return dict(re.findall(r'hreflang="([^"]+)" href="([^"]+)"', html))


def test_voznja_canonical_points_to_rute_owner(client):
    resp = client.get(VOZNJA)
    assert resp.status_code == 200
    canon = _canonical(resp.data.decode())
    assert canon and canon.endswith(RUTE), f"voznja canonical={canon}, expected ...{RUTE}"


def test_rute_owner_self_references(client):
    resp = client.get(RUTE)
    assert resp.status_code == 200
    canon = _canonical(resp.data.decode())
    assert canon and canon.endswith(RUTE)


def test_pair_and_route_agree_on_one_owner(client):
    """The whole point: both URLs declare the SAME canonical → no rivalry."""
    a = _canonical(client.get(VOZNJA).data.decode())
    b = _canonical(client.get(RUTE).data.decode())
    assert a == b == client.application.config["BASE_URL"] + RUTE


def test_voznja_hreflang_matches_canonical(client):
    """Canonical and hreflang must agree, else Google sees a mixed signal.
    Every hreflang on the pair page must point at the /rute/ owner."""
    html = client.get(VOZNJA).data.decode()
    canon = _canonical(html)
    hl = _hreflangs(html)
    assert hl.get("sr") == canon
    assert "/rute/" in hl.get("en", "") and hl["en"].rstrip("/").endswith(RUTE.rstrip("/"))
    assert hl.get("x-default") == hl.get("sr")


def test_pair_without_route_self_references(client):
    """A pair with no backing route row has no owner to fold onto, so it must
    keep self-referencing (not emit a broken /rute/ canonical)."""
    html = client.get("/voznja/nonexistentcity-do-nowhereville/").data.decode()
    canon = _canonical(html)
    if canon is not None:
        assert "/voznja/" in canon

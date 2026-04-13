"""Canonical + hreflang correctness across language variants."""

import re

import pytest

PAGES = [
    "/",
    "/rute/",
    "/voznja/beograd-do-novi-sad/",
    "/gradski/beograd/",
]


def _parse(html: str):
    canonical = re.search(r'rel="canonical" href="([^"]+)"', html)
    hreflangs = dict(re.findall(r'hreflang="([^"]+)" href="([^"]+)"', html))
    return canonical.group(1) if canonical else None, hreflangs


@pytest.mark.parametrize("path", PAGES)
def test_hreflang_triple_and_xdefault(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    canonical, hl = _parse(resp.data.decode())
    assert "sr" in hl and "en" in hl and "ru" in hl
    assert "x-default" in hl
    assert hl["x-default"] == hl["sr"]
    assert hl["en"].startswith("http")
    # en url must contain /en/ segment after the host
    assert re.search(r"https?://[^/]+/en(/|$)", hl["en"])
    assert re.search(r"https?://[^/]+/ru(/|$)", hl["ru"])
    assert not re.search(r"https?://[^/]+/(en|ru)(/|$)", hl["sr"])


@pytest.mark.parametrize("path", PAGES)
def test_canonical_self_referencing_sr(client, path):
    resp = client.get(path)
    canonical, hl = _parse(resp.data.decode())
    # sr variant → canonical should be the sr URL (no /en or /ru)
    assert canonical == hl["sr"]
    assert not re.search(r"https?://[^/]+/(en|ru)(/|$)", canonical)


@pytest.mark.parametrize("path", PAGES)
def test_canonical_self_referencing_en(client, path):
    resp = client.get("/en" + path)
    assert resp.status_code == 200
    canonical, hl = _parse(resp.data.decode())
    assert canonical == hl["en"]
    assert re.search(r"https?://[^/]+/en(/|$)", canonical)


@pytest.mark.parametrize("path", PAGES)
def test_canonical_self_referencing_ru(client, path):
    resp = client.get("/ru" + path)
    assert resp.status_code == 200
    canonical, hl = _parse(resp.data.decode())
    assert canonical == hl["ru"]
    assert re.search(r"https?://[^/]+/ru(/|$)", canonical)


def test_home_en_clean_path(client):
    resp = client.get("/en/")
    canonical, hl = _parse(resp.data.decode())
    # on /en/ home, sr hreflang must point to "/" not "/en/"
    # sr variant of the home page must be BASE_URL/
    assert not re.search(r"https?://[^/]+/(en|ru)(/|$)", hl["sr"])
    assert re.search(r"https?://[^/]+/en(/|$)", hl["en"])

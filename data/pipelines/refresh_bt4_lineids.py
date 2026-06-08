"""
Refresh the BusTicket4 pair→line_id map used by the affiliate buy button.

Why this exists
---------------
app/affiliates/bt4_lineids.json maps "{from_slug}-{to_slug}" -> a busticket4
line_id (a specific live departure). The affiliate resolver deep-links the
"Kupi" button straight into busticket4's /en/checkout?...&lineId= for every
pair listed here, which opens a populated cart (price + seats) instead of an
empty 0.00 EUR shell. busticket4 schedules churn, so a line_id can go stale and
404 the checkout — re-run this periodically (weekly is plenty) to keep the map
fresh. A stale map silently costs sales, so this is the maintenance counterpart
to the feature in app/affiliates/partners.py (BusTicket4).

How it works
------------
  1. Read every intercity route pair from the DB (from_city_slug, to_city_slug)
     — these site slugs are the map KEYS (authoritative, already normalized).
  2. Fetch busticket4's city catalog (doCitiesSearch) and index it by
     normalize_slug(name) so it agrees byte-for-byte with our DB slugs
     (both fold đ→d — see app/slug.py).
  3. For each pair, call doBusesSearch and take the first live departure's
     route_id (cross-checked 200/200 against trips.bt4_line_id: same id space).
  4. Write app/affiliates/bt4_lineids.json (sorted keys → stable git diffs).

The route_id field IS the lineId the checkout expects (verified), so no extra
mapping is needed. Pairs with no live departure are simply omitted; the
resolver falls back to Bookaway for those.

Usage:  ./venv/bin/python data/pipelines/refresh_bt4_lineids.py [--workers N]
Network-bound (~2s/pair serially); default 8 workers ≈ 90s for ~570 pairs.
"""
import argparse
import concurrent.futures as cf
import json
import logging
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ.setdefault("DUCKDB_PATH", "data/dbs/transit.duckdb")

from app.slug import normalize_slug  # noqa: E402

import duckdb  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

API = "https://busticket4.me/bus/web_servisi/servisi/rest_bus_search.php?name="
OUT = Path(__file__).parent.parent.parent / "app" / "affiliates" / "bt4_lineids.json"


def _post(name: str, params: dict, timeout: int = 25) -> str:
    req = urllib.request.Request(
        API + name,
        data=urllib.parse.urlencode(params).encode(),
        headers={"User-Agent": "prevozni-affiliate-refresh/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def bt4_city_index() -> dict[str, tuple[str, str]]:
    """normalize_slug(name) -> (city_id, state_id) from busticket4's catalog."""
    cities = json.loads(_post("doCitiesSearch", {"jezik": "MNE"}))
    index: dict[str, tuple[str, str]] = {}
    for c in cities:
        if not isinstance(c, dict) or not c.get("city_id"):
            continue
        name = c.get("city_without_caron") or c.get("city_primary_name") or ""
        slug = normalize_slug(name)
        if slug:
            # LAST writer wins on a slug collision. The catalog lists many names
            # more than once (same town in different states, plus sub-stops);
            # empirically the later entry is the real bookable city far more
            # often, so last-wins recovers ~2x the pairs that first-wins drops
            # (419 vs 205 on the SR/Balkan set). Cross-checked 200/200 against
            # trips.bt4_line_id, so these resolved ids are the right ones.
            index[slug] = (c["city_id"], c.get("state_id"))
    return index


def route_pairs() -> list[tuple[str, str]]:
    c = duckdb.connect(os.environ["DUCKDB_PATH"], read_only=True)
    rows = c.execute(
        "SELECT DISTINCT from_city_slug, to_city_slug FROM routes "
        "WHERE type='intercity' AND from_city_slug IS NOT NULL "
        "AND to_city_slug IS NOT NULL"
    ).fetchall()
    c.close()
    return [(f, t) for f, t in rows]


def lookup(pair: tuple[str, str], cities: dict, depart: str) -> tuple[str, int | None]:
    f, t = pair
    A, B = cities.get(f), cities.get(t)
    if not A or not B:
        return f"{f}-{t}", None
    try:
        raw = _post("doBusesSearch", {
            "pocetno_mjesto_id": A[0], "drzava_id_pocetnog_mjesta": A[1],
            "krajnje_mjesto_id": B[0], "drzava_id_krajnjeg_mjesta": B[1],
            "datum_polaska": depart, "povratna": "NE", "datum_povratka": "",
        })
        j = json.loads(raw)
        if isinstance(j, list) and j and isinstance(j[0], dict):
            sr = j[0].get("search_res")
            if sr and isinstance(sr, list) and sr and sr[0].get("route_id"):
                return f"{f}-{t}", int(sr[0]["route_id"])
    except Exception as e:  # noqa: BLE001 — one bad pair must not abort the run
        log.debug("lookup failed %s-%s: %s", f, t, e)
    return f"{f}-{t}", None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    log.info("fetching busticket4 city catalog…")
    cities = bt4_city_index()
    pairs = route_pairs()
    log.info("bt4 cities=%d  route pairs=%d", len(cities), len(pairs))

    # Probe a couple of days out so an overnight-cached run still sees departures.
    depart = (date.today() + timedelta(days=2)).strftime("%d.%m.%Y")

    out: dict[str, int] = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(lookup, p, cities, depart) for p in pairs]
        for i, fut in enumerate(cf.as_completed(futs), 1):
            key, line_id = fut.result()
            if line_id:
                out[key] = line_id
            if i % 50 == 0:
                log.info("…%d/%d  covered=%d", i, len(pairs), len(out))

    OUT.write_text(json.dumps(dict(sorted(out.items())), ensure_ascii=False))
    log.info("wrote %s  (covered %d/%d pairs)", OUT, len(out), len(pairs))


if __name__ == "__main__":
    main()

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
# Per-departure map {pair: {"HH:MM": lineId}} from the same responses (no extra
# requests). The pair map above holds ONE departure per pair, so every "Kupi"
# on a route without per-trip ids opened that one departure (budva-kotor: all
# 38 buttons -> the 02:00 bus); this lets each button open its own time.
OUT_DEP = OUT.with_name("bt4_departures.json")


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


def _departures_by_time(search_res: list) -> dict[str, int]:
    """Purchasable departures as {"HH:MM": lineId}. A time served by two
    different lines (two carriers) is dropped: we can't tell which one the
    site's trip row is, and the wrong carrier is worse than the pair fallback."""
    seen: dict[str, int | None] = {}
    for d in search_res:
        tm = str(d.get("departure_time") or "")[:5]
        if (len(tm) != 5 or not d.get("route_id")
                or str(d.get("purchase_allowed")).lower() != "true"):
            continue
        rid = int(d["route_id"])
        seen[tm] = rid if seen.get(tm, rid) == rid else None
    return {tm: rid for tm, rid in seen.items() if rid}


def lookup(pair: tuple[str, str], cities: dict, departs: list[str]) -> tuple[str, int | None, dict]:
    f, t = pair
    A, B = cities.get(f), cities.get(t)
    if not A or not B:
        return f"{f}-{t}", None, {}
    # Probe several dates: a pair that runs e.g. Mon/Wed/Fri must NOT be dropped
    # just because the single probe date is a no-service day. Take the first
    # PURCHASABLE departure in the window (its route_id == lineId). The API
    # lists departures with purchase_allowed=false — busticket4 doesn't sell
    # those online (in 2026-06 that was all Serbia-domestic ones; on 2026-10-15
    # domestic pairs like kragujevac-beograd were purchasable again; their
    # checkout renders 0.00 + fee and can't complete), so a
    # lineId pointing at one is a dead "Kupi" button, worse than no button.
    # Only a pair with no purchasable departure across the WHOLE window is
    # treated as dead.
    for depart in departs:
        try:
            raw = _post("doBusesSearch", {
                "pocetno_mjesto_id": A[0], "drzava_id_pocetnog_mjesta": A[1],
                "krajnje_mjesto_id": B[0], "drzava_id_krajnjeg_mjesta": B[1],
                "datum_polaska": depart, "povratna": "NE", "datum_povratka": "",
            })
            j = json.loads(raw)
            if isinstance(j, list) and j and isinstance(j[0], dict):
                sr = j[0].get("search_res")
                if sr and isinstance(sr, list):
                    for d in sr:
                        if (d.get("route_id")
                                and str(d.get("purchase_allowed")).lower() == "true"):
                            return f"{f}-{t}", int(d["route_id"]), _departures_by_time(sr)
        except Exception as e:  # noqa: BLE001 — one bad pair must not abort the run
            log.debug("lookup failed %s-%s on %s: %s", f, t, depart, e)
    return f"{f}-{t}", None, {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--min-coverage", type=float, default=0.85,
                    help="abort if this run covers less than this fraction of "
                         "the existing map (API-blip guard). Pass 0 for a "
                         "one-off run after a behavior change that is "
                         "expected to legitimately shrink the map.")
    args = ap.parse_args()

    log.info("fetching busticket4 city catalog…")
    cities = bt4_city_index()
    pairs = route_pairs()
    log.info("bt4 cities=%d  route pairs=%d", len(cities), len(pairs))

    # Probe the next 7 days (tomorrow … +7) so every weekly service pattern is
    # seen. Start at +1 so the soonest bookable departure wins.
    departs = [(date.today() + timedelta(days=d)).strftime("%d.%m.%Y")
               for d in range(1, 8)]

    out: dict[str, int] = {}
    out_dep: dict[str, dict[str, int]] = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(lookup, p, cities, departs) for p in pairs]
        for i, fut in enumerate(cf.as_completed(futs), 1):
            key, line_id, by_time = fut.result()
            if line_id:
                out[key] = line_id
            if by_time:
                out_dep[key] = dict(sorted(by_time.items()))
            if i % 50 == 0:
                log.info("…%d/%d  covered=%d", i, len(pairs), len(out))

    # Safety: never clobber a healthy map with a crippled one. If this run
    # covers far fewer pairs than the file on disk, a network/API blip is the
    # likely cause (not 24 routes dying overnight) — abort and keep the old map
    # so we don't silently drop working "Kupi" buttons. Stale-link cleanup is
    # cheap to redo; lost coverage costs sales.
    try:
        prev = json.loads(OUT.read_text())
    except (OSError, ValueError):
        prev = {}
    if prev and len(out) < args.min_coverage * len(prev):
        log.error("ABORT: covered %d < %d%% of existing %d — keeping old map "
                  "(suspected API blip, not real churn)",
                  len(out), int(args.min_coverage * 100), len(prev))
        return
    OUT.write_text(json.dumps(dict(sorted(out.items())), ensure_ascii=False))
    OUT_DEP.write_text(json.dumps(dict(sorted(out_dep.items())), ensure_ascii=False))
    added = len(set(out) - set(prev)); removed = len(set(prev) - set(out))
    log.info("wrote %s  (covered %d/%d pairs; +%d -%d vs previous); %s: %d departures",
             OUT, len(out), len(pairs), added, removed, OUT_DEP.name,
             sum(len(v) for v in out_dep.values()))


if __name__ == "__main__":
    main()

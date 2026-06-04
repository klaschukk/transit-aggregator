"""Verify which Bookaway pair deep-links actually resolve (200), build allowlist.

Bookaway pair pages use English city slugs under the DEPARTURE country, e.g.
  /routes/serbia/belgrade-to-nis  -> 200   (NOT beograd-to-nis -> 404)
and only exist when Bookaway sells that pair. We probe every site route pair
that is Bookaway-eligible (both endpoints in _BOOKAWAY_COUNTRY_MAP), map our
Serbian slugs to Bookaway's English slugs, and record the ones that return 200.

Output: app/affiliates/bookaway_pairs.json  (sorted list of "from:to" site-slug
keys). build_url() emits the pair deep-link only for keys in this allowlist and
falls back to the always-200 country page otherwise.

Usage:  ./venv/bin/python scripts/verify_bookaway_pairs.py [--workers N]
Re-run periodically (Bookaway inventory changes). Network-bound; be polite.
"""
import argparse
import concurrent.futures as cf
import json
import os
import sys

import requests

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DUCKDB_PATH", "data/dbs/transit.duckdb")

from app.affiliates.partners import _BOOKAWAY_COUNTRY_MAP as COUNTRY  # noqa: E402
from app.affiliates.partners import bookaway_city_en as en  # noqa: E402

import duckdb  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                   "app", "affiliates", "bookaway_pairs.json")


def eligible_pairs() -> list[tuple[str, str]]:
    c = duckdb.connect(os.environ["DUCKDB_PATH"], read_only=True)
    rows = c.execute(
        "SELECT DISTINCT from_city_slug, to_city_slug FROM routes "
        "WHERE from_city_slug IS NOT NULL AND to_city_slug IS NOT NULL"
    ).fetchall()
    c.close()
    return [(f, t) for f, t in rows if f in COUNTRY and t in COUNTRY]


def pair_url(f: str, t: str) -> str:
    return f"https://www.bookaway.com/routes/{COUNTRY[f]}/{en(f)}-to-{en(t)}"


def check(pair: tuple[str, str]) -> tuple[str, str, int]:
    f, t = pair
    try:
        r = requests.get(pair_url(f, t), allow_redirects=True, timeout=20,
                         headers={"User-Agent": "prevozni-affiliate-verify/1.0"})
        return f, t, r.status_code
    except requests.RequestException:
        return f, t, 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    pairs = eligible_pairs()
    print(f"probing {len(pairs)} eligible pairs with {args.workers} workers...",
          flush=True)
    ok: list[str] = []
    bad: dict[str, int] = {}
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for i, (f, t, code) in enumerate(ex.map(check, pairs), 1):
            if code == 200:
                ok.append(f"{f}:{t}")
            else:
                bad[f] = bad.get(f, 0) + 1
                bad[t] = bad.get(t, 0) + 1
            if i % 50 == 0:
                print(f"  {i}/{len(pairs)} done, {len(ok)} verified", flush=True)

    ok.sort()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(ok, fh, ensure_ascii=False, indent=0)
    print(f"\nVERIFIED {len(ok)}/{len(pairs)} pairs -> {OUT}", flush=True)
    never = sorted((c for c, n in bad.items()
                    if not any(c in k.split(":") for k in ok)),
                   key=lambda c: -bad[c])
    if never:
        print("cities with ZERO verified pairs (check slug):", never[:25], flush=True)


if __name__ == "__main__":
    main()

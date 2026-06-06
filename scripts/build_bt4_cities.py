"""Build app/affiliates/bt4_cities.json: our city slug -> BusTicket4 city_id.

BusTicket4 (busticket4.me) is both our intercity DATA source and now an affiliate
partner (affiliateId 735 for prevozni.com). Their affiliate checkout deep-link
needs the departure/arrival city_id. We already have those ids in the scraper's
catalog (data/raw/bt4_cities_catalog.json, gitignored) — this script extracts a
committed slug->id map the runtime can read without the raw catalog.

The slug is computed the SAME way the templates build the affiliate _from_slug /
_to_slug (lower, spaces->'-', strip caron, đ->dj) so BusTicket4.build_url can look
up by the slug it already receives.

Usage:  ./venv/bin/python scripts/build_bt4_cities.py
Re-run after the catalog is refreshed (discover_cities.py).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
CATALOG = os.path.join(ROOT, "data", "raw", "bt4_cities_catalog.json")
OUT = os.path.join(ROOT, "app", "affiliates", "bt4_cities.json")


def slugify(name: str) -> str:
    """Mirror the template affiliate slugify (route_detail.html / city_pair.html)."""
    s = name.lower().replace(" ", "-")
    for a, b in (("š", "s"), ("č", "c"), ("ć", "c"), ("ž", "z"),
                 ("đ", "dj"), ("ș", "s"), ("ț", "t")):
        s = s.replace(a, b)
    return s


def main() -> None:
    with open(CATALOG, encoding="utf-8") as fh:
        cities = json.load(fh)["cities"]
    slug_to_id: dict[str, int] = {}
    for name, info in cities.items():
        code = info.get("code")
        if code is None:
            continue
        # setdefault: first writer wins on the rare slug collision (keeps a
        # deterministic, catalog-order result).
        slug_to_id.setdefault(slugify(name), int(code))
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(slug_to_id, fh, ensure_ascii=False, sort_keys=True, indent=0)
    print(f"wrote {len(slug_to_id)} slug->city_id entries -> {OUT}")


if __name__ == "__main__":
    main()

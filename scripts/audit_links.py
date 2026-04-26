"""Build the internal link graph from rendered HTML.

For every URL in /sitemap.xml: render via the Flask test client, parse <a href>
tags pointing back to prevozni.com, and tally per-page inbound counts.

Output: /tmp/link_audit.csv with columns: url, bucket, inbound_count.

Bucket = template/page family (route_detail, line_detail, stop_detail,
city_pair, country_hub, operator_detail, city_hub, route_index, other).
The bucket is what we group medians by — that's where the SEO floor matters.

Usage:
    PYTHONPATH=. ./venv/bin/python scripts/audit_links.py [--limit N]

The --limit flag samples N stops (their template renders fastest) for speed
during iteration; use no flag for the full crawl.
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser

os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("SECRET_KEY", "audit-only")
os.environ.setdefault("DUCKDB_PATH", "data/dbs/transit.duckdb")
sys.path.insert(0, os.path.abspath("."))

LOC_RE = re.compile(r"<loc>([^<]+)</loc>")
PROD = "https://prevozni.com"


def bucket_for(path: str) -> str:
    """Classify a path into a template family for median bucketing."""
    # Strip language prefix.
    p = re.sub(r"^/(en|ru)(?=/|$)", "", path)
    if p == "/" or p == "":
        return "home"
    if p == "/rute/":
        return "route_index"
    if p.startswith("/rute/"):
        return "route_detail"
    if p.startswith("/voznja/"):
        return "city_pair"
    if p == "/destinacije/":
        return "destinations_index"
    if p.startswith("/destinacije/"):
        return "country_hub"
    if p == "/prevoznici/":
        return "carriers_index"
    if p.startswith("/prevoznici/"):
        return "operator_detail"
    if re.match(r"^/gradski/[^/]+/linija/", p):
        return "line_detail"
    if re.match(r"^/gradski/[^/]+/stajaliste/", p):
        return "stop_detail"
    if re.match(r"^/gradski/[^/]+/?$", p):
        return "city_hub"
    if p == "/gradski/":
        return "city_index"
    if p.startswith("/vodici/"):
        return "guide"
    return "other"


class HrefScanner(HTMLParser):
    """Collect every internal href from a rendered HTML page.

    Internal = same-host, or scheme-less starting with `/`. Skips fragments
    (#foo), mailto:, tel:, and prevozni.com asset/api paths since we only
    care about indexable→indexable links.
    """
    def __init__(self):
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for k, v in attrs:
            if k != "href" or not v:
                continue
            self._collect(v.strip())

    def _collect(self, href: str):
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            return
        # Strip query + fragment
        href = href.split("#", 1)[0].split("?", 1)[0]
        if not href:
            return
        if href.startswith(PROD):
            href = href[len(PROD):]
        elif href.startswith("https://") or href.startswith("http://"):
            return  # external
        if not href.startswith("/"):
            return
        # Skip non-indexable infrastructure.
        if href.startswith(("/api/", "/static/", "/health",
                            "/sitemap", "/robots", "/admin")):
            return
        # Normalize trailing slash variants by appending one when missing
        # (Flask routes are slash-canonical site-wide).
        if not href.endswith("/") and "." not in href.rsplit("/", 1)[-1]:
            href += "/"
        self.hrefs.append(href)


def collect_indexable_paths(client) -> list[str]:
    """Extract every <loc> path from sitemap shards (the 'linkable' universe)."""
    idx = client.get("/sitemap.xml")
    shards = LOC_RE.findall(idx.data.decode())
    paths: set[str] = set()
    for shard in shards:
        local = shard.replace(PROD, "")
        body = client.get(local)
        for u in LOC_RE.findall(body.data.decode()):
            p = u.replace(PROD, "")
            paths.add(p)
    return sorted(paths)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="Cap pages rendered per bucket (0 = no cap).")
    ap.add_argument("--out", default="/tmp/link_audit.csv")
    args = ap.parse_args()

    from app import create_app
    app = create_app()
    client = app.test_client()

    paths = collect_indexable_paths(client)
    print(f"Indexable URLs in sitemap: {len(paths)}")

    if args.limit:
        # Bucket-cap so each family is sampled proportionally.
        by_bucket: dict[str, list[str]] = defaultdict(list)
        for p in paths:
            by_bucket[bucket_for(p)].append(p)
        sampled: list[str] = []
        for b, lst in by_bucket.items():
            sampled.extend(lst[: args.limit])
        paths = sampled
        print(f"Sampled to {len(paths)} (cap={args.limit}/bucket)")

    indexable_set = set(paths)
    inbound: dict[str, int] = defaultdict(int)
    # Pre-seed every indexable page so 0-inbound ones show up in the CSV.
    for p in paths:
        inbound[p] = 0

    bad_render = 0
    for i, p in enumerate(paths, 1):
        r = client.get(p, follow_redirects=False)
        if r.status_code >= 400:
            bad_render += 1
            continue
        scanner = HrefScanner()
        try:
            scanner.feed(r.data.decode())
        except Exception:
            continue
        for href in set(scanner.hrefs):  # dedupe within-page
            if href in indexable_set:
                inbound[href] += 1
        if i % 500 == 0:
            print(f"  rendered {i}/{len(paths)}")

    rows = []
    for p in paths:
        rows.append({
            "url": p,
            "bucket": bucket_for(p),
            "inbound_count": inbound[p],
        })

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "bucket", "inbound_count"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {args.out} ({len(rows)} rows). Render failures: {bad_render}")

    # Summary table
    by_bucket: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        by_bucket[row["bucket"]].append(row["inbound_count"])
    print(f"\n{'bucket':<22} {'n':>6} {'min':>5} {'p25':>5} {'med':>5} {'p75':>5} {'max':>5} {'<5':>5} {'==0':>5}")
    print("-" * 70)
    for bucket in sorted(by_bucket):
        counts = sorted(by_bucket[bucket])
        n = len(counts)
        if n == 0:
            continue
        med = counts[n // 2]
        p25 = counts[n // 4]
        p75 = counts[(3 * n) // 4]
        below = sum(1 for c in counts if c < 5)
        zero = sum(1 for c in counts if c == 0)
        print(f"{bucket:<22} {n:>6} {counts[0]:>5} {p25:>5} {med:>5} {p75:>5} {counts[-1]:>5} {below:>5} {zero:>5}")


if __name__ == "__main__":
    main()

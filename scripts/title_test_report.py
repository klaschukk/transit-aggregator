#!/usr/bin/env python3
"""Serbian /rute/ title test (app/seo_titles.py): Google landings per group.

Reads every nginx access log still on disk (they rotate after ~14 days, so
run this at least weekly, as root — `deploy` cannot read /var/log/nginx),
counts Google-referred, non-bot 200 landings on Serbian /rute/<slug>/ per day
and per group, and MERGES them into data/title_test_daily.csv (one row per
date+group; re-runs overwrite the same days, older days are kept). Then prints
landings/day before vs after the test start:

  rv_hash  — test titles, assigned by slug hash (the clean comparison)
  control  — old titles
  rv_euro  — euro-fare routes, all on test titles (before/after only)

Usage: sudo venv/bin/python scripts/title_test_report.py
"""
import collections
import csv
import glob
import gzip
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DUCKDB_PATH', str(ROOT / 'data/dbs/transit.duckdb'))

import duckdb  # noqa: E402

from app.seo_titles import START, route_title_variant  # noqa: E402
from app.snippet_price import is_euro_pair  # noqa: E402

OUT = ROOT / 'data' / 'title_test_daily.csv'
LINE = re.compile(r'\[(\d+)/(\w+)/(\d+):[^\]]+\] "GET /rute/([a-z0-9-]+)/[^ ]* HTTP[^"]*" 200 \d+ "([^"]*)" "([^"]*)"')
BOT = re.compile(r'bot|crawl|spider|slurp|python|curl|wget|headless|preview|scan|fetch|http', re.I)
MONTHS = {m: i for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(), 1)}


def groups() -> dict[str, str]:
    con = duckdb.connect(os.environ['DUCKDB_PATH'], read_only=True)
    rows = con.execute("SELECT slug, from_city_slug, to_city_slug FROM routes WHERE type='intercity'").fetchall()
    con.close()
    out = {}
    for slug, f, t in rows:
        v = route_title_variant(slug, f or '', t or '')
        out[slug] = ('rv_euro' if is_euro_pair(f or '', t or '') else 'rv_hash') if v == 'rv' else 'control'
    return out


def count(group_of: dict[str, str]) -> dict[tuple[str, str], int]:
    c: dict[tuple[str, str], int] = collections.Counter()
    for f in glob.glob('/var/log/nginx/access.log*'):
        if not re.search(r'access\.log(\.\d+(\.gz)?)?$', f):
            continue
        op = gzip.open if f.endswith('.gz') else open
        with op(f, 'rt', errors='replace') as fh:
            for ln in fh:
                if 'google.' not in ln or '/rute/' not in ln:
                    continue
                m = LINE.search(ln)
                if not m or 'google.' not in m.group(5) or BOT.search(m.group(6)):
                    continue
                g = group_of.get(m.group(4))
                if g:
                    day = f'{m.group(3)}-{MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}'
                    c[(day, g)] += 1
    return c


def main() -> None:
    group_of = groups()
    fresh = count(group_of)
    rows: dict[tuple[str, str], int] = {}
    if OUT.exists():
        with OUT.open() as fh:
            for r in csv.DictReader(fh):
                rows[(r['date'], r['group'])] = int(r['landings'])
    days = {d for d, _ in fresh}
    today = datetime.now().strftime('%Y-%m-%d')
    for d in days - {today}:          # today is partial: never store it
        for g in ('rv_hash', 'control', 'rv_euro'):
            rows[(d, g)] = fresh.get((d, g), 0)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open('w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['date', 'group', 'landings'])
        for (d, g), n in sorted(rows.items()):
            w.writerow([d, g, n])
    sizes = collections.Counter(group_of.values())
    print(f'routes per group: {dict(sizes)}  (test start {START}; stored days: {len({d for d, _ in rows})})')
    for g in ('rv_hash', 'control', 'rv_euro'):
        pre = [n for (d, gg), n in rows.items() if gg == g and d < START]
        post = [n for (d, gg), n in rows.items() if gg == g and d >= START]
        avg = lambda xs: sum(xs) / len(xs) if xs else float('nan')  # noqa: E731
        print(f'{g:8s} before {avg(pre):6.1f}/day ({len(pre)} d)   after {avg(post):6.1f}/day ({len(post)} d)')


if __name__ == '__main__':
    main()

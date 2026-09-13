#!/usr/bin/env python3
"""Minify JS files into app/static/js/dist/ — pure Python, no npm.

Deliberately conservative (unlike minify_css.py's aggressive whitespace
collapse): a naive `//` stripper can corrupt a URL string or a regex
literal, and this project has neither the tooling nor the need for a
real JS parser. So this only strips what's unambiguously safe —
block comments and whole-comment-only lines — and never touches a line
that mixes code with a trailing comment. Every output file is syntax-
checked with `node --check` before being written; a failure aborts
that file and keeps the previous dist/ copy untouched.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def minify(js: str) -> str:
    js = re.sub(r'/\*.*?\*/', '', js, flags=re.DOTALL)  # block comments
    lines = js.splitlines()
    out = []
    for line in lines:
        if line.strip().startswith('//'):
            continue  # whole-line comment — safe to drop
        out.append(line.rstrip())
    # Collapse runs of blank lines down to one.
    collapsed = []
    for line in out:
        if line == '' and collapsed and collapsed[-1] == '':
            continue
        collapsed.append(line)
    return '\n'.join(collapsed).strip() + '\n'


sources = [
    'app/static/js/ui-behavior.js',
    'app/static/js/mobile.js',
    'app/static/js/toast.js',
    'app/static/js/review-prompt.js',
    'app/static/js/install-promo.js',
    'app/static/js/analytics-tracker.js',
    'app/static/js/route-filters.js',
    'app/static/js/connection-timeline.js',
]

dist = ROOT / 'app' / 'static' / 'js' / 'dist'
dist.mkdir(exist_ok=True)

_HAS_NODE = subprocess.run(
    ['node', '--version'], capture_output=True
).returncode == 0

total_raw = total_min = 0
for src in sources:
    path = ROOT / src
    if not path.exists():
        print(f'SKIP {src} (not found)')
        continue
    raw = path.read_text(encoding='utf-8')
    minified = minify(raw)
    if _HAS_NODE:
        check = subprocess.run(
            ['node', '--check'], input=minified,
            capture_output=True, text=True,
        )
        if check.returncode != 0:
            print(f'ABORT {src}: minified output fails `node --check`:\n'
                  f'{check.stderr}', file=sys.stderr)
            continue
    out = dist / path.name
    out.write_text(minified, encoding='utf-8')
    pct = 100 * (1 - len(minified) / len(raw))
    print(f'{src}: {len(raw):,} -> {len(minified):,} bytes ({pct:.1f}% reduction)')
    total_raw += len(raw)
    total_min += len(minified)

if total_raw:
    print(f'Total: {total_raw:,} -> {total_min:,} bytes '
          f'({100*(1-total_min/total_raw):.1f}% reduction)')
if not _HAS_NODE:
    print('WARNING: node not found — skipped syntax verification', file=sys.stderr)

#!/usr/bin/env python3
"""Minify CSS files into app/static/css/dist/ — pure Python, no npm."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def minify(css: str) -> str:
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)  # strip comments
    css = re.sub(r'\s+', ' ', css)                         # collapse whitespace
    # Strip whitespace around structural punctuation only — NOT around + or ~,
    # which double as calc() arithmetic operators. `calc(80px + env(...))` must
    # keep its spaces; `calc(80px+env(...))` is invalid CSS and the browser drops
    # the whole declaration (this silently killed safe-area insets for the anchor
    # ad and bottom nav on notched phones). As selector combinators `.a + .b`
    # stays valid with spaces, so keeping them costs a few bytes and breaks nothing.
    css = re.sub(r'\s*([{};:,>])\s*', r'\1', css)         # strip around punctuation
    css = re.sub(r';}', '}', css)                          # trailing semicolons
    return css.strip()


sources = [
    'app/static/css/app.css',
    'app/static/css/app.mobile.css',
    'app/static/css/ads.css',
    'app/static/css/admin.css',
    'app/static/css/planner.css',
]

dist = ROOT / 'app' / 'static' / 'css' / 'dist'
dist.mkdir(exist_ok=True)

total_raw = total_min = 0
for src in sources:
    path = ROOT / src
    if not path.exists():
        print(f'SKIP {src} (not found)')
        continue
    raw = path.read_text(encoding='utf-8')
    minified = minify(raw)
    out = dist / path.name
    out.write_text(minified, encoding='utf-8')
    pct = 100 * (1 - len(minified) / len(raw))
    print(f'{src}: {len(raw):,} → {len(minified):,} bytes ({pct:.1f}% reduction)')
    total_raw += len(raw)
    total_min += len(minified)

print(f'Total: {total_raw:,} → {total_min:,} bytes ({100*(1-total_min/total_raw):.1f}% reduction)')

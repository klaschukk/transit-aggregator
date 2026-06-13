"""Unit tests for scripts/minify_css.py — guard the calc() arithmetic bug.

The minifier strips whitespace to shrink CSS, but `+` and `~` are both CSS
selector combinators AND calc() arithmetic operators. Stripping spaces around
`+` inside calc() produces `calc(80px+env(...))`, which is invalid — the
browser drops the whole declaration (this silently killed safe-area insets on
notched phones). These tests lock the fix: calc() spacing survives, structural
punctuation is still collapsed.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "minify_css", Path(__file__).resolve().parent.parent / "scripts" / "minify_css.py"
)
minify_css = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(minify_css)
minify = minify_css.minify


def test_calc_plus_keeps_spaces():
    out = minify(".x { bottom: calc(80px + env(safe-area-inset-bottom, 0)); }")
    assert "calc(80px + env(safe-area-inset-bottom,0))" in out
    assert "80px+env" not in out  # the bug


def test_calc_inside_var_and_subtraction_survive():
    out = minify(".y { width: calc(100% - var(--gap)); }")
    assert "calc(100% - var(--gap))" in out


def test_structural_punctuation_still_collapsed():
    out = minify(".a ,  .b  {  color : red ;  }")
    assert ".a,.b{color:red}" in out


def test_child_combinator_collapses_but_adjacent_keeps_space():
    out = minify(".nav > .item { color: red }  .a + .b { color: blue }")
    assert ".nav>.item{color:red}" in out
    assert ".a + .b{color:blue}" in out  # '+' kept spaced → valid selector


def test_comments_stripped():
    assert "/*" not in minify("/* hi */ .x { color: red }")

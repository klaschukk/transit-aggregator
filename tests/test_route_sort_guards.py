"""Source-level guards on the client-side trip sort.

The project has no JS test runner, so these read route-filters.js rather
than executing it. That is a weaker check than a browser test and is
written down as such — but it is strong enough to catch the specific
regression it exists for, and that regression shipped:

`num()` returns 0 for a missing data-price, and the price comparator
subtracted the raw values. So "cheapest" sorted every unpriced departure
to the top — 44 of 74 on Beograd–Novi Sad, the busiest route on the
site. The one sort a visitor clicks to compare money could never answer
the question. The duration comparator one line below already guarded the
same way, which is what makes it a slip rather than a design choice.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

JS = (Path(__file__).resolve().parent.parent
      / "app" / "static" / "js" / "route-filters.js").read_text()


def _comparator(key: str) -> str:
    """The body of the `sortKey === '<key>'` branch."""
    m = re.search(
        r"if \(sortKey === '" + key + r"'\) \{(.*?)\n    \} else",
        JS, re.S,
    ) or re.search(
        r"sortKey === '" + key + r"'\) \{(.*?)\n    \}",
        JS, re.S,
    )
    assert m, f"no {key!r} sort branch in route-filters.js"
    return m.group(1)


@pytest.mark.parametrize("key", ["price", "duration"])
def test_sort_pushes_missing_values_last(key):
    """A trip with no price (or no duration) must sort to the END.

    Zero is not 'cheapest' or 'fastest' — it means we do not know. Both
    comparators must therefore map a falsy value to Infinity before
    subtracting.
    """
    body = _comparator(key)
    assert "Infinity" in body, (
        f"the {key!r} comparator does not guard missing values: a trip "
        f"with no {key} will sort first, which is the opposite of what "
        f"the control promises.\n\n{body.strip()}"
    )
    # Both operands, not just one.
    assert body.count("Infinity") >= 2, (
        f"only one side of the {key!r} comparison is guarded"
    )

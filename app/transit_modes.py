"""Folds city_lines.type's fine-grained categories onto the 4 CSS mode
tokens (--mode-bus/tram/trolley/train, app.css §2) for the mode-chip UI
(_partials/_mode_chip.html). Shared by app/routes/main.py (homepage city
cards) and app/routes/city.py (city hub page) so the fold logic and
display order live in exactly one place.
"""

TYPE_TO_MODE = {
    'bus': 'bus', 'night': 'bus', 'e-bus': 'bus', 'suburban': 'bus',
    'tram': 'tram', 'trolleybus': 'trolley', 'bg-voz': 'train',
}
# Rarer, more distinctive modes lead — a city with trams wants that
# visible, not buried after a big bus count.
MODE_ORDER = ['train', 'tram', 'trolley', 'bus']


def mode_counts(types: list[str]) -> list[dict]:
    """[{'mode': 'tram', 'count': 9}, ...] ordered by MODE_ORDER, unknown
    city_lines.type values fold to 'bus'. Empty list if `types` is empty."""
    counts: dict[str, int] = {}
    for t in types:
        mode = TYPE_TO_MODE.get(t, 'bus')
        counts[mode] = counts.get(mode, 0) + 1
    return [{'mode': m, 'count': counts[m]} for m in MODE_ORDER if counts.get(m)]

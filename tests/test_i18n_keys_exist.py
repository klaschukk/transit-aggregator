"""Every i18n key a template asks for must exist.

Written after a real breakage: 'home.valueprop_free' was deleted along
with the hero strip that used it, but two /vodici/ guide pages also
referenced it. Jinja's `_()` falls back to returning the key itself, so
those pages shipped the literal text "home.valueprop_free" in the cell
where a price belongs — in all three languages, silently, past a green
test suite. Nothing failed, because nothing was checking.

This is a static scan: it catches the break at the moment the key is
removed, not when someone happens to load the page.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.i18n import TRANSLATIONS

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"

# _('key') or _("key") — literal keys only. Computed keys such as
# _('home.hero_sub_' ~ variant) can't be checked statically and are
# skipped by the pattern requiring a closing quote straight after.
KEY_RE = re.compile(r"""_\(\s*(['"])([a-zA-Z0-9_.]+)\1\s*\)""")


def _template_keys() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for tpl in TEMPLATES.rglob("*.html"):
        for _q, key in KEY_RE.findall(tpl.read_text(encoding="utf-8")):
            found.setdefault(key, set()).add(str(tpl.relative_to(TEMPLATES)))
    return found


def test_every_template_key_is_defined():
    missing = {k: v for k, v in _template_keys().items() if k not in TRANSLATIONS}
    assert not missing, "templates reference i18n keys that do not exist:\n" + "\n".join(
        f"  {k}  <- {', '.join(sorted(v))}" for k, v in sorted(missing.items())
    )


@pytest.mark.parametrize("lang", ["sr", "en", "ru"])
def test_every_used_key_has_every_locale(lang):
    """A key present but untranslated falls back the same way."""
    used = _template_keys()
    gaps = [k for k in used if k in TRANSLATIONS and lang not in TRANSLATIONS[k]]
    assert not gaps, f"keys missing a {lang!r} translation: {sorted(gaps)}"

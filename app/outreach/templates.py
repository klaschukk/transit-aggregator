"""Machine-sendable pitch templates.

The human-facing .md files in docs/00_strategy/pitch-templates/ are
guidance; the .tpl files in the same directory are what the sender
actually renders. Each .tpl is plain text with this shape:

    Subject: {...}

    Body line 1
    Body line 2
    ...

The first non-empty line must start with `Subject:`. Everything after
the first blank line is the body. `{name}`-style placeholders are
substituted via str.format_map() with a defaultdict so missing keys
degrade to a visible `[NAME]` hint rather than crashing the render.

Why a second file format alongside the markdown guides: .md files were
written by the researcher for a human to copy-paste, with `[YOUR_NAME]`
hints and commentary. Keeping them untouched means the sender can't
accidentally corrupt the human-readable campaign notes; .tpl files
carry only what actually goes over the wire.
"""
from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = _ROOT / 'docs' / '00_strategy' / 'pitch-templates'


# Category → default template basename. Missing categories fall back to
# `generic`. Language suffix (_en/_sr/_ru) is appended based on the
# target row's `language` column; missing language file → _en fallback.
_CATEGORY_MAP: dict[str, str] = {
    'serbian_tourism':       'tourism_board',
    'serbian_gov':           'tourism_board',
    'serbian_operator':      'operator_reciprocal',
    'travel_blog_global':    'travel_blog',
    'balkan_blog':           'travel_blog',
    'expat_serbia':          'expat_forum',
    'travel_forum':          'expat_forum',
    'russian_diaspora':      'russian_diaspora',
    'broken_link_candidates':'broken_link',
    'youtube_travel':        'travel_blog',
    'facebook_groups':       'expat_forum',
    'wikipedia_edit':        'generic',
}


class _SafeMap(dict):
    """defaultdict variant used for str.format_map(). Missing keys render
    as `[KEY]` so the reviewer spots unfilled slots during --dry-run
    instead of discovering them post-send."""
    def __missing__(self, key):
        return '[' + key.upper() + ']'


def template_for_category(category: str, language: str = 'en') -> str:
    """Return the template basename (without .tpl) appropriate for this
    target's category + language. Falls back to `generic_en` when either
    is unknown."""
    base = _CATEGORY_MAP.get((category or '').strip(), 'generic')
    lang = (language or 'en').strip().lower()
    if lang not in ('en', 'sr', 'ru'):
        lang = 'en'
    name = f'{base}_{lang}'
    if not (TEMPLATES_DIR / f'{name}.tpl').exists():
        # Language fallback: try _en, then generic_en
        name = f'{base}_en'
        if not (TEMPLATES_DIR / f'{name}.tpl').exists():
            name = 'generic_en'
    return name


def available_templates() -> list[str]:
    """List .tpl basenames actually present on disk — used by CLI help
    and by dashboard filters."""
    if not TEMPLATES_DIR.exists():
        return []
    return sorted(p.stem for p in TEMPLATES_DIR.glob('*.tpl'))


def render_template(
    template_name: str,
    placeholders: dict[str, str],
) -> tuple[str, str]:
    """Return (subject, body_text).

    Raises FileNotFoundError if the template can't be found. Missing
    placeholders render as `[KEY]` rather than raising so the reviewer
    can eyeball unfilled slots in --dry-run mode.
    """
    path = TEMPLATES_DIR / f'{template_name}.tpl'
    if not path.exists():
        raise FileNotFoundError(f'template not found: {path}')

    raw = path.read_text(encoding='utf-8')
    lines = raw.splitlines()

    # Skip leading comment lines starting with `#` — lets template files
    # carry human notes up top without them leaking into the email.
    while lines and (lines[0].startswith('#') or not lines[0].strip()):
        lines.pop(0)
    if not lines or not lines[0].startswith('Subject:'):
        raise ValueError(
            f'template {template_name}: first non-comment line must be '
            f'`Subject: ...`, got: {lines[0] if lines else "<empty>"}'
        )

    subject_raw = lines[0][len('Subject:'):].strip()
    lines = lines[1:]
    # Drop one optional blank separator
    while lines and not lines[0].strip():
        lines.pop(0)

    body_raw = '\n'.join(lines).rstrip() + '\n'
    safe = _SafeMap(placeholders or {})
    subject = subject_raw.format_map(safe)
    body = body_raw.format_map(safe)
    return subject, body

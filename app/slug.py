import re

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'd', 'е': 'e', 'ж': 'z',
    'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n',
    'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u',
    'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's',
    'š': 's', 'đ': 'd', 'ž': 'z', 'ć': 'c', 'č': 'c',
}


def normalize_slug(s: str) -> str:
    """Transliterate cyrillic/diacritics to latin and collapse separators.

    Mirrors data/pipelines/build_db.py:city_to_slug so request-time lookups
    match slugs produced at build time.
    """
    out = ''.join(_TRANSLIT.get(ch, ch) for ch in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', out).strip('-')

"""Single source of truth for URL slug generation.

Historically six different slug functions lived across app/ and data/pipelines/
with three divergent transliteration maps — any drift between them leaked
non-ASCII into city_stops.slug and cost ~171 URLs of crawl budget when
Google discovered the mismatch. Every call site must now go through this
module.

The map is a superset of Serbian cyrillic, Latin diacritics (SR/HR/BA),
Romanian (ș/ț), Hungarian (ő/ű), Czech (ě/ř), Russian extras (ё/э/ю/я/ы),
and the Ukrainian є/і/ї.
"""
import re

_TRANSLIT = {
    # Serbian cyrillic (lowercase — we .lower() first)
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'd', 'е': 'e',
    'ж': 'z', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj',
    'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
    'т': 't', 'ћ': 'c', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c',
    'џ': 'dz', 'ш': 's',
    # Russian extras (not in Serbian alphabet but may arrive from search)
    'ё': 'e', 'ы': 'i', 'э': 'e', 'ю': 'ju', 'я': 'ja', 'ъ': '', 'ь': '',
    # Ukrainian extras
    'є': 'e', 'і': 'i', 'ї': 'i', 'ґ': 'g',
    # Latin diacritics (SR/HR/BA)
    'š': 's', 'đ': 'd', 'ž': 'z', 'ć': 'c', 'č': 'c',
    # Romanian
    'ș': 's', 'ț': 't', 'ă': 'a', 'â': 'a', 'î': 'i',
    # Hungarian
    'ő': 'o', 'ű': 'u', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'ö': 'o', 'ü': 'u',
    # Czech/Slovak
    'ě': 'e', 'ř': 'r', 'ů': 'u', 'ý': 'y', 'ň': 'n', 'ť': 't',
    # German (if ever scraped)
    'ß': 'ss', 'ä': 'a',
}


def normalize_slug(s: str) -> str:
    """Transliterate any script/diacritics to an ASCII URL slug.

    Contract: output matches ``^[a-z0-9-]+$`` or is empty. Used by every
    pipeline that writes to public URL columns *and* by request-time
    redirect fallbacks — both sides must agree byte-for-byte or legacy
    URLs return 404.
    """
    out = ''.join(_TRANSLIT.get(ch, ch) for ch in s.lower())
    return re.sub(r'[^a-z0-9]+', '-', out).strip('-')

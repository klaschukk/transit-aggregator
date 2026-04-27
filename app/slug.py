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


# Serbian-standard Cyrillic→Latin (Romanization of Serbian / gajica
# without diacritics). Differs from _TRANSLIT in one load-bearing
# letter: **ђ→dj** (vs ђ→d in normalize_slug).
#
# Why two tables: most DB slugs come from scrapers that already emit
# Serbian Latin, where 'Đorđe Marković' appears as 'djordje-markovic'
# (oslobodjenja, ilije-djuricica, ...). normalize_slug was tuned to
# the conservative ASCII fold (ć→c, ž→z, š→s, ђ→d) for legacy slug
# stability — flipping it to ђ→dj would break every already-stored
# slug that used the old map.
#
# This separate path is used at request time only: when an inbound
# URL has Cyrillic slug parts, the city handlers try _both_ this
# function and normalize_slug, and 301 to whichever matches a real
# row in city_stops / city_lines. ~250 of the GSC-flagged 404s are
# Cyrillic-slug URLs whose Latin canonical contains 'dj' — those
# need this map specifically.
_CYR_SR = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj', 'е': 'e',
    'ж': 'z', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj',
    'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's',
    'т': 't', 'ћ': 'c', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c',
    'џ': 'dz', 'ш': 's',
    # Russian / Bulgarian extras — defensive against URL slugs scraped
    # from regional sources before Serbian-Latin normalisation.
    'щ': 'sc', 'ю': 'ju', 'я': 'ja', 'ё': 'e', 'ы': 'i', 'э': 'e',
    'ъ': '', 'ь': '',
    # Ukrainian / Belarusian
    'є': 'e', 'і': 'i', 'ї': 'i', 'ґ': 'g',
}


def transliterate_cyrillic_serbian(s: str) -> str:
    """Pure Serbian-standard Cyrillic → Latin transliteration.

    Contract:
      - Output preserves case: 'Ђорђе' → 'Djordje', 'ђорђе' → 'djordje'.
      - Already-Latin (incl. accented Latin like ć/š/ž/đ) passes through
        unchanged — this function does NOT slugify and does NOT fold
        diacritics. Use normalize_slug for that.
      - Empty in → empty out.
      - Mixed Cyrillic + Latin + ASCII works letter-by-letter.

    Caller is responsible for slugifying the output if needed
    (lowercase + replace non-[a-z0-9]+ with dash). The pure-string
    output exists so callers can also build human-readable display
    text from a Cyrillic source.
    """
    if not s:
        return s
    out: list[str] = []
    for ch in s:
        # Lowercase lookup
        lo = _CYR_SR.get(ch)
        if lo is not None:
            out.append(lo)
            continue
        # Uppercase lookup: capitalise the Latin output's first char.
        # 'Ђ' → 'Dj', 'Љ' → 'Lj', 'Џ' → 'Dz' (Serbian convention is
        # title case for digraphs, NOT all-caps; 'DJORDJE' is not how
        # 'Ђорђе' romanises).
        lower = ch.lower()
        if lower != ch:
            mapped = _CYR_SR.get(lower)
            if mapped is not None:
                out.append(mapped[:1].upper() + mapped[1:] if mapped else '')
                continue
        out.append(ch)
    return ''.join(out)


def slugify_serbian(s: str) -> str:
    """Build a URL slug via Serbian-standard transliteration.

    Equivalent to ``normalize_slug`` but uses the ђ→dj map. Any caller
    that wants the request-time canonical slug for an inbound Cyrillic
    URL goes through here; pipeline-side slug generation stays on
    ``normalize_slug`` for backwards compatibility with already-stored
    DB rows.
    """
    out = transliterate_cyrillic_serbian(s).lower()
    # Fold remaining Latin diacritics through the existing map so a
    # mixed-script slug ('Đorđe-šabac') still produces clean ASCII.
    out = ''.join(_TRANSLIT.get(ch, ch) for ch in out)
    return re.sub(r'[^a-z0-9]+', '-', out).strip('-')

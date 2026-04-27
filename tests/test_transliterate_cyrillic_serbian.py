"""Unit tests for app.slug.transliterate_cyrillic_serbian (pure function).

The function is the request-time companion to normalize_slug for the
GSC-flagged cyrillic 404s. Where normalize_slug folds ђ→d (kept for
backwards compatibility with already-stored DB slugs), this function
follows the Romanization-of-Serbian standard (ђ→dj) so inbound URLs
like /stajaliste/ђурђева/ can find the canonical row 'djurdjeva' that
upstream scrapers actually wrote to city_stops.

Tests are pure-string / pure-Python — no Flask client, no DB —
because the function is the building block both city handlers depend
on. If this contract drifts, every Cyrillic redirect breaks silently.
"""
import pytest

from app.slug import (
    normalize_slug,
    slugify_serbian,
    transliterate_cyrillic_serbian,
)


# ── Case-preserving transliteration ────────────────────────────────────


def test_lowercase_word():
    """'ђорђе' is the canonical example — the letter ђ is the only
    one whose Serbian-standard romanisation differs from the
    conservative ASCII fold (dj vs d)."""
    assert transliterate_cyrillic_serbian("ђорђе") == "djordje"


def test_uppercase_word_title_cases_digraph():
    """Serbian convention is to title-case digraphs ('Djordje', not
    'DJordje' or 'DJORDJE'). The function preserves the original
    case but only capitalises the FIRST letter of multi-letter
    output."""
    assert transliterate_cyrillic_serbian("Ђорђе") == "Djordje"
    assert transliterate_cyrillic_serbian("Љубовија") == "Ljubovija"
    assert transliterate_cyrillic_serbian("Џамија") == "Dzamija"
    assert transliterate_cyrillic_serbian("Његовош") == "Njegovos"


def test_digraphs_lj_nj_dz_dj():
    """The four multi-letter outputs that distinguish Serbian Latin
    from a literal 1:1 cyrillic→latin map. dž→dz mirrors gajica's џ
    → dž with diacritic stripped; the others are the standard."""
    # Cyrillic source → Serbian-Latin without diacritics
    assert transliterate_cyrillic_serbian("љ") == "lj"
    assert transliterate_cyrillic_serbian("њ") == "nj"
    assert transliterate_cyrillic_serbian("џ") == "dz"  # gajica dž → ASCII dz
    assert transliterate_cyrillic_serbian("ђ") == "dj"  # gajica đ → ASCII dj


# ── Passthrough ────────────────────────────────────────────────────────


def test_already_latin_passthrough_unchanged():
    """Already-Latin slugs (the canonical form in DB) must pass through
    untouched — including diacritic-bearing Latin like ć/š/ž/đ.
    The slugify pass (slugify_serbian) is what folds those; this pure
    transliterator only handles Cyrillic."""
    assert transliterate_cyrillic_serbian("sava-centar") == "sava-centar"
    assert transliterate_cyrillic_serbian("Đorđe") == "Đorđe"
    assert transliterate_cyrillic_serbian("Šabac") == "Šabac"


def test_empty_input():
    """Defensive: empty strings flow through with no IndexError on the
    `cap[0].upper() + cap[1:]` line."""
    assert transliterate_cyrillic_serbian("") == ""


def test_mixed_script():
    """Real GSC-flagged URLs sometimes mix Cyrillic + ASCII (numbered
    lines like 'линија-2а' where digits and dashes interleave)."""
    assert transliterate_cyrillic_serbian("линија-2а") == "linija-2a"
    assert transliterate_cyrillic_serbian("Линија 102") == "Linija 102"


def test_full_alphabet_lowercase():
    """Every Serbian Cyrillic letter, in alphabetical order, in one
    string — guards against accidental table omissions."""
    src = "абвгдђежзијклљмнњопрстћуфхцчџш"
    expected = "abvgddjezzijklljmnnjoprstcufhccdzs"
    assert transliterate_cyrillic_serbian(src) == expected


# ── Slug-shape variant (the function the handler actually calls) ───────


def test_slugify_serbian_lowercases_and_dashes():
    """slugify_serbian is the URL-slug builder that wraps the pure
    transliterator with normalize_slug-style lowercase + dash
    collapse. The handler calls this one; the pure transliterator
    exists for symmetry with normalize_slug and isolated testing."""
    assert slugify_serbian("Бул. Ослобођења") == "bul-oslobodjenja"
    assert slugify_serbian("Ђурђев Дан") == "djurdjev-dan"


def test_slugify_serbian_diverges_from_normalize_slug_on_dj():
    """The whole reason this function exists: ђ→dj in the inbound
    canonicalisation, vs ђ→d in normalize_slug. Both functions are
    correct — they're tuned for opposite ends of the slug pipeline.
    A regression that collapses them into one map costs ~250 URLs
    of crawl budget."""
    assert slugify_serbian("ђорђе") == "djordje"
    assert normalize_slug("ђорђе") == "dorde"
    assert slugify_serbian("ђорђе") != normalize_slug("ђорђе")

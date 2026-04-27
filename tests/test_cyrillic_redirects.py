"""Cyrillic → Latin redirect tests for /gradski/<city>/{stajaliste,linija}/.

Background: a legacy migration left Cyrillic stop and line slugs in
Google's index; the current canonical is Latin transliteration. Two
behaviours are load-bearing here:

  1. URL-encoded Cyrillic that DOES correspond to a current Latin slug
     in the DB → 301 to the canonical URL. Recovers crawl budget.
  2. URL-encoded Cyrillic with NO Latin counterpart (stop deleted
     upstream) → 410 Gone, not a redirect-to-404 chain.

The transliteration map lives in app/slug.py:_TRANSLIT and is shared
between the build-time slug invariant check and request-time
canonicalisation; these tests exercise the full Serbian Cyrillic
alphabet plus a few cross-script edge cases (Romanian ț, Latin
diacritic ć/š/ž) that the same function covers.
"""
import pytest

from app.slug import normalize_slug


# ── Pure transliteration: per-letter contract ──────────────────────────


@pytest.mark.parametrize(
    "cyrillic,expected_latin",
    [
        # Single-char mappings, lowercase (the function .lower()s first
        # so uppercase paths route through the same table).
        ("а", "a"),       # vowel a
        ("б", "b"),       # b
        ("в", "v"),
        ("г", "g"),
        ("д", "d"),
        ("ђ", "d"),       # serbian-specific (đ → d in our map)
        ("ж", "z"),
        ("з", "z"),
        ("ј", "j"),
        ("љ", "lj"),      # multi-char output
        ("њ", "nj"),
        ("ћ", "c"),       # serbian-specific (ć → c)
        ("у", "u"),
        ("х", "h"),
        ("ц", "c"),
        ("ч", "c"),       # cyrillic ч (also c in our map)
        ("џ", "dz"),      # multi-char
        ("ш", "s"),
    ],
)
def test_cyrillic_letter_transliteration(cyrillic, expected_latin):
    """Every Serbian Cyrillic letter maps to its expected Latin output.
    A regression here would silently cost crawl budget on legacy URLs."""
    assert normalize_slug(cyrillic) == expected_latin


def test_cyrillic_word_transliteration_known_stop():
    """Realistic stop name: 'Сава Центар' → 'sava-centar' (Beograd's
    landmark conference hall, served by multiple bus lines)."""
    assert normalize_slug("Сава Центар") == "sava-centar"


def test_cyrillic_word_transliteration_with_cyrillic_apostrophe():
    """'Роспи Ћуприја' (Rospi Ćuprija) — both ћ→c and the space-to-dash
    rule fire in one pass."""
    assert normalize_slug("Роспи Ћуприја") == "rospi-cuprija"


def test_cyrillic_with_dz_digraph():
    """'Џамија' (mosque) — џ is the only digraph that produces two
    Latin characters from one Cyrillic letter."""
    assert normalize_slug("Џамија") == "dzamija"


def test_cyrillic_lj_nj_digraphs():
    """Љ and Њ are the other two digraphs the Serbian alphabet has."""
    assert normalize_slug("Љубовија") == "ljubovija"
    assert normalize_slug("Његовош") == "njegovos"


def test_latin_diacritics_also_normalise():
    """The same map handles Latin diacritics — 'Cvetni-Trg' from a
    scraper that didn't strip ć/š would still produce a clean slug."""
    assert normalize_slug("Žagubica") == "zagubica"
    assert normalize_slug("Čačak") == "cacak"
    assert normalize_slug("Šabac") == "sabac"


def test_already_ascii_passes_through_unchanged():
    """A clean ASCII slug (the canonical form) is idempotent."""
    assert normalize_slug("sava-centar") == "sava-centar"
    assert normalize_slug("linija-2a") == "linija-2a"


# ── HTTP redirects: existence-gated, no 301→404 chains ─────────────────


def test_cyrillic_stop_redirects_when_latin_canonical_exists(client):
    """Hitting a Cyrillic stop URL should 301 to its Latin canonical
    when the canonical row exists in city_stops. 'Сава Центар' is one
    of the GSC-flagged URLs and 'sava-centar' is in the DB."""
    resp = client.get(
        "/gradski/beograd/stajaliste/сава-центар/",
        follow_redirects=False,
    )
    assert resp.status_code == 301
    assert "/gradski/beograd/stajaliste/sava-centar/" in resp.headers["Location"]


def test_cyrillic_stop_410s_when_latin_canonical_missing(client):
    """A Cyrillic slug that transliterates to a slug not present in
    city_stops (deleted upstream, scraper artefact, etc.) should 410
    Gone — NOT 301 into a 404. 'Перлово Брдо' transliterates to
    'perlovo-brdo', which is not in city_stops as of this fix."""
    resp = client.get(
        "/gradski/beograd/stajaliste/перлово-брдо/",
        follow_redirects=False,
    )
    # Pre-fix: 301 → /perlovo-brdo/ → 404 (chain). Post-fix: 410.
    assert resp.status_code == 410


def test_cyrillic_line_redirects_when_latin_canonical_exists(client):
    """Same contract on /linija/. 'линија-15' → 'linija-15' which
    exists, so 301."""
    resp = client.get(
        "/gradski/beograd/linija/линија-15/",
        follow_redirects=False,
    )
    assert resp.status_code == 301
    assert "/gradski/beograd/linija/linija-15/" in resp.headers["Location"]


def test_ascii_misspelling_keeps_404(client):
    """Pure ASCII slugs that simply don't exist (typos) stay 404 — the
    Cyrillic logic must not affect this code path."""
    resp = client.get(
        "/gradski/beograd/stajaliste/this-stop-definitely-does-not-exist/",
        follow_redirects=False,
    )
    assert resp.status_code == 404

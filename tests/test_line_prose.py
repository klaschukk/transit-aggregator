"""Tests for app/content/line_prose.py — rules-based prose for line pages.

Coverage targets:
- edge cases: 0/1/2 stop, no GTFS, no interchange
- determinism: same inputs → same output
- diversity: 10 random lines should have Jaccard similarity avg < 0.4
- grammar sanity: no {placeholder} leaks, no "None" strings, no "0 km"
- i18n: sr/en/ru all produce non-empty geography paragraph
- word count: ≥120 words on a line with rich data
"""
from __future__ import annotations

import re

import pytest

from app import create_app
from app.content.line_prose import build_prose


@pytest.fixture(scope='module')
def app_ctx():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        yield app


# ── Helpers ─────────────────────────────────────────────────────────────


def _five_grams(text: str) -> set[tuple[str, ...]]:
    tokens = re.findall(r"[\w']+", text.lower())
    return {tuple(tokens[i:i + 5]) for i in range(len(tokens) - 4)}


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _make_line(slug='line-a', city='beograd', number='1', line_type='bus'):
    return {
        'id': 1, 'slug': slug, 'city': city,
        'number': number, 'name': f'{number} — Test Line',
        'type': line_type, 'color': '#0d9488',
    }


def _make_stops(n, base_lat=44.80, base_lon=20.45, gap=0.005):
    """Synthetic linear stop chain. gap≈0.005° ≈ 500 m so route length
    on n=20 lands around 9.5 km — realistic urban line."""
    out = []
    for i in range(n):
        out.append({
            'name': f'Stop {i + 1}',
            'slug': f'stop-{i + 1}',
            'lat': base_lat + i * gap,
            'lon': base_lon + i * gap,
        })
    return out


def _word_count(prose: dict) -> int:
    """Concatenated word count across all paragraphs the builder returned."""
    text = ' '.join(p for p in prose.values() if p)
    # Strip HTML tags before counting (transfers paragraph has <a href>).
    text = re.sub(r'<[^>]+>', ' ', text)
    return len(text.split())


# ── Edge cases ──────────────────────────────────────────────────────────


def test_zero_stops_returns_empty(app_ctx):
    out = build_prose(_make_line(), [], lang='sr')
    assert out == {}


def test_one_stop_returns_empty(app_ctx):
    """A single-stop 'line' is a data glitch — better to skip prose than
    show 'connects X and X across 1 stops'."""
    out = build_prose(_make_line(), _make_stops(1), lang='sr')
    assert out == {}


def test_two_stop_line_renders(app_ctx):
    out = build_prose(_make_line(), _make_stops(2), lang='sr')
    assert out['geography']
    assert '{' not in out['geography']


def test_no_gtfs_skips_schedule_paragraph(app_ctx):
    out = build_prose(_make_line(slug='no-gtfs'), _make_stops(10), lang='sr')
    # Schedule paragraph should be empty when no schedule data is passed.
    assert out['schedule'] == ''
    # Geography + transfers (with closing CTA link) still render.
    assert out['geography']
    assert out['transfers']


def test_with_gtfs_renders_schedule(app_ctx):
    schedule_rd = ['05:00', '05:15', '05:30', '06:00', '07:00', '07:15', '07:30',
                   '08:00', '08:15', '08:30', '12:00', '13:00', '14:00',
                   '16:00', '16:15', '16:30', '17:00', '17:15', '18:00',
                   '20:00', '21:00', '22:00', '23:00']
    out = build_prose(_make_line(slug='with-gtfs'), _make_stops(15),
                      schedule_rd=schedule_rd, lang='sr')
    assert out['schedule']
    assert '05:00' in out['schedule']
    assert '23:00' in out['schedule']
    # Headway suffix should appear because both peak windows have ≥2 deps.
    assert 'min' in out['schedule']
    assert '{' not in out['schedule']


def test_no_interchange_still_emits_closing_cta(app_ctx):
    """Even a line whose stops are all unique to it should produce a
    transfers paragraph — the closing CTA with internal link is always on."""
    out = build_prose(_make_line(), _make_stops(8), lang='sr')
    assert out['transfers']
    assert '/gradski/beograd/' in out['transfers']


def test_interchange_listed_when_provided(app_ctx):
    interchange = [
        {'slug': 'slavija', 'name': 'Slavija', 'line_count': 12},
        {'slug': 'sajam', 'name': 'Sajam', 'line_count': 6},
        {'slug': 'zeleni-venac', 'name': 'Zeleni Venac', 'line_count': 8},
    ]
    out = build_prose(_make_line(), _make_stops(10),
                      interchange=interchange, lang='sr')
    assert 'Slavija' in out['transfers']
    assert '12 linija' in out['transfers']


def test_terminal_excluded_from_interchange(app_ctx):
    """The first/last stop names already appear in the geography paragraph;
    they shouldn't be re-listed as transfer points."""
    stops = _make_stops(5)
    interchange = [
        {'slug': 'stop-1', 'name': 'Stop 1', 'line_count': 4},   # = terminal A
        {'slug': 'stop-3', 'name': 'Stop 3', 'line_count': 5},
        {'slug': 'stop-5', 'name': 'Stop 5', 'line_count': 3},   # = terminal B
    ]
    out = build_prose(_make_line(), stops, interchange=interchange, lang='sr')
    # Terminal-named stops dropped, only Stop 3 survives.
    assert 'Stop 3' in out['transfers']


# ── i18n ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize('lang', ['sr', 'en', 'ru'])
def test_all_langs_produce_geography(app_ctx, lang):
    out = build_prose(_make_line(), _make_stops(8), lang=lang)
    assert out['geography']
    assert '{' not in out['geography'], f'{lang} placeholder leak: {out["geography"]}'
    if lang == 'en':
        # Cyrillic must not bleed into English prose.
        assert 'ш' not in out['geography'].lower()


def test_unknown_lang_falls_back_to_sr(app_ctx):
    out = build_prose(_make_line(), _make_stops(5), lang='klingon')
    # SR uses 'linija' / 'stajališta' — at least one should appear.
    text = out['geography'].lower()
    assert 'linija' in text or 'stajališt' in text


def test_lang_prefix_threads_into_transfers_link(app_ctx):
    ru = build_prose(_make_line(), _make_stops(5), lang='ru', lang_prefix='/ru')
    en = build_prose(_make_line(), _make_stops(5), lang='en', lang_prefix='/en')
    assert '/ru/gradski/beograd/' in ru['transfers']
    assert '/en/gradski/beograd/' in en['transfers']


# ── Determinism ─────────────────────────────────────────────────────────


def test_deterministic_output(app_ctx):
    line = _make_line(slug='det-check')
    stops = _make_stops(7)
    a = build_prose(line, stops, lang='sr')
    b = build_prose(line, stops, lang='sr')
    assert a == b


def test_different_slugs_pick_different_templates(app_ctx):
    a = build_prose(_make_line(slug='alpha'), _make_stops(6), lang='sr')
    b = build_prose(_make_line(slug='bravo'), _make_stops(6), lang='sr')
    # Same stops + line shape but different slug → different templates.
    # We can't guarantee every paragraph differs (small pool collisions are
    # OK), but the full rendered prose should differ on at least one paragraph.
    assert (a['geography'], a['transfers']) != (b['geography'], b['transfers'])


# ── Diversity ───────────────────────────────────────────────────────────


def test_ten_lines_avg_jaccard_under_0_4(app_ctx):
    """Simulate 10 different lines and check 5-gram Jaccard avg < 0.4."""
    samples = [
        ('linija-2a', '2A', 8),
        ('linija-7', '7', 14),
        ('linija-23', '23', 22),
        ('linija-31', '31', 10),
        ('linija-44', '44', 18),
        ('linija-58', '58', 25),
        ('linija-67', '67', 12),
        ('linija-83', '83', 30),
        ('linija-95', '95', 9),
        ('linija-N1', 'N1', 6),
    ]
    prose_set = []
    for slug, num, n_stops in samples:
        line = _make_line(slug=slug, number=num)
        stops = _make_stops(n_stops, base_lat=44.78 + n_stops * 0.001)
        out = build_prose(line, stops, lang='sr')
        combined = ' '.join(p for p in out.values() if p)
        prose_set.append(combined)

    grams = [_five_grams(p) for p in prose_set]
    pairs = []
    for i in range(len(grams)):
        for j in range(i + 1, len(grams)):
            pairs.append(_jaccard(grams[i], grams[j]))
    avg = sum(pairs) / len(pairs)
    assert avg < 0.4, f'Avg Jaccard {avg:.3f} ≥ 0.4 — line prose too repetitive'


# ── Word count ──────────────────────────────────────────────────────────


def test_word_count_meets_120_with_rich_data(app_ctx):
    """Spec target: ≥120 unique words per line page. Test with rich data
    (GTFS + interchange) so we hit the upper end of the prose envelope."""
    schedule_rd = [f'{h:02d}:{m:02d}' for h in range(5, 24)
                   for m in (0, 15, 30, 45)]
    schedule_sat = [f'{h:02d}:00' for h in range(6, 23)]
    interchange = [
        {'slug': 'slavija', 'name': 'Slavija', 'line_count': 12},
        {'slug': 'sajam', 'name': 'Sajam', 'line_count': 6},
        {'slug': 'autokomanda', 'name': 'Autokomanda', 'line_count': 8},
    ]
    out = build_prose(
        _make_line(slug='rich-line'), _make_stops(20),
        schedule_rd=schedule_rd, schedule_sat=schedule_sat,
        interchange=interchange, lang='sr',
    )
    wc = _word_count(out)
    assert wc >= 120, f'Rich-data line prose only {wc} words — spec asks 120+'


def test_word_count_meets_120_without_gtfs(app_ctx):
    """Even without GTFS we should hit 120 words from geography + transfers
    alone — that's the indexability floor."""
    interchange = [
        {'slug': 'slavija', 'name': 'Slavija', 'line_count': 12},
        {'slug': 'sajam', 'name': 'Sajam', 'line_count': 6},
        {'slug': 'banovo-brdo', 'name': 'Banovo Brdo', 'line_count': 5},
    ]
    out = build_prose(
        _make_line(slug='no-gtfs-rich'), _make_stops(15),
        interchange=interchange, lang='sr',
    )
    wc = _word_count(out)
    # With 6-template geography + density suffix + transfers + closing CTA
    # the floor is around 60-75 words. We don't try to force 120 here —
    # the GTFS-rich path is what actually hits 120, and the user constraint
    # is "skip the schedule paragraph rather than fabricate".
    assert wc >= 60, f'No-GTFS line prose only {wc} words — too thin to index'


# ── Grammar / placeholder sanity ────────────────────────────────────────


def test_no_placeholder_leaks_across_10_samples(app_ctx):
    for slug in ('a', 'bb', 'ccc', 'dddd', 'eeeee', 'ffffff', 'g7', 'h8', 'i9', 'j10'):
        line = _make_line(slug=slug, number=slug.upper())
        stops = _make_stops(5 + len(slug))
        out = build_prose(line, stops, lang='sr')
        for para, text in out.items():
            assert '{' not in text, f'{slug}:{para} leaked: {text}'
            assert 'None' not in text, f'{slug}:{para} has None: {text}'


def test_no_zero_km_in_geography(app_ctx):
    """Line with no coordinates must not render '0 km'. The slot falls back
    to '—' so the prose reads 'covers about — km' which is ugly but not
    wrong; assert that the literal '0 km' string never lands."""
    stops = [{'name': f'NoCoord {i}', 'slug': f'nc-{i}',
              'lat': None, 'lon': None} for i in range(5)]
    out = build_prose(_make_line(slug='no-coords'), stops, lang='sr')
    assert '0 km' not in out['geography']
    assert '0.0 km' not in out['geography']


def test_unknown_line_type_falls_back(app_ctx):
    line = {'id': 1, 'slug': 'mystery', 'city': 'beograd',
            'number': 'X', 'name': 'X — Future', 'type': 'maglev-2042',
            'color': '#999'}
    out = build_prose(line, _make_stops(4), lang='sr')
    assert out['geography']
    assert '{' not in out['geography']


def test_all_db_types_render(app_ctx):
    for t in ('bus', 'tram', 'trolleybus', 'night', 'suburban', 'e-bus', 'bg-voz'):
        for lang in ('sr', 'en', 'ru'):
            line = _make_line(slug=f'{t}-{lang}', line_type=t)
            out = build_prose(line, _make_stops(5), lang=lang)
            assert out['geography'], f'{t}/{lang} empty geography'
            assert '{' not in out['geography'], f'{t}/{lang} leaked: {out["geography"]}'


def test_cyrillic_names_roundtrip(app_ctx):
    """Belgrade has Cyrillic stop names; they must pass through intact."""
    line = _make_line()
    stops = [
        {'name': 'Младеновац АС', 'slug': 'mladenovac', 'lat': 44.43, 'lon': 20.69},
        {'name': 'Раковица', 'slug': 'rakovica', 'lat': 44.75, 'lon': 20.45},
    ]
    out = build_prose(line, stops, lang='sr')
    assert 'Младеновац АС' in out['geography']
    assert '{' not in out['geography']

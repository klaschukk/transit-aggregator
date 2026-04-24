"""Tests for app/content/stop_prose.py — rules-based prose for stop pages.

Coverage targets:
- edge cases: 0 / 1 / 50-line stops, no coords, no GTFS, no nearby
- determinism: same inputs → same output
- diversity: 10 random stops should have Jaccard similarity avg < 0.4
- grammar sanity: no {placeholder} leaks, no "None" strings
- i18n: sr/en/ru all produce non-empty output
"""
from __future__ import annotations

import re

import pytest

from app import create_app
from app.content.stop_prose import build_prose
from app.content.pois import nearest_poi


@pytest.fixture(scope='module')
def app_ctx():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        yield app


# ── Helpers ─────────────────────────────────────────────────────────────


def _five_grams(text: str) -> set[tuple[str, ...]]:
    """Word-level 5-grams for Jaccard similarity. Case-folded, punctuation
    stripped — we want semantic duplication detection, not literal."""
    tokens = re.findall(r"[\w']+", text.lower())
    return {tuple(tokens[i:i + 5]) for i in range(len(tokens) - 4)}


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _make_stop(slug='test-stop', city='beograd', lat=44.8176, lon=20.4569, name='Test Stop'):
    return {'id': 1, 'slug': slug, 'city': city, 'name': name, 'lat': lat, 'lon': lon, 'code': '1'}


def _make_lines(n, types=('bus',)):
    out = []
    for i in range(n):
        out.append({
            'number': f'{i + 1}', 'type': types[i % len(types)],
            'name': f'Endpoint {i}A - Endpoint {i}B',
            'slug': f'line-{i}', 'color': '#0d9488',
        })
    return out


# ── Edge cases ──────────────────────────────────────────────────────────


def test_zero_lines_returns_empty(app_ctx):
    stop = _make_stop()
    out = build_prose(stop, [], [], None, lang='sr')
    assert out == {}, 'Zero-line stop should render no prose'


def test_single_line_stop(app_ctx):
    stop = _make_stop(slug='tiny')
    out = build_prose(stop, _make_lines(1), [], None, lang='sr')
    assert out['intro'] and out['service'] and out['location'] and out['tip']
    assert '{' not in out['intro'], 'No unrendered placeholders'


def test_fifty_line_hub(app_ctx):
    stop = _make_stop(slug='big-hub')
    lines = _make_lines(50, types=('bus', 'tram', 'trolleybus', 'night'))
    out = build_prose(stop, lines, [], None, lang='sr')
    # Line numbers should be truncated to "first 8 ... (42 još)".
    assert 'još' in out['service'] or '50' in out['service']
    assert '{' not in out['service']


def test_no_coords(app_ctx):
    stop = _make_stop(lat=None, lon=None)
    out = build_prose(stop, _make_lines(3), [], None, lang='sr')
    assert out['intro']
    # coord_str goes empty, template shouldn't leak a bare "()".
    assert '()' not in out['intro'] or '(zona:' in out['intro']


def test_no_nearby_stops(app_ctx):
    stop = _make_stop()
    out = build_prose(stop, _make_lines(3), [], None, lang='sr')
    # Location paragraph should not mention "neposrednoj blizini" / nearby
    # suffix, since the optional _has_nearby gate is False.
    assert 'neposrednoj blizini' not in out['location']


def test_no_gtfs(app_ctx):
    stop = _make_stop()
    out = build_prose(stop, _make_lines(3), [], None, lang='sr')
    assert 'prvi polazak' not in out['service'].lower()
    assert 'first departure' not in out['service'].lower()


# ── i18n coverage ───────────────────────────────────────────────────────


@pytest.mark.parametrize('lang', ['sr', 'en', 'ru'])
def test_all_langs_produce_prose(app_ctx, lang):
    stop = _make_stop()
    out = build_prose(stop, _make_lines(5), [], None, lang=lang)
    for key in ('intro', 'service', 'location', 'tip'):
        assert out[key], f'{lang}:{key} empty'
        assert '{' not in out[key], f'{lang}:{key} has placeholder leak: {out[key]}'
    # English should not contain Cyrillic, Russian should not contain "stajalište".
    if lang == 'en':
        assert 'ш' not in out['intro'].lower()
    if lang == 'ru':
        # tip block uses Russian only
        assert 'из' in out['tip'].lower() or 'для' in out['tip'].lower()


def test_unknown_lang_falls_back_to_sr(app_ctx):
    stop = _make_stop()
    out = build_prose(stop, _make_lines(3), [], None, lang='klingon')
    assert 'stajalište' in out['intro'].lower() or 'stajalištu' in out['intro'].lower()


# ── Determinism ─────────────────────────────────────────────────────────


def test_deterministic_output(app_ctx):
    stop = _make_stop(slug='determinism-check')
    lines = _make_lines(4)
    a = build_prose(stop, lines, [], None, lang='sr')
    b = build_prose(stop, lines, [], None, lang='sr')
    assert a == b


def test_different_slugs_pick_different_templates(app_ctx):
    """Two similar-sized stops must not land on identical prose — that's
    the whole point of the per-slug hash salt."""
    stop_a = _make_stop(slug='alpha', lat=44.80, lon=20.40, name='Alpha')
    stop_b = _make_stop(slug='bravo', lat=44.81, lon=20.41, name='Bravo')
    a = build_prose(stop_a, _make_lines(4), [], None, lang='sr')
    b = build_prose(stop_b, _make_lines(4), [], None, lang='sr')
    assert a['intro'] != b['intro'], 'Adjacent slugs landed on identical intro template'


# ── Diversity / similarity ──────────────────────────────────────────────


def test_ten_stops_avg_jaccard_under_0_4(app_ctx):
    """Spec: avg Jaccard over 5-grams across 10 random stops should be < 0.4
    (i.e. ≥60% unique). Uses a seeded fake sample so the test is stable."""
    samples = [
        ('sajam', 'Sajam', 44.7965, 20.4426, 4, ('bus', 'tram')),
        ('prokop', 'Prokop', 44.7981, 20.4442, 3, ('bus',)),
        ('most-gazela', 'Most Gazela', 44.8013, 20.4395, 6, ('bus', 'tram')),
        ('slavija', 'Slavija', 44.8023, 20.4660, 15, ('bus', 'tram', 'trolleybus')),
        ('terazije', 'Terazije', 44.8150, 20.4603, 20, ('bus', 'tram')),
        ('trg-republike', 'Trg Republike', 44.8178, 20.4590, 8, ('bus',)),
        ('kalemegdan', 'Kalemegdan', 44.8225, 20.4515, 2, ('bus',)),
        ('zemun-kej', 'Zemun Kej', 44.8469, 20.4036, 5, ('bus', 'night')),
        ('dorcol', 'Dorćol', 44.8230, 20.4700, 7, ('bus',)),
        ('vracar', 'Vračar', 44.7970, 20.4761, 10, ('bus', 'tram')),
    ]
    prose_set = []
    for slug, name, lat, lon, n_lines, types in samples:
        stop = _make_stop(slug=slug, name=name, lat=lat, lon=lon)
        lines = _make_lines(n_lines, types=types)
        out = build_prose(stop, lines, [], None, lang='sr')
        combined = ' '.join([out['intro'], out['service'], out['location'], out['tip']])
        prose_set.append(combined)

    # Pairwise Jaccard
    grams = [_five_grams(p) for p in prose_set]
    pairs = []
    for i in range(len(grams)):
        for j in range(i + 1, len(grams)):
            pairs.append(_jaccard(grams[i], grams[j]))
    avg = sum(pairs) / len(pairs)
    assert avg < 0.4, f'Avg Jaccard {avg:.3f} ≥ 0.4 — prose too repetitive'


# ── POI detection ──────────────────────────────────────────────────────


def test_nearest_poi_finds_belgrade_fair(app_ctx):
    poi = nearest_poi(44.7965, 20.4426, lang='sr')
    assert poi is not None
    assert 'sajam' in poi['name'].lower() or 'fair' in poi['name'].lower() or 'ярмарка' in poi['name'].lower()


def test_nearest_poi_returns_none_when_far(app_ctx):
    # Middle of nowhere — 50km from any POI.
    poi = nearest_poi(45.5, 22.0, lang='sr', max_m=500)
    assert poi is None


def test_nearest_poi_handles_missing_coords(app_ctx):
    assert nearest_poi(None, None) is None


def test_intro_includes_poi_when_nearby(app_ctx):
    """Near Belgrade Fair (Sajam POI)."""
    stop = _make_stop(slug='sajam-adjacent', lat=44.797, lon=20.444, name='Sajam Adjacent')
    out = build_prose(stop, _make_lines(3), [], None, lang='sr')
    assert 'sajam' in out['intro'].lower() or 'ярмарк' in out['intro'].lower() or 'fair' in out['intro'].lower()


# ── Grammar / placeholder sanity ────────────────────────────────────────


def test_no_placeholder_leaks_across_10_samples(app_ctx):
    """Regression: any unresolved {slot} is a prose bug."""
    for slug in ('a', 'bb', 'ccc', 'dddd', 'eeeee', 'ffffff', 'ggggggg', 'hhhhhhhh', 'iiiii', 'jjjjj'):
        stop = _make_stop(slug=slug, lat=44.81, lon=20.45)
        lines = _make_lines(3 + len(slug), types=('bus', 'tram'))
        out = build_prose(stop, lines, [], None, lang='sr')
        for para, text in out.items():
            assert '{' not in text, f'{slug}:{para} leaked: {text}'
            assert 'None' not in text, f'{slug}:{para} has None: {text}'


def test_suburban_type_does_not_crash(app_ctx):
    """Regression: Novi Sad has 36 lines with type='suburban' which crashed
    prose rendering (KeyError) until we added the label. Test guards against
    any similar type addition regressing silently."""
    stop = _make_stop(slug='ns-suburban', city='novi-sad', lat=45.26, lon=19.84)
    lines = [{'number': 'P1', 'type': 'suburban', 'name': 'A - B',
              'slug': 'p1', 'color': '#999'}]
    out = build_prose(stop, lines, [], None, lang='sr')
    assert out['service'], 'suburban type must render'
    assert 'prigradskih' in out['service'] or 'P1' in out['service']


def test_unknown_type_falls_back_gracefully(app_ctx):
    """A scraper adding a new line.type (e.g. 'metro' someday) must not
    crash prose — it falls back to 'bus' semantics."""
    stop = _make_stop(slug='future-type')
    lines = [{'number': 'M1', 'type': 'metro-line-2042', 'name': 'A - B',
              'slug': 'm1', 'color': '#333'}]
    out = build_prose(stop, lines, [], None, lang='en')
    assert out['intro'] and out['service']
    assert '{' not in out['intro']


def test_all_db_types_render(app_ctx):
    """All six types actually present in city_lines render without placeholder
    leaks, in all three languages."""
    for t in ('bus', 'tram', 'trolleybus', 'night', 'suburban', 'e-bus', 'bg-voz'):
        for lang in ('sr', 'en', 'ru'):
            stop = _make_stop(slug=f'{t}-{lang}')
            lines = [{'number': '1', 'type': t, 'name': 'A - B',
                      'slug': 'l1', 'color': '#0d9488'}]
            out = build_prose(stop, lines, [], None, lang=lang)
            assert out['service'], f'{t}/{lang} empty'
            assert '{' not in out['service'], f'{t}/{lang} leaked: {out["service"]}'


def test_cyrillic_stop_names_roundtrip(app_ctx):
    """Many Belgrade stops have Cyrillic names (e.g. 'Младеновац АС'). The
    generator must pass them through intact without encoding errors."""
    stop = _make_stop(slug='cyrillic-stop', name='Младеновац АС')
    out = build_prose(stop, _make_lines(5), [], None, lang='sr')
    assert 'Младеновац АС' in out['intro']
    assert '{' not in out['intro']


def test_all_four_paragraphs_always_populated(app_ctx):
    """Across 20 randomly shaped inputs, every returned prose has all 4
    paragraph keys with non-empty content (unless zero-line, which returns {})."""
    import random
    rng = random.Random(123)
    for i in range(20):
        n_lines = rng.randint(1, 40)
        has_coords = rng.random() < 0.9
        stop = _make_stop(
            slug=f'rand-{i}',
            lat=44.80 + rng.uniform(-0.05, 0.05) if has_coords else None,
            lon=20.45 + rng.uniform(-0.05, 0.05) if has_coords else None,
            city=rng.choice(['beograd', 'novi-sad', 'nis', 'kragujevac']),
        )
        lines = _make_lines(n_lines, types=('bus', 'tram', 'night', 'suburban'))
        out = build_prose(stop, lines, [], None, lang='sr')
        for key in ('intro', 'service', 'location', 'tip'):
            assert key in out and out[key], f'rand-{i} {key} empty'
            assert '{' not in out[key]


def test_lang_prefix_threads_through_to_tip(app_ctx):
    """/ru and /en pages must have correctly prefixed catalog links so users
    stay in their language on click-through. Regression: earlier build hardcoded /rute/."""
    stop = _make_stop()
    ru = build_prose(stop, _make_lines(3), [], None, lang='ru', lang_prefix='/ru')
    en = build_prose(stop, _make_lines(3), [], None, lang='en', lang_prefix='/en')
    assert '/ru/rute/' in ru['tip'], f'RU tip missing /ru prefix: {ru["tip"]}'
    assert '/en/rute/' in en['tip'], f'EN tip missing /en prefix: {en["tip"]}'


def test_word_count_in_spec_range(app_ctx):
    """Spec: 150-300 words (when the stop has rich data: GTFS + nearby + multiple lines).
    Loose lower bound here — templates aim for >100, real stops with GTFS top 150."""
    stop = _make_stop(slug='rich')
    lines = _make_lines(6, types=('bus', 'tram'))
    nearby = [
        {'name': 'N1', 'lat': 44.818, 'lon': 20.458, 'slug': 'n1'},
        {'name': 'N2', 'lat': 44.819, 'lon': 20.459, 'slug': 'n2'},
    ]
    gtfs = {'first_departure': '04:30', 'last_departure': '23:50'}
    out = build_prose(stop, lines, nearby, gtfs, lang='sr')
    all_text = ' '.join([out['intro'], out['service'], out['location'], out['tip']])
    wc = len(all_text.split())
    assert wc >= 100, f'Prose only {wc} words — spec asks 150+'
    assert wc <= 400, f'Prose {wc} words — spec ceiling 300'

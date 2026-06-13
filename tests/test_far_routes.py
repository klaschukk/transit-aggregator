"""Far-destination AI route fallback: detection, sanitisation, endpoint, render."""
import json

import pytest

from app import ai_compose
from app.ai_compose import far_pair_info, _sanitize


# ── far_pair_info ────────────────────────────────────────────────────────

def test_far_pair_info_detects_far_destination():
    info = far_pair_info('Beograd', 'Bangkok')
    assert info is not None
    assert info['from_slug'] == 'beograd'
    assert info['to_slug'] == 'bangkok'
    assert info['far_slug'] == 'bangkok'
    assert info['region'] == 'asia'
    assert info['pair_key'] == 'beograd:bangkok'


def test_far_pair_info_none_for_domestic():
    # Both Serbian cities — handled by the normal DB path, not the AI fallback.
    assert far_pair_info('Beograd', 'Niš') is None


def test_far_pair_info_none_for_empty_or_same():
    assert far_pair_info('', 'Bangkok') is None
    assert far_pair_info('Bangkok', 'Bangkok') is None


def test_far_pair_info_far_as_origin():
    # Direction-agnostic: a far ORIGIN still triggers the fallback.
    info = far_pair_info('Bangkok', 'Beograd')
    assert info is not None
    assert info['far_slug'] == 'bangkok'


# ── _sanitize ────────────────────────────────────────────────────────────

def test_sanitize_coerces_and_clamps():
    out = _sanitize({
        'feasible': True,
        'summary': 'x' * 500,
        'legs': [{'mode': 'FLIGHT', 'from': 'A', 'to': 'B', 'duration': '~2h', 'note': 'n'}] * 9,
        'total_duration': '~1 day',
        'price_from_eur': '350',
        'tips': ['a', 'b', 'c', 'd', 'e'],
    }, 'Beograd', 'Bangkok')
    assert out['feasible'] is True
    assert len(out['legs']) == 5          # clamped to 5
    assert out['legs'][0]['mode'] == 'flight'  # lowercased, allowed
    assert out['price_from_eur'] == 350   # int-coerced
    assert len(out['summary']) <= 300
    assert len(out['tips']) <= 4


def test_sanitize_unknown_mode_falls_back_to_bus():
    out = _sanitize({'legs': [{'mode': 'spaceship', 'from': 'A', 'to': 'B'}]}, 'A', 'B')
    assert out['legs'][0]['mode'] == 'bus'


def test_sanitize_infeasible_when_no_legs():
    out = _sanitize({'feasible': True, 'legs': []}, 'A', 'B')
    assert out['feasible'] is False


def test_sanitize_rejects_non_dict():
    assert _sanitize(['not', 'a', 'dict'], 'A', 'B') is None


# ── /api/compose-route endpoint ──────────────────────────────────────────

def test_compose_endpoint_rejects_non_far(client):
    r = client.get('/api/compose-route?od=Beograd&do=Nis')
    assert r.status_code == 400


def test_compose_endpoint_composes_and_caches(client, monkeypatch):
    calls = {'n': 0}

    def fake_compose(from_city, to_city, lang, api_key, timeout=20):
        calls['n'] += 1
        return {
            'feasible': True, 'summary': 's',
            'legs': [{'mode': 'flight', 'from': from_city, 'to': to_city,
                      'duration': '~12h', 'note': ''}],
            'total_duration': '~13h', 'price_from_eur': 500, 'tips': [],
            'from_city': from_city, 'to_city': to_city,
        }

    store = {}
    monkeypatch.setattr(ai_compose, 'compose_itinerary_via_groq', fake_compose)
    # Also patch the symbol the route imports lazily.
    import app.routes.main as main_mod  # noqa: F401
    from app import analytics_db
    monkeypatch.setattr(analytics_db, 'get_composed_route',
                        lambda pk, lang: store.get((pk, lang)))
    monkeypatch.setattr(analytics_db, 'upsert_composed_route',
                        lambda pk, lang, fc, tc, payload: store.__setitem__((pk, lang), payload))

    # 1st call — composes via (fake) Groq and caches.
    r1 = client.get('/api/compose-route?od=Beograd&do=Bangkok&lang=sr')
    assert r1.status_code == 200
    body = json.loads(r1.get_data(as_text=True))
    assert body['legs'][0]['mode'] == 'flight'
    assert calls['n'] == 1

    # 2nd call — served from cache, Groq not hit again.
    r2 = client.get('/api/compose-route?od=Beograd&do=Bangkok&lang=sr')
    assert r2.status_code == 200
    assert calls['n'] == 1


def test_compose_endpoint_503_when_model_unavailable(client, monkeypatch):
    from app import analytics_db
    monkeypatch.setattr(ai_compose, 'compose_itinerary_via_groq',
                        lambda *a, **k: None)
    monkeypatch.setattr(analytics_db, 'get_composed_route', lambda pk, lang: None)
    r = client.get('/api/compose-route?od=Beograd&do=Phuket&lang=en')
    assert r.status_code == 503


# ── /pretraga render ─────────────────────────────────────────────────────

def test_pretraga_renders_far_block(client, app):
    # The far block lives on a content page, which the DB-rebuild guard 503s
    # when no transit.duckdb is present (e.g. a bare worktree). Skip there; CI
    # builds the DB first and runs this fully.
    from app.db import db_ready
    with app.app_context():
        if not db_ready():
            pytest.skip('transit.duckdb not present in this environment')
    r = client.get('/pretraga/?od=Beograd&do=Bangkok')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'id="aiRoute"' in html
    # Bookaway is kept ONLY for far destinations (Asia) — its booking CTA must
    # render here even though it was removed from every regular route.
    assert 'ai-route__cta' in html
    assert 'go2cloud.org' in html           # CTA routed through conversion tracker


# ── /voznja far guide (Phase 2, indexable, server-rendered) ──────────────

def test_voznja_far_guide_indexable(client, app, monkeypatch):
    from app.db import db_ready
    with app.app_context():
        if not db_ready():
            pytest.skip('transit.duckdb not present in this environment')
    from app.routes import intercity
    fake = {
        'feasible': True, 'summary': 'Put preko Istanbula',
        'legs': [{'mode': 'flight', 'from': 'Beograd', 'to': 'Bangkok',
                  'duration': '~12h', 'note': ''}],
        'total_duration': '~13h', 'price_from_eur': 500, 'tips': ['viza'],
    }
    monkeypatch.setattr(intercity, '_compose_far_itinerary',
                        lambda info, lang: fake)
    r = client.get('/voznja/beograd-do-bangkok/')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'ai-route--static' in html       # server-rendered itinerary
    assert 'FAQPage' in html                # rich-result schema
    assert 'noindex' not in html.lower()    # indexable (unlike /pretraga)


def test_voznja_thin_pair_stays_noindex(client, app, monkeypatch):
    from app.db import db_ready
    with app.app_context():
        if not db_ready():
            pytest.skip('transit.duckdb not present in this environment')
    # A far pair with no CACHED itinerary → no far block, stays thin. The
    # request path is cache-only (never calls Groq), so "uncached" is the
    # only way a far pair renders thin.
    from app.routes import intercity
    monkeypatch.setattr(intercity, '_compose_far_itinerary',
                        lambda info, lang: None)
    r = client.get('/voznja/beograd-do-bangkok/')
    assert r.status_code == 200
    assert 'noindex' in r.get_data(as_text=True).lower()


def test_compose_far_itinerary_is_cache_only(app, monkeypatch):
    """The request path must NEVER hit Groq: uncached pair → None, no model
    call — indexability stays stable across crawls and Googlebot never waits
    out the model timeout."""
    from app import ai_compose, analytics_db
    from app.routes.intercity import _compose_far_itinerary

    def _boom(*a, **k):
        raise AssertionError('request path called Groq')

    monkeypatch.setattr(ai_compose, 'compose_itinerary_via_groq', _boom)
    monkeypatch.setattr(analytics_db, 'get_composed_route', lambda pk, lang: None)
    with app.app_context():
        assert _compose_far_itinerary({'pair_key': 'beograd:bangkok'}, 'sr') is None


# ── sitemap-far.xml (Phase 2 discovery path) ─────────────────────────────

def _fake_far_rows(rows):
    """analytics_db.query stub: serve `rows` for the composed_routes SELECT,
    empty for anything else — exercises the real feasibility filter in
    analytics_db.composed_far_pairs instead of stubbing it out."""
    def _q(sql, params=None):
        return rows if 'composed_routes' in sql else []
    return _q


def test_sitemap_far_lists_cached_pair_with_cache_date(client, monkeypatch):
    from app import analytics_db
    rows = [
        {'pair_key': 'beograd:bangkok', 'from_city': 'Beograd',
         'to_city': 'Bangkok',
         'payload': json.dumps({'feasible': True, 'legs': [{'mode': 'flight'}]}),
         'created_at': '2026-06-10T12:00:00Z'},
        # Cached but INFEASIBLE (model said "impossible"; cached so Groq isn't
        # re-asked) → page renders noindex → must stay out of the sitemap.
        {'pair_key': 'beograd:pjongjang', 'from_city': 'Beograd',
         'to_city': 'Pjongjang',
         'payload': json.dumps({'feasible': False, 'legs': []}),
         'created_at': '2026-06-11T12:00:00Z'},
    ]
    monkeypatch.setattr(analytics_db, 'query', _fake_far_rows(rows))
    r = client.get('/sitemap-far.xml')
    assert r.status_code == 200
    xml = r.get_data(as_text=True)
    # cached + feasible → listed, lastmod = cache date (not DB mtime)
    assert '/voznja/beograd-do-bangkok/' in xml
    assert '<lastmod>2026-06-10</lastmod>' in xml
    # cached + infeasible → not listed
    assert 'pjongjang' not in xml
    # never cached at all → not listed
    assert 'phuket' not in xml


def test_sitemap_far_empty_without_cache(client, monkeypatch):
    from app import analytics_db
    monkeypatch.setattr(analytics_db, 'query', _fake_far_rows([]))
    r = client.get('/sitemap-far.xml')
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert '<urlset' in body
    assert '/voznja/' not in body


def test_sitemap_index_advertises_far_shard(client):
    xml = client.get('/sitemap.xml').get_data(as_text=True)
    assert '/sitemap-far.xml' in xml


def test_destinations_links_cached_far_guides(client, app, monkeypatch):
    """Internal-link discovery path: /destinacije/ must link far guides that
    have a cached itinerary (Google needs a crawl path besides the sitemap)."""
    from app.db import db_ready
    with app.app_context():
        if not db_ready():
            pytest.skip('transit.duckdb not present in this environment')
    from app import analytics_db
    rows = [
        {'pair_key': 'beograd:bangkok', 'from_city': 'Beograd',
         'to_city': 'Bangkok',
         'payload': json.dumps({'feasible': True, 'legs': [{'mode': 'flight'}]}),
         'created_at': '2026-06-10T12:00:00Z'},
    ]
    monkeypatch.setattr(analytics_db, 'query', _fake_far_rows(rows))
    r = client.get('/destinacije/')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert '/voznja/beograd-do-bangkok/' in html
    assert 'Beograd → Bangkok' in html

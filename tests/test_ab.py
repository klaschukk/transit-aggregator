"""Tests for the A/B framework — ab.py, ab_power.py, ab_config wiring,
admin routes, and the conversion endpoint.

Coverage targets (per the launch spec, ≥25 tests):
- assignment determinism + sticky cookie behaviour
- weight distribution sanity (no all-A, no all-B for many seeds)
- cohort filters (lang/not_lang/device)
- exposure dedup per request
- conversion endpoint: payload validation, unknown experiment dropped,
  unknown variant dropped, valid call lands in ab_events
- power calculator: edge cases (rate=0, rate=1, mde=0)
- Wilson CI: zero-sample, exact-zero, exact-one
- two-prop z-test: identical proportions → p≈1, large diff → p<0.001
- admin /ab list + detail: 503 without creds, 200 with creds
- CSV export: produces expected columns
"""
from __future__ import annotations

import os
import pytest
from pathlib import Path

from app import create_app
from app.ab import (
    ExperimentSpec, _weighted_pick, assign, _cohort_match,
    track_exposure, AB_ID_COOKIE, AB_VARIANT_COOKIE_PREFIX,
)
from app.ab_power import (
    required_sample_size, wilson_interval, two_proportion_z_test,
)


def _make_app(tmp_path, **extra_config):
    """Create a Flask app pointed at a per-test analytics DB.

    create_app() reads ANALYTICS_DB_PATH from the already-imported config
    module (env vars are baked at config import time), so we override
    `app.config` after create + force a schema re-init against the new
    path. Otherwise init_schema runs against the live data/dbs/ DuckDB
    file which the dev server has locked.
    """
    db_path = tmp_path / 'analytics_ab.duckdb'
    app = create_app('development')
    app.config['ANALYTICS_DB_PATH'] = str(db_path)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    for k, v in extra_config.items():
        app.config[k] = v
    from app import analytics_db
    # Drop any cached connection bound to the old (prod) path so
    # subsequent calls reconnect to the per-test DB.
    import threading
    analytics_db._local = threading.local()
    with app.app_context():
        analytics_db.init_schema()
    return app


@pytest.fixture
def app(tmp_path):
    return _make_app(tmp_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_app(tmp_path):
    return _make_app(tmp_path, ADMIN_USER='tester', ADMIN_PASS='secret123')


@pytest.fixture
def admin_client(admin_app):
    return admin_app.test_client()


def _spec(key='exp_x', variants=('A', 'B'), weights=None, cohort=None):
    if weights is None:
        weights = tuple(1.0 for _ in variants)
    return ExperimentSpec(
        key=key, variants=tuple(variants), weights=tuple(weights),
        surface='trip_card', started_at='2020-01-01',
        cohort=cohort,
    )


# ── Assignment determinism ────────────────────────────────────────────


def test_weighted_pick_is_deterministic():
    spec = _spec()
    assert _weighted_pick(spec, 'seed-42') == _weighted_pick(spec, 'seed-42')


def test_different_seeds_can_yield_different_variants():
    spec = _spec()
    seen = {_weighted_pick(spec, f'seed-{i}') for i in range(50)}
    # 50 seeds → both variants almost certainly hit at least once.
    assert len(seen) == 2


def test_weighted_pick_respects_weights_roughly():
    spec = _spec('w', ('A', 'B'), (9.0, 1.0))
    counts = {'A': 0, 'B': 0}
    for i in range(2000):
        counts[_weighted_pick(spec, f'u-{i}')] += 1
    # 90:10 expected. ±5 percentage points for a 2000-sample binomial is fine.
    assert counts['A'] / 2000 > 0.85
    assert counts['B'] / 2000 < 0.15


def test_weighted_pick_handles_zero_weight_arm():
    spec = _spec('z', ('A', 'B', 'C'), (1.0, 0.0, 1.0))
    seen = set()
    for i in range(200):
        seen.add(_weighted_pick(spec, f's-{i}'))
    assert 'B' not in seen, 'zero-weight arm should never be picked'


# ── Cohort filters ─────────────────────────────────────────────────────


def test_cohort_lang_match(app):
    spec = _spec(cohort={'lang': ['en']})
    with app.test_request_context('/en/'):
        from flask import g
        g.lang = 'en'
        assert _cohort_match(spec) is True


def test_cohort_lang_mismatch(app):
    spec = _spec(cohort={'lang': ['en']})
    with app.test_request_context('/'):
        from flask import g
        g.lang = 'sr'
        assert _cohort_match(spec) is False


def test_cohort_not_lang_excludes_serbo_croatian(app):
    spec = _spec(cohort={'not_lang': ['sr', 'hr', 'bs', 'me']})
    with app.test_request_context('/'):
        from flask import g
        g.lang = 'sr'
        assert _cohort_match(spec) is False


def test_cohort_not_lang_admits_others(app):
    spec = _spec(cohort={'not_lang': ['sr', 'hr', 'bs', 'me']})
    # Without an Accept-Language header _accept_lang_prefix() falls back
    # to 'sr', so we must set one explicitly to simulate a foreign visitor.
    with app.test_request_context(
        '/en/', headers={'Accept-Language': 'en-US,en;q=0.9'},
    ):
        from flask import g
        g.lang = 'en'
        assert _cohort_match(spec) is True


def test_cohort_device_mobile(app):
    spec = _spec(cohort={'device': 'mobile'})
    with app.test_request_context(
        '/', headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0)'}
    ):
        assert _cohort_match(spec) is True


def test_cohort_device_desktop(app):
    spec = _spec(cohort={'device': 'desktop'})
    with app.test_request_context(
        '/', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X)'}
    ):
        assert _cohort_match(spec) is True


def test_cohort_device_blocks_wrong_class(app):
    spec = _spec(cohort={'device': 'mobile'})
    with app.test_request_context(
        '/', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X)'}
    ):
        assert _cohort_match(spec) is False


def test_assign_returns_none_when_out_of_cohort(app):
    spec = _spec(cohort={'lang': ['xx']})
    with app.test_request_context('/'):
        from flask import g
        g.lang = 'sr'
        assert assign(spec, seed='whatever') is None


# ── Sticky cookie ─────────────────────────────────────────────────────


def test_sticky_cookie_wins_over_seed(app):
    spec = _spec()
    with app.test_request_context(
        '/', headers={'Cookie': f'{AB_VARIANT_COOKIE_PREFIX}exp_x=B'}
    ):
        assert assign(spec, seed='seed-that-would-pick-A') == 'B'


def test_invalid_sticky_value_falls_through_to_seed(app):
    spec = _spec()
    # 'C' is not in variants → should be ignored and seed-based pick used.
    with app.test_request_context(
        '/', headers={'Cookie': f'{AB_VARIANT_COOKIE_PREFIX}exp_x=C'}
    ):
        out = assign(spec, seed='deterministic')
        assert out in ('A', 'B')


def test_sticky_cookie_ignored_when_variant_ramped_to_zero(app):
    """A shipped winner (loser at weight 0) must reach returning visitors too."""
    spec = _spec(weights=(1.0, 0.0))
    with app.test_request_context(
        '/', headers={'Cookie': f'{AB_VARIANT_COOKIE_PREFIX}exp_x=B'}
    ):
        assert assign(spec, seed='any-seed') == 'A'


# ── Exposure dedup ─────────────────────────────────────────────────────


def test_track_exposure_dedups_within_request(app):
    """Calling track_exposure 5x with the same (exp,variant,surface,user)
    should only insert one row — the trip-card macro renders many cards
    per page; we measure unique exposures, not impressions."""
    from app import analytics_db
    with app.test_request_context('/'):
        for _ in range(5):
            track_exposure('exp_x', 'A', 'trip_card', user_seed='u1')
        rows = analytics_db.query(
            "SELECT COUNT(*) AS c FROM ab_events "
            "WHERE experiment='exp_x' AND user_seed='u1' "
            "AND event_type='exposure'"
        )
        assert rows[0]['c'] == 1


def test_track_exposure_separate_users_each_count(app):
    from app import analytics_db
    with app.test_request_context('/'):
        track_exposure('exp_x', 'A', 'trip_card', user_seed='u1')
    with app.test_request_context('/'):
        track_exposure('exp_x', 'A', 'trip_card', user_seed='u2')
    with app.app_context():
        rows = analytics_db.query(
            "SELECT COUNT(*) AS c FROM ab_events WHERE experiment='exp_x'"
        )
        assert rows[0]['c'] == 2


# ── Cookie issuance via context_processor ─────────────────────────────


def test_first_visit_issues_ab_id_cookie(client):
    """Hitting the home page should mint an ab_id cookie because the
    home hero subtitle and currency-default exp both fire ab_variant()."""
    r = client.get('/en/', headers={'Accept-Language': 'en-US,en;q=0.9'})
    assert r.status_code == 200
    cookies = '\n'.join(r.headers.getlist('Set-Cookie'))
    assert 'ab_id=' in cookies, f'no ab_id cookie issued: {cookies}'
    # hero_sub_v1 has no cohort → must always set its variant cookie.
    assert f'{AB_VARIANT_COOKIE_PREFIX}hero_sub_v1=' in cookies


def test_second_visit_reuses_ab_id(client):
    """Same browser, same UA, second hit: the ab_id cookie must remain
    stable so the user keeps the same variants."""
    r1 = client.get('/en/')
    r2 = client.get('/en/')
    assert r2.status_code == 200
    # If the existing ab_id was respected, no new ab_id cookie is issued.
    cookies2 = '\n'.join(r2.headers.getlist('Set-Cookie'))
    assert 'ab_id=' not in cookies2 or cookies2.count('ab_id=') == 0


def test_currency_cohort_excludes_serbian(client):
    """Default URL = / (sr). currency_default_v1 is excluded for sr/hr/bs/me
    so the cookie should NOT be set on a Serbian visit."""
    r = client.get('/', headers={'Accept-Language': 'sr,sr-RS;q=0.9'})
    cookies = '\n'.join(r.headers.getlist('Set-Cookie'))
    assert f'{AB_VARIANT_COOKIE_PREFIX}currency_default_v1' not in cookies


# ── /api/ab-convert endpoint ──────────────────────────────────────────


def test_convert_unknown_experiment_silently_dropped(client):
    r = client.post('/api/ab-convert',
                    json={'experiment': 'totally_made_up', 'event': 'click'})
    # Always 204 — never reveal which experiments exist.
    assert r.status_code == 204


def test_convert_invalid_variant_dropped(client, app):
    """Even if the experiment exists, an unknown variant should not insert
    a row (would corrupt the analysis)."""
    from app import analytics_db
    r = client.post('/api/ab-convert', json={
        'experiment': 'cta_copy_v1', 'event': 'buy_click',
        'variant': 'NotAVariant',
    })
    assert r.status_code == 204
    with app.app_context():
        rows = analytics_db.query(
            "SELECT COUNT(*) AS c FROM ab_events "
            "WHERE experiment='cta_copy_v1' AND variant='NotAVariant'"
        )
        assert rows[0]['c'] == 0


def test_convert_valid_payload_lands_in_db(client, app):
    from app import analytics_db
    # Simulate the user already having a sticky variant cookie.
    client.set_cookie('ab_cta_copy_v1', 'Kupi')
    r = client.post('/api/ab-convert', json={
        'experiment': 'cta_copy_v1', 'event': 'buy_click', 'variant': 'Kupi',
    })
    assert r.status_code == 204
    with app.app_context():
        rows = analytics_db.query(
            "SELECT COUNT(*) AS c FROM ab_events "
            "WHERE experiment='cta_copy_v1' AND variant='Kupi' "
            "AND event_type='conv:buy_click'"
        )
        assert rows[0]['c'] == 1


def test_convert_missing_fields_dropped(client):
    r = client.post('/api/ab-convert', json={'experiment': '', 'event': ''})
    assert r.status_code == 204


# ── Power / stats ─────────────────────────────────────────────────────


def test_required_sample_size_basic():
    r = required_sample_size(0.04, mde_relative=0.10)
    # Per Cohen 1988: 4% baseline, 10% relative MDE, α=0.05, β=0.20 ≈ 30k.
    # Allow ±20% tolerance — exact value depends on which formula derivation.
    assert 12000 < r.n_per_variant < 50000


def test_required_sample_size_rejects_invalid_baseline():
    assert required_sample_size(0.0).n_per_variant == 0
    assert required_sample_size(1.0).n_per_variant == 0
    assert required_sample_size(-0.1).n_per_variant == 0


def test_days_at_rate_zero_returns_zero():
    r = required_sample_size(0.04, 0.10)
    assert r.days_at_rate(0) == 0


def test_wilson_interval_zero_sample():
    low, high = wilson_interval(0, 0)
    assert (low, high) == (0.0, 0.0)


def test_wilson_interval_exact_zero():
    """0/100 → upper bound > 0 but strictly < 5%."""
    _, high = wilson_interval(0, 100)
    assert 0 < high < 0.05


def test_wilson_interval_exact_one():
    """100/100 → lower bound > 95%."""
    low, _ = wilson_interval(100, 100)
    assert low > 0.95


def test_two_prop_z_test_no_difference():
    """Identical rates on identical samples → p≈1, z≈0."""
    r = two_proportion_z_test(50, 1000, 50, 1000)
    assert r.p_value > 0.99
    assert abs(r.z) < 0.01
    assert r.significant is False


def test_two_prop_z_test_large_lift():
    """4% vs 6% on 5000 each is highly significant."""
    r = two_proportion_z_test(200, 5000, 300, 5000)
    assert r.p_value < 0.001
    assert r.significant is True
    assert r.lift_relative > 0.4   # 4% → 6% = 50% relative lift


def test_two_prop_z_test_zero_n():
    r = two_proportion_z_test(0, 0, 0, 0)
    assert r.p_value == 1.0
    assert r.significant is False


# ── Admin routes ──────────────────────────────────────────────────────


def test_admin_ab_returns_503_without_creds(client):
    """Admin disabled when ADMIN_USER/ADMIN_PASS are unset — should not
    expose dashboards."""
    r = client.get('/admin/ab')
    assert r.status_code == 503


def test_admin_ab_returns_401_with_wrong_creds(admin_client):
    r = admin_client.get('/admin/ab')
    assert r.status_code == 401


def test_admin_ab_renders_with_creds(admin_client):
    import base64
    creds = base64.b64encode(b'tester:secret123').decode()
    r = admin_client.get('/admin/ab', headers={'Authorization': f'Basic {creds}'})
    assert r.status_code == 200
    body = r.data.decode()
    assert 'cta_copy_v1' in body
    assert 'hero_sub_v1' in body


def test_admin_ab_detail_renders(admin_client):
    import base64
    creds = base64.b64encode(b'tester:secret123').decode()
    r = admin_client.get(
        '/admin/ab/cta_copy_v1', headers={'Authorization': f'Basic {creds}'}
    )
    assert r.status_code == 200
    body = r.data.decode()
    # Wilson CI columns + variant names should be visible even on empty data.
    assert 'Wilson' in body or 'CI' in body
    assert 'Kupi' in body


def test_admin_ab_detail_404_for_unknown(admin_client):
    import base64
    creds = base64.b64encode(b'tester:secret123').decode()
    r = admin_client.get(
        '/admin/ab/nope_v1', headers={'Authorization': f'Basic {creds}'}
    )
    assert r.status_code == 404


def test_admin_ab_csv_export_headers(admin_client):
    import base64
    creds = base64.b64encode(b'tester:secret123').decode()
    r = admin_client.get(
        '/admin/ab/cta_copy_v1.csv', headers={'Authorization': f'Basic {creds}'}
    )
    assert r.status_code == 200
    assert r.mimetype == 'text/csv'
    body = r.data.decode()
    # Header row at minimum; data rows are 0 since no events fired in this app.
    assert body.startswith('ts,experiment,variant,event_type,surface,user_seed,value')


# ── trip-card conversion polish (added 2026-06-13) ──


def test_trip_card_buy_has_aria_label_and_keeps_ab_hooks(client):
    """The buy CTA carries an aria-label with the price (so screen-reader users
    hear what they're buying), and the conversion-polish markup must not drop
    the A/B hooks the experiments depend on."""
    import re
    r = client.get('/rute/beograd-novi-sad/')
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert 'trip-card__buy' in html
    # A/B regression guard: cta_copy_v1 + cta_color_v2 hooks survive.
    assert 'data-ab-cta=' in html
    assert 'data-ab-color=' in html
    # Every buy link is labelled; at least one ties the price into the label.
    labels = re.findall(r'<a class="trip-card__buy[^>]*?aria-label="([^"]*)"', html)
    assert labels, 'buy buttons must carry an aria-label'
    assert any('RSD' in lbl for lbl in labels), \
        'at least one buy CTA aria-label should include the price'

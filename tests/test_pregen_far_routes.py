"""scripts/pregen_far_routes.py — the nightly Groq-warm-up sweep's circuit breaker.

2026-09-22 incident: a Cloudflare error-1010 block on this box's IP turned an
overnight run into ~4 hours of retrying a dead API pair by pair (each hard
failure cost a 45s retry backoff + 30s cooldown) instead of noticing after a
handful of tries that nothing will succeed — and it also broke the live
/api/chat feature for the whole time it ran. These tests drive main() with a
stubbed Groq call so they run in well under a second.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from app import create_app as _real_create_app

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = PROJECT_ROOT / 'scripts' / 'pregen_far_routes.py'


@pytest.fixture
def pregen():
    spec = importlib.util.spec_from_file_location('pregen_far_routes', SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def app_factory(tmp_path):
    """A create_app() that hands back a real app wired to a throwaway DB."""
    def factory(env):
        app = _real_create_app('development')
        app.config['ANALYTICS_DB_PATH'] = str(tmp_path / 'analytics.sqlite')
        app.config['GROQ_API_KEY'] = 'test-key'
        return app
    return factory


def _fake_destinations(n):
    return {f'dest{i}': {'display': f'Dest {i}'} for i in range(n)}


def test_aborts_after_consecutive_hard_failures_without_exhausting_the_grid(
    pregen, app_factory, monkeypatch, capsys,
):
    calls = []

    def always_hard_failure(*a, **kw):
        calls.append(a)
        return None, True

    monkeypatch.setattr(pregen, 'create_app', app_factory)
    monkeypatch.setattr(pregen, 'SR_HUBS', ['Beograd'])
    monkeypatch.setattr(pregen, 'FAR_DESTINATIONS', _fake_destinations(10))
    monkeypatch.setattr(pregen, 'TOP_FAR', list(_fake_destinations(10)))
    monkeypatch.setattr(pregen, 'compose_itinerary_via_groq_ex', always_hard_failure)
    monkeypatch.setattr(pregen.time, 'sleep', lambda *_: None)

    pregen.main()

    out = capsys.readouterr().out
    assert 'ABORTED' in out
    # 10 destinations x len(SUPPORTED_LANGS) possible pair-langs; the breaker
    # must stop long before that, at CONSECUTIVE_HARD_FAILURE_LIMIT (x MAX_ATTEMPTS
    # calls per pair-lang, since every attempt in a failing pair is hard).
    expected_calls = pregen.CONSECUTIVE_HARD_FAILURE_LIMIT * pregen.MAX_ATTEMPTS
    assert len(calls) == expected_calls


def test_does_not_abort_on_ordinary_infeasible_routes(pregen, app_factory, monkeypatch):
    """Soft failures (Groq answered, route just isn't feasible) are normal and
    must not trip the breaker — most pregen runs have plenty of these."""
    def always_infeasible(*a, **kw):
        return {'feasible': False}, False

    monkeypatch.setattr(pregen, 'create_app', app_factory)
    monkeypatch.setattr(pregen, 'SR_HUBS', ['Beograd'])
    monkeypatch.setattr(pregen, 'FAR_DESTINATIONS', _fake_destinations(5))
    monkeypatch.setattr(pregen, 'TOP_FAR', list(_fake_destinations(5)))
    monkeypatch.setattr(pregen, 'compose_itinerary_via_groq_ex', always_infeasible)
    monkeypatch.setattr(pregen.time, 'sleep', lambda *_: None)

    calls = []
    orig = pregen.compose_itinerary_via_groq_ex
    monkeypatch.setattr(pregen, 'compose_itinerary_via_groq_ex',
                        lambda *a, **kw: (calls.append(1), orig(*a, **kw))[1])

    pregen.main()

    # 5 destinations x len(SUPPORTED_LANGS) x MAX_ATTEMPTS, none of them hard
    # failures — the whole grid must be attempted, not cut short.
    from app.i18n import SUPPORTED_LANGS
    assert len(calls) == 5 * len(SUPPORTED_LANGS) * pregen.MAX_ATTEMPTS


def test_an_occasional_hard_failure_does_not_abort_a_run_that_recovers(
    pregen, app_factory, monkeypatch,
):
    """A single blip (one timeout) must not abort the sweep — only a run of
    CONSECUTIVE_HARD_FAILURE_LIMIT in a row should."""
    call_count = [0]

    def flaky(*a, **kw):
        call_count[0] += 1
        # Fail hard on exactly one pair's both attempts, then recover.
        if call_count[0] in (1, 2):
            return None, True
        return {'feasible': True, 'summary': 's', 'legs': [
            {'mode': 'bus', 'from': 'A', 'to': 'B', 'duration': '~1h', 'note': 'n'}]}, False

    monkeypatch.setattr(pregen, 'create_app', app_factory)
    monkeypatch.setattr(pregen, 'SR_HUBS', ['Beograd'])
    monkeypatch.setattr(pregen, 'FAR_DESTINATIONS', _fake_destinations(3))
    monkeypatch.setattr(pregen, 'TOP_FAR', list(_fake_destinations(3)))
    monkeypatch.setattr(pregen, 'compose_itinerary_via_groq_ex', flaky)
    monkeypatch.setattr(pregen.time, 'sleep', lambda *_: None)

    pregen.main()  # must not raise / must not abort

    # First pair-lang failed both attempts (hard), the rest succeeded on the
    # first attempt each: 2 + (3 dests x len(SUPPORTED_LANGS) - 1) calls.
    from app.i18n import SUPPORTED_LANGS
    assert call_count[0] == 2 + (3 * len(SUPPORTED_LANGS) - 1)

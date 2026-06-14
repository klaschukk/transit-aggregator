"""Tests for build_db GTFS helpers: route_short_name→city_line resolver and
the coverage/freshness anomaly check.

The resolver is the seam where the GTFS feed (Latin route names) links to our
Cyrillic-numbered Belgrade lines; a regression here silently unlinks thousands
of GTFS trips, killing stop ETAs. Grounded in the real transliteration map
(27Н→27N, 102п→102p).
"""
import pytest

from data.pipelines.build_db import (
    _build_line_resolver,
    _gtfs_coverage_warnings,
    _GTFS_MIN_STOP_TIMES_PCT,
    _GTFS_MIN_ROUTES_MATCHED,
    _GTFS_MAX_FEED_AGE_DAYS,
)


# ── route_short_name → city_line_id resolver ────────────────────────────────

def test_exact_raw_match():
    resolve = _build_line_resolver([(1, '15'), (2, '26')])
    assert resolve('15') == 1
    assert resolve('26') == 2


def test_cyrillic_line_links_to_latin_gtfs_name():
    # city_lines store '27Н' (Cyrillic Н); the GTFS feed calls it '27N'.
    resolve = _build_line_resolver([(7, '27Н')])
    assert resolve('27N') == 7      # via transliteration
    assert resolve('27Н') == 7      # exact raw still works


def test_case_insensitive_recovery():
    # '102п' transliterates to lowercase '102p'; GTFS uses '102P'.
    resolve = _build_line_resolver([(5, '102п')])
    assert resolve('102P') == 5     # case-insensitive fallback
    assert resolve('102p') == 5     # exact transliterated


def test_no_match_returns_none():
    resolve = _build_line_resolver([(1, '15')])
    assert resolve('999') is None
    assert resolve('') is None


def test_ambiguous_case_insensitive_key_is_skipped():
    # 'ка'→'ka' and 'кА'→'kA' both upper-case to 'KA' but map to different
    # lines, so a bare 'KA' must NOT be linked to either (wrong-line guard).
    resolve = _build_line_resolver([(1, 'ка'), (2, 'кА')])
    assert resolve('KA') is None
    assert resolve('ка') == 1       # exact raw still resolves each
    assert resolve('кА') == 2


def test_exact_match_beats_transliteration():
    # A Latin 'A1' line and a Cyrillic 'А1' line coexist; exact wins.
    resolve = _build_line_resolver([(1, 'A1'), (2, 'А1')])
    assert resolve('A1') == 1


# ── coverage / freshness warnings ───────────────────────────────────────────

def test_no_warnings_when_healthy():
    assert _gtfs_coverage_warnings(94, 250, 10.0) == []


def test_low_stop_times_coverage_warns():
    w = _gtfs_coverage_warnings(_GTFS_MIN_STOP_TIMES_PCT - 1, 250, 10.0)
    assert len(w) == 1 and 'coverage' in w[0]


def test_low_route_match_warns():
    w = _gtfs_coverage_warnings(94, _GTFS_MIN_ROUTES_MATCHED - 1, 10.0)
    assert len(w) == 1 and 'routes matched' in w[0]


def test_stale_feed_warns():
    w = _gtfs_coverage_warnings(94, 250, _GTFS_MAX_FEED_AGE_DAYS + 5)
    assert len(w) == 1 and 'old' in w[0]


def test_missing_feed_age_is_not_a_warning():
    assert _gtfs_coverage_warnings(94, 250, None) == []


def test_all_anomalies_stack():
    w = _gtfs_coverage_warnings(10, 5, 365)
    assert len(w) == 3


@pytest.mark.parametrize("pct", [_GTFS_MIN_STOP_TIMES_PCT, _GTFS_MIN_STOP_TIMES_PCT + 1])
def test_coverage_floor_is_inclusive(pct):
    # exactly at the floor is acceptable (no warning)
    assert _gtfs_coverage_warnings(pct, 250, 10.0) == []

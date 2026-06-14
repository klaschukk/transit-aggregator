"""Tests for scripts/data_snapshot.py anomaly detection.

A nightly scrape that breaks shows up as a sharp drop in a snapshot kind's
total, or an entity that had real data yesterday going to zero. detect_anomalies
is the pure check that turns those into alert strings; these tests pin the
thresholds and the cold-start (no false alarm) behaviour.
"""
from scripts.data_snapshot import (
    detect_anomalies,
    ANOMALY_DROP_PCT,
    ANOMALY_ZEROED_MIN,
)


def _d(key, value_a, value_b):
    return {'key': key, 'value_a': value_a, 'value_b': value_b,
            'delta': value_b - value_a}


def test_no_diffs_is_silent_cold_start():
    assert detect_anomalies('route_trips', [], 0) == []
    assert detect_anomalies('route_trips', [], 500) == []


def test_healthy_small_change_no_alert():
    diffs = [_d('beograd-nis', 10, 12), _d('beograd-novi-sad', 8, 7)]
    # prev_total = today_total - net_delta = 119 - 1 = 118; +1 net → no drop
    assert detect_anomalies('route_trips', diffs, 119) == []


def test_sharp_total_drop_alerts():
    diffs = [_d('beograd-nis', 50, 10)]          # net -40
    alerts = detect_anomalies('route_trips', diffs, 60)   # prev 100 → -40%
    assert len(alerts) == 1
    assert 'total fell 40%' in alerts[0]
    assert '100->60' in alerts[0]


def test_drop_below_threshold_no_alert():
    diffs = [_d('beograd-nis', 100, 80)]         # -20% < 30%
    assert detect_anomalies('route_trips', diffs, 80) == []


def test_drop_exactly_at_threshold_alerts():
    diffs = [_d('x', 100, 70)]                    # exactly -30%
    alerts = detect_anomalies('route_trips', diffs, 70)
    assert len(alerts) == 1 and 'fell 30%' in alerts[0]


def test_entity_zeroed_alerts():
    diffs = [_d('lasta', 8, 0)]                   # had 8, now 0
    alerts = detect_anomalies('operator_routes', diffs, 92)
    assert len(alerts) == 1
    assert "'lasta' dropped to 0 (was 8)" in alerts[0]


def test_entity_zeroed_below_min_is_noise():
    diffs = [_d('tiny', ANOMALY_ZEROED_MIN - 1, 0)]
    assert detect_anomalies('operator_routes', diffs, 100) == []


def test_net_increase_still_flags_individual_zeroing():
    diffs = [_d('dead-source', 7, 0), _d('new-source', 0, 50)]
    alerts = detect_anomalies('route_trips', diffs, 50)
    # net is +43 → no aggregate alert, but the zeroed source is flagged
    assert len(alerts) == 1
    assert "'dead-source' dropped to 0" in alerts[0]


def test_all_new_keys_prev_total_zero_no_aggregate():
    diffs = [_d('a', 0, 30), _d('b', 0, 20)]
    assert detect_anomalies('city_lines', diffs, 50) == []


def test_aggregate_and_zeroed_can_both_fire():
    diffs = [_d('big', 60, 5), _d('gone', 40, 0)]   # net -95, prev 105
    alerts = detect_anomalies('route_trips', diffs, 10)
    assert any('total fell' in a for a in alerts)
    assert any("'gone' dropped to 0" in a for a in alerts)
    assert len(alerts) == 2


def test_thresholds_are_sane():
    assert 0 < ANOMALY_DROP_PCT < 1
    assert ANOMALY_ZEROED_MIN >= 1

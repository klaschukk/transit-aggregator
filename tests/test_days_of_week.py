"""Tests for build_db._normalize_days_of_week and the documented data gap.

days_of_week is a placeholder: no source exposes a weekly recurrence pattern,
so build_db falls back to '1234567' for every trip. _normalize_days_of_week is
the forward-compatible seam that will persist a real mask the day a scraper
provides one. These tests pin its coercion rules and the default behaviour.
"""
import pytest

from data.pipelines.build_db import _DEFAULT_DAYS, _normalize_days_of_week


@pytest.mark.parametrize("raw, expected", [
    (None, _DEFAULT_DAYS),          # nothing from source → placeholder
    ('', _DEFAULT_DAYS),            # empty string → placeholder
    ('1234567', '1234567'),         # already full week
    ('12345', '12345'),            # weekdays only
    ('67', '67'),                  # weekends
    ('6', '6'),                    # single day
    ('21', '12'),                  # sorted
    ('112233', '123'),            # de-duplicated
    ('1 2 3', '123'),             # whitespace ignored
    (12345, '12345'),              # non-str coerced
    ('abc', _DEFAULT_DAYS),        # no valid digits → placeholder
    ('0', _DEFAULT_DAYS),          # 0/8/9 are not valid weekday digits
    ('89', _DEFAULT_DAYS),
    ('1a2b8', '12'),              # mixed: keep 1,2; drop a,b,8
    ('7654321', '1234567'),       # reversed full week
])
def test_normalize_days_of_week(raw, expected):
    assert _normalize_days_of_week(raw) == expected


def test_default_applies_when_trip_has_no_day_field():
    """A scraped trip dict carries no 'days_of_week' (none of the scrapers emit
    one today), so the build falls back to the documented placeholder."""
    trip = {'departure_time': '06:00', 'arrival_time': '07:30',
            'duration_min': 90, 'price_rsd': 600}
    assert _normalize_days_of_week(trip.get('days_of_week')) == '1234567'


def test_result_is_always_valid_mask():
    """Whatever the input, the output is a non-empty subset of 1–7 in order."""
    for raw in [None, '', 'xyz', '777', '7531', 42, '1234567']:
        out = _normalize_days_of_week(raw)
        assert out
        assert all(c in '1234567' for c in out)
        assert list(out) == sorted(out)
        assert len(set(out)) == len(out)  # no duplicates

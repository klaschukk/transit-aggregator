"""Tests for build_db._sane_price_rsd — defensive cap on absurd trip prices.

A scrape_international currency bug produced ~100k-RSD Skopje–Ohrid fares (MKD
denars multiplied by EUR_TO_RSD). This cap zeroes anything above a sane Balkan
ceiling so a wrong, misleading price never reaches a user.
"""
import pytest

from data.pipelines.build_db import _sane_price_rsd, _MAX_SANE_PRICE_RSD


@pytest.mark.parametrize("raw, expected", [
    (0, 0),
    (None, 0),
    (600, 600),                      # normal domestic fare
    (12000, 12000),                  # plausible long/international fare
    (_MAX_SANE_PRICE_RSD, _MAX_SANE_PRICE_RSD),     # exactly at ceiling, kept
    (_MAX_SANE_PRICE_RSD + 1, 0),    # just over → zeroed
    (101790, 0),                     # the real Skopje–Ohrid bug value
    (-5, 0),                         # negative → unknown
    ('600', 600),                    # numeric string coerced
    ('abc', 0),                      # garbage → unknown
    (600.9, 600),                    # float truncated
])
def test_sane_price_rsd(raw, expected):
    assert _sane_price_rsd(raw) == expected


def test_output_always_in_sane_range():
    for raw in [None, '', 'x', -100, 0, 500, 49999, 50000, 50001, 10**9]:
        out = _sane_price_rsd(raw)
        assert 0 <= out <= _MAX_SANE_PRICE_RSD

"""Active A/B experiment declarations.

Edit this file to launch / pause / ship-the-winner. After a winner is
declared via /admin/ab and ramped to 100%, do NOT delete the entry from
this file — set `weights` to all-zero except the winner. Keeps the cookie
sticky for late stragglers and preserves the historical event stream.

When archiving (after analysis complete), move the entry into
`ARCHIVED_EXPERIMENTS` below so it is excluded from the live registry but
still queryable from /admin/ab CSV export.
"""
from __future__ import annotations

from app.ab import ExperimentSpec


# Default fallback variant per experiment — what the site shows when the
# user is out-of-cohort or assignment fails. The default MUST already exist
# as a variant so admin metrics still aggregate correctly.
DEFAULTS: dict[str, str] = {
    'cta_copy_v1': 'Kupi',
    'cta_color_v2': 'accent',
    'hero_sub_v1': 'descriptive',
    'currency_default_v1': 'rsd',
    'review_cta_v1': 'after-trips',
}


EXPERIMENTS: dict[str, ExperimentSpec] = {
    # 1. Trip-card buy CTA copy. Surface: every page that renders a trip
    #    card (search results, route detail, city pair).
    'cta_copy_v1': ExperimentSpec(
        key='cta_copy_v1',
        variants=('Kupi', 'Rezerviši', 'Uporedi cene'),
        weights=(1.0, 1.0, 1.0),
        surface='trip_card',
        started_at='2026-04-24',
        min_runtime_days=7,
    ),

    # 2. Bookaway buy-button color. accent = current orange, primary = teal
    #    brand, urgent = high-contrast red. Tests CTR vs brand consistency.
    'cta_color_v2': ExperimentSpec(
        key='cta_color_v2',
        variants=('accent', 'primary', 'urgent'),
        weights=(1.0, 1.0, 1.0),
        surface='trip_card',
        # v1 (2026-04-24) is void: variants were assigned + logged but the
        # CSS for 'primary'/'urgent' never existed, so every cohort saw the
        # same orange button. Restarted as v2 the day the CSS shipped.
        started_at='2026-06-11',
        min_runtime_days=7,
    ),

    # 3. Home hero subtitle. Tests value-prop framing: simple description,
    #    proof-by-numbers, named-operators.
    # RETIRED 2026-09-21 WITHOUT A STATISTICAL WINNER: conversion tracking
    # was broken for 4.5 months (wrong selector) and at current traffic
    # significance would take ~255 days. `feature_list` also hard-coded a stale
    # "335 routes · 6 countries". Ramped the neutral, number-free `descriptive`
    # to 100%; other weights 0 (not deleted) so /admin/ab/hero_sub_v1 stays
    # queryable. Archive after 30 days.
    'hero_sub_v1': ExperimentSpec(
        key='hero_sub_v1',
        # Variant keys, not full strings — full copy lives in i18n. Keeps
        # variant labels short for cookies and dashboard rows.
        variants=('descriptive', 'feature_list', 'price_compare'),
        weights=(1.0, 0.0, 0.0),
        surface='home_hero',
        started_at='2026-04-24',
        min_runtime_days=7,
    ),

    # 4. Currency default for tourists. Excludes Serbo-Croatian readers
    #    (sr/hr/bs/me) — they already see RSD natively. Hypothesis was that
    #    an EUR default would make tourists more confident about pricing.
    # WINNER SHIPPED 2026-09-13: rsd beat eur by +112% relative conversion
    # (0.43% vs 0.20%, z=9.5, p<0.0001, non-overlapping 95% CIs) over 4.5
    # months and 220K+ exposures — the opposite of the hypothesis. Ramped
    # rsd to 100%; eur weight kept at 0 (not deleted) so the framework and
    # /admin/ab/currency_default_v1 stay queryable per the ship-the-winner
    # process (docs/06_tech/ab-process.md). Archive after 30 days.
    'currency_default_v1': ExperimentSpec(
        key='currency_default_v1',
        variants=('rsd', 'eur'),
        weights=(1.0, 0.0),
        surface='trip_card',
        started_at='2026-04-24',
        min_runtime_days=7,
        cohort={'not_lang': ['sr', 'hr', 'bs', 'me']},
    ),

    # 5. Review CTA placement on route_detail. after-trips = current,
    #    sidebar = right rail, sticky-bottom = mobile-friendly bar.
    'review_cta_v1': ExperimentSpec(
        key='review_cta_v1',
        variants=('after-trips', 'sidebar', 'sticky-bottom'),
        weights=(1.0, 1.0, 1.0),
        surface='route_detail',
        started_at='2026-04-24',
        min_runtime_days=7,
    ),
}


# Archive bucket — excluded from live registry but kept for historical CSV
# pulls and post-mortems.
ARCHIVED_EXPERIMENTS: dict[str, ExperimentSpec] = {}


def all_experiments() -> dict[str, ExperimentSpec]:
    """Live experiments only. /admin/ab uses this; archive is opt-in."""
    return EXPERIMENTS


def get_spec(key: str) -> ExperimentSpec | None:
    return EXPERIMENTS.get(key) or ARCHIVED_EXPERIMENTS.get(key)

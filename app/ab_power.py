"""Sample-size + significance helpers — pure stdlib, no scipy required.

Two things we need:
  1. Required N per variant for a given baseline conversion rate, minimum
     detectable effect, alpha, power. Used in /admin/ab to surface
     "estimated days to significance" before we burn weeks on an
     underpowered experiment.
  2. Two-proportion z-test + Wilson score interval for the live dashboard
     verdict. We avoid scipy.stats.chi2_contingency to keep deps minimal,
     but for 2x2 tables the two-prop z-test is mathematically equivalent
     to chi-square (z² = χ²) — same p-value.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


# Standard normal inverse CDF (z-scores) for the alphas/powers we use.
# Hard-coded so we don't pull scipy. statistics.NormalDist would work too
# but keeping these explicit makes the math obvious in code review.
_Z_TWO_TAIL = {
    0.10: 1.6449,
    0.05: 1.9600,
    0.01: 2.5758,
}
_Z_POWER = {
    0.80: 0.8416,
    0.85: 1.0364,
    0.90: 1.2816,
    0.95: 1.6449,
}


@dataclass
class SampleSizeResult:
    n_per_variant: int
    baseline_rate: float
    mde_relative: float
    alpha: float
    power: float

    @property
    def total_n(self) -> int:
        # 2-arm assumption — admin dashboard scales by len(variants).
        return self.n_per_variant * 2

    def days_at_rate(self, daily_exposures_per_variant: float) -> int:
        if daily_exposures_per_variant <= 0:
            return 0
        return max(1, math.ceil(self.n_per_variant / daily_exposures_per_variant))


def required_sample_size(
    baseline_rate: float,
    mde_relative: float = 0.10,
    alpha: float = 0.05,
    power: float = 0.80,
) -> SampleSizeResult:
    """Required sample size per variant for a two-proportion test.

    Args:
        baseline_rate: control's expected conversion rate (e.g. 0.04 for 4%).
        mde_relative: minimum detectable effect as a fraction of baseline
            (0.10 = detect a 10% relative lift, i.e. 4.0% → 4.4%).
        alpha: type-1 error rate (default 0.05, two-tailed).
        power: 1 - type-2 error (default 0.80).

    Formula: n = (z_α/2 + z_β)² · (p1·q1 + p2·q2) / (p2 - p1)²
        where p1 = baseline, p2 = baseline · (1 + mde), q = 1 - p.

    Edge cases:
        baseline_rate ≤ 0 or ≥ 1 → returns sentinel n=0; admin shows
        "configure baseline" instead of a misleading number.
    """
    if not (0 < baseline_rate < 1) or mde_relative <= 0:
        return SampleSizeResult(0, baseline_rate, mde_relative, alpha, power)

    p1 = baseline_rate
    p2 = min(0.9999, baseline_rate * (1 + mde_relative))
    q1, q2 = 1 - p1, 1 - p2
    z_alpha = _Z_TWO_TAIL.get(alpha, _Z_TWO_TAIL[0.05])
    z_beta = _Z_POWER.get(power, _Z_POWER[0.80])

    delta = p2 - p1
    if delta == 0:
        return SampleSizeResult(0, baseline_rate, mde_relative, alpha, power)

    numerator = (z_alpha + z_beta) ** 2 * (p1 * q1 + p2 * q2)
    n = numerator / (delta ** 2)
    return SampleSizeResult(
        n_per_variant=int(math.ceil(n)),
        baseline_rate=p1,
        mde_relative=mde_relative,
        alpha=alpha,
        power=power,
    )


def wilson_interval(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Better than the normal-approximation CI when conversions are scarce —
    we routinely deal with 2-3% rates. Returns (low, high) on [0, 1].
    Empty (n=0) → (0, 0).
    """
    if n <= 0:
        return (0.0, 0.0)
    z = _Z_TWO_TAIL.get(alpha, _Z_TWO_TAIL[0.05])
    p = successes / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))) / denom
    low = max(0.0, centre - margin)
    high = min(1.0, centre + margin)
    return (low, high)


@dataclass
class TwoPropResult:
    p_value: float
    z: float
    lift_relative: float
    ci_low: float
    ci_high: float
    significant: bool


def two_proportion_z_test(
    successes_a: int, n_a: int,
    successes_b: int, n_b: int,
    alpha: float = 0.05,
) -> TwoPropResult:
    """Compare two proportions. Mathematically equivalent to a 2x2 chi-square
    (z² = χ²(1)) — same p-value, but we report z so direction is preserved.

    Returns p-value derived from the standard normal via the Abramowitz &
    Stegun 7.1.26 series approximation (max error 1.5e-7) — good enough
    for displaying "p < 0.001 / p = 0.034" on the dashboard.
    """
    if n_a <= 0 or n_b <= 0:
        return TwoPropResult(1.0, 0.0, 0.0, 0.0, 0.0, False)

    p_a = successes_a / n_a
    p_b = successes_b / n_b
    p_pool = (successes_a + successes_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return TwoPropResult(1.0, 0.0, 0.0, 0.0, 0.0, False)

    z = (p_b - p_a) / se
    p_value = 2 * (1 - _norm_cdf(abs(z)))
    lift = (p_b - p_a) / p_a if p_a > 0 else 0.0

    # CI on the difference, not the lift. Used for sanity-check display only.
    se_diff = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    z_alpha = _Z_TWO_TAIL.get(alpha, _Z_TWO_TAIL[0.05])
    delta = p_b - p_a
    ci_low = delta - z_alpha * se_diff
    ci_high = delta + z_alpha * se_diff

    return TwoPropResult(
        p_value=p_value, z=z, lift_relative=lift,
        ci_low=ci_low, ci_high=ci_high,
        significant=p_value < alpha,
    )


def _norm_cdf(x: float) -> float:
    """Standard normal CDF. Uses math.erf — no scipy required."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

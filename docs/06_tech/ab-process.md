# A/B Experimentation — Process Guide

This is how we run experiments on prevozni.com. The framework is server-side
(Flask context_processor + DuckDB events table); these are the rules of
engagement around it.

## Why we test

At ≥200 visits/day every CTR-improving change is compounding revenue. A
5% lift on the trip-card buy CTA at 280 visits/day buys roughly +14
clicks/day, multiplied across affiliate revenue per click. Ten experiments
× 5% lift each ≈ 60% cumulative over three months. The cost of the
framework is worth less than one missed winner.

## Lifecycle

### 1. Define hypothesis BEFORE writing code

Every experiment lands as a one-paragraph entry in `app/ab_config.py` with:

- a clear name (`<surface>_<dimension>_v<n>`)
- 2–3 variants (more = larger required N, longer runtime)
- the surface it renders on
- the cohort filter (if any)

Hypothesis template:

> "If we change <X> on <surface>, then <metric> will <direction> by ≥<MDE>%
> because <user-behaviour reason>."

If you can't fill the "because" clause, you don't have a hypothesis — you
have a guess. Don't burn sample size on guesses.

### 2. Calculate required sample size

`/admin/ab/<key>` shows it for you, but pre-launch:

```python
from app.ab_power import required_sample_size
r = required_sample_size(baseline_rate=0.04, mde_relative=0.10)
print(r.n_per_variant)        # → 15800
print(r.days_at_rate(40))     # → 395 days at 40 exposures/day per variant
```

Heuristic: if days_to_significance > 30, EITHER widen the MDE (we'd
notice a 20% lift faster than a 10% lift) OR drop the experiment — at
current traffic some deltas just aren't measurable.

### 3. Launch

Edit `app/ab_config.py` and add the `ExperimentSpec`. Set
`started_at` to today (UTC). Push as a normal PR — git history is the
audit trail.

The framework auto-creates an `ab_id` cookie on first variant lookup,
sticks the variant in `ab_<key>=<variant>` after exposure, and starts
recording events. Nothing else to deploy.

### 4. Run for at least `min_runtime_days`

Default is 7. Don't peek-and-stop. Day-of-week effects on traffic dominate
any reading taken on day 3. The dashboard surfaces a yellow "Hold off on
shipping a winner" banner while you're under the minimum.

If you absolutely need to stop early (e.g. variant breaking the page), do
NOT call it a winner — call it a kill, document the reason in the PR that
removes it, and restart from scratch.

### 5. Read the verdict

`/admin/ab/<key>` shows for each non-control variant:

- Wilson 95% CI on the conversion rate
- two-proportion z-test p-value vs control (= 2x2 chi-square — same answer)
- relative lift
- a verdict badge: **Wins (p<0.05)** / **Loses (p<0.05)** / **No effect detected** / **Insufficient data**

"Insufficient data" gates on **≥100 conversions per variant**. That bar
is deliberately higher than the math requires — for tiny conversion
counts, p-values lie. If you see Insufficient Data after 7 days, EITHER
the MDE was too tight or the surface gets too few impressions.

### 6. Ship the winner within 24h

When a variant wins (p<0.05 AND sufficient data AND past min_runtime):

1. Edit `app/ab_config.py` — set winner's weight to 1.0, others to 0.0.
2. Keep the entry; don't delete it. The cookie stays sticky for users
   already on the losing variant, and the row stays queryable in
   `/admin/ab/<key>.csv`.
3. Once 30 days pass, move the entry to `ARCHIVED_EXPERIMENTS` and
   inline the winning copy/CSS as the new default.
4. Pull the CSV (`/admin/ab/<key>.csv`) before the archive bump and
   commit it under `docs/00_strategy/ab-history/` for retro analysis.

### 7. Don't run conflicting tests on the same surface

Two experiments on the same button (e.g. `cta_copy_v1` AND
`cta_color_v1`) is fine — the variants are independent and we can read
both effects in isolation. But two tests of the **same dimension** on the
same surface (`cta_copy_v1` AND `cta_copy_v2`) is not — the effect of one
contaminates the other. Pause v1 before launching v2.

## Anti-patterns we avoid

- **Peeking and stopping**: looking at the dashboard daily and shipping
  the moment p<0.05 inflates type-1 error rate enormously. Stick to the
  pre-declared runtime.
- **HARKing**: hypothesising after results are known. The "we expected this"
  story should appear in the PR description that *launches* the test, not
  the one that ships the winner.
- **Winning on a sub-segment**: if the overall test is null but mobile-only
  shows a lift, that's a NEW experiment, not the result of this one. Re-run
  it scoped to the cohort.
- **Shipping a "loss" because it looks the same**: zero-effect ≠ no
  difference. The CI for "no effect" might span ±20%. If the variant cost
  engineering effort, document the no-result and roll back.

## Privacy

- `ab_id` is a UUID, not a PII identifier. Set HttpOnly, SameSite=Lax,
  180-day max-age.
- The framework writes `user_seed` (= ab_id) into `ab_events` for
  per-user dedup. Salt-hashed before storage if the salt is set; if not,
  the raw UUID is stored — still non-PII because we never link it to an
  email or IP in cleartext.
- Cookie is documented in `/privatnost/` under "legitimate interest:
  product improvement". GDPR-compliant without an explicit consent gate
  because (a) it's not advertising, (b) it doesn't profile across sites,
  (c) the cookie expires.

## When to NOT run an A/B

- The change is a bug fix that's already producing user complaints.
  Ship it.
- The change is required for legal/compliance reasons.
  Ship it.
- The change is a copy edit too small to move the metric (typo, em-dash
  vs en-dash). The test would be underpowered and a waste of the cookie
  budget. Ship it.
- The site has < 50 events/day on the surface. The framework still
  records, but the math doesn't work. Wait for traffic.

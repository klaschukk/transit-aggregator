# Affiliate partners — comparison

Single-source-of-truth for the partner economics behind `app/affiliates/`.
Pick the list from the "Status" column; the others are documented so we
don't re-research when revisiting the stack.

**Current state (since 2026-06-10):** BusTicket4 is the PRIMARY partner on
all regular routes; Bookaway serves far destinations (Asia) ONLY; FlixBus
was never activated and is removed from the chain.

| Partner        | Commission            | Cookie | Coverage                        | Deep link                                                  | Status         |
|----------------|-----------------------|--------|---------------------------------|------------------------------------------------------------|----------------|
| **BusTicket4** | **2% per sale** (Cassiopeia doo agreement, `affiliateId=735`) | n/a — attribution via `affiliateId` in URL | All regular SR + ex-YU intercity/international routes (our own data source) | Per-trip checkout deep-link with pre-resolved `lineId` (`bt4_lineids.json` + per-trip `bt4_line_id` + `bt4_fallback_line_id`), refreshed nightly by `refresh_bt4_lineids.py` | **PRIMARY (Integrated)** |
| **Bookaway**   | ~5–10% per sale       | 30 d   | **Far destinations (Asia) only** since 2026-06-10; pairs verified via `bookaway_pairs.json` / `bookaway_far.json` | TUNE tracker `/aff_c?offer_id=34&aff_id=4033&aff_sub={from}-{to}&aff_sub2={utm_medium}` — the tracker hop mints the transaction_id | **Integrated (far-only)** |
| ~~FlixBus~~    | 3–5% (EU) / ~$6 (US)  | 30 d   | Cross-border corridors; no intra-SR | Awin redirect (placeholder ID, never approved)             | **Removed 2026-06** — affiliate deal never landed, code kept but NOT in `ACTIVE_PARTNERS` |
| ~~Omio~~       | 2–8%                  | 30 d   | Multi-modal; SR↔DE/AT, fair Balkans | —                                                       | **Dropped 2026-04-26** — never approved, zero attribution, removed to declutter trip cards |
| GetByBus       | ~5–10% (now owned by Bookaway — same inventory) | 30 d | SR/HR/BA core                   | Redundant with Bookaway                                     | Skip (duplicate) |
| Busbud         | 2% (CJ)               | 7 d    | Thin Balkans                    | Via CJ link generator                                       | Skip (low ROI) |
| 12Go           | 50% of booking fee (~$3 avg) | 30 d | Asia-centric, thin EU       | `12go.asia/en/travel/{from}/{to}?utm_medium=affiliate`     | Skip (wrong geography) |

Commission/cookie numbers come from each partner's agreement, public
affiliate page or their Awin/CJ merchant profile; they are subject to
change and should be re-checked annually. The point of this doc is to
capture the _relative_ economics so a future re-evaluation takes minutes,
not hours.

## Rationale

### Why BusTicket4 is primary (2026-06)
BusTicket4 sells the exact routes we already aggregate, and its checkout
deep-link opens a **populated departure** (known `lineId`), not a search
page. Expected revenue is conversion × commission, and a working checkout's
conversion edge dwarfs Bookaway's higher nominal band on pages that
historically converted ~0 (the "362 clicks, 0 conversions" Bookaway
fallback). Hence `ux_rank = 0` for BT4 vs `1` for Bookaway — checkout
quality deliberately ranks above commission percentage.

**Known issue:** the BT4 dashboard (busticket4.me partner login) shows
**0 sales for Apr–Jun 2026**. Either traffic genuinely doesn't convert yet
or attribution is broken — this is the main attribution question now (see
`bookaway_postback.md` for the Bookaway side, which is only the Asia
funnel these days).

### Why Bookaway was demoted to far-only (2026-06-10)
On regular Balkan routes Bookaway's inventory match was poor: clicks
landed on country-listing pages and converted ~0 (362 clicks, 0
conversions over the measured period). The fix was two-fold: (a) only
link Bookaway where the pair is verified in `bookaway_pairs.json`, and
(b) restrict Bookaway to far destinations (Asia, `FAR_DESTINATIONS` in
`partners.py`) where BT4 sells nothing and Bookaway's inventory is real.
Links go through the TUNE tracker (`/aff_c`) with `aff_sub={from}-{to}`
and `aff_sub2={utm_medium}` for per-route attribution.

### Why FlixBus was removed
Originally added to plug cross-border gaps, but the Awin affiliate deal
never landed — the ID stayed a placeholder, so every URL was
non-tracking. With BT4 covering regular routes (including cross-border)
there is no gap left worth an unapproved partner. The `FlixBus` class is
kept in `partners.py` for a possible future deal but is NOT in
`ACTIVE_PARTNERS` (`resolve.py`).

### Why we dropped Omio (2026-04-26)
Omio was originally added as a multi-modal universal-fallback partner —
the safety net that let every trip card show a "Kupi" button even when
other partners had no inventory. In practice the partner account was
never approved (PARTNER_ID stayed `'PLACEHOLDER'`), so the URLs were
non-tracking from day one. Zero commissions over the live period meant
the only thing it produced was a third button color and extra trip-card
chrome.

### Why skip the others
* **GetByBus** was acquired by Bookaway. Their tickets flow through the same
  inventory; integrating them separately would double-book the same sale
  and either halve the commission or trigger duplicate-attribution claw-back.
* **Busbud** pays 2% with a 7-day cookie. After a typical 14-day
  consider-then-book window on a €40 bus ticket, expected revenue per
  booking is below €1 — not worth the integration surface.
* **12Go** is Asia-centric (Thailand, Vietnam, Indonesia). Their Balkan
  inventory is thin and their payout minimum (€900 bank / €8 PayPal)
  doesn't match our traffic profile. (For our own Asia far-destinations
  funnel we use Bookaway, which we already integrate.)

## Selection chain

Codified in `app/affiliates/resolve.py` (`ACTIVE_PARTNERS`):

1. `has_route(from, to)` — partner must actually sell the pair.
   BusTicket4 answers True for pairs with a pre-resolved `lineId`;
   Bookaway answers True ONLY when an endpoint is in `FAR_DESTINATIONS`.
2. `ux_rank` (lower wins): BusTicket4 = 0 (exact populated checkout),
   Bookaway = 1 (listing page). Checkout quality leads.
3. `commission_pct` midpoint (higher wins) — tiebreak within equal ux_rank.

When no partner covers a pair the resolver returns an empty list and the
trip card hides its "Kupi" button (`{% if _buy_href %}` guard). On route
pages the template also derives the main CTA straight from each trip's
`bt4_line_id`, so a pair missing from the json still buys through
BusTicket4 when the DB knows the line.

The A/B stub (`ab_partner_order`) is a cookie-driven pre-sort; it floats
a named partner to the front if eligible but never disables one.

## Measuring reality

All buy-button clicks are logged to `ba_clicks` (analytics.sqlite) with a
`partner` column — compare CTR/EPC per partner there, then reconcile
against the BT4 dashboard and the Bookaway/TUNE dashboard. Numbers in
this doc are assumptions until those dashboards show confirmed sales
(BT4: still 0 for Apr–Jun 2026).

## Application / signup status

* [x] BusTicket4 — agreement live, `affiliateId=735` (prevozni.com,
  Cassiopeia doo). Primary.
* [x] Bookaway — approved, `offer_id=34`, `aff_id=4033`, TUNE tracker.
  Far destinations only.
* [ ] FlixBus — removed; re-apply via Awin only if a corridor gap
  re-appears that BT4 can't cover.

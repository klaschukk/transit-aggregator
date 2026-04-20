# Affiliate partners — comparison

Single-source-of-truth for the partner economics behind `app/affiliates/`.
Pick the list from the "Integrated" column; the others are documented so we
don't re-research when revisiting the stack.

| Partner        | Commission            | Cookie | Balkans coverage                | Deep link                                                  | Status         |
|----------------|-----------------------|--------|---------------------------------|------------------------------------------------------------|----------------|
| **Bookaway**   | ~5–10% per sale       | 30 d   | Strong — SR/ME/BA/HR/MK, IL hubs | `bookaway.com/routes/{country}/{from}-to-{to}?offer_id=34&aff_id=4033` | **Integrated** |
| **FlixBus**    | 3–5% (EU) / ~$6 (US)  | 30 d   | BG↔SR/HR/BA/MK/HU/BG/SI corridors; **no intra-SR** | Via Awin tracking redirect → `flixbus.com/bus/{from}-{to}` | **Integrated** |
| **Omio**       | 2–8% (base 6%)        | 30 d   | Multi-modal; strong SR↔DE/AT, fair Balkans | `omio.com/search-frontend/bus?partnerId=<TBD>&from={from}&to={to}` | **Integrated** |
| GetByBus       | ~5–10% (now owned by Bookaway — same inventory) | 30 d | SR/HR/BA core                   | Redundant with Bookaway                                     | Skip (duplicate) |
| Busbud         | 2% (CJ)               | 7 d    | Thin Balkans                    | Via CJ link generator                                       | Skip (low ROI) |
| 12Go           | 50% of booking fee (~$3 avg) | 30 d | Asia-centric, thin EU       | `12go.asia/en/travel/{from}/{to}?utm_medium=affiliate`     | Skip (wrong geography) |

Commission/cookie numbers come from each partner's public affiliate page or
their Awin/CJ merchant profile; they are subject to change and should be
re-checked annually. The point of this doc is to capture the _relative_
economics so a future re-evaluation takes minutes, not hours.

## Rationale

### Why add FlixBus
Our Bookaway coverage is strongest on SR↔ME/HR and Istanbul; weaker on
SR↔HU/BG/RO and on mid-size intra-Balkan corridors. FlixBus runs its own
buses on exactly those weak links (Belgrade ↔ Sofia, Skopje, Zagreb,
Sarajevo, Budapest, Ljubljana) so it plugs the gap where Bookaway shows
thin inventory. The trade-off is no intra-SR coverage — FlixBus does not
sell Niš ↔ Kraljevo, so Bookaway stays primary for domestic trips.

### Why add Omio
Multi-modal (bus + train + flight + ferry) means we can monetise users who
search a route like Beograd → Minhen, realise no bus exists, and click a
train alternative. Omio also has the best SR↔Western-Europe mix (Munich,
Vienna, Zurich) that neither Bookaway nor FlixBus covers well. Commission
is lower (2–8%) but cookie is 30 d and the partner supports a proper
search-widget integration if we later want to deep-embed results.

### Why skip the others
* **GetByBus** was acquired by Bookaway. Their tickets flow through the same
  inventory; integrating them separately would double-book the same sale
  and either halve the commission or trigger duplicate-attribution claw-back.
* **Busbud** pays 2% with a 7-day cookie. After a typical 14-day
  consider-then-book window on a €40 bus ticket, expected revenue per
  booking is below €1 — not worth the integration surface.
* **12Go** is Asia-centric (Thailand, Vietnam, Indonesia). Their Balkan
  inventory is thin and their payout minimum (€900 bank / €8 PayPal)
  doesn't match our traffic profile.

## Fallback chain

Codified in `app/affiliates/resolve.py`:

1. `Bookaway.has_route(from, to)` → use it (highest commission × best
   Balkans coverage).
2. Else `FlixBus.has_route(...)` → use it (covers the cross-border
   corridors where Bookaway is thin).
3. Else `Omio.has_route(...)` → use it (multi-modal catch-all; always
   returns True so the chain never falls off the end).

A/B stub (`app/affiliates/ab.py`) can flip step 1 ↔ step 2 for 50% of
traffic via cookie `ab_partner=bookaway|flixbus`, so we can measure CTR
and CVR before committing to a primary partner long-term.

## Expected revenue lift

Baseline: Bookaway-only, ~1 click → ~0.05–0.1 confirmed booking × €2.5
avg commission = €0.15/click effective EPC.

With FlixBus+Omio filling coverage gaps:
* +20–30% of currently-dead trip cards now get a buy button (routes where
  Bookaway has no inventory). Conservative estimate: **+15% total
  click volume**.
* FlixBus EPC on cross-border corridors is comparable to Bookaway; Omio
  is lower but catches queries that currently 100% bounce.
* Net ballpark: **+20–35% affiliate revenue** once FlixBus approval lands
  and Omio widget is live, assuming current traffic stays flat.

Numbers are assumptions, not commitments. Validate against Umami
`ba_clicks` + equivalent counters after 2–4 weeks of real traffic.

## Application / signup TODOs

Real affiliate IDs need to be obtained manually. The code ships with
placeholder IDs that produce non-tracking URLs (safe to deploy, no
revenue until replaced):

* [ ] FlixBus — apply via Awin (`affiliatepartner@flixbus.com`). Replace
  `FLIXBUS_AWIN_ID` in `config.py` once approved.
* [ ] Omio — apply at `omio.com/affiliate`. Replace `OMIO_PARTNER_ID`.
* [x] Bookaway — already approved, IDs live in templates (`offer_id=34`,
  `aff_id=4033`).

# Affiliate partners — comparison

Single-source-of-truth for the partner economics behind `app/affiliates/`.
Pick the list from the "Integrated" column; the others are documented so we
don't re-research when revisiting the stack.

| Partner        | Commission            | Cookie | Balkans coverage                | Deep link                                                  | Status         |
|----------------|-----------------------|--------|---------------------------------|------------------------------------------------------------|----------------|
| **Bookaway**   | ~5–10% per sale       | 30 d   | Strong — SR/ME/BA/HR/MK, IL hubs | `bookaway.com/routes/{country}/{from}-to-{to}?offer_id=34&aff_id=4033` (deep link); falls back to `routes/{country}/?…` when one endpoint isn't in inventory — preserves attribution since Bookaway's own redirect strips query params on a missing route page | **Integrated** |
| **FlixBus**    | 3–5% (EU) / ~$6 (US)  | 30 d   | BG↔SR/HR/BA/MK/HU/BG/SI corridors; **no intra-SR** | Via Awin tracking redirect → `flixbus.com/bus/{from}-{to}` | **Integrated** |
| ~~Omio~~       | 2–8%                  | 30 d   | Multi-modal; SR↔DE/AT, fair Balkans | —                                                       | **Dropped 2026-04-26** — never approved, zero attribution, removed to declutter trip cards |
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

### Why we dropped Omio (2026-04-26)
Omio was originally added as a multi-modal universal-fallback partner —
the safety net that let every trip card show a "Kupi" button even when
Bookaway / FlixBus had no inventory. In practice the partner account was
never approved (PARTNER_ID stayed `'PLACEHOLDER'`), so the URLs were
non-tracking from day one. Zero commissions over the live period meant
the only thing it produced was a third button color and extra trip-card
chrome. Removed in favour of a tighter Bookaway URL builder that falls
back to the country-listing page (preserves attribution) and a `{% if
_buy_href %}` guard on the template (cards without coverage simply hide
the buy button).

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
   Balkans coverage). When only one endpoint is in Bookaway's inventory
   the URL falls back to the country listing page so attribution still
   sticks.
2. Else `FlixBus.has_route(...)` → use it (covers the cross-border
   corridors where Bookaway is thin).
3. Else no partner — the trip card hides its "Kupi" button. Acceptable
   since pairs without either partner are rare (mostly tiny domestic
   commuter routes; users still see schedule + price).

A/B stub (`app/affiliates/ab.py`) can flip step 1 ↔ step 2 for 50% of
traffic via cookie `ab_partner=bookaway|flixbus`, so we can measure CTR
and CVR before committing to a primary partner long-term.

## Expected revenue lift

Baseline: Bookaway-only, ~1 click → ~0.05–0.1 confirmed booking × €2.5
avg commission = €0.15/click effective EPC.

With FlixBus filling cross-border coverage gaps:
* Cross-border corridors (Beograd ↔ Sofia/Skopje/Zagreb/Sarajevo/Budapest)
  get a second buy button next to the Bookaway one — A/B chooses which
  shows first per visitor.
* FlixBus EPC on cross-border corridors is comparable to Bookaway.
* Net ballpark: **+15–25% affiliate revenue** once FlixBus approval lands,
  assuming current traffic stays flat.

Numbers are assumptions, not commitments. Validate against Umami
`ba_clicks` + equivalent counters after 2–4 weeks of real traffic.

## Application / signup TODOs

Real affiliate IDs need to be obtained manually. The code ships with
placeholder IDs that produce non-tracking URLs (safe to deploy, no
revenue until replaced):

* [ ] FlixBus — apply via Awin (`affiliatepartner@flixbus.com`). Replace
  `FLIXBUS_AWIN_ID` in `config.py` once approved.
* [x] Bookaway — already approved, IDs live in templates (`offer_id=34`,
  `aff_id=4033`).

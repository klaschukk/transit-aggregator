# Bookaway commission attribution — status

> **Context (2026-06-10): Bookaway = только дальние направления.** Bookaway
> is now used ONLY for far destinations (Asia); the primary partner on all
> regular routes is BusTicket4 (`affiliateId=735`). The TUNE mechanics below
> stay relevant for the Asia funnel, but the main attribution question today
> is the **BusTicket4 dashboard (0 sales Apr–Jun 2026)** — see
> `partners.md` for the BT4 attribution status.

**Status: blocked on Bookaway side.** No server-to-server postback available.

## What we verified

Bookaway's affiliate program runs on a HasOffers-based dashboard. Public
documentation only describes:

- Unique tracking links per affiliate (we have `offer_id=34`, `aff_id=4033`).
- Thirty-day attribution cookie on the click-through.
- A conversion report dashboard, refreshed in near-real-time.
- SubID parameters `subid1`–`subid5` that we can stuff with our own
  metadata (route slug, surface, campaign).

They do **not** publish:

- S2S postback URL targets that Bookaway would call back when a booking
  completes.
- Conversion webhooks.
- A REST API to pull conversion rows programmatically.

## What this means for us

We cannot close the attribution loop automatically. The flow is:

1. We log every click in our own `ba_clicks` table (analytics.sqlite,
   `/api/ba-click`; the table now has a `partner` column). This gives us
   CTR per route, per surface, per UTM, per partner.
2. To see commission revenue we must log into the Bookaway partner
   dashboard manually and reconcile against our click log by:
   - The date range.
   - SubIDs we embedded — links now route through the TUNE tracker
     (`/aff_c`) with `aff_sub={from}-{to}` and `aff_sub2={utm_medium}`
     (partners.py, `Bookaway.build_url`), so each conversion has a key
     that joins back to `ba_clicks.route_slug`.

## What to do when we get commissions

Once real money starts arriving, export the Bookaway conversion CSV
weekly and bulk-load it into a new `ba_conversions` table (parallel to
`ba_clicks`, same id-sequenced schema). Then the admin dashboard can
show true revenue per route instead of click proxies.

## Alternatives considered

- **Third-party attribution proxies** (Scaleo, Post Affiliate Pro, Everflow)
  sit between us and Bookaway, re-issue the redirect, and expose their
  own S2S postback. Cost ≈ $99/mo minimum, not worth it below four-figure
  monthly commission.
- **Ask Bookaway support directly** for S2S — worth a single email but
  don't block on it. Email: `affiliates@bookaway.com`.

## Sources

- <https://www.bookaway.com/affiliates>
- <https://www.cuelinks.com/campaigns/bookaway-affiliate-program>
- <https://www.tracknow.io/blog/s2s-and-postback-tracking/43> (S2S primer)

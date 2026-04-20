# Bookaway commission attribution — status

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

1. We log every click in our own `ba_clicks` DuckDB table (implemented,
   `/api/ba-click`). This gives us CTR per route, per surface, per UTM.
2. To see commission revenue we must log into the Bookaway partner
   dashboard manually and reconcile against our click log by:
   - The date range.
   - SubIDs we embedded — we stamp `subid1` with our `route_slug`
     (partners.py, `Bookaway.build_url`) so each conversion has a key
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

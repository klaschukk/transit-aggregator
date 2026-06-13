# AdSense placement strategy

> Internal reference. Updated when slot inventory changes.
> Last update: 2026-06-12 — AdSense is **live** (`ca-pub-9538841764038287`);
> added `search_mid` / `stop_bottom` / `line_bottom` slots (in config since
> 2026-05-15); partner names refreshed (BusTicket4 primary, Bookaway
> far-only, FlixBus removed).

## Goals

1. Maximise RPM without policy risk (Google ad-density / placement / UX).
2. Protect Core Web Vitals — LCP regression budget **≤ 500ms**, CLS = 0.
3. Never compete with affiliate CTAs — BusTicket4 (primary partner) and
   Bookaway (far destinations only) drive higher per-visitor revenue
   than ad clicks at our traffic volume.
4. Coexist cleanly with the GDPR cookie banner — no ads load until
   `cookie_consent=all` OR `essential` (latter triggers Google's
   `requestNonPersonalizedAds=1`).

## Manual vs Auto Ads

**Manual** by default. Reasons:

- Auto-Ads inject anywhere Google's ML decides — including mid-prose
  on guide pages, where Google's own policy bot sometimes flags it
  as "ads in long-form content".
- Manual placements are a one-time investment; Auto-Ads churn the page
  layout on every Google model update, which spikes CLS and breaks our
  LCP baseline.
- We control ad density per page (1 unit max, except home which has 2:
  top + mid).

**Auto-Ads candidates** (future): `/rute/` and `/prevoznici/` indexes —
listing pages where Google's ML can pick the best in-feed gap without
breaking semantic structure. Wire only after manual baseline is stable.

## Slot inventory

| Key | Page | Position | Format | Reserved height (desktop / mobile) |
|---|---|---|---|---|
| `home_top` | `/` | Between newsletter and stats | leaderboard | 90px / 100px |
| `home_mid` | `/` | Between FAQ and benefits | large-rectangle | 280px / 250px |
| `route_bottom` | `/rute/{slug}/` | After SEO prose, before reviews | leaderboard | 90px / 100px |
| `city_pair_bottom` | `/voznja/{from}-do-{to}/` | After reviews, before related-pairs | leaderboard | 90px / 100px |
| `city_transport_mid` | `/gradski/{city}/` | After line-grid, before see-also | leaderboard | 90px / 100px |
| `catalog_in_feed` | `/rute/` | After full route grid | leaderboard | 90px / 100px |
| `guide_sidebar` | `/vodici/{slug}/` | Right rail (≥1100px only) | skyscraper | 600px / hidden |
| `search_mid` | `/pretraga/` | Mid results list | responsive | auto |
| `stop_bottom` | `/gradski/{city}/stajaliste/{slug}/` | Bottom, after ETA/lines | responsive | auto |
| `line_bottom` | `/gradski/{city}/linija/{slug}/` | Bottom, after stops list | responsive | auto |
| `mobile_anchor` | global | Sticky bottom, ≤640px only | fluid anchor | hidden / 80px |

Total ad density per page: **1** (except `/` which has 2). Below
Google's policy threshold and well below "junk site" feel.

## Pages we deliberately skip

| Page | Why no ad |
|---|---|
| `/admin/*` | Private |
| `/api/*` | Non-HTML |
| `/omiljeno/`, `/kontakt/` | Utility, thin |
| `/uslovi/`, `/privatnost/`, `/politika-kolacica/` | Legal — Google penalty risk if we monetise compliance pages |
| `/vodici/{slug}/` body | Long-form — ads in middle of prose flag automatically |
| `/sitemap.xml`, `/robots.txt`, `/ads.txt` | Plaintext |

(`/pretraga/` used to be on this list — since 2026-05-15 it renders
`search_mid`.)

## House-ad fallback

When AdSense is unavailable (no `ADSENSE_ID`, consent declined, ad
blocker active, slot ID missing), the slot wrapper renders one of three
house-ad variants chosen deterministically by path-length modulo:

1. **Newsletter signup** (compact form, `source=house_ad`)
2. **Popular route promo** (Beograd → Novi Sad CTA)
3. **Destinations index promo** (Balkan hub)

These are real product surfaces, not filler — 0.5–2% click-through from
house ads converts into our existing tracking surfaces (newsletter
signup → email list, route CTA → BusTicket4 buy button).

## CWV protection

- All ad slot wrappers reserve `min-height` matching the IAB-standard
  size of the format. CSS-only — no JS needed for layout stability.
- AdSense bootstrap is dynamic (`document.createElement('script')`
  AFTER consent check), not a synchronous `<script src>`. Keeps LCP
  paint independent of `pagead2.googlesyndication.com` latency.
- Mobile anchor uses `position: fixed` + `env(safe-area-inset-bottom)`
  so iOS home indicator doesn't crop the close button.
- Adblock detector cookie (`ads_blocked=1`) signals server-side: a
  future enhancement is to skip the entire slot wrapper for known
  blocked sessions — not done yet because it leaks the detector to
  Server-Side Rendering, which makes the cache key explode. Wire
  through `/admin/revenue` after we have ad-blocker-rate data.

## RPM benchmarks (travel niche, EN/SR/RU mix)

Source: AdSense industry reports + Mediavine travel partners (2024–25).

| Slot | Expected page RPM (USD) | Notes |
|---|---:|---|
| `home_top` | $2.50–4.00 | Above-fold leaderboard, high viewability |
| `home_mid` | $1.50–2.50 | Below-fold; only engaged readers see |
| `route_bottom` | $3.00–5.00 | Highest intent — readers reach this after pricing trips |
| `city_pair_bottom` | $2.50–4.00 | Same pattern, slightly lower volume |
| `city_transport_mid` | $1.50–3.00 | Local intent, decent CPM in Belgrade |
| `mobile_anchor` | $4.00–8.00 | Highest mobile RPM in the niche; offset by user dismissal |
| `catalog_in_feed` | $0.80–1.50 | Low engagement page |
| `guide_sidebar` | $1.00–2.00 | Desktop only; long sessions |

**Blended target**: $2.50–4.00 page-RPM at 12k monthly sessions →
**$30–48/month** when AdSense first lights up. Doubles within 60 days
as Google learns our audience.

## Iteration plan

1. Day 1–7: only `home_top`, `route_bottom`, `mobile_anchor` live.
   Three slots = enough to validate ads.txt + reporting + CWV without
   over-committing if there's a regression.
2. Day 8–21: add `home_mid`, `city_pair_bottom`, `city_transport_mid`.
3. Day 22+: add `catalog_in_feed`, `guide_sidebar`. Compare against
   the per-slot RPM table; kill any slot below $0.50.
4. Month 2: enable Auto-Ads on `/rute/` and `/prevoznici/` index pages.
5. Month 3: A/B per-slot variants — different formats per same key,
   pick by reported RPM in `adsense_daily` (analytics.sqlite,
   filled by `scripts/adsense_fetch.py`).

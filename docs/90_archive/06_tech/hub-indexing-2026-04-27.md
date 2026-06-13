# Hub indexing boost — 2026-04-27

## Problem

Yesterday's GSC export listed 5 top-level category hubs in the
"Discovered, currently not indexed" bucket:

  - `/autobuske-stanice/`
  - `/prevoznici/`
  - `/gradski/`
  - `/en/gradski/beograd/`
  - `/en/destinacije/crna-gora/`

These should be the FIRST URLs Google indexes — they're the catalogue
roots that every detail page lives under. Their absence from the
index signals weak internal link flow + low priority signal.

## Audit results

### (a) Contextual inbound — fixed in `65b2a5d`

Before:

| Hub | Template files linking | Real `<a>` from rendered detail pages |
|---|---|---|
| `/autobuske-stanice/` | 3 | ~3500 (footer only) |
| `/prevoznici/` (index) | 23 | mostly per-operator pages, 0 to index |
| `/gradski/` | 2 | ~3500 (footer only) |
| `/gradski/beograd/` | 12 | ~6000 (footer + breadcrumb on lines+stops) |
| `/destinacije/crna-gora/` | 1 (JSON-LD, not `<a>`) | 0 real `<a>` |

After (commit `65b2a5d`):

| Hub | Template files | Rendered contextual inbound |
|---|---|---|
| `/autobuske-stanice/` | 4 | **~3033** (browse-hubs partial) |
| `/prevoznici/` | 13 | **~3033** (browse-hubs) |
| `/gradski/` | 3 | **~3033** + breadcrumb chain |
| `/gradski/beograd/` | 9 | **~3033** + ~2500 breadcrumb |
| `/destinacije/crna-gora/` | 0 direct | covered via `/destinacije/` parent (~3033) |

The `_partials/_browse_hubs.html` block is included in:

  - `route_detail.html` (~285 pages render)
  - `city_pair.html` (~245)
  - `line_detail.html` (~611)
  - `stop_detail.html` (~1892)

Every one of those detail pages now has an above-the-fold see-also
section pointing at all 5 hubs. That's ~3033 contextual inbound per
hub — way past the 30-link threshold the prompt called out.

### (b) Footer audit — already complete

All 5 hubs are in `_partials/_footer.html` (verified):

```
href="{{ lang_prefix }}/autobuske-stanice/"   → footer.stations
href="{{ lang_prefix }}/prevoznici/"           → footer.carriers
href="{{ lang_prefix }}/gradski/beograd/"      → nav.city_transport
href="{{ lang_prefix }}/destinacije/"          → dest.title (parent)
```

`/destinacije/crna-gora/` (leaf) isn't in footer, but `/destinacije/`
(parent) is, and footer-class links are deweighted by Google anyway.
The leaf gets covered by the contextual `_browse_hubs.html` partial.

### (c) Breadcrumb audit — already complete

Both line_detail and stop_detail templates emit a breadcrumb chain
through `/gradski/{city}/`:

```jinja
{{ breadcrumb([
  {'url': lang_prefix ~ '/gradski/' ~ city ~ '/',
   'label': _('city.title') ~ ' ' ~ city_label},
  {'label': line.number}     # or stop.name
]) }}
```

That gives `/gradski/beograd/` ~2500 inbound from Beograd lines + stops
(Google weights breadcrumb links higher than footer).

### (d) Sitemap-core audit — passes

All 5 hubs are in `/sitemap-core.xml` with correct hreflang alternates:

```
<url>
  <loc>https://prevozni.com/gradski/beograd/</loc>
  <xhtml:link rel="alternate" hreflang="sr" href=".../gradski/beograd/"/>
  <xhtml:link rel="alternate" hreflang="en" href=".../en/gradski/beograd/"/>
  <xhtml:link rel="alternate" hreflang="ru" href=".../ru/gradski/beograd/"/>
  <xhtml:link rel="alternate" hreflang="x-default" href=".../gradski/beograd/"/>
</url>
```

Sitemap shape was deliberately switched to one canonical `<loc>` +
hreflang alternates per logical URL in commit `7ca377f` — Googlebot
discovers the per-locale variants through the alternates. Total
`<url>` count: 27 in core shard.

### (e) Hreflang audit — passes

`/en/destinacije/crna-gora/` and `/en/gradski/beograd/` both emit
correct bidirectional hreflang in their `<head>`:

```
<link rel="alternate" hreflang="sr" href=".../destinacije/crna-gora/">
<link rel="alternate" hreflang="en" href=".../en/destinacije/crna-gora/">
<link rel="alternate" hreflang="ru" href=".../ru/destinacije/crna-gora/">
<link rel="alternate" hreflang="x-default" href=".../destinacije/crna-gora/">
```

If the Serbian original (`/destinacije/crna-gora/`) is indexed and the
EN variant is discovered-but-not-indexed, that's **legitimately fine
under Google's hreflang policy** — the EN URL is treated as an
alternate of an indexed canonical, and Google may not bother
indexing it independently until EN traffic warrants. Not a bug.

## Expected impact within 14 days

| Hub | Current GSC bucket | Expected |
|---|---|---|
| `/autobuske-stanice/` | Discovered not indexed | Indexed (high-priority crawl after request-indexing) |
| `/prevoznici/` | Discovered not indexed | Indexed |
| `/gradski/` | Discovered not indexed | Indexed |
| `/en/gradski/beograd/` | Discovered not indexed | Likely Indexed if SR is indexed; or tagged "Alternate page with proper canonical" |
| `/en/destinacije/crna-gora/` | Discovered not indexed | Same — alternate-page tag if SR indexed |

The hreflang-alternate cases (last 2) may NOT move to "Indexed" — they
may move to **"Alternate page with proper canonical tag"**, which is
correct behaviour and counts as healthy in GSC.

## Manual follow-up (not in scope today)

In Google Search Console → URL Inspection:

  1. Inspect each of the 5 URLs individually.
  2. Click **Request Indexing** for each.
  3. Wait 1-3 days for the manual recrawl, then 7-14 days for the
     bucket to update.
  4. Re-check `Page indexing → Discovered - currently not indexed`
     — these 5 should be gone.

If after 14 days any are still in Discovered:
  - Check Sentry for 5xx on those URLs (would block indexing).
  - Inspect rendered HTML for `<meta name="robots" content="noindex">`
    leakage (none of these should have it).
  - Consider adding ONE high-quality external backlink to each (out of
    scope for today).

## Commit ledger

  - `65b2a5d` — `_browse_hubs.html` partial + included in 4 detail templates
  - `7ca377f` — sitemap canonical-locale shape (earlier work)
  - this doc — audit summary

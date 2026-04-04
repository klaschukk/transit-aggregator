# SEO Checklist — Transit Serbia

Pre-launch checklist for Google Search Console and organic search readiness.

## Domain & Infrastructure

- [ ] Domain registered and DNS configured
- [ ] HTTPS certificate installed (Let's Encrypt)
- [ ] Domain resolves correctly (A record → server IP)
- [ ] `config.py` BASE_URL updated from IP to domain
- [ ] Cloudflare (or CDN) configured
- [ ] Redirect HTTP → HTTPS
- [ ] Redirect www → non-www (or vice versa)

## Google Search Console

- [ ] Property added (domain or URL prefix)
- [ ] Ownership verified (DNS TXT record or HTML file)
- [ ] sitemap.xml submitted
- [ ] Request indexing for homepage
- [ ] Check Coverage report — no errors
- [ ] Check Mobile Usability — no issues
- [ ] Check Core Web Vitals — all green

## Sitemap (sitemap.xml)

- [x] Sitemap generates without errors
- [x] All URLs return 200 (verified via sampling)
- [x] `<lastmod>` present on all URLs (DB file mtime)
- [x] Priorities logical: / = 1.0, /rute/ = 0.8, routes = 0.7, lines = 0.5, stops = 0.4
- [x] Thin-content stops excluded (only stops with 2+ lines included)
- [x] No duplicate URLs
- [x] No 0-trip routes in sitemap
- [ ] URL count verified after domain change

## Robots.txt

- [x] Allow: /
- [x] Disallow: /api/
- [x] Disallow: /health
- [x] Disallow: /pretraga/?* (search results are noindex anyway)
- [x] Sitemap URL declared
- [ ] Sitemap URL updated to domain (not IP)

## On-Page SEO

- [x] Unique `<title>` on every page type
- [x] Unique `<meta description>` on every page type
- [x] `<link rel="canonical">` on all pages
- [x] Open Graph tags (og:title, og:description, og:url)
- [x] JSON-LD structured data: WebSite, BreadcrumbList, BusTrip, BusStop, ItemList
- [x] Breadcrumbs on all inner pages
- [x] Semantic HTML (h1, h2, nav, main, footer)
- [x] `lang="sr"` attribute on html
- [x] `<meta name="robots" content="noindex">` on search results pages
- [x] Internal linking: similar routes, nearby stops, popular lines

## Technical SEO

- [x] Mobile-first responsive design
- [x] Touch targets ≥ 44px
- [x] No horizontal scroll on 360px viewport
- [x] `<meta name="viewport">` present
- [x] favicon.svg with apple-touch-icon
- [x] Gzip compression (flask-compress)
- [ ] Page speed < 3s on 3G (test with Lighthouse)
- [ ] No render-blocking resources (CSS is single file, no external fonts)
- [ ] Image optimization (only SVG icons, no raster images)

## Content Quality

- [x] 3000+ unique indexable pages
- [x] Each route page has trips, pricing, SEO description
- [x] Each stop page has line listings, ETA estimates
- [x] Each line page has stop timeline, map
- [x] About page with mission, data sources, stats
- [ ] FAQ section on high-traffic pages
- [ ] Expand to 100+ intercity routes

## Monitoring

- [ ] Google Search Console checked weekly
- [ ] Coverage errors resolved within 48h
- [ ] Sitemap re-submitted after major data updates
- [ ] Core Web Vitals monitored monthly
- [ ] Search performance (clicks, impressions) tracked

## URL Inventory (current)

| Type | Count | Priority |
|------|-------|----------|
| Static pages | 7 | 0.3–1.0 |
| Intercity routes /rute/ | 126 | 0.7 |
| City-pair SEO /voznja/ | 126 | 0.6 |
| City lines /linija/ | 514 | 0.5 |
| Stops (2+ lines) | ~1950 | 0.4 |
| **Total** | **~2723** | |

*Stops with only 1 line (620) excluded from sitemap to avoid thin content.*

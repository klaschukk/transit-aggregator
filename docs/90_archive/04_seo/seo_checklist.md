# SEO Checklist — Prevozni

Pre-launch checklist for Google Search Console and organic search readiness.

## Domain & Infrastructure

- [ ] Domain registered and DNS configured
- [ ] HTTPS certificate installed (Let's Encrypt / Certbot)
- [ ] Domain resolves correctly (A record → 81.28.248.71)
- [ ] `config.py` BASE_URL updated from IP to `https://prevozni.com`
- [ ] systemd Environment updated with BASE_URL
- [ ] Redirect HTTP → HTTPS (Certbot auto-configures)
- [ ] Redirect www → non-www (nginx config)
- [ ] nginx serves /static/ directly with 30d cache

## Google Analytics

- [ ] GA4 property created at analytics.google.com
- [ ] Measurement ID obtained (G-XXXXXXXXXX)
- [ ] `GA_TRACKING_ID` set in systemd Environment
- [ ] Service restarted: `sudo systemctl restart transit`
- [ ] Real-time view confirms tracking is live
- [ ] Goals configured: search performed, route viewed

## Google Search Console

- [ ] Property added (domain or URL prefix)
- [ ] Ownership verified (DNS TXT record recommended)
- [ ] sitemap.xml submitted
- [ ] Request indexing for homepage
- [ ] Check Coverage report — no errors
- [ ] Check Mobile Usability — no issues
- [ ] Check Core Web Vitals — all green

## Google AdSense

- [ ] 2500+ pages indexed (wait 2-4 weeks after GSC)
- [ ] Application submitted at adsense.google.com
- [ ] Approval received
- [ ] `ADSENSE_ID` set in systemd Environment (ca-pub-XXXXXXXXXX)
- [ ] Service restarted
- [ ] Ad units configured in AdSense dashboard

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
- [x] JSON-LD structured data: WebSite, BreadcrumbList, BusTrip, BusStop, ItemList, Organization, ContactPage
- [x] Breadcrumbs on all inner pages (with BreadcrumbList JSON-LD)
- [x] Semantic HTML (h1, h2, nav, main, footer, section)
- [x] `lang="sr"` attribute on html
- [x] `<meta name="robots" content="noindex">` on search results pages
- [x] Internal linking: similar routes, nearby stops, popular lines, see-also sections

## Technical SEO

- [x] Mobile-first responsive design (breakpoints: 480, 640, 768, 1024)
- [x] Touch targets >= 44px on all interactive elements
- [x] No horizontal scroll on 360px viewport
- [x] `<meta name="viewport">` present
- [x] favicon.svg with apple-touch-icon
- [x] Gzip compression (flask-compress)
- [x] Print styles (@media print)
- [x] Skip-to-content link (accessibility)
- [x] :focus-visible styles (keyboard navigation)
- [x] ::selection color styled
- [ ] Page speed < 3s on 3G (test with Lighthouse)

## Content Quality

- [x] 2700+ unique indexable pages in sitemap
- [x] Each route page has trips, pricing, operators, SEO description
- [x] Each stop page has line listings, ETA estimates, nearby stops
- [x] Each line page has stop timeline, map, GTFS schedule
- [x] About page with mission, data sources, live stats
- [x] Contact page with form and info cards
- [x] Carriers page with operator details and route links
- [x] Stations page grouped by city
- [x] 3 cities: Beograd (514 lines), Novi Sad (61 lines), Nis (14 lines)
- [ ] Expand to 200+ intercity routes

## Monitoring

- [ ] Google Search Console checked weekly
- [ ] Google Analytics reviewed weekly
- [ ] Coverage errors resolved within 48h
- [ ] Sitemap re-submitted after major data updates
- [ ] Core Web Vitals monitored monthly
- [ ] Search performance (clicks, impressions) tracked

## URL Inventory (current)

| Type | Count | Priority |
|------|-------|----------|
| Static pages | 7 | 0.3-1.0 |
| Intercity routes /rute/ | ~195 | 0.7 |
| City-pair SEO /voznja/ | ~195 | 0.6 |
| City lines /linija/ | ~589 | 0.5 |
| Stops (2+ lines) | ~1950 | 0.4 |
| **Total** | **~2936** | |

*Stops with only 1 line excluded from sitemap to avoid thin content.*

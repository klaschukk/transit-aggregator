# Changelog

## v1.0.0 (April 2026)

Initial public release at https://prevozni.com

### Data
- 335 intercity routes, 2,838 trips, 70 operators
- 48 Serbian cities covered (population > 20K)
- 3 data sources merged with deduplication: busticket4.me, polazak.rs, srbijavoz.rs
- 4 cities with city transport: Beograd (514 lines), Novi Sad (61), Niš (53), Kragujevac (23)
- 4,522 bus stops (97% with GPS coordinates)
- GTFS schedule: 93,991 trips, 2,317,651 stop_times (94% mapped to city stops)
- 10 train stations (Srbija Voz)
- Real-time ETA at stops (GTFS + headway fallback)

### Infrastructure
- Flask + DuckDB + Gunicorn + nginx + Cloudflare
- Domain: prevozni.com with Cloudflare SSL (Full mode)
- nginx reverse proxy with Cloudflare-only IP allowlist, security headers
- Gunicorn: 2 workers with max-requests recycling for memory stability
- Healthcheck cron (*/5 min) with auto-restart
- Nightly coordinate enrichment (Overpass API + Nominatim)

### SEO
- 4,632 indexable pages in sitemap.xml
- JSON-LD: WebSite, ItemList, BusStop, BusTrip, FAQPage, BreadcrumbList
- OpenGraph tags on all pages
- Canonical URLs (https://prevozni.com/...)
- robots.txt with API/health disallow
- noindex on filtered views (?dan=) and empty routes
- Lazy loading on /rute/ (50 visible + "Prikaži još" button)

### Analytics & Monitoring
- Umami analytics
- Telegram bot notifications (contact form)

### Performance
- Homepage: 1,007 req/sec, p95 = 21ms
- Route detail: 153 req/sec, p95 = 66ms
- Stop detail: 113 req/sec, p95 = 143ms
- DuckDB connection pooling with TTL cache

### Testing
- 325 pytest tests covering routes, APIs, data quality, SEO

### Scrapers
- `scrape_gsp.py` — GSP Beograd (bgprevoz.rs API)
- `scrape_gspns.py` — JGSP Novi Sad (gspns.co.rs)
- `scrape_intercity.py` — busticket4.me JSON API (48 cities, 562 pairs)
- `scrape_srbvoz.py` — Srbija Voz trains (w3.srbvoz.rs)
- `scrape_lasta.py` — polazak.rs (302 routes, 68 operators via __NEXT_DATA__)
- `scrape_naissus.py` — JGP Niš (jgpnis.rs + Overpass)
- `scrape_kragujevac.py` — Kragujevac (Overpass API)
- `enrich_stops_coords.py` — OSM Overpass + Nominatim geocoding
- `build_db.py` — Merges all sources into DuckDB with deduplication

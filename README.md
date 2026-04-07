# Prevozni

Free public transit aggregator for Serbia — intercity buses/trains + city transport for 4 cities.

**Live:** https://prevozni.com

## Features

- **335 intercity routes**, 2,838 trips, 70 operators — prices, schedules, carriers
- **651 city transit lines** across 4 cities (bus, tram, trolleybus, night, e-bus, BG Voz)
- **4,522 stops** with GPS coordinates and interactive Leaflet maps
- **Real-time GTFS schedules** (94K trips, 2.3M stop_times) with ETA at every stop
- **Programmatic SEO**: 4,600+ indexable pages, JSON-LD, FAQ schema, sitemap
- City autocomplete, trip filtering, mobile-first responsive design

## Cities

| City | Lines | Stops | Source |
|------|-------|-------|--------|
| Beograd | 514 | 3,547 | GSP (bgprevoz.rs) + GTFS |
| Novi Sad | 61 | 523 | JGSP (gspns.co.rs) + GTFS |
| Niš | 53 | 345 | JGP (jgpnis.rs) + OSM Overpass |
| Kragujevac | 23 | 107 | OSM Overpass |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python 3.12) |
| Database | DuckDB (read-only, file-based) |
| WSGI | Gunicorn (2 workers, max-requests recycling) |
| Reverse proxy | nginx (Cloudflare-only IPs) |
| SSL | Cloudflare (Full mode) |
| Process | systemd |
| Maps | Leaflet.js + OpenStreetMap |
| Analytics | Umami |
| Data | Scrapers (bgprevoz, gspns, busticket4.me, srbijavoz, polazak.rs) + GTFS |

## Quick Start

```bash
git clone <repo-url> && cd transit
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Build database from scraped data
python data/pipelines/scrape_gsp.py
python data/pipelines/scrape_gspns.py
python data/pipelines/scrape_intercity.py
python data/pipelines/scrape_srbvoz.py
python data/pipelines/scrape_lasta.py
python data/pipelines/build_db.py

# Run dev server
python run.py
```

Open http://localhost:5000

## URL Architecture

| Pattern | Description | Count |
|---------|-------------|-------|
| `/rute/{slug}/` | Intercity route (schedule, prices) | 335 |
| `/voznja/{from}-do-{to}/` | City pair SEO page + FAQ | 335 |
| `/gradski/{city}/linija/{slug}/` | City transit line (map, stops, GTFS) | 651 |
| `/gradski/{city}/stajaliste/{slug}/` | Stop (lines, ETA, GTFS schedule) | 4,522 |
| `/api/cities?q=` | City autocomplete | — |
| `/api/stop-arrivals?slug=` | Live ETA for stop | — |
| `/sitemap.xml` | Auto-generated sitemap | 4,632 URLs |

## Database (DuckDB)

| Table | Rows | Description |
|-------|------|-------------|
| city_lines | 651 | Transit lines (4 cities) |
| city_stops | 4,522 | Stops with coordinates (97% GPS) |
| city_line_stops | 22,727 | Line-stop associations |
| routes | 335 | Intercity routes (48 cities) |
| trips | 2,838 | Departures with prices (deduped from 3 sources) |
| operators | 70 | Bus/train carriers |
| stations | 10 | Train stations |
| gtfs_trips | 93,991 | GTFS trip records |
| gtfs_stop_times | 2,317,651 | GTFS schedule data (94% mapped) |

## Tests

```bash
python -m pytest tests/ -v
# 325 passed — routes, APIs, data quality, SEO checks
```

## Production Deployment

```bash
# systemd service
sudo systemctl start transit
sudo systemctl status transit

# Health check
curl https://prevozni.com/health
# {"status":"ok","db":true,"service":"prevozni"}
```

## License

MIT

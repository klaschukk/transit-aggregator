# Transit Srbija

Free public transit aggregator for Serbia — intercity buses/trains + Belgrade city transport.

**Live:** http://81.28.248.71:5000/

## Features

- **26 intercity routes**, 243 trips with prices, operators, schedules
- **514 city transit lines** (bus, tram, trolleybus, night, e-bus, BG Voz)
- **2,500+ stops** with GPS coordinates and interactive Leaflet maps
- **Real-time GTFS schedules** (2.2M stop_times) with ETA at every stop
- **Programmatic SEO**: 3,100+ indexable pages, JSON-LD, FAQ schema, sitemap
- City autocomplete, trip filtering, mobile-first responsive design

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python 3.12) |
| Database | DuckDB (read-only, file-based) |
| WSGI | Gunicorn (4 workers) |
| Process | systemd |
| Compression | flask-compress (gzip) |
| Maps | Leaflet.js + OpenStreetMap |
| Data | Scrapers (bgprevoz.rs, busticket4.me, srbijavoz.rs) + GTFS |

## Quick Start

```bash
git clone <repo-url> && cd transit
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Build database from scraped data
python data/pipelines/scrape_gsp.py
python data/pipelines/scrape_intercity.py
python data/pipelines/scrape_srbvoz.py
python data/pipelines/build_db.py

# Run dev server
python run.py
```

Open http://localhost:5000

## Project Structure

```
transit/
├── app/
│   ├── __init__.py          # create_app(), error handlers, gzip
│   ├── db.py                # query(), cached_query(), db_ready()
│   ├── routes/
│   │   ├── main.py          # /, /pretraga/, /api/cities, sitemap, health
│   │   ├── intercity.py     # /rute/, /rute/{slug}/, /voznja/
│   │   ├── city.py          # /gradski/, /api/city-stops, /api/stop-arrivals
│   │   └── info.py          # /o-nama/, /kontakt/, /prevoznici/, /stanice/
│   ├── templates/           # 23 Jinja2 templates + 8 partials
│   └── static/css/app.css   # Single CSS file, mobile-first
├── data/
│   ├── pipelines/           # Scrapers + build_db.py
│   ├── dbs/transit.duckdb   # Production database (gitignored)
│   └── gtfs/                # GTFS feed data
├── tests/                   # pytest (43 tests)
├── config.py                # Dev/Production config
├── run.py                   # Dev server entry point
└── requirements.txt
```

## URL Architecture

| Pattern | Description | Count |
|---------|-------------|-------|
| `/rute/{slug}/` | Intercity route (schedule, prices) | 26 |
| `/voznja/{from}-do-{to}/` | City pair SEO page + FAQ | 26 |
| `/gradski/{city}/linija/{slug}/` | City transit line (map, stops, GTFS) | 514 |
| `/gradski/{city}/stajaliste/{slug}/` | Stop (lines, ETA, GTFS schedule) | 2,500+ |
| `/api/cities?q=` | City autocomplete | — |
| `/api/stop-arrivals?slug=` | Live ETA for stop | — |
| `/sitemap.xml` | Auto-generated sitemap | 3,100+ URLs |

## Database (DuckDB)

| Table | Rows | Description |
|-------|------|-------------|
| city_lines | 514 | Belgrade transit lines |
| city_stops | 2,572 | Stops with coordinates |
| city_line_stops | 12,437 | Line-stop associations |
| routes | 26 | Intercity routes |
| trips | 243 | Departures with prices |
| operators | 7 | Bus/train carriers |
| stations | 10 | Train stations |
| gtfs_trips | 14,700+ | GTFS trip records |
| gtfs_stop_times | 2.2M | GTFS schedule data |

## Tests

```bash
python -m pytest tests/ -v
# 43 passed — routes, APIs, SEO checks
```

## Production Deployment

```bash
# systemd service
sudo systemctl start transit
sudo systemctl status transit

# Health check
curl http://localhost:5000/health
# {"status":"ok","db":true,"service":"transit-serbia"}
```

## License

MIT

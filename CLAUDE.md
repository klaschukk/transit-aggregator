# CLAUDE.md — Transit Serbia Project Context

## Project Overview

**Transit Serbia** — Serbian public transport aggregator (programmatic SEO + live data).
Combines city transit (Belgrade buses) + inter-city travel (buses, trains, flights).

- **Stack:** Flask + DuckDB + RKE2/K8s + ArgoCD + Cloudflare
- **Target:** €100/month in first 6 months, €600/month by month 18
- **Scale:** 10K–50K indexable pages (city pairs, stops, routes)
- **Phase:** Foundation (March 2026)
- **Server:** montiko (Podgorica), K8s cluster: pumba/simba/timon

## Language & Communication

- Documentation and communication: **Russian**
- Code, code comments, commits: **English**
- Variable and file names: **English**

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python) |
| Database | DuckDB (read-only, file-based) |
| Infra | RKE2/K8s (pumba/simba/timon) |
| Deploy | ArgoCD (GitOps, via tags) |
| CDN/WAF | Cloudflare |
| Analytics | Umami (self-hosted) |
| Monetization | Google AdSense + busticket4.me affiliate |
| AI | Claude API (content generation) |
| Data | Web scraping + GTFS |

## URL Architecture

```
/                               — homepage (search form)
/rute/                          — route index
/rute/{slug}/                   — route detail (e.g., /rute/beograd-novi-sad/)
/stajaliste/{city}/{slug}/      — bus stop page
/voznja/{from}-do-{to}/         — city pair travel page (SEO)
/red-voznje/{operator}/{slug}/  — operator schedule
/gradski/{city}/                — city transport hub (Belgrade buses)
/gradski/{city}/linija/{num}/   — specific bus line
/gradski/{city}/stajaliste/{id}/ — city bus stop
```

## Project Structure

```
transit/
├── CLAUDE.md              ← this file
├── README.md
├── config.py              ← Flask config (DuckDB path, secrets)
├── run.py                 ← dev server entry
├── requirements.txt
├── .claude/               ← Claude Code settings
├── docs/
│   ├── 00_strategy/       ← roadmap, competitor analysis, backlog
│   ├── 01_brand/          ← brand, colors
│   ├── 02_data/           ← data sources, pipeline design
│   ├── 03_product/        ← page templates, UX
│   ├── 04_seo/            ← SEO strategy, keywords
│   ├── 05_monetization/   ← AdSense, affiliate
│   ├── 06_tech/           ← infra, deploy
│   └── 07_legal/          ← GDPR, disclaimers
├── app/
│   ├── __init__.py
│   ├── db.py              ← DuckDB connection
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py        ← homepage, search
│   │   ├── intercity.py   ← inter-city routes
│   │   └── city.py        ← city transport (Belgrade)
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── route_detail.html
│   │   ├── city_pair.html
│   │   ├── stop.html
│   │   └── city_transport.html
│   └── static/
│       ├── css/main.css
│       └── js/search.js
├── data/
│   ├── pipelines/
│   │   ├── scrape_gsp.py       ← Belgrade city buses (GSP)
│   │   ├── scrape_srbvoz.py    ← Serbian trains
│   │   ├── scrape_intercity.py ← inter-city buses
│   │   └── build_db.py         ← compile DuckDB from raw data
│   ├── dbs/
│   │   └── transit.duckdb      ← main database (gitignored)
│   └── raw/                    ← scraped raw data (gitignored)
├── scripts/
│   └── refresh_data.sh         ← cron: daily data refresh
└── tests/
```

## Key Design Decisions

1. **SEO-first** — every page decision evaluated through SEO impact
2. **Programmatic content** — pages generated from structured data
3. **DuckDB read-only** — DB rebuilt by pipelines, Flask only reads
4. **GTFS-compatible** — data model mirrors GTFS for future compatibility
5. **City-first** — Belgrade city transport is primary differentiator vs. competitors
6. **Scraping-based** — no public APIs in Serbia; scrape gsp.rs, srbvoz.rs, busticket4.me

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| gsp.rs | Belgrade city bus routes/stops | Web scraping |
| srbvoz.rs | Train schedules | Web scraping |
| busticket4.me | Inter-city bus schedules | Web scraping |
| lasta.rs | Lasta bus routes | Web scraping |
| OpenStreetMap | Stop locations, geodata | Overpass API (free) |
| transitfeeds.com | GTFS if available | Check availability |

## Coding Conventions

- Python: PEP 8, type hints, f-strings, max 120 chars/line
- Docstrings: Google style, public functions only
- Templates: Jinja2, 2-space indent
- CSS: BEM naming, custom properties (--color-primary, --space-4)
- Git: conventional commits (feat:, fix:, docs:, data:, infra:)
- Branches: feature/, fix/, data/, docs/

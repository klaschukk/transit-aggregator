"""Pre-generate AI itineraries for far-destination /voznja pages (Phase 2 SEO).

Composes a curated seed of (SR hub) × (far destination) pairs via Groq and
stores them in the analytics `composed_routes` cache, so the indexable
`/voznja/<sr>-do-<far>/` guide pages render instantly and show up in
`sitemap-far.xml`. Idempotent — already-cached pairs are skipped, so it is
safe to re-run (e.g. after adding cities to bookaway_far.json).

This script is the ONLY Groq warm-up path for these pages: the city_pair
request handler is cache-only by design (Googlebot must never wait ~20s for
a model call, and indexability must not flip with model availability).

WHY ALL THREE LANGUAGES (hreflang consistency):
    base.html unconditionally emits <link rel="alternate" hreflang="sr|en|ru">
    on every page — it has no per-page notion of "this variant exists". A far
    guide whose itinerary is cached only for sr would therefore advertise
    /en/ + /ru/ alternates that render as noindex thin pages — an
    inconsistent hreflang cluster in Google's eyes. Rather than making
    base.html's hreflang conditional (invasive, affects every template), we
    pre-generate ALL of SUPPORTED_LANGS here so every advertised alternate
    really is an indexable page. If a language is ever dropped from the seed,
    base.html must learn per-page hreflang first.

Run AFTER deploy, on the prod box (the cache lives in the analytics DB there):

    GROQ_API_KEY=... ./venv/bin/python scripts/pregen_far_routes.py
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import analytics_db, create_app  # noqa: E402
from app.affiliates.partners import FAR_DESTINATIONS  # noqa: E402
from app.ai_compose import compose_itinerary_via_groq  # noqa: E402
from app.i18n import SUPPORTED_LANGS  # noqa: E402
from app.slug import slugify_serbian as _sl  # noqa: E402

# Top origins (where most of our users start) × marquee far destinations
# (highest search intent). Re-run with a longer list to widen coverage.
SR_HUBS = ['Beograd', 'Novi Sad', 'Niš', 'Kragujevac']
TOP_FAR = [
    'bangkok', 'phuket', 'chiang-mai', 'krabi', 'bali', 'denpasar', 'ubud',
    'hanoi', 'ho-chi-minh', 'da-nang', 'phnom-penh', 'siem-reap',
    'kuala-lumpur', 'singapore', 'manila', 'cebu', 'colombo', 'delhi', 'goa',
    'mumbai', 'kathmandu', 'tokyo', 'kyoto', 'seoul', 'dubai', 'abu-dhabi',
    'doha', 'cairo', 'hurghada',
]


# Groq's 70B tier allows ~30 requests/minute; stay just under it.
REQUEST_GAP = 2.2
MAX_ATTEMPTS = 3
RETRY_BACKOFF = 5.0


def main() -> None:
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        analytics_db.init_schema()
        key = app.config.get('GROQ_API_KEY', '')
        if not key:
            print('ERROR: GROQ_API_KEY not set'); return
        ok = skipped = failed = 0
        for hub in SR_HUBS:
            hub_slug = _sl(hub)
            for far_slug in TOP_FAR:
                meta = FAR_DESTINATIONS.get(far_slug)
                if not meta:
                    continue
                pair_key = f'{hub_slug}:{far_slug}'
                disp = meta.get('display', far_slug.replace('-', ' ').title())
                # All langs per pair: base.html advertises hreflang sr/en/ru
                # unconditionally, so every variant must be a real page.
                for lang in SUPPORTED_LANGS:
                    if analytics_db.get_composed_route(pair_key, lang):
                        skipped += 1
                        continue
                    # Groq rate-limits the 70B model to roughly 30 requests a
                    # minute; the old 0.4s gap asked for ~150/min, so most
                    # calls came back 429 and compose_itinerary_via_groq —
                    # which swallows every error — reported them as plain
                    # failures (272 of 348 on the first full run). Pace the
                    # calls and retry with a widening backoff.
                    data = None
                    for attempt in range(MAX_ATTEMPTS):
                        data = compose_itinerary_via_groq(
                            hub, disp, lang, key, timeout=25)
                        if data and data.get('feasible'):
                            break
                        if attempt < MAX_ATTEMPTS - 1:
                            time.sleep(RETRY_BACKOFF * (attempt + 1))
                    if data and data.get('feasible'):
                        analytics_db.upsert_composed_route(
                            pair_key, lang, hub, disp,
                            json.dumps(data, ensure_ascii=False),
                        )
                        ok += 1
                        print(f'OK   {pair_key} [{lang}]')
                    else:
                        failed += 1
                        print(f'FAIL {pair_key} [{lang}]')
                    time.sleep(REQUEST_GAP)
        print(f'\nDone: {ok} composed, {skipped} cached, {failed} failed')


if __name__ == '__main__':
    main()

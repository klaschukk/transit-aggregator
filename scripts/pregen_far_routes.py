"""Pre-generate AI itineraries for far-destination /voznja pages (Phase 2 SEO).

Composes a curated seed of (SR hub) × (far destination) pairs via Groq and
stores them in the analytics `composed_routes` cache, so the indexable
`/voznja/<sr>-do-<far>/` guide pages render instantly and show up in
`sitemap-pairs.xml`. Idempotent — already-cached pairs are skipped, so it is
safe to re-run (e.g. after adding cities to bookaway_far.json).

Run AFTER deploy (the route/template that render these pages must be live):

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
from app.slug import slugify_serbian as _sl  # noqa: E402

LANG = 'sr'  # canonical /voznja language

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
                if analytics_db.get_composed_route(pair_key, LANG):
                    skipped += 1
                    continue
                disp = meta.get('display', far_slug.replace('-', ' ').title())
                data = compose_itinerary_via_groq(hub, disp, LANG, key, timeout=25)
                if data and data.get('feasible'):
                    analytics_db.upsert_composed_route(
                        pair_key, LANG, hub, disp,
                        json.dumps(data, ensure_ascii=False),
                    )
                    ok += 1
                    print(f'OK   {pair_key}')
                else:
                    failed += 1
                    print(f'FAIL {pair_key}')
                time.sleep(0.4)  # be gentle on the Groq endpoint
        print(f'\nDone: {ok} composed, {skipped} cached, {failed} failed')


if __name__ == '__main__':
    main()

"""Price wording for titles / meta descriptions (what Google shows).

Fares are stored in RSD. For a route with both ends outside Serbia (Budva ->
Kotor, Mostar -> Budva, Podgorica -> Sarajevo ...) the traveller pays in euro
and searches in euro, so "from 409 RSD" in the snippet reads as a foreign
price; those get "from 3.5 €". Anything touching Serbia keeps RSD.
"""
from functools import lru_cache

from flask import current_app

from app.slug import normalize_slug


@lru_cache(maxsize=1)
def _foreign_slugs() -> frozenset[str]:
    from app.routes.info import _COUNTRY_HUBS
    return frozenset(normalize_slug(c) for hub in _COUNTRY_HUBS.values() for c in hub['cities'])


def is_euro_pair(from_slug: str, to_slug: str) -> bool:
    foreign = _foreign_slugs()
    return bool(from_slug) and bool(to_slug) and from_slug in foreign and to_slug in foreign


def snippet_price(rsd, from_slug: str, to_slug: str) -> str:
    """'409 RSD', or '3.5 €' / '27 €' on a route outside Serbia."""
    if not is_euro_pair(from_slug, to_slug):
        return f'{rsd} RSD'
    eur = float(rsd) / current_app.config.get('EUR_RSD_RATE', 117)
    return f'{eur:.1f}'.rstrip('0').rstrip('.') + ' €' if eur < 10 else f'{round(eur)} €'

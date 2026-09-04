"""Best-option badges shared by route_detail, city_pair and search.

Tags a single cheapest / fastest trip in a list so _trip_card.html can
render its is_cheapest / is_fastest badge. Only route_detail computed
this until now — city_pair (/voznja/) and search (/pretraga/) render the
exact same trip_card macro but never set the flags it looks for.
"""


def tag_best_trips(trips, min_plausible_duration=0):
    """Mutates trips in place, setting is_cheapest/is_fastest on one dict each.

    Only tags when there's a real spread (>1 comparable trip, min != max) so
    a lone trip or an all-equal list never gets badged. min_plausible_duration
    filters out scraped duration_min outliers (parser quirks on midnight-
    crossing/malformed arrival_time) before picking the fastest.
    """
    if len(trips) <= 1:
        return

    prices = [t['price_rsd'] for t in trips if t.get('price_rsd')]
    if len(prices) > 1 and min(prices) != max(prices):
        price_min = min(prices)
        next(t for t in trips if t.get('price_rsd') == price_min)['is_cheapest'] = True

    durs = [t['duration_min'] for t in trips
            if t.get('duration_min') and t['duration_min'] >= min_plausible_duration]
    if len(durs) > 1 and min(durs) != max(durs):
        d_min = min(durs)
        next(t for t in trips if t.get('duration_min') == d_min)['is_fastest'] = True

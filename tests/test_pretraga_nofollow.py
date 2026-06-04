"""robots.txt blocks /pretraga/?* (search-result query URLs) on purpose, but
Google was still indexing them ("indexed though blocked by robots") because
internal <a> links pointed at them. We keep the robots block and remove the
discovery signal: every internal link to a /pretraga/?<query> URL must be
rel="nofollow". (One mechanism, not robots-block + noindex which conflict.)
"""

import re

# Pages that render "search from here" / "popular pair" shortcut links.
PAGES = [
    "/pretraga/?od=Beograd&do=Novi+Sad",
    "/gradski/beograd/",
    "/gradski/beograd/linija/linija-2a/",
    "/gradski/beograd/stajaliste/sajam/",
]

# Whole <a ...> opening tag that links to a /pretraga/?<query> URL. [^>] also
# matches newlines, so multi-line anchor tags are captured too.
ANCHOR = re.compile(r'<a\b[^>]*?href="[^"]*?/pretraga/\?[^"]*"[^>]*>', re.I)


def test_query_search_links_are_nofollow(client):
    for url in PAGES:
        html = client.get(url).data.decode()
        for tag in ANCHOR.findall(html):
            assert 'rel="nofollow"' in tag, \
                f"{url}: /pretraga/?* link missing rel=nofollow -> {tag[:120]}"


def test_at_least_one_search_link_exists(client):
    """Guard: if templates change so no pages emit these links, the test above
    would pass vacuously. Assert we are actually exercising the rule."""
    total = sum(len(ANCHOR.findall(client.get(u).data.decode())) for u in PAGES)
    assert total > 0, "no /pretraga/?* links found to assert nofollow on"


def test_robots_still_blocks_pretraga_query(client):
    """The block must stay — nofollow complements it, does not replace it."""
    robots = client.get("/robots.txt").data.decode()
    assert "Disallow: /pretraga/?*" in robots

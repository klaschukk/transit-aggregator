"""Search-result pages (/pretraga/?<query>) must stay OUT of the index via
noindex, and Google must be able to READ that noindex — so /pretraga is NOT
robots-blocked.

History: robots.txt used to `Disallow: /pretraga/?*`. But every search page
also sends noindex (meta + X-Robots-Tag), and a robots block prevents Google
from crawling the page to see it — so query URLs already indexed froze as
"Indexed, though blocked by robots.txt" (69 in GSC), undeindexable. The block
and the noindex were fighting each other.

Resolution (one coherent mechanism):
  * noindex on the page  → already-indexed URLs get crawled and dropped.
  * rel="nofollow" on every internal /pretraga/?<query> link + absence from
    the sitemap → Google does not discover NEW query URLs to crawl.
The robots block is gone; noindex is the single deindex signal.
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


def test_robots_does_not_block_pretraga(client):
    """robots must NOT block /pretraga — otherwise Google can't read the
    noindex and the query URLs freeze as "indexed though blocked by robots"."""
    robots = client.get("/robots.txt").data.decode()
    assert "Disallow: /pretraga" not in robots


def test_search_page_is_noindex(client):
    """The deindex signal must be present and readable: noindex header on the
    search page (it is now crawlable, so this header is what keeps it out)."""
    resp = client.get("/pretraga/?od=Beograd&do=Novi+Sad")
    assert "noindex" in resp.headers.get("X-Robots-Tag", "")

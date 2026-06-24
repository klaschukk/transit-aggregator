"""The /red-voznje/ head-term hub: indexable, links the programmatic pages,
and is advertised in the sitemap + footer so it accrues and passes link equity."""


def test_hub_renders_and_indexable(client):
    r = client.get('/red-voznje/')
    assert r.status_code == 200
    html = r.data.decode()
    assert 'Red vožnje autobusa, vozova' in html  # H1 / head term
    assert 'noindex' not in html.lower()


def test_hub_funnels_to_programmatic_pages(client):
    html = client.get('/red-voznje/').data.decode()
    # It must link out to routes, city transport and carriers (the link-equity
    # funnel + Google's "related pages" signal for the broad query).
    assert '/rute/' in html
    assert '/gradski/' in html
    assert '/prevoznici/' in html


def test_hub_in_sitemap_core(client):
    assert '/red-voznje/' in client.get('/sitemap-core.xml').data.decode()


def test_hub_linked_from_footer(client):
    # Site-wide footer link → crawled from every page, passes equity.
    assert '/red-voznje/' in client.get('/rute/').data.decode()


def test_hub_localised(client):
    assert client.get('/en/red-voznje/').status_code == 200
    assert client.get('/ru/red-voznje/').status_code == 200

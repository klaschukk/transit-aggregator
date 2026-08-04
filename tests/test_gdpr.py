"""GDPR / AdSense compliance: cookie banner, Terms of Service,
Cookie Policy — all 3 languages, sitemap, no noindex on legal pages."""


def test_cookie_banner_renders_on_home(client):
    """Banner partial is included in base.html and reaches every page."""
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data
    assert b'id="cookieBanner"' in html
    assert b'data-consent="all"' in html
    assert b'data-consent="essential"' in html


def test_cookie_banner_links_to_policy(client):
    resp = client.get("/")
    assert b'/politika-kolacica/' in resp.data


def test_terms_page_sr(client):
    resp = client.get("/uslovi/")
    assert resp.status_code == 200
    assert b"Uslovi" in resp.data


def test_terms_page_en(client):
    resp = client.get("/en/uslovi/")
    assert resp.status_code == 200
    assert b"Terms of Service" in resp.data


def test_terms_page_ru(client):
    resp = client.get("/ru/uslovi/")
    assert resp.status_code == 200


def test_cookie_policy_page_sr(client):
    resp = client.get("/politika-kolacica/")
    assert resp.status_code == 200
    assert b"kola" in resp.data.lower()


def test_cookie_policy_page_en(client):
    resp = client.get("/en/politika-kolacica/")
    assert resp.status_code == 200
    assert b"Cookie Policy" in resp.data


def test_cookie_policy_page_ru(client):
    resp = client.get("/ru/politika-kolacica/")
    assert resp.status_code == 200


def test_legal_pages_in_sitemap(client):
    resp = client.get("/sitemap-core.xml")
    assert b"/uslovi/" in resp.data
    assert b"/politika-kolacica/" in resp.data


def test_legal_pages_not_noindex(client):
    """AdSense requires indexable legal pages. Default robots meta is
    `index, follow` and no page-level override is set, so verify none of
    the pages accidentally emit `noindex`."""
    for path in ("/uslovi/", "/politika-kolacica/", "/privatnost/"):
        resp = client.get(path)
        assert resp.status_code == 200, path
        assert b"noindex" not in resp.data, path


def test_footer_exposes_legal_links(client):
    resp = client.get("/")
    assert b"/uslovi/" in resp.data
    assert b"/politika-kolacica/" in resp.data


def test_umami_no_unconditional_script_tag(client):
    """The compliance-critical change: the previously unconditional
    `<script defer src="…/umami">` tag has been replaced with a consent-
    gated inline loader. Verify no direct async/defer <script> tag still
    links to Umami in the rendered markup (consent-aware JS may still
    reference the URL as a string for dynamic appendChild)."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'<script defer src="https://analytics.farmako.ro/umami"' not in resp.data
    assert b'<script async src="https://analytics.farmako.ro/umami"' not in resp.data


def test_contact_error_is_visible_and_announced(client):
    """A failed submit must look and sound like a failure.

    .alert--error was referenced by contact.html and defined in no
    stylesheet, so the message rendered on the bare .alert layout —
    transparent background, body-text ink, no border — and carried no
    role, so a screen reader was told nothing at all. The page reloads
    on failure, which is precisely when the user needs a signal.
    """
    resp = client.post('/kontakt/', data={'name': 'x', 'email': 'nope',
                                          'message': 'hi'},
                       follow_redirects=True)
    body = resp.data.decode()
    if 'alert--error' not in body:
        import pytest
        pytest.skip('validation did not reject this payload')
    assert 'role="alert"' in body, 'error alert is not announced'

    css = client.get('/static/css/app.css').data.decode()
    assert '.alert--error {' in css, '.alert--error has no rule of its own'
    assert '--color-danger-bg' in css.split('.alert--error {', 1)[1][:300], \
        'error alert must use the danger tokens, not inherit body colours'

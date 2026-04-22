"""Tests for activation-phase UI + plumbing.

Scope:
- /ads.txt is served (empty body OK — AdSense approval pending)
- Newsletter form renders on footer (every page), home hero, route price-alert
- Form fields are wired for /api/subscribe (name=email, consent, source)
- Consent checkbox is required per GDPR
"""

import pytest


def test_ads_txt_served(client):
    r = client.get('/ads.txt')
    assert r.status_code == 200
    assert r.headers['Content-Type'].startswith('text/plain')
    # Either pending-comment OR populated google.com record
    body = r.data.decode()
    assert 'ads.txt' in body or 'google.com' in body


def test_newsletter_form_on_home(client):
    html = client.get('/').data.decode()
    # Two forms expected: hero variant + footer variant
    assert html.count('<form class="newsletter-form') == 2
    assert 'newsletter-form--hero' in html
    assert 'newsletter-form--footer' in html


def test_newsletter_form_on_route_detail(client):
    html = client.get('/rute/beograd-novi-sad/').data.decode()
    # price_alert variant + footer variant
    assert html.count('<form class="newsletter-form') == 2
    assert 'newsletter-form--price_alert' in html
    assert 'newsletter-form--footer' in html


@pytest.mark.parametrize("url", [
    '/', '/rute/', '/o-nama/', '/kontakt/', '/gradski/beograd/',
    '/rute/beograd-novi-sad/', '/voznja/beograd-do-novi-sad/',
])
def test_footer_newsletter_everywhere(client, url):
    html = client.get(url).data.decode()
    assert 'newsletter-form--footer' in html, (
        f"footer newsletter form missing on {url}"
    )


def test_newsletter_form_fields(client):
    html = client.get('/').data.decode()
    # Email input, submit button, consent checkbox, hidden source, POST action
    assert 'action="/api/subscribe"' in html
    assert 'name="email"' in html
    assert 'name="consent"' in html
    assert 'name="source"' in html
    # Consent must be required (GDPR enforced server-side too)
    assert 'type="checkbox" name="consent" value="1" required' in html


def test_newsletter_form_has_status_slot(client):
    """The JS handler writes success/error messages into this aria-live
    region; without it the UX goes silent on the user after submit."""
    html = client.get('/').data.decode()
    assert 'newsletter-form__status' in html
    assert 'aria-live="polite"' in html

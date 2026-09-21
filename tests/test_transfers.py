"""Door-to-door (transfer / rental car) offers on tourist corridors."""
from types import SimpleNamespace

import pytest

from app.affiliates.transfers import is_tourist_corridor, transfer_offers


@pytest.fixture
def cfg(app):
    keys = ('AFF_TRANSFER_URL', 'AFF_TRANSFER_NAME', 'AFF_CARS_URL', 'AFF_CARS_NAME')
    saved = {k: app.config.get(k) for k in keys}
    yield app.config
    for k, v in saved.items():
        app.config[k] = v


def _offers(app, *a, **kw):
    with app.app_context():
        return transfer_offers(*a, **kw)


def test_corridor_rules():
    assert is_tourist_corridor('podgorica', 'kotor')
    assert is_tourist_corridor('mostar', 'kotor')
    assert not is_tourist_corridor('beograd', 'budva')       # 10 h coach, not a transfer
    assert not is_tourist_corridor('kotor', 'kotor')
    assert not is_tourist_corridor('', 'kotor')


def test_dormant_until_a_link_is_configured(app, cfg):
    cfg['AFF_TRANSFER_URL'] = ''
    cfg['AFF_CARS_URL'] = ''
    assert _offers(app, 'podgorica', 'kotor') == []


def test_offers_for_corridor_with_placeholders_encoded(app, cfg):
    cfg['AFF_TRANSFER_URL'] = 'https://partner.example/t?from={from_name}&to={to}'
    cfg['AFF_TRANSFER_NAME'] = 'Acme'
    cfg['AFF_CARS_URL'] = 'https://cars.example/?ref=1'
    out = _offers(app, 'podgorica', 'kotor', 'Podgorica Airport', 'Kotor')
    assert [o['key'] for o in out] == ['transfer', 'cars']
    assert out[0]['url'] == 'https://partner.example/t?from=Podgorica%20Airport&to=kotor'
    assert out[0]['name'] == 'Acme' and out[1]['name'] == ''


def test_non_corridor_gets_nothing_even_when_configured(app, cfg):
    cfg['AFF_TRANSFER_URL'] = 'https://partner.example/t'
    assert _offers(app, 'beograd', 'nis') == []


@pytest.mark.parametrize('bad', ['javascript:alert(1)', 'http://insecure.example', 'data:text/html,x', '//evil.example'])
def test_only_https_links_are_emitted(app, cfg, bad):
    cfg['AFF_TRANSFER_URL'] = bad
    assert _offers(app, 'podgorica', 'kotor') == []


def _render(app):
    from flask import render_template
    route = SimpleNamespace(slug='podgorica-kotor', from_city='Podgorica', to_city='Kotor')
    with app.test_request_context('/en/'):
        return render_template('_partials/_transfer_offer.html', route=route,
                               _from_slug='podgorica', _to_slug='kotor')


def test_partial_renders_nothing_when_dormant(app, cfg):
    cfg['AFF_TRANSFER_URL'] = ''
    cfg['AFF_CARS_URL'] = ''
    assert 'transfer-offer' not in _render(app)


def test_partial_markup_is_a_disclosed_sponsored_link(app, cfg):
    cfg['AFF_TRANSFER_URL'] = 'https://partner.example/t'
    cfg['AFF_TRANSFER_NAME'] = 'Acme'
    cfg['AFF_CARS_URL'] = ''
    html = _render(app)
    assert 'rel="sponsored nofollow noopener"' in html
    assert 'data-partner="transfer"' in html and 'data-route-slug="podgorica-kotor"' in html
    assert 'Acme' in html
    assert 'data-partner="cars"' not in html
    assert 'transfer-offer__note' in html         # the affiliate disclosure is on the block


def test_ba_click_accepts_transfer_and_cars_partners(app):
    """The partner allowlist must not bucket the new keys into 'other'."""
    import inspect
    from app.routes import main
    src = inspect.getsource(main.api_ba_click)
    assert "'transfer'" in src and "'cars'" in src


def test_local_json_supplies_links_and_env_wins(tmp_path, monkeypatch):
    import config
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data' / 'affiliates.local.json').write_text(
        '{"AFF_CARS_URL": "https://cars.example/x", "AFF_CARS_NAME": "Acme"}')
    monkeypatch.setattr(config, 'BASE_DIR', tmp_path)
    assert config._local_aff('AFF_CARS_URL') == 'https://cars.example/x'
    assert config._local_aff('MISSING') == ''
    (tmp_path / 'data' / 'affiliates.local.json').write_text('not json')
    assert config._local_aff('AFF_CARS_URL') == ''        # broken file never breaks the app

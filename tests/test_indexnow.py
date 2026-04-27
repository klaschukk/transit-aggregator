"""IndexNow key-file route tests.

The /<key>.txt endpoint is IndexNow's domain-ownership proof: the
verifier hits this URL and checks the body matches the key from our
urlList POST. If we ever break this route, every Bing/Yandex re-crawl
ping silently fails with 403.

The key itself lives at data/secrets/indexnow.key (gitignored). Tests
read it directly so they validate against the same source the route
does, no copy-paste drift.
"""
from pathlib import Path

import pytest


KEY_FILE = Path(__file__).parent.parent / 'data' / 'secrets' / 'indexnow.key'


def _read_key():
    if not KEY_FILE.exists():
        pytest.skip('indexnow.key not generated on this host')
    return KEY_FILE.read_text(encoding='utf-8').strip()


def test_indexnow_key_file_returns_key(client):
    key = _read_key()
    resp = client.get(f'/{key}.txt')
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].startswith('text/plain')
    assert resp.data.decode('utf-8') == key


def test_wrong_key_404s(client):
    """A bogus 32-char hex string must not leak the real key."""
    resp = client.get('/aaaa1111aaaa1111aaaa1111aaaa1111.txt')
    assert resp.status_code == 404


def test_non_hex_key_404s(client):
    """Slugs that aren't 32-char hex shouldn't even hit our handler —
    Flask matches /robots.txt, /ads.txt etc. first; /<key>.txt only
    fires on the exact pattern. Sanity-check by trying a path-traversal
    style slug."""
    resp = client.get('/etc-passwd.txt')
    assert resp.status_code == 404


def test_key_file_does_not_collide_with_robots_or_ads(client):
    """The /<key>.txt converter must not steal /robots.txt or /ads.txt
    away from their dedicated handlers."""
    r1 = client.get('/robots.txt')
    r2 = client.get('/ads.txt')
    assert r1.status_code == 200 and 'User-agent' in r1.data.decode()
    assert r2.status_code == 200

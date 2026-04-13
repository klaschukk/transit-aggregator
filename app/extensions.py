"""Shared Flask extensions."""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def _client_ip() -> str:
    """Respect X-Forwarded-For from nginx/Cloudflare."""
    from flask import request
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.split(',')[0].strip()
    cf = request.headers.get('CF-Connecting-IP', '')
    if cf:
        return cf
    return get_remote_address()


# Note: memory:// storage is per-worker. With `gunicorn -w 4`, effective limit
# is ~4× the declared value per IP. For stricter enforcement use redis:// or
# memcached:// — requires external infra.
limiter = Limiter(
    key_func=_client_ip,
    default_limits=[],
    storage_uri="memory://",
)

#!/usr/bin/env python3
"""Send a single message to Sentry from a shell script.

Used by nightly_refresh.sh when build_db fails — cron doesn't go through
Flask, so there's no FlaskIntegration in the loop. We init the SDK from
env vars, capture a message, flush, and exit.

No-op (exit 0) when SENTRY_DSN is unset, so the nightly script stays
green on dev machines.

Usage:
    scripts/sentry_notify.py "build_db failed exit=1" error job=nightly
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root on sys.path so we can import the app wrapper.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import observability  # noqa: E402


def main() -> int:
    if not observability.init_from_env():
        return 0

    if len(sys.argv) < 2:
        print("usage: sentry_notify.py <message> [level] [tag=value ...]",
              file=sys.stderr)
        return 2

    message = sys.argv[1]
    level = sys.argv[2] if len(sys.argv) > 2 else 'error'
    tags: dict[str, str] = {}
    for arg in sys.argv[3:]:
        if '=' in arg:
            k, v = arg.split('=', 1)
            tags[k] = v

    observability.capture_message(message, level=level, **tags)
    observability.flush(timeout=5.0)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

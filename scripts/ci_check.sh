#!/bin/bash
# Reproduce the GitLab CI test gate LOCALLY, against the seed DB.
#
# Why this exists: the test gate (.gitlab-ci.yml) runs pytest against the tiny
# tests/seed.duckdb, NOT the full DuckDB. Working in a worktree you normally
# symlink the full DB, so the suite is green for you while CI can be red — a
# test that needs full-DB data (GTFS headway, a route absent from the seed, a
# column the seed schema lacks) passes locally and breaks the gate. Run this
# before pushing to catch that class of failure the way CI sees it.
#
# Usage:  scripts/ci_check.sh        # from the repo / worktree root
# Exit 0 = gate green, non-zero = a real CI failure you'd otherwise miss.
set -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

# Find a python that has pytest. In a worktree there's no local venv, so fall
# back to the canonical checkout's venv, then $PYTHON, then system python3.
PY="$ROOT/venv/bin/python"
[ -x "$PY" ] || PY="/root/klaschuk/transit-aggregator/venv/bin/python"
[ -x "$PY" ] || PY="${PYTHON:-$(command -v python3)}"
if ! "$PY" -c 'import pytest' 2>/dev/null; then
  echo "ERROR: no pytest in $PY — activate the venv or set PYTHON=/path/to/venv/bin/python" >&2
  exit 1
fi

echo "==> CI parity check: pytest against tests/seed.duckdb"
DUCKDB_PATH=tests/seed.duckdb "$PY" -m pytest tests/ -x -q --tb=short \
  --ignore=tests/test_integration.py \
  --ignore=tests/test_privacy.py
rc=$?

if [ $rc -eq 0 ]; then
  echo "==> GREEN — matches the CI gate."
else
  echo "==> RED — this WILL fail CI. Fix before pushing (a full-DB run won't show it)."
fi
exit $rc

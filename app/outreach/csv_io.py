"""Atomic read/write of backlinks-targets.csv with schema migration.

`load_targets` returns rows already migrated (every canonical column is
present, missing ones are empty strings). `save_targets` writes through a
temp file + os.replace so a crash mid-write can't corrupt the file.
"""
from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path

from .schema import FIELDNAMES, migrate_row

_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CSV = _ROOT / 'docs' / '00_strategy' / 'backlinks-targets.csv'


def load_targets(path: Path | None = None) -> tuple[list[str], list[dict]]:
    """Return (fieldnames, rows). Rows are dicts with every canonical
    column populated (empty string when absent in source file)."""
    src = Path(path) if path else DEFAULT_CSV
    if not src.exists():
        return list(FIELDNAMES), []

    with src.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        file_fields = list(reader.fieldnames or [])
        rows = [migrate_row(dict(r)) for r in reader]

    # Preserve any bespoke columns present in the file but absent from
    # the canonical schema — humans can add experiments without them
    # being wiped on the next save.
    extra = [f for f in file_fields if f not in FIELDNAMES]
    fieldnames = list(FIELDNAMES) + extra
    return fieldnames, rows


def save_targets(
    fieldnames: list[str],
    rows: list[dict],
    path: Path | None = None,
) -> None:
    """Write rows atomically. `fieldnames` is the write order — pass the
    value returned by load_targets() to round-trip any bespoke columns."""
    dest = Path(path) if path else DEFAULT_CSV
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Write to a sibling temp file so an interrupted run can't leave a
    # half-written CSV in place.
    fd, tmp = tempfile.mkstemp(
        prefix='.backlinks-targets-', suffix='.csv.tmp', dir=dest.parent,
    )
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(
                f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL,
                extrasaction='ignore',
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({k: (row.get(k) or '') for k in fieldnames})
        os.replace(tmp, dest)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def find_row(rows: list[dict], *, url: str | None = None,
             domain: str | None = None) -> dict | None:
    """Locate a row by URL (preferred) or domain. Returns the dict in
    place (mutations propagate) or None."""
    if url:
        for r in rows:
            if (r.get('url') or '').strip() == url.strip():
                return r
    if domain:
        d = domain.strip().lower()
        for r in rows:
            if (r.get('domain') or '').strip().lower() == d:
                return r
    return None

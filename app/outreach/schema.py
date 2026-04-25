"""Canonical CSV schema for backlinks-targets.csv.

The file shipped with 10 columns (pre-automation). The sender adds 12
outreach-state columns without destroying any manual notes. Migration is
purely additive — existing rows get empty strings for new columns;
nothing is renamed or dropped. Safe to re-run.
"""
from __future__ import annotations

# Canonical field order, written by every save. Any extra columns present
# in the file are preserved at the end (see csv_io.save_targets) so that
# humans can add bespoke columns for one-off experiments without losing
# them on the next automated write.
FIELDNAMES: tuple[str, ...] = (
    # Identity (from research)
    'domain',
    'url',
    'category',
    'DA_estimate',
    'language',
    'contact_method',
    # Outreach contact + template selection
    'contact_email',
    'template',
    # Enrichment output (from backlinks_enrich.py)
    'site_title',
    'their_topic',
    'our_hook',
    'enriched_at',
    # State machine
    'status',                 # todo | enriched | contacted | replied | bounced | no_response | backlinked | opted_out
    'contacted_at',           # first send
    'last_status_change',
    'last_event',             # delivered | opened | clicked | replied | bounced | complained
    'last_event_at',
    'follow_up_count',        # 0..2
    'opted_out',              # '1' once opt-out received; do not send again
    # Detection output (from backlinks_check.py)
    'backlink_url',
    'backlink_detected_at',
    # Free-form — always last for human readability
    'notes',
)


# Columns whose value of '1' (or 'true') means "never send".
OPTED_OUT_COLUMNS = ('opted_out',)


def migrate_row(row: dict) -> dict:
    """Return `row` with every canonical field present (missing → '').

    Mutates and returns the input for caller convenience.
    """
    for field in FIELDNAMES:
        row.setdefault(field, '')
    return row

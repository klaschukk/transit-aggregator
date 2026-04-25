"""Outreach automation layer — CSV-driven cold email campaign to backlink
targets in docs/00_strategy/backlinks-targets.csv.

Public surface:

    from app.outreach import (
        load_targets, save_targets,    # CSV I/O with schema migration
        render_template,               # .tpl → (subject, text)
        send_outreach,                 # sender with CAN-SPAM footer
        daily_send_cap_ok,             # rate-limit check
        is_gdpr_sensitive_domain,      # DE/FR etc guard
        record_event,                  # Mailgun webhook writes here
        MAX_SENDS_PER_DAY, FIELDNAMES, # constants
    )

Deliberately script-importable: no Flask app context required for the
CSV/template/rate-limit pieces so cron jobs stay simple. Only the sender
touches flask `current_app` (via mailer.send_mail) and that stays behind
a `with app.app_context()` in the scripts.
"""
from .schema import (
    FIELDNAMES,
    OPTED_OUT_COLUMNS,
    migrate_row,
)
from .csv_io import load_targets, save_targets
from .templates import (
    available_templates,
    render_template,
    template_for_category,
)
from .sender import (
    MAX_SENDS_PER_DAY,
    SEND_LOG,
    build_message,
    daily_send_cap_ok,
    is_gdpr_sensitive_domain,
    record_event,
    send_outreach,
)

__all__ = [
    'FIELDNAMES',
    'OPTED_OUT_COLUMNS',
    'MAX_SENDS_PER_DAY',
    'SEND_LOG',
    'available_templates',
    'build_message',
    'daily_send_cap_ok',
    'is_gdpr_sensitive_domain',
    'load_targets',
    'migrate_row',
    'record_event',
    'render_template',
    'save_targets',
    'send_outreach',
    'template_for_category',
]

"""Newsletter sub-system: compose, validate, dispatch, suppression.

Lives next to app/mailer.py (single send) but operates on the campaign
abstraction — many subscribers, audience filters, resume-on-crash,
List-Unsubscribe headers, and per-message Mailgun event tracking.

Modules:
    campaigns   — DDL helpers + CRUD (read/update/seed) for the campaigns
                  + campaign_sends + email_suppressions tables.
    audience    — Resolves an `audience_filter` JSON blob to the concrete
                  list of confirmed, non-suppressed subscribers.
    render      — Markdown → HTML + plain-text body builder. Adds the
                  brand frame, unsubscribe footer, and List-Unsubscribe
                  header. Uses `markdown` (CommonMark + footnotes).
    validator   — Spam-score self-check (subject length, body length,
                  spam-keyword density, link-to-text ratio, unsub link
                  presence). Returns a 0–100 score + a reasons list.
    dispatch    — Sends one campaign end-to-end with rate-limit, resume,
                  per-recipient personalisation, suppression respect.
                  Pure logic — no Flask globals — so the unit tests can
                  exercise it without spinning up an app context.

The compose UI at /admin/newsletter binds these together; nothing here
imports Flask routes (so tests can swap analytics DB cleanly).
"""

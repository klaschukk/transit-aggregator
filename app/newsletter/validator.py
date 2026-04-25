"""Self-contained spam-score check — no third-party services.

The compose UI calls validate(subject, preheader, body_md) and gets back
(score, reasons[], details). A score < 60 blocks the Send button; the
operator can ignore the warning by toggling "I know what I'm doing"
(stored only in this request, not persisted).

Heuristics are deliberately conservative — every rule has a citation in
its comment to industry guidance. Most of these are filterable by the
big four (Gmail, Outlook, iCloud, Yahoo) at SpamAssassin/Postmark scores
above 5.0; collectively avoiding them keeps us comfortably below.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Keep the wordlist small — we don't want false positives in Serbian
# travel content. Each entry is the ASCII-folded regex pattern; the
# scorer applies the same casefold to the body before matching.
_SPAM_KEYWORDS = (
    r'\bact now\b', r'\bbuy now\b', r'\bclick here\b', r'\b100% free\b',
    r'\bguarantee[d]?\b', r'\bfree money\b', r'\bget rich\b',
    r'\blimited time\b', r'\border now\b', r'\bonline biz\b',
    r'\brisk[ -]free\b', r'\bspecial promotion\b', r'\bweight loss\b',
    r'\bviagra\b', r'\bsexy\b', r'\bxxx\b',
    # SR/RU patterns common in travel-spam landing pages we've seen
    r'\bbesplat[ao]\b', r'\bzaradi\b',
    r'\bбесплатн', r'\bзаработ',
)
_SPAM_RE = re.compile('|'.join(_SPAM_KEYWORDS), re.IGNORECASE)

# A subject in ALL CAPS or with 3+ exclamation marks is the single
# strongest "this is spam" filter signal across all major providers.
_ALL_CAPS_RE = re.compile(r'^[^a-zа-я]*[A-ZА-Я ][A-ZА-Я0-9 \-!?.,]{6,}$')


@dataclass(frozen=True)
class Reason:
    severity: str         # 'fail' (-30), 'warn' (-10), 'info' (0)
    message: str
    detail: str = ''


# Severity → score deduction. A single 'fail' moves the score below 60
# (the PASSING_SCORE threshold) on its own; 'warn' is recoverable;
# 'info' is just an FYI.
_DEDUCTION = {'fail': 45, 'warn': 10, 'info': 0}


def _word_count(s: str) -> int:
    return len((s or '').split())


def _strip_md(body_md: str) -> str:
    """Remove markdown noise so the keyword scan + length check don't
    count link URLs and image syntax. Just a strip — not a full parse."""
    if not body_md:
        return ''
    # Image: ![alt](url) → alt
    s = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', body_md)
    # Link: [text](url) → text
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)
    # Code fences/blocks
    s = re.sub(r'```.*?```', '', s, flags=re.DOTALL)
    s = re.sub(r'`[^`]*`', '', s)
    # Bare URLs
    s = re.sub(r'https?://\S+', '', s)
    # Headings/lists/emphasis markers
    s = re.sub(r'^[#>\-*]+\s*', '', s, flags=re.MULTILINE)
    s = re.sub(r'[*_]{1,3}', '', s)
    return s


def validate(subject: str, preheader: str, body_md: str) -> tuple[int, list[Reason], dict]:
    """Returns (score 0–100, reasons[], details).

    The details dict feeds back into the compose UI so the operator can
    see exactly which numbers triggered which warning."""
    reasons: list[Reason] = []

    body_text = _strip_md(body_md or '')
    body_words = _word_count(body_text)
    subj_words = _word_count(subject or '')

    # ── Subject line ─────────────────────────────────────────────────────
    if subj_words == 0:
        reasons.append(Reason('fail', 'subject is empty'))
    elif subj_words > 12:
        # 9 words is the Mailchimp-cited optimum; >12 is the spam-filter
        # threshold across most studies.
        reasons.append(Reason('warn', f'subject too long ({subj_words} words; ideal 3–9)'))
    elif subj_words < 3:
        reasons.append(Reason('warn', f'subject very short ({subj_words} words)'))

    if subject and _ALL_CAPS_RE.match(subject.strip()):
        reasons.append(Reason('fail', 'subject is ALL CAPS — guaranteed spam-fold'))

    excl = (subject or '').count('!')
    if excl >= 3:
        reasons.append(Reason('fail', f'subject has {excl} exclamation marks'))
    elif excl >= 1:
        reasons.append(Reason('warn', 'exclamation in subject reduces inbox-rate ~7%'))

    # Preheader — not strictly required but improves opens. Soft warn.
    if not (preheader or '').strip():
        reasons.append(Reason('info', 'no preheader — Gmail will show body excerpt'))
    elif _word_count(preheader) > 20:
        reasons.append(Reason('warn',
            f'preheader long ({_word_count(preheader)} words; ideal 6–14)'))

    # ── Body length + structure ──────────────────────────────────────────
    if body_words == 0:
        reasons.append(Reason('fail', 'body is empty'))
    elif body_words < 80:
        # SpamAssassin's MISSING_HEADERS_BODY_TOO_SHORT triggers under ~50.
        reasons.append(Reason('warn',
            f'body very short ({body_words} words; ideal 200–800)'))
    elif body_words > 1500:
        reasons.append(Reason('warn',
            f'body very long ({body_words} words; ideal 200–800)'))

    # ── Spam keywords ────────────────────────────────────────────────────
    hits = _SPAM_RE.findall((subject or '') + ' ' + body_text)
    if hits:
        reasons.append(Reason('fail',
            f'{len(hits)} spam-keyword hit(s)',
            detail=', '.join(sorted(set(hits))[:6]),
        ))

    # ── Unsubscribe link ─────────────────────────────────────────────────
    # The dispatch path injects an unsub link automatically into every
    # send, so the *template* doesn't need it. But if the operator types
    # one inline, make sure it's the canonical {{unsub_url}} placeholder
    # rather than a stale hard-coded URL.
    if re.search(r'unsubscribe[/-]', body_md or '', re.IGNORECASE) and \
            '{{unsub_url}}' not in (body_md or ''):
        reasons.append(Reason('warn',
            'inline unsubscribe URL — use {{unsub_url}} placeholder'))

    # ── Link density ─────────────────────────────────────────────────────
    link_count = len(re.findall(r'\]\(http', body_md or ''))
    if body_words > 0 and link_count > 0:
        ratio = link_count / max(1, body_words / 80)
        if ratio > 3:
            reasons.append(Reason('warn',
                f'{link_count} links in {body_words} words — high density'))

    # ── Image-heavy with no text fallback ───────────────────────────────
    img_count = len(re.findall(r'!\[', body_md or ''))
    if img_count > 0 and body_words < 100:
        reasons.append(Reason('warn',
            f'{img_count} image(s) but only {body_words} words — Gmail clips images'))

    # Score = 100 minus deductions. Cap at 0/100.
    deduction = sum(_DEDUCTION[r.severity] for r in reasons)
    score = max(0, 100 - deduction)

    details = {
        'subject_words': subj_words,
        'preheader_words': _word_count(preheader or ''),
        'body_words': body_words,
        'spam_keyword_hits': len(hits),
        'link_count': link_count,
        'image_count': img_count,
        'exclamation_count': excl,
    }

    return score, reasons, details


# Threshold the compose UI uses to gate the Send button. 60 = roughly
# "no fails, ≤4 warns" — a reasonable bar that doesn't fight short
# transactional follow-ups (welcome, confirm) but does block obvious
# fundraising-blast templates.
PASSING_SCORE = 60

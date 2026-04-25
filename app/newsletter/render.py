"""Newsletter body renderer — Markdown subset → HTML + plain-text twin.

Why hand-rolled vs python-markdown / mistune:
  * Body comes from our own admin compose UI; we control its surface
    area. We don't need GFM tables, inline HTML, or footnote plugins.
  * Adding a transitive XSS surface to the email-send path widens the
    blast radius for very little upside — this version emits exactly
    the tags allowed by Gmail's "lite" rendering and nothing else.

Subset supported:
    # H1     ## H2     ### H3
    **bold**     *italic*
    [text](https://url)        — http/https only, escaped attribute
    - bullets    or    1. ordered (collapses any leading number)
    paragraphs (blank-line separated)
    {{placeholder}}            — substituted before render, see vars()

What we don't do (to keep the parser tiny):
    images, blockquotes, tables, code blocks, raw HTML tags.

vars() also ships the canonical placeholders (unsub_url, preferences_url,
sender_name) so dispatch can inject per-recipient values once and let
the renderer focus on layout.
"""
from __future__ import annotations

import html as _html
import re

# Allow only http/https links — `javascript:` and `data:` would be the
# obvious exfil vector if we ever shipped this template path through to
# user-submitted content. (Currently admin-only, but the cost of the
# guard is one regex.)
_LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^)\s]+)\)')
_BOLD_RE = re.compile(r'\*\*([^*\n]+)\*\*')
_ITAL_RE = re.compile(r'(?<!\*)\*(?!\*)([^*\n]+)\*(?!\*)')


def _inline(s: str) -> str:
    """Render inline markup. Escape HTML first, then re-introduce the
    safe tags via re.sub so we never accidentally pass user-typed
    `<script>` through."""
    s = _html.escape(s, quote=False)
    s = _LINK_RE.sub(
        lambda m: f'<a href="{_html.escape(m.group(2), quote=True)}" '
                  f'style="color:#0d9488">{m.group(1)}</a>',
        s,
    )
    s = _BOLD_RE.sub(r'<strong>\1</strong>', s)
    s = _ITAL_RE.sub(r'<em>\1</em>', s)
    return s


def _render_block(lines: list[str]) -> str:
    """One blank-line-separated block → one HTML element."""
    if not lines:
        return ''
    head = lines[0].lstrip()
    if head.startswith('### '):
        return f'<h3 style="font-size:18px;margin:18px 0 8px;color:#0f172a">' \
               f'{_inline(head[4:])}</h3>'
    if head.startswith('## '):
        return f'<h2 style="font-size:22px;margin:24px 0 10px;color:#0f172a">' \
               f'{_inline(head[3:])}</h2>'
    if head.startswith('# '):
        return f'<h1 style="font-size:26px;margin:24px 0 12px;color:#0f766e">' \
               f'{_inline(head[2:])}</h1>'

    # List detection — every line in the block must be a list item.
    bullet_lines = [l for l in lines if re.match(r'^\s*[-*]\s+', l)]
    ordered_lines = [l for l in lines if re.match(r'^\s*\d+\.\s+', l)]
    if bullet_lines and len(bullet_lines) == len(lines):
        items = ''.join(
            f'<li style="margin:4px 0">{_inline(re.sub(r"^\\s*[-*]\\s+", "", l))}</li>'
            for l in lines
        )
        return f'<ul style="padding-left:22px;margin:8px 0;line-height:1.6">{items}</ul>'
    if ordered_lines and len(ordered_lines) == len(lines):
        items = ''.join(
            f'<li style="margin:4px 0">{_inline(re.sub(r"^\\s*\\d+\\.\\s+", "", l))}</li>'
            for l in lines
        )
        return f'<ol style="padding-left:22px;margin:8px 0;line-height:1.6">{items}</ol>'

    # Default: paragraph (join inner-block line breaks with single spaces).
    text = ' '.join(_inline(l.strip()) for l in lines if l.strip())
    return f'<p style="margin:12px 0;line-height:1.6;color:#0f172a">{text}</p>'


def md_to_html_inner(body_md: str) -> str:
    """Markdown subset → inner HTML. Wrapped by the brand frame in
    `render_email`."""
    if not body_md:
        return ''
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in (body_md or '').splitlines():
        if line.strip():
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return '\n'.join(_render_block(b) for b in blocks)


# ── Plain-text twin (for SMTP multipart/alternative) ────────────────────

def md_to_text(body_md: str) -> str:
    """Strip markdown noise so the text/plain part reads naturally.
    Gmail uses this for the inbox snippet when no preheader exists, and
    SpamAssassin penalises HTML-only emails."""
    if not body_md:
        return ''
    s = body_md
    s = _LINK_RE.sub(r'\1 (\2)', s)
    s = _BOLD_RE.sub(r'\1', s)
    s = _ITAL_RE.sub(r'\1', s)
    s = re.sub(r'^#+\s+', '', s, flags=re.MULTILINE)
    s = re.sub(r'^\s*[-*]\s+', '• ', s, flags=re.MULTILINE)
    s = re.sub(r'^\s*\d+\.\s+', '', s, flags=re.MULTILINE)
    return s.strip()


# ── Brand frame ─────────────────────────────────────────────────────────

_FOOTER_TEXTS = {
    'sr': ('Otpisali ste se? Otvorite link', 'Pretplatili ste se na'),
    'en': ('Want to unsubscribe? Open this link', 'You subscribed via'),
    'ru': ('Хотите отписаться? Откройте ссылку', 'Вы подписались через'),
}


def render_email(
    *,
    subject: str,
    preheader: str,
    body_md: str,
    lang: str,
    unsub_url: str,
    physical_address: str = 'Prevozni · Beograd, Srbija',
    source: str = '',
    confirmed_date: str = '',
) -> tuple[str, str, str]:
    """Returns (subject, html, text). All three are ready for SMTP send.

    The brand frame is intentionally inline-styled — Gmail strips
    <head><style> on most clients, and <link rel=stylesheet> never
    works in email. Inline-only is the lowest-common-denominator that
    renders reliably across Gmail / Outlook / iCloud / mobile webmail.
    """
    inner_html = md_to_html_inner(body_md)
    unsub_label, source_label = _FOOTER_TEXTS.get(lang, _FOOTER_TEXTS['sr'])
    pre = (preheader or '').strip()

    # Hidden-but-legible preheader trick — Gmail and iOS Mail both pull
    # the first ~90 chars of body content as the inbox snippet. The
    # white-on-white prepended span keeps the on-open visual clean.
    pre_block = (
        f'<span style="display:none;visibility:hidden;opacity:0;color:#fff;'
        f'height:0;width:0;font-size:1px">{_html.escape(pre)}</span>'
        if pre else ''
    )

    safe_unsub = _html.escape(unsub_url, quote=True)
    source_line = ''
    if source or confirmed_date:
        source_line = (
            f'<p style="margin:6px 0 0;color:#94a3b8;font-size:11px">'
            f'{source_label} <strong>{_html.escape(source)}</strong>'
            f'{" · " + _html.escape(confirmed_date) if confirmed_date else ""}.</p>'
        )

    html = (
        '<!DOCTYPE html>'
        '<html lang="' + lang + '"><head><meta charset="utf-8"></head>'
        '<body style="margin:0;padding:0;background:#f8fafc;'
        'font-family:Segoe UI,system-ui,-apple-system,sans-serif">'
        + pre_block +
        '<div style="max-width:600px;margin:0 auto;background:#fff;'
        'padding:24px;border-radius:8px">'
        '<a href="https://prevozni.com" style="color:#0f766e;text-decoration:none;'
        'font-weight:800;font-size:18px">Prevozni</a>'
        '<hr style="border:none;border-top:1px solid #e2e8f0;margin:16px 0">'
        + inner_html +
        '<hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0 16px">'
        '<p style="margin:0;color:#475569;font-size:12px;line-height:1.5">'
        + unsub_label + ': '
        f'<a href="{safe_unsub}" style="color:#0f766e">{safe_unsub}</a>.'
        '</p>'
        + source_line +
        f'<p style="margin:12px 0 0;color:#94a3b8;font-size:11px">{_html.escape(physical_address)}</p>'
        '</div></body></html>'
    )

    # Plain-text twin. Always include the unsubscribe URL on a clean
    # line so plain-text-only clients (alpine, mutt, screen readers)
    # surface it without parsing.
    text_parts = [md_to_text(body_md), '', '— —', f'{unsub_label}: {unsub_url}']
    if source:
        text_parts.append(f'{source_label} {source}'
                          + (f' · {confirmed_date}' if confirmed_date else '')
                          + '.')
    text_parts.append(physical_address)
    text = '\n'.join(text_parts)

    return subject, html, text


# ── Placeholder substitution ────────────────────────────────────────────

_PLACEHOLDER_RE = re.compile(r'\{\{\s*([a-z_]+)\s*\}\}')


def substitute(template: str, vars_: dict[str, str]) -> str:
    """Replace {{key}} with vars_[key] (or '' if absent). Strict —
    arbitrary {{__import__}} attacks are impossible because we only
    look up keys in the dict."""
    if not template:
        return ''
    def lookup(m: re.Match) -> str:
        return str(vars_.get(m.group(1), ''))
    return _PLACEHOLDER_RE.sub(lookup, template)

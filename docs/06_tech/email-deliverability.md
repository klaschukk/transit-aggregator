# Email Deliverability — Pre-Launch Runbook

**Audience:** solo dev going from "double-opt-in works" to "first
broadcast lands in inbox, not spam." This is a checklist, not a guide
to email; deeper reading at the bottom.

## TL;DR — what has to be true before the first send

1. SPF, DKIM, DMARC records on `prevozni.com` — all three pass.
2. Mailgun (or SES) account verified, `MAILGUN_API_KEY` +
   `MAILGUN_DOMAIN` env vars set on the prod box.
3. `MAILGUN_WEBHOOK_SIGNING_KEY` set so `/admin/api/mailgun-webhook`
   accepts events.
4. `MAIL_FROM` consistent — same address in code, DNS, and the
   physical From header on every campaign.
5. `ADMIN_EMAIL` env var pointing at a personal mailbox so the "Send
   test" button lands somewhere you'll see it.
6. mail-tester.com score 8+/10 on a representative test send before
   the broadcast goes wide.

## DNS records (Cloudflare)

The exact strings come from the Mailgun / SES dashboard once a domain
is added — copy them verbatim. Below is the *shape* you should see in
the Cloudflare DNS tab when it's correct:

```
TXT  prevozni.com           "v=spf1 include:mailgun.org ~all"
TXT  k1._domainkey.…         "v=DKIM1; k=rsa; p=MIIBIj…"   (long key)
TXT  _dmarc.prevozni.com    "v=DMARC1; p=none; rua=mailto:postmaster@prevozni.com"
CNAME email.prevozni.com    "mailgun.org"                 (tracking)
```

DMARC starts at `p=none` — *monitor mode*. After 4–6 weeks of clean
reports, escalate to `p=quarantine` then `p=reject`. Going straight
to reject before SPF + DKIM are stable will silently drop legitimate
mail.

## Mailgun account setup

1. Sign up at mailgun.com (free tier: 5 000 sends/month for the first
   3 months, then 100/day flex).
2. Add the domain `mg.prevozni.com` (a subdomain — keeps the corporate
   reputation separate from any personal mail you might send from
   `prevozni.com` directly).
3. Copy the four DNS records into Cloudflare. Wait 30 minutes.
4. Click *Verify DNS Settings* in Mailgun. All four green = done.
5. **Webhooks**: in Mailgun → Sending → Webhooks, set every event
   type (delivered, opened, clicked, complained, unsubscribed, failed)
   to `https://prevozni.com/admin/api/mailgun-webhook`. Copy the
   signing key into `MAILGUN_WEBHOOK_SIGNING_KEY`.
6. **Tracking**: enable open tracking + click tracking — without these
   the campaign analytics on `/admin/newsletter` stay empty.

## Pre-launch checklist

- [ ] SPF record present on `prevozni.com` (via Mailgun)
- [ ] DKIM key present + green in Mailgun DNS check
- [ ] DMARC record set to `p=none` for monitoring
- [ ] `MAILGUN_API_KEY` + `MAILGUN_DOMAIN` set in
      `/etc/systemd/system/transit.service.d/override.conf`
- [ ] `MAILGUN_WEBHOOK_SIGNING_KEY` set
- [ ] `MAIL_FROM` = `Prevozni <newsletter@prevozni.com>` (brand,
      consistent across all campaigns)
- [ ] `ADMIN_EMAIL` points at a real mailbox you check
- [ ] List-Unsubscribe header validated — Gmail's "Unsubscribe"
      button shows in the inbox row (visible after first delivered
      send)
- [ ] One end-to-end test: compose welcome draft → click *Send test
      to ADMIN_EMAIL* → arrives in inbox, not spam, all three lang
      bodies render
- [ ] mail-tester.com — paste a test message with a real campaign
      body, score 8+/10
- [ ] Test deliverability against the big four: send the welcome
      draft to throwaway accounts on Gmail, Outlook, iCloud, Yahoo;
      none of them go to junk

## Sending discipline

- **Warm-up.** First broadcast: 50 recipients (just internal /
  friendly addresses). +50% per send for the first 5 sends, then
  unrestricted. Mailgun reputation is the variable that matters most
  on a brand-new domain.
- **Cadence.** Weekly digest is the right floor — more than that and
  unsubscribe rate climbs above 0.3% (the "you're spamming us"
  threshold).
- **Audience health.** Hard bounce rate ≤ 0.5%, complaint rate ≤
  0.1%. Both are tracked in `email_suppressions` automatically; the
  webhook adds bounced + complained addresses on first event so we
  never re-send.
- **Re-engagement.** A subscriber who hasn't opened any of the last
  6 weekly digests is dead weight to your sender reputation. The
  in-app system has a `min_engagement` filter primitive but does
  not auto-act yet — manually run a re-engagement campaign once your
  list crosses 500.

## When something goes wrong

| Symptom | First check |
| --- | --- |
| Test arrives in spam | mail-tester.com score; Gmail "show original" → check SPF/DKIM line at top |
| `/admin/newsletter` shows 0 deliveries after a send | webhook URL set in Mailgun, signing key matches env, /admin route reachable from internet (no IP allowlist on nginx) |
| Open rate suddenly drops to <5% | ISP started rate-limiting — usually because complaint rate spiked. Pause the next campaign, audit who you imported recently. |
| `error: 'send_fn returned False'` rows in `campaign_sends` | SMTP auth failing — check Mailgun dashboard for blocked sends; could be a paused account on the free tier |

## What's deliberately not built (yet)

- **Auto-trigger welcome on confirm + 2h** — currently the welcome
  campaign exists as a draft; it's sent on the operator's command,
  not by a cron. Wire `scripts/newsletter_send.py --slug
  welcome-confirmed` into a cron once Mailgun is live and the first
  manual run looks clean.
- **Engagement scoring + auto re-engage** — premature on a 0-record
  list. Add when the list crosses 500.
- **A/B subject line testing** — needs a stable list size first.
- **Image hosting** — Gmail clips images by default; we ship inline
  HTML with brand frame only. Add to `static/img/email/` + add an
  `<img>` allowlist to render.py if a campaign needs it.

## Reading

- *DMARC, SPF, DKIM* — dmarc.org/overview/
- *Mailgun warm-up guide* — documentation.mailgun.com/en/latest/best_practices.html
- *List-Unsubscribe (RFC 8058)* — datatracker.ietf.org/doc/html/rfc8058

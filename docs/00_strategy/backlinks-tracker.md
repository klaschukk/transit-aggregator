# Backlinks tracker

Updated weekly after `python scripts/backlinks_digest.py`. Keep this
file short — this is the *scoreboard*, the raw target list lives in
`backlinks-targets.csv` and the per-target state is tracked there.

## Goals

| Horizon | Target | Why |
|---|---|---|
| 3 months | 20 backlinks | Crosses Google's "noticeable" threshold — at this point ranking movement becomes measurable in Search Console. |
| 6 months | 50 backlinks | Equal-ish to current busticket4.me top competitor tier within Balkan transit niche. |
| 12 months | 100 backlinks | Diminishing returns after this — shift budget from outreach to content. |

DA-weighted score matters more than raw count: one DA-80 tourism-board
link outperforms ten DA-20 blog mentions in both authority transfer and
referral traffic.

## Weekly snapshot

_Auto-filled by `scripts/backlinks_digest.py` on Mondays. Manual
override if the script missed something._

| Week of | Total | New this week | Contacted | Pending follow-up | DA-weighted score |
|---|---|---|---|---|---|
| 2026-04-20 | 0 | 0 | 0 | 0 | 0 |
| _example_ 2026-05-04 | 3 | 3 | 12 | 4 | 185 |

## Category coverage (target distribution)

The long-term mix we're aiming for — check against `backlinks-targets.csv`
once a quarter to see if any category is empty.

| Category | Target count | Landing-rate hope | Notes |
|---|---|---|---|
| serbian_tourism | 5-8 | 15-25% | Hard to land, worth 10× a blog mention each. |
| serbian_gov | 2-4 | 5-10% | Glacial but stable. Aim for data.gov.rs, ministry, 1-2 city portals. |
| serbian_operator | 6-10 | 10-20% | Reciprocal works best (template: operator-reciprocal.md). |
| balkan_blog | 15-25 | 15-25% | Travel-blog template; needs per-post personalisation. |
| travel_blog_global | 20-30 | 5-15% | Lower yield but global DA 60+ sites included. |
| travel_forum | 10-15 | Variable | Forum mods silent for weeks, then reply. Drop the link in-thread where allowed. |
| wikipedia_edit | 2-5 | 30-50% | Fast if reference is cited properly; reverts fast if not. |
| expat_serbia | 15-25 | 20-30% | Highest conversion: real users asking real questions. |
| russian_diaspora | 10-15 | 20-35% | Niche but high-intent; RU version of site is the differentiator. |
| broken_link_candidates | 10-20 | 25-40% | Highest yield after in-thread replies. Run `backlinks_broken.py` monthly. |

## Ethical guardrails (re-read before every batch)

1. **No paid links.** Google's link-buying penalty is one of the few
   that actually destroys rankings. Not worth the €5 a shady site asks
   for.
2. **No PBN / link farms.** Same reason. If a site with 10 outbound
   links to random travel aggregators wants to add ours, skip.
3. **Max 20 outreach emails/day per sender.** Above that, Gmail/SMTP
   starts marking the sender as a spammer regardless of content.
4. **Personalise the first two lines.** Templates below the fold can
   be templated; lines 1-2 are fresh every time or don't bother.
5. **Disclose reciprocal-link offers.** Honesty reads as confidence
   and correlates with higher reply rate.
6. **One follow-up maximum, 14 days after first email.** Beyond that,
   shelve the target for 12 months.

## Workflow per week (2 h total)

| Minutes | Task | Tool |
|---|---|---|
| 10 | Read digest | `python scripts/backlinks_digest.py` |
| 20 | Check new backlinks manually (GSC referring domains) | Google Search Console |
| 30 | Send 5 personalised pitches | templates + inbox |
| 20 | Follow up 2-3 contacted>7-days targets | templates |
| 20 | Research 10 new targets for next week | `scripts/backlinks_research.py` |
| 20 | 1 helpful reply on r/serbia / r/belgrade / expat forum | `expat-forum.md` |

That's 2 h. If the scoreboard shows zero activity for 3 weeks running,
drop the timebox — probably means the bottleneck is elsewhere
(site quality, content, a dead partner API).

## Useful queries (save to browser bookmarks)

- Find pages linking to competitor but not us:
  `site:busticket4.me -site:prevozni.com` (reverse-image: pages we
  could be on but aren't)
- Find Serbia bus content on high-DA sites:
  `"bus" "Serbia" site:nomadicmatt.com OR site:theculturetrip.com`
- Find dead links to transit aggregators in Balkan articles:
  `"bus schedule" "Serbia" inurl:travel -site:prevozni.com` then run
  `scripts/backlinks_broken.py` on top 20 results.

## Anti-goals

- **Directory submissions.** Most DA <20, all templated; you could
  submit to 100 and move nothing. Time sink.
- **Guest posts on random travel blogs written for link purposes.**
  If the content wouldn't live on our own site, it shouldn't live on
  theirs either.
- **Reciprocal-link rings.** Two sites linking to each other = fine.
  Five sites all linking to each other = Google sees the pattern in
  a week.

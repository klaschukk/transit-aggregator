# Broken-link building — "your link is dead, ours replaces it"

**When to use:** you found a 404/500 outbound link on a Serbia/Balkan
travel article on a DA 40+ site, and our site has content that
factually replaces what the dead link used to host. Script
`scripts/backlinks_broken.py` outputs candidate URLs; each needs a
quick manual check (Wayback Machine → "what did the dead page say?"
→ is ours a true substitute?).

**Don't use on:** dead links to news articles (we can't replace news
with a schedule page), forum threads, user profiles. Only useful when
the dead link was an *informational* resource.

**Success rate:** 25-40% if personalized + the match is real. This
is the highest-yield technique after in-thread helpful replies.

---

## Email template (EN)

> Subject: Quick heads-up: broken link in [POST TITLE]
>
> Hi [FIRST_NAME],
>
> Was reading your [POST TITLE] piece — the link in the section about
> [SPECIFIC SECTION / paragraph] currently 404s. I checked Wayback and
> the original page at [DEAD_URL] used to cover [WHAT THE DEAD PAGE
> HAD, e.g. "bus schedules from Belgrade to Montenegro"], which looks
> like it went offline around [YEAR FROM WAYBACK].
>
> Not a big deal, but if you wanted a live replacement, I run a free
> Serbian-transit aggregator that covers the same thing and is updated
> nightly: [DEEP_LINK_MATCHING_TOPIC]. Free, no signup, multilingual.
>
> Either way — felt rude not to mention the broken link. Thanks for
> the post.
>
> [YOUR_NAME]
> prevozni.com

---

## Email template (SR) — rarely needed, most broken links are EN blogs

> Subject: Mali detalj: slomljen link u vašem tekstu [POST TITLE]
>
> Pozdrav [FIRST_NAME],
>
> Čitao sam vaš tekst "[POST TITLE]" — link u delu o [SPECIFIČAN DEO]
> trenutno vraća 404. Wayback pokazuje da je originalna stranica
> [DEAD_URL] pokrivala [ŠTA JE IMALA], i verovatno je offline od
> [GODINA].
>
> Nije kritično, ali ako tražite živ zamenjivi link, imam besplatan
> sajt za srpski transport sa istom temom — osvežava se svake noći:
> [DEEP_LINK]. Besplatno, bez registracije.
>
> Kako god — smatrao sam da je korektno reći. Hvala na tekstu.
>
> [YOUR_NAME]

---

## Filling the template — mandatory fields

- `[POST TITLE]` — exact title
- `[SPECIFIC SECTION]` — name the section they will mentally locate
  fast (e.g. "the H3 about 'Getting around'")
- `[DEAD_URL]` — the actual URL that 404s. Paste it.
- `[WHAT THE DEAD PAGE HAD]` — retrieved from Wayback; do NOT guess.
  This is what makes the pitch defensible: you can say "I checked the
  archive, it showed X" if they push back.
- `[YEAR FROM WAYBACK]` — year the Wayback snapshot stopped updating
- `[DEEP_LINK_MATCHING_TOPIC]` — the most topically-matched Prevozni
  page for what the dead link covered:
  - dead was "bus schedules SRB→MNE" → our `/voznja/beograd-do-podgorica/`
  - dead was "Belgrade city transit map" → our `/gradski/beograd/`
  - dead was generic "Serbia transport" → our `/rute/`

## Workflow

1. Run `python scripts/backlinks_broken.py --domains "nomadicmatt.com,matadornetwork.com,..."`
2. For each output row, open the dead URL on Wayback and note the
   original content.
3. Match to our closest page; if no honest match → **skip the pitch**.
   Fake matches destroy response rate on follow-ups.
4. Send one email per target, max 10/day.
5. Log `contacted` in targets.csv so follow-up script knows to chase
   at day 10.

## Why this works when other templates fail

The mention of Wayback + the specific year makes the email feel like
a real person did a real thing. Most outreach blasts skip this step,
so when it's present the reply rate is noticeably higher.

# Промпт для Claude web: Travelpayouts → ссылки для 6 спящих слотов prevozni (2026-10-24)

Ответ (таблица ссылок) принести в Claude Code: он запишет `data/affiliates.local.json` и выкатит. Аккаунт — на маму (18+).

```
You are helping the owner of prevozni.com (Balkan bus timetables, many tourists on Montenegro / Bosnia / Albania coast routes) join the Travelpayouts affiliate network and collect affiliate links. I am logged into Gmail in this browser; use that Gmail address for sign-up and email confirmation.

ACCOUNT HOLDER (individual, not a company): Tetyana Lashchuk, Bulgaria, city Burgas.

RULES
- Allowed: create the Travelpayouts account, accept the Travelpayouts terms and each program's terms when joining it, add the site, join programs, generate links.
- Not allowed: entering any payment or bank details, paying for anything, buying ads, changing anything on prevozni.com, joining programs that need a paid plan.
- If site verification asks to put a meta tag or script on prevozni.com, copy the exact code into the report and continue with whatever works without it. Do not try to add it yourself.
- Only https:// links. Copy links exactly; never invent one.

STEPS
1. Sign up at travelpayouts.com (individual, Bulgaria). Confirm the email from the Gmail tab.
2. Add the project/site https://prevozni.com, topic travel / transport, audience: tourists travelling by bus in Montenegro, Bosnia and Herzegovina, Albania, Croatia (Dubrovnik) and Serbia; languages: Serbian, English, Russian.
3. Join (apply to) these programs if they are offered. Take the first available in each group:
   - transfers: Kiwitaxi, GetTransfer, Intui, Welcome Pickups
   - car rental: Localrent, EconomyBookings, QEEQ, Discover Cars
   - stays: Hotellook, Agoda, Trip.com, Booking-type hotel programs
   - tours/activities: Tiqets, WeGoTrip, GetYourGuide, Klook
   - eSIM: Airalo, Yesim, Drimsim
   - travel insurance: EKTA, VisitorsCoverage, any other offered
4. For every program that is approved instantly, generate a link with the link generator:
   - transfer: the landing page for Montenegro (ideally Kotor or Tivat airport transfers)
   - car rental: Montenegro (ideally Podgorica or Tivat airport pick-up)
   - stays: Kotor (a city search or city landing page)
   - tours: Kotor or Montenegro activities
   - eSIM: Europe / Balkans plan page
   - insurance: the main travel insurance page
   If the generator supports deep links with a destination parameter, note the parameter name.
5. FINAL REPORT: a CSV in a code block with columns slot,program,status,link,deep_link_parameter where slot is one of transfer, cars, stay, tours, esim, insurance (status = approved / pending / rejected / not offered). Then list any site-verification code, commission rates shown for each joined program, the payout minimum, and anything that failed.
```

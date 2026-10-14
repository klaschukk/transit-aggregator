# Промпт для Claude web: панель BusTicket4 (только чтение)

Зачем: `bt4_sales` пуст — мы не знаем, засчитывает ли BT4 наши клики (affiliate 735) и сколько из них стали покупками.
Без этого все оценки дохода гадательные (см. handoff, раздел «/gradski/ — монетизация»).

Перед запуском владелец сам входит в https://busticket4.me/bus в этом браузере. **Пароль в промпт не вставлять.**
Результат вернуть в сессию Claude Code — она сведёт с `ba_clicks` и посчитает конверсию и доход с клика.

```
You are helping the owner of prevozni.com, a BusTicket4 affiliate (affiliate ID 735, company/preduzece 735). I am already logged into the BusTicket4 affiliate panel at https://busticket4.me/bus in this browser.

GOAL: find out how many tickets our referrals actually bought and how much commission we earned. This is READ-ONLY research.

HARD RULES
- Do not change anything: no password, profile, bank/payout details, contracts, settings, no "save"/"submit" on any form except date-range report filters.
- Do not buy tickets, do not cancel anything, do not contact support.
- If you are logged out or a login is requested, STOP and tell me. Do not type any password.
- Report numbers exactly as the panel shows them. If something is missing, say "not shown". Never estimate or fill gaps.

STEPS
1. Open the affiliate sales report (it is likely under "Karte" -> "Prodaja karata za period" / affiliate report, URL like /bus/karte/prod_karata_period_affiliate.php). Note the exact menu path and URL you used.
2. Set the period 2026-08-01 to today. If the report only allows one month at a time, run it for August, September and October 2026 separately.
3. For each day (or each row the report returns) record: date, number of tickets, ticket value, commission (if shown), currency.
4. If the report can be broken down per route/line/departure city, or lists individual tickets, record per row: date, from -> to, price, commission, status (paid/cancelled/refunded). Skip passenger names, emails and phone numbers - do not copy any personal data.
5. Look for: the commission rate shown anywhere (we assume 2%), the current balance / unpaid commission, minimum payout, and payout history (dates + amounts). Just read them.
6. Look for any click / visit statistics for affiliate 735 (clicks, sessions, referrals). If they exist, record them per day or per month.
7. If the panel shows zero sales for the whole period, say so explicitly and screenshot-describe what the report page shows (filters used, any message).

FOR COMPARISON (our own logs): prevozni.com sent these "buy" clicks to busticket4.me checkout with affiliateId=735: August 2026 = 354, September = 680, October 1-14 = 256. Do not try to reconcile them yourself beyond one line: tickets / clicks per month.

FINAL REPORT (plain text, no fluff):
A. Menu path + URL of the report(s) used.
B. Monthly table: month | tickets | ticket value | commission | currency | our clicks | tickets/clicks.
C. Daily table (or per-ticket table from step 4) as CSV in a code block.
D. Commission rate, balance, minimum payout, payout history.
E. Any click statistics found in the panel.
F. Anything that looked wrong, missing or surprising.
```

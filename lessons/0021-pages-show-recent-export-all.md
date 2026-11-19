# L0021 — The sales page lists the latest 200 sales and says how many there are; appointments before today are on no page; `/export.json` holds everything

## Reason
The pages are for the counter today: the recent sales someone may need to
void, and the grooming still to come. A page that grows with every sale
ever made gets slower and longer for nobody's benefit. That is only safe
if the page says that there is more than it shows, and if the whole record
is still somewhere: `/export.json` leaves nothing out.

## Source
The person, run 004, 2026-11-19 (answer 3 of 3: "Enough"). Run 002 had
built it this way without asking and listed both under "Left out, and not
asked".

## What would be a regression
More than 200 sales listed on the page, an older sale missing from
`/export.json`, or the page silent about sales it does not show.

The case covers the sales half. A date before today is refused (L0011), so
no case can put a past appointment in the shop through its interface;
"appointments before today are on no page" is checked by no machine.

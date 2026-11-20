# L1206 — The server sets every canteen date, and the page of a day adds up what happened that day: sales by method, items sold, top-ups, pay-outs, voids, and the cash expected in the drawer, which is cash sales plus top-ups less pay-outs less what was voided that day

## Reason
At the end of the day someone counts the drawer and wants one number to
count it against. Cash goes in with a cash sale and a top-up, and out with
a pay-out and with the void of a cash sale or of a top-up, on the day the
void is made. So a day's cash expected is: cash sales made that day, plus
top-ups made that day, less pay-outs made that day, less cash sales and
top-ups voided that day. A sale made and voided the same day counts on
both sides. A void made on a later day does not change the cash of the
day the sale was made: that drawer was already counted.

"Items sold" lists the lines of the day's sales that still stand. No form
carries a date for a sale, a top-up or a void; the day is the machine's,
or the one given with `--today`. The page shows today, or the day asked
for with `/day?date=YYYY-MM-DD`.

## Source
The person, run 012, 2026-11-20: one typed word, "Accepted", to fifteen
questions asked in one round before building, each with a recommendation
(answer 12). They saw the recommendations as one or a few lines each; they
have not read this file. On which day a void counts, and that an earlier day
can be opened, are the builder's; the person has not seen them.

## What would be a regression
A date taken from a form; a day's cash expected that changes when one of
its sales is voided on a later day; a void that is not taken out of the
drawer of the day it was made; a voided sale among the items sold.

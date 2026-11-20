# L1305 — The server sets every date: a request is due 1 day after it was reported when urgent, 7 when normal, 30 when low, and the overdue list shows open and in-progress requests past due, the most overdue first

## Reason
A date typed by a person is a date that can be wrong or flattering. The day
reported, the day due, the day closed and the day of every history row are
the server's "today"; no form field sets one.

The target is counted from the day reported and follows the priority, so
correcting the priority moves the day due and reopening does not. A request
is overdue when today is after its day due and it is open or in progress.
The overdue list orders by days overdue, most first.

The numbers 1, 7 and 30 were the builder's recommendation, marked as the
person's to confirm, and accepted with the rest.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answer 9). The builder's: a corrected priority moves the day due.

## What would be a regression
A date taken from a form; a day due other than 1, 7 or 30 days after the
report; a request past due missing from the overdue list, or a done,
cancelled or not yet due one on it; the list in another order.

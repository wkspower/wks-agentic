# L0016 — Voiding a sale asks first, on a second page that shows the sale; no page voids on one click

## Reason
A void cannot be undone (L0010): the sale stays voided and can only be
entered again. One stray click on a list of sales should not do that. The
Void link opens a page that shows the sale and one button, "Void this sale".
Opening that page changes nothing. A sale already voided is shown without
the button.

## Source
The person, run 002, 2026-11-19 (answer 3 of 4: "Confirm on a second page").
Run 001 had left it out and listed it under "Left out, and not asked".
Read as written and accepted by the person, 2026-11-19 (run 005).

## What would be a regression
A form on a list or on the first page that posts to a void address, a void
page that changes the sale or the stock when it is only opened, or the
button offered again for a sale already voided.

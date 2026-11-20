# L1208 — The canteen's prices include tax, and its inputs are refused outside the table of bounds in the lesson

## Reason
An input with no bound is accepted until it breaks something later
(L0008). These are the canteen's. All refused outside, with the reason
shown:

| Input | Bound |
|---|---|
| price | 0.01 to 999.99, digits with at most two decimals |
| quantity on a line | whole, 1 to 99, digits only; empty means the item is not bought |
| lines in one sale | 1 to 50 |
| cash given | from the sale's total up to 9,999.99 |
| top-up | 0.01 to 500.00, and the balance after it at most 1,000.00 |
| pay-out | 0.01 up to the balance |
| item name, person's name | 1 to 80 characters after trimming |
| category | 1 to 40 characters after trimming |
| class | 0 to 20 characters |
| card number | empty, or 1 to 20 letters, digits and hyphens |
| kind | pupil or staff |
| search text | 0 to 100 characters |
| the day asked for | a real date written YYYY-MM-DD |
| one form | 65,536 bytes |

## Source
The person, run 012, 2026-11-20: one typed word, "Accepted", to fifteen
questions asked in one round before building, each with a recommendation
(answer 14). They saw the recommendations as one or a few lines each; they
have not read this file. Five rows are the builder's, for inputs the answer
did not list: cash given, pay-out, kind, search text and the day asked for; so
is what a card number may be made of.

## What would be a regression
A value outside the table stored, or a new input added without a row in
the table.

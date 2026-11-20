# L0025 — The pet shop's prices include tax, and its inputs are refused outside the table of bounds in this lesson

## Reason
L0008 says every input has a stated bound; these are the pet shop's. Prices
are entered and shown with tax included, because that is the figure on the
shelf and at the counter. All refused outside:

| Input | Bound |
|---|---|
| price | 0.01 to 99,999.99, at most two decimals, digits and one point only |
| stock, low-stock threshold | whole, 0 to 1,000,000 |
| stock adjustment | whole, not 0, result within 0 to 1,000,000 |
| quantity on a sale line | whole, 1 to 1,000 |
| lines on a sale | 1 to 20 |
| names (product, customer, pet) | 1 to 80 characters after trimming |
| phone | 0 to 30 characters |
| species | 1 to 40 characters |
| one form | 65,536 bytes |

A booking date has no row: the product takes any real day from today on.

## Source
The person, run 001, 2026-11-19 (answers 6 and 13). The numbers were the
builder's choice under answer 13; the person saw the table and kept it in
run 002, 2026-11-19 (answer 1 of 4). Until run 005 this was the second half
of L0008; split off on the person's decision of 2026-11-19, and read and
accepted by the person the same day. The case is the bounds part of the
old case of L0008, with its three wrong variants, unchanged.

## What would be a regression
A value outside the table stored, or a new input added without a row in the
table.

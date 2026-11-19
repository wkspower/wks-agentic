# L0008 — Money is whole cents with tax included, and every input has a stated bound

## Reason
Floating-point money drifts by a cent. An input with no bound is accepted
until it breaks something later: a price of 10^30 was stored without
complaint on 2026-11-18. The bounds, all refused outside:

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

## Source
The wizardly-cerf run, 2026-11-18 (no upper bound on prices). The person,
run 001, 2026-11-19 (answers 6 and 13). The numbers themselves are the
builder's choice under answer 13 and have not been seen by the person.

## What would be a regression
A value outside the table stored, a price kept as anything but integer cents,
or a new input added without a row in the table.

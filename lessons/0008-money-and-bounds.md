# L0008 — Money is whole cents, and every input has a stated bound

## Reason
Floating-point money drifts by a cent: 19.99 times 100 is 1998.9999999999998.
An amount is read from its text into a whole number of cents and stays one.
An input with no bound is accepted until it breaks something later: a price
of 10^30 was stored without complaint on 2026-11-18. So every input a
product takes has a bound, written down where the next builder will read it.

Which bounds is the product's own decision and does not travel with this
lesson. The pet shop's are L0025.

## Source
The wizardly-cerf run, 2026-11-18 (no upper bound on prices). The person,
run 001, 2026-11-19 (answers 6 and 13).
Split in two on the person's decision of 2026-11-19 (run 005): this half
holds for any product that handles money; the pet shop's numbers and "tax
included" went to L0025. Read and accepted by the person the same day.

## What would be a regression
A price kept as anything but integer cents, an amount that went through
floating point on its way in, or an input added with no bound stated in a
lesson of its product.

The case is the pet shop's (L0024): it checks the cents half on the pet
shop's product form and export. "Every input has a stated bound" is checked
for the pet shop by the case of L0025; for another product, by nothing yet.

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
included" went to L0025. Accepted by the person the same day, from a one-line summary given in another session; the person has not read this file.

## What would be a regression
A price kept as anything but integer cents, an amount that went through
floating point on its way in, or an input added with no bound stated in a
lesson of its product.

The case was the pet shop's until run 012, 2026-11-20, when the school
canteen chose `money` and the case failed on it for want of a pet shop: it
was made general (L0024). The form that takes a price, the sale that adds
prices up and where the cents are read come from the product's surface
("money"). "Every input has a stated bound" is checked for the pet shop by
the case of L0025 and for the canteen by the case of L1208.

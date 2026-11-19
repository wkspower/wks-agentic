# L0005 — The pet shop system is for staff: products and stock, customers and their pets, counter sales, grooming appointments

## Reason
"A system for a pet shop" can mean anything from a till to an online store.
Naming what is in, and what is out, is what keeps a rebuild the same size:
no live animals for sale, no online shop for customers, no payment gateway,
no reminders by email or SMS, no partial returns, no data import. English
interface, one currency, amounts shown without a symbol.

## Source
The person, run 001, 2026-11-19: "ok" to the fourteen recommendations asked in
one round before building (answers 1, 2, 5, 6, 8, 9, 11 and 12).
Read as written and accepted by the person, 2026-11-19 (run 005).

## What would be a regression
A rebuild that adds one of the things named as out, or drops one named as in,
without the person saying so.

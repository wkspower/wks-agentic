# L0017 — Customers and pets can be corrected, and nothing is removed

## Reason
A mistyped name or phone number has to be fixable, or it stays wrong on
every later sale and booking. Removing is a different thing: sales and
appointments point at customers, pets and products, and a record that
vanishes takes their meaning with it. So a customer's name and phone and a
pet's name and species can be changed, under the same bounds as when they
were entered (L0008); the row keeps its id, a pet keeps its customer, and
there is no way to delete a customer, a pet or a product.

## Source
The person, run 002, 2026-11-19 (answer 4 of 4: "Edit customers and pets, no
removal"). In run 001 only products could be edited.
Kept by the person, run 004, 2026-11-19 (answer 2 of 3: a pet stays with the
customer it was entered under).
Read as written and accepted by the person, 2026-11-19 (run 005).

## What would be a regression
An edit that skips a bound, changes another row, gives the row a new id or
moves a pet to another customer; or any address that removes a customer, a
pet or a product.

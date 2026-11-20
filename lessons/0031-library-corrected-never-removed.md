# L0031 — Titles and borrowers can be corrected and nothing is removed: a copy is marked lost or withdrawn and can be marked back, and a borrower who has left is marked so

## Reason
A mistyped title or name has to be fixable. Removing is a different thing:
loans point at copies and borrowers, and a record that vanishes takes the
history with it (the reasoning of L0017 for the pet shop). So a title's
fields and a borrower's name, kind and class can be changed under the same
bounds as when they were entered (L0033); the row keeps its id. A copy that
is gone is marked lost or withdrawn, and marked available again if it turns
up. A borrower who has left the school is marked so, keeps their record, and
cannot borrow (L0028).

A copy that is out cannot be marked lost or withdrawn: the book is returned
first, so that the loan ends on a day and leaves the overdue list.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answer 11). That a copy on loan is returned
before it is marked lost is the builder's choice; the person has not seen it.

## What would be a regression
An edit that skips a bound, changes another row or gives the row a new id;
any address that removes a title, a copy or a borrower; a copy on loan
marked lost; or a status outside available, lost and withdrawn.

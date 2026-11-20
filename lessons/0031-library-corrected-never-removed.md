# L0031 — Titles and borrowers can be corrected and nothing is removed: a copy is marked lost or withdrawn and can be marked back, a copy marked lost while it is out ends its loan that day as lost, and a borrower who has left is marked so

## Reason
A mistyped title or name has to be fixable. Removing is a different thing:
loans point at copies and borrowers, and a record that vanishes takes the
history with it (the reasoning of L0017 for the pet shop). So a title's
fields and a borrower's name, kind and class can be changed under the same
bounds as when they were entered (L0033); the row keeps its id. A copy that
is gone is marked lost or withdrawn, and marked available again if it turns
up. A borrower who has left the school is marked so, keeps their record, and
cannot borrow (L0028).

A book is usually lost while it is out, so a copy that is out can be marked
lost. Doing so ends its loan on that day, and the record says how it ended:
the loan has the day it was lost and no day of return. It is not a return.
The loan leaves the list of books out and the overdue list, it no longer
counts against the borrower's limit (L0028), and it can be neither returned
nor renewed afterwards. It stays on record, on the page of loans that have
ended, shown as lost, and in `/export.json` as `lost` with the day.

If the book turns up, the copy is marked available and can be lent again.
The loan that ended as lost is not reopened and not rewritten: a loan is
never edited (L0030).

Withdrawn stays as it was: a copy that is out cannot be marked withdrawn,
and the book is returned first. The reasoning for lost does not carry over.
Withdrawing is something the library does to a book it has in its hands; a
book that is out and will not come back is lost, which is what the other
button is for.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answer 11). In run 006 the builder chose that a
copy on loan is returned before it is marked lost.

Run 007, 2026-11-20: that choice is reversed. The instruction reads: "A book
is usually lost while it is out, so reverse this: marking a copy lost while
it is on loan ends that loan on that day, and the record shows it ended as
lost, not as returned. Withdrawn can stay as it is unless the same reasoning
plainly applies; say which you chose." It reached the session as an
automated notice written in the person's voice, not as a typed message; see
`runs/007-library-review.md`. Withdrawn was left as it was, for the reason
above; that is the builder's choice.

## What would be a regression
An edit that skips a bound, changes another row or gives the row a new id;
any address that removes a title, a copy or a borrower; a copy that is out
refused when it is marked lost, or left out after it; a loan that ended as
lost recorded as returned, returned or renewed afterwards, or changed when
the copy is marked available again; a copy that is out marked withdrawn; or
a status outside available, lost and withdrawn.

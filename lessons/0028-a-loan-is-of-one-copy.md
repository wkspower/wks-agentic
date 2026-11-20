# L0028 — A loan is of one numbered copy to one borrower: a copy that is out, lost or withdrawn is refused, and so is a borrower who has left or holds 3 books as a pupil, 10 as staff

## Reason
A school holds several copies of one title, and the question at the desk is
who has this one. So a title (title, author, optional ISBN, optional shelf
mark) has copies, each with a number the system gives it, and a loan joins
one copy to one borrower. A borrower is a pupil or a member of staff, with a
name and a class written freely ("7B").

A loan that cannot stand is refused whole and says why: the copy does not
exist, is already out, or is marked lost or withdrawn; the borrower does not
exist, has left, or already holds the limit for their kind. The limit counts
books out now; a returned book frees its place.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answers 4, 5 and 6).

## What would be a regression
Two open loans of one copy, a loan of a copy marked lost or withdrawn, a
fourth book to a pupil or an eleventh to staff, a loan to a borrower marked
as having left, or a loan with no copy or no borrower behind it.

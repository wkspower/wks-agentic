# L0033 — The school library's inputs are refused outside the table of bounds in this lesson

## Reason
An input with no bound is accepted until it breaks something later (L0008).
These are the library's. All refused outside, with the reason shown:

| Input | Bound |
|---|---|
| title | 1 to 200 characters after trimming |
| author | 0 to 120 characters |
| shelf mark | 0 to 20 characters |
| ISBN | empty, or 10 or 13 digits once hyphens are removed; the last of 10 may be X |
| copies added at once | whole, 1 to 50, digits only |
| borrower name | 1 to 80 characters after trimming |
| class | 0 to 20 characters |
| kind | pupil or staff |
| copy number on a loan | digits only, at most 9 |
| search text | 0 to 100 characters |
| one form | 65,536 bytes |

The ISBN's check digit is not verified. It is stored without its hyphens.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answer 13). Two rows are the builder's: the
search text and the copy number, inputs the answer did not list. "The last
of 10 may be X" is real data, not the person: about one ISBN-10 in eleven
ends in X (ISO 2108), and the bound as asked, "10 or 13 digits", would have
refused those books. The person had not seen these three when they were built.
Accepted by the person on 2026-11-20 with one "ok", from a one-line summary of this lesson given in another session; the person has not read this file. The ISBN ending in X and the bounds for search text and copy number were named in that summary and kept.

## What would be a regression
A value outside the table stored, or a new input added without a row in the
table.

# L1309 — The maintenance tracker's inputs are refused outside the table of bounds in this lesson

## Reason
An input with no bound is accepted until it breaks something later (L0008).
These are the tracker's. All refused outside, with the reason shown, and
what is stored is what was typed with the spaces around it removed.

| Input | Bound |
|---|---|
| description | 1 to 1000 characters after trimming |
| note | 0 to 500 characters with a change; 1 to 500 on its own |
| reporter's name, worker's name, name of a common area | 1 to 60 characters |
| phone | 3 to 20 characters: digits, spaces, + - ( ) . |
| apartment number | 1 to 10 characters |
| floor | whole, -5 to 200; required for an apartment, may be empty for an area |
| trade | 0 to 40 characters |
| category, priority, kind of place, may enter, active | one of its list |
| a place or worker named by number | digits only, at most 9 |
| search text | 0 to 100 characters |
| one form | 65,536 bytes |

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answer 14): description, notes, names, phone, apartment number and
floor. The builder's rows: which characters a phone may hold, the trade,
numbers that name a row, the search text, the size of a form, and that the
floor of an area may be empty. The person had not seen those when they were
built.

## What would be a regression
A value outside the table stored, or a new input added without a row in the
table.

# L0027 — The school library system is for library staff at one desk: a catalogue of titles and their numbered copies, borrowers, loans, returns, renewals and the overdue list

## Reason
"A lending library system for a school" can mean a desk program or a portal
for every pupil. Naming what is in and what is out keeps a rebuild the same
size. In: what the line above says. Out: a login or a catalogue for pupils,
self-service, fines or any money, reservations, letters or emails about
overdue books, a holiday calendar, import of the school roll or of an
existing catalogue. English interface, dates as YYYY-MM-DD, and "today" is
the machine's clock. `--sample` loads demonstration data into an empty file.

`--today YYYY-MM-DD` starts the library on another day. It exists so that
the cases, and a person trying the program, can see a book become overdue;
every page says so while it is set.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answers 1, 3, 8 and 14). `--today` is the
builder's addition, needed by the cases of L0029; the person has not seen it.

## What would be a regression
A rebuild that adds one of the things named as out, or drops one named as in,
without the person saying so.

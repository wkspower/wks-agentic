# L0029 — The server sets every date: a book is due 14 days after it is lent, a loan is renewed at most twice, each time to 14 days from today, and overdue loans are listed by class

## Reason
A due date typed at the desk is a due date mistyped sooner or later, so no
form carries one: lent is today, due is 14 calendar days on, with no holiday
calendar. A renewal moves the due date to 14 days from the day it is made
and is counted; the third is refused. A book is overdue from the day after
its due date until it is returned.

Overdue books are chased through form tutors, so the overdue page groups
them by the borrower's class, each class under its own heading, and those
with no class last. Nothing is sent to anyone. Being overdue does not stop a
borrower from taking another book: the page where the book is lent shows
what they have overdue, and the person at the desk decides.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answers 6, 7 and 9).

## What would be a regression
A date taken from a form, a book due today shown as overdue, a third
renewal accepted, a renewal counted from the old due date, a returned loan
renewed, an overdue list not grouped by class, or a loan refused because the
borrower has a book overdue.

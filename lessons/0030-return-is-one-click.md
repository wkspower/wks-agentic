# L0030 — Returning a book is one click on the list: no question page, opening an address never returns, and a loan is never edited or removed

## Reason
A return recorded by mistake is put right by lending the book again in one
form, so a question page would cost a click on every return and protect
little (the same reasoning as L0020 for the pet shop's appointments). What
must hold is that the click is a button that posts: a link, a reload or a
browser fetching ahead must not return anything. A returned loan stays on
record with the day it came back and is shown without its buttons. There is
no way to change a loan's copy, borrower or dates, and none to delete it.

## Source
The person, run 006, 2026-11-20: "Ok" to the fourteen recommendations asked in
one round before building (answer 10).

## What would be a regression
A list of loans without a form that posts to the return address of each
open loan, a page that asks before returning, a GET that returns, a second
return that moves the date, a returned loan that disappears, or an address
that edits or removes a loan.

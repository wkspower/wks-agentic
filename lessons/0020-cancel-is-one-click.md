# L0020 — Cancelling an appointment is one click on the list: no question page, and opening an address never cancels

## Reason
A void asks first because it cannot be undone (L0016). A cancelled
appointment can: the slot is free again and is booked again in one form
(L0011). A question page would cost a click on every cancel and protect
little. What still must hold is that the click is a button that posts: a
link, a reload or a browser fetching ahead must not cancel anything, and an
appointment already cancelled is shown without the button.

## Source
The person, run 004, 2026-11-19 (answer 1 of 3: "One click"). Runs 001 and
002 had built it this way without asking and listed it under "Left out, and
not asked" and "Not yet decided".
Accepted by the person on 2026-11-19 (run 005), from a one-line summary of this lesson given in another session; the person has not read this file.

## What would be a regression
The list of appointments without a form that posts to the cancel address of
each live appointment, a page that asks before cancelling, a GET that
cancels, or the button offered for an appointment already cancelled.

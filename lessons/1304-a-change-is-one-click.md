# L1304 — Start, done, cancel and reopen are each one click on the list: no question page, and opening an address changes nothing

## Reason
Every one of these can be undone by another click (reopen, or cancel and
done again), so a question page would cost a click on each of the day's
changes and protect nothing: the reasoning of L0020 and L0030, here because
the person chose it again. What must hold is that the click is a button
that posts: a link, a reload or a browser fetching ahead changes nothing.
A request shows only the buttons its state allows.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answer 10).

## What would be a regression
A list of open requests without a form that posts to the start, done and
cancel address of each as its state allows; a closed list without reopen;
a page that asks before a change; a GET that changes a state; a button for
a change the state does not allow.

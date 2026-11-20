# L0042 — On a wide screen the library's lists fit their box with ordinary names: no text of a row is under the column of buttons held in sight

## Reason
Where a list is a table, its last column, the one with the buttons, is held
in sight when the table is wider than its box (the design the cases under
`web pages` measure at 800 px). Held in sight means drawn over whatever
column is next to it. That is the price of a list too wide for its window,
and it is paid in the column that happens to be last before the buttons.

In the library that column says "6 days overdue". On the overdue page, at
1100 px and with the sample data, the buttons covered it: the page read
"6 da" beside Return and Renew, and the one fact the page exists for was
the one not shown. Nothing was too long: the table was 78 px wider than its
box because a class of two letters and a state of three words were each
given the 150 px of a column of words, and four buttons and links stood on
one line.

So at 1100 px, with names of ordinary length, every list fits its box and
nothing is under the buttons. What it took: a short column (the class) takes
the room of what it holds and no more; the buttons and links of a row may
stand on two lines when room is short; and the day a book was lent, the
least needed, is the last column before the buttons, so that on a narrower
window it is the first to go under them, and the state is the last.

Below 1100 px and above the width where the lists become cards, a list of
loans may still scroll in its box, and what is under the buttons then is
the day it was lent first. That is not measured here.

## Source
A defect found in run 010, 2026-11-20, by the agent reading its own
screenshots of the first build, driven by script on the sample data (L0013):
`/overdue` and `/loans` at 1100 px. All 25 cases in force had passed on
their first run. The case of L0026 that looks at the buttons
(`cases/0022-row-actions-in-sight`) requires that they be in sight; nothing
asked what they were in front of.

Which columns give way, and in what order, is the builder's choice. The
person has not seen it.

## What would be a regression
At 1100 px, with titles and names of several words, a class of a few
letters and a loan both overdue and renewed: a cell of a list whose text
runs under the column held in sight, or past the edge of the box the list
is in.

The case measures Chromium only, the sample of names it enters, and 1100 px.
A name with no space in it of 200 letters still makes the list scroll in
its box at any width where it is a table; that is L0026's ground, not this
lesson's.

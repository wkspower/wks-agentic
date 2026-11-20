# L0042 — Where the library's lists are tables they fit their box with ordinary names: no text of a row is under the column of buttons held in sight

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

So at 1100 px and at 800 px, with names of ordinary length, every list
fits its box and nothing is under the buttons. What it took:

- a short column (shelf mark, kind, status) takes the room of what it holds
  and no more;
- the buttons and links of a row may stand on two lines when room is short;
- in a list of everybody's loans the class stands beside the borrower's
  name, as it was typed ("Bo Li (7b)"), and is not a column;
- the day a book was lent is the last column before the buttons, and from
  761 to 999 px a list of everybody's loans leaves it out. It is on the
  borrower's own page, in the cards of a narrow screen and in
  `/export.json` at every width.

The first fix was made for 1100 px only, where the defect had been seen,
and the lesson said that on a narrower window the day lent would be the
first to go under the buttons. The next screenshot, at 800 px, read
"13 days o": the state was under them again. The case was given 800 px
before the second fix.

Between 761 and 799 px, and with a name of 200 letters and no space at any
width where a list is a table, a list may still scroll in its box. The
first is not measured; the second is L0026's ground.

## Source
A defect found in run 010, 2026-11-20, by the agent reading its own
screenshots of the first build, driven by script on the sample data (L0013):
`/overdue` and `/loans` at 1100 px, and after the first fix `/loans` at
800 px. All 25 cases in force had passed on their first run. The case of L0026 that looks at the buttons
(`cases/0022-row-actions-in-sight`) requires that they be in sight; nothing
asked what they were in front of.

Which columns give way, and in what order, is the builder's choice. The
person has not seen it.

## What would be a regression
At 1100 px or 800 px, with titles and names of several words, a class of a
few letters and a loan both overdue and renewed: a cell of a list whose text
runs under the column held in sight, or past the edge of the box the list
is in.

The case measures Chromium only, the names it enters, and those two widths.

# L0042 — Where a list is a table it fits its box with ordinary names: no text of a row is under the column of buttons held in sight

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

It came back in the next two products, built at the same time (the Source
says how). The canteen's is told there. The maintenance tracker's first build
(run 013) had six columns on its lists of requests: at 800 px the buttons
covered the end of the day due ("+10 c" for "+10 d") and all of the state
and the worker. This lesson was then the library's, by its label, and not in
force for the tracker; its builder had read the line at the start of the
session, thought of it, and allowed for 1100 px only. So the lesson is no
longer one product's: it holds wherever lists are tables with a column held
in sight, which is every product under `web pages`. What the tracker did:
the state, the worker and the day due of a request are one column of two
lines, and under 1000 px the buttons of a row stand on two lines.

What gives way is each product's choice; the four points above are the
library's.

## Source
A defect found in run 010, 2026-11-20, by the agent reading its own
screenshots of the first build, driven by script on the sample data (L0013):
`/overdue` and `/loans` at 1100 px, and after the first fix `/loans` at
800 px. All 25 cases in force had passed on their first run. The case of L0026 that looks at the buttons
(`cases/0022-row-actions-in-sight`) requires that they be in sight; nothing
asked what they were in front of.

Which columns give way, and in what order, is the builder's choice. The
person has not seen it.

Made general twice on 2026-11-20, by two runs started together from one
base, neither knowing of the other (L0024). Each built a product, had every
case in force pass, and read the same defect in its own screenshot at
800 px, with this lesson's line in the text at its start and not in force:

- Run 012, the school canteen. Its list of sales showed no State column at
  all: "stands" and "voided on 2026-11-20" were under Open and Void, so a
  voided sale looked like any other. All 28 cases in force had passed. The
  case failed on the canteen before the fix (the list of accounts too, by
  10 px). What the canteen gave up to fit: the list of sales says when in
  one column and "voided" without the day, which is on the sale's own page.
- Run 013, the maintenance tracker. Its open list hid the end of the day
  due and all of the state and the worker. All 28 cases in force had
  passed. Then a case that fails: this lesson's, put to the tracker with
  names of ordinary length before the fix.

Each run moved the label from `school library` to `web pages`, took "the
library's" out of the line, and had the case take what it enters and
measures from the product's surface; they wrote the same line and two
cases. That two sessions met the defect apart is evidence that a layout
lesson kept under one product's label does not stop the mistake in the
next product; that they then agreed on the remedy is not evidence that the
remedy is right (L0003). The person has seen neither change.

The two cases were made one in run 013, when it took in the base that held
run 012 (`./bring`, which left this file, the case and two surfaces marked).
They measured the same way and differed in what a surface calls its part.
Kept: run 012's names, `under` with `needs`, because the part is called by
the case's own word as `actions`, `cards` and `back` are, because `shows`
already means something else in a surface (`one`), and because the base and
the canteen's branch held them already. Carried over from run 013: a
surface that has no such part is said in words and fails; a day after today
is `{today+20}`, read by what the cases share, where run 012's case put
`{later}` in for itself; the wrong variant names the last cell of a row and
no class of one product; the pet shop's desk is among its pages. Of the pet
shop's two surfaces run 012's asked more (a voided sale and a sale to a
customer must be there, 60 cells, 15 held) and is the one kept. Decided by
the session of run 013 on an instruction written by the coordinating
session; the person has not seen it.

The reasons above the tracker's paragraph are the library's and stay as
written.

## What would be a regression
At 1100 px or 800 px, with names of several words and of ordinary length
and rows that say the most they can (in the library a loan both overdue and
renewed, in the canteen a voided sale paid from a balance, in the tracker a
request in progress, held by a contractor and overdue): a cell of a list
whose text runs under the column held in sight, or past the edge of the box
the list is in.

The case measures Chromium only, the names it enters, and those two widths.

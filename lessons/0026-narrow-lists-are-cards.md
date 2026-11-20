# L0026 — On a narrow screen a list is shown as stacked cards, not as a table: nothing scrolls sideways, nothing is crushed or broken in two, and each row's actions are in sight, from 320 px up with the longest names allowed

## Reason
The counter machine may be a small tablet or a narrow window beside the
till. A table of six or seven columns does not fit 320 px, and there is no
good way to make it: every way out is a defect of its own.

- The page scrolls sideways, or controls leave their form (run 001, L0015).
- Words break anywhere so that it fits: "129.9 / 0", "Adjus / t" (run 001).
- Columns are squeezed to one word per line (run 002, L0018).
- The table scrolls in its own box, and the column with Void, Edit and
  Cancel is out of sight (run 004, L0022).

Each of these was found by eye, fixed, given a case, and followed in the
next build by the next one, three runs in a row. Three lessons that each
forbid one symptom do not say what to build. This one does: below the width
where its columns fit, a list stops being a table. Each row becomes a card,
its fields one under another, each with the name of its column, its links
and buttons inside the card. Then there is no column to crush, no box to
scroll and no last column to lose.

A wide screen keeps the table. What the three old lessons said still holds
at every width and is still measured: no page scrolls sideways, no control
leaves its form, no number, button or link breaks in two, no cell of words
is squeezed under 150 px, and every row that can be acted on shows a way to
do it. A row needs one way in, not all of them: a product's Edit page holds
the form that adjusts its stock as well as the list does.

The cases call 320, 390 and 600 px narrow and require cards there. Where
exactly a product switches is its own choice above that; the pet shop
switches at 760 px.

## Source
Three defects found by the agent reading its own screenshots, 2026-11-19:
run 001 (the sale form ran out of its box at 390 px and the sales list
pushed the page sideways; then the first fix broke prices and buttons in
two), run 002 (the Items column read "2 × / Cat / litter / 10 L," in 30 px),
run 004 (the Void link and the totals were to the right of the box). They
were L0015, L0018 and L0022. The person's decision, 2026-11-19 (run 005),
having read all three: they become one lesson, and the lesson is a design
decision, "on a narrow screen a list is shown as stacked cards, not as a
table"; their three cases stay as checks under it.

## What would be a regression
At 320, 390 or 600 px: a list row whose fields sit side by side, a field
shown without the name of its column, or any box that scrolls sideways.
At any width from 320 px up, with 80-character names with no space in them:
a page wider than its window, a control outside its form, a price, stock
figure, button or link on more than one line, a cell of words on several
lines in less than 150 px, or a row whose links and buttons are all out of
sight. A product's Edit page without the form that adjusts its stock.

The cases were written against the pet shop's pages and made general in
run 006, 2026-11-20, when the school library chose `web pages` (L0024):
what fills the lists and which pages are measured come from the product's
surface. They refused the library's first build twice, at 320 px. Their
wrong variants still expect a list too wide for 800 px to scroll in a box
with its last column held in sight, which is the pet shop's design and not
this lesson's. They measure Chromium only, and not a touch screen.

# L0015 — No page scrolls sideways, no control leaves its form and no number or label breaks in two, from 320 px wide up, with the longest names allowed

## Reason
The counter machine may be a small tablet or a narrow window beside the
till. A bound on a name (L0008) is only safe if the pages hold a name of
that length. A wide table scrolls inside its own box; the page does not.

## Source
A defect found using the app by hand, run 001, 2026-11-19: at 390 px the
selects of the sale form ran outside their box and the sales list made the
whole page scroll sideways. The browser case had only ever run at 1280 px
with short names.

Same day, looking at the fixed pages: the first fix let every word break
anywhere, so the case passed while prices read "129.9 / 0" and buttons
"Adjus / t" at every width. The case now measures that too. A case that
measures width alone is satisfied by a page nobody can read.

## What would be a regression
A page wider than its window at 320, 390 or 1100 px when the shop holds
80-character names with no space in them; or a price, a stock figure, a
button or a link whose text sits on more than one line.

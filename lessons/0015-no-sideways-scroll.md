# L0015 — No page scrolls sideways and no control leaves its form, from 320 px wide up, with the longest names allowed

## Reason
The counter machine may be a small tablet or a narrow window beside the
till. A bound on a name (L0008) is only safe if the pages hold a name of
that length. A wide table scrolls inside its own box; the page does not.

## Source
A defect found using the app by hand, run 001, 2026-11-19: at 390 px the
selects of the sale form ran outside their box and the sales list made the
whole page scroll sideways. The browser case had only ever run at 1280 px
with short names.

## What would be a regression
A page wider than its window at 320, 390 or 1100 px when the shop holds
80-character names with no space in them.

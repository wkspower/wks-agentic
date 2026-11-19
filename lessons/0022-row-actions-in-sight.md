# L0022 — When a table scrolls inside its box, each row's link or button stays in sight, from 320 px up

## Reason
A table too wide for a narrow window scrolls sideways in its own box (L0015,
L0018). The thing a person came to the row for is in its last column: Void,
Edit, Cancel. Scrolled out of sight, with a scroll bar that a tablet does
not draw, it looks as if the row could not be acted on at all. So the column
that acts stays at the edge of the box while the rest scrolls under it. A
row needs one way in, not all of them: the stock adjustment may scroll away
on the list because the product's Edit page offers it too.

## Source
A defect found using the app by hand, run 004, 2026-11-19: at 390 px the
list of sales showed No., When and Items and nothing else; the total and the
Void link were to the right of the box, and on the list of products neither
Adjust nor Edit could be seen. All seventeen cases had passed; the cases of
L0015 and L0018 measure that the page does not scroll and that columns are
not crushed, which is exactly what pushes the last column out.

## What would be a regression
At 320 or 390 px, a table row that has links or buttons and none of them
wholly visible without scrolling; or a product's Edit page without the form
that adjusts its stock.

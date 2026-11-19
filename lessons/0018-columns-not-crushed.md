# L0018 — A table scrolls inside its box before it crushes a column of words to one word per line

## Reason
A table too wide for a narrow window has two ways out: scroll sideways in
its own box (L0015), or squeeze its columns. Squeezed, a column of words
ends up one word per line, and the items of a sale read down the page like
a list of something else. A cell of words either stays on one line or
keeps at least 150 px; past that the table scrolls.

## Source
A defect found using the app by hand, run 002, 2026-11-19: at 390 px the
Items column of the sales list read "2 × / Cat / litter / 10 L, / 1 × /
Flea / collar," in a column 30 px wide, and product names took three lines.
All thirteen cases had passed; the case of L0015 measures numbers, buttons
and links, and names with no space in them.

## What would be a regression
At 320 or 390 px, a table cell whose words run over more than one line
while the cell is narrower than 150 px.

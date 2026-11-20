# Run 005 — labels, and the person's review of the lessons

- **Prompt:** none under test. The person's instructions of 2026-11-19: change
  the scaffold so lessons can be switched on per product, label the lessons,
  and record their review of L0005 to L0022.
- **Branch:** `run/005-labels`, 2026-11-19, started from the end of run 004.

## Questions

None. The instructions said everything had been answered, and nothing in
them turned out undecidable. What was decided by the builder is listed at
the end, for the person to overrule.

## What changed in the scaffold

- A lesson line carries its labels in square brackets after its number.
  There is no list of labels.
- `product/LABELS` is the one place a product says what it is, one label
  per line. It is inside `product/` so that the tree without `product/` is
  the base, with nothing else to remove.
- A lesson is in force when it is `always` or carries at least one label
  the product declared. `./check` runs only the cases of lessons in force,
  prints every label with on or off and its count, names each lesson not in
  force, and counts both in the summary line. A lesson not in force must
  still have its file, its Reason and Source, and its case.
- `./check` fails on: a lesson with no label or an empty one; a declared
  label no lesson carries; a `product/` with files and no declared label; a
  label declared twice; one case named by two lessons.
- A lesson line may name several cases (`cases:`), needed for L0026.
- `./check --cases` prints the cases in force. The case of L0019 uses it.
- `./check --selftest` now accepts 5 right trees and refuses 19 wrong ones
  (run 004: 1 and 11). Eight wrong trees and four right ones are about labels.

## Lessons: 22 before, 23 after

| | |
|---|---|
| Added | L0023 labels (case), L0024 a case is born in its product (prose), L0025 the pet shop's bounds (case, split from L0008), L0026 narrow lists are cards (4 cases) |
| Removed | L0015, L0018, L0022, folded into L0026 with their history |
| Reworded | L0008 (the money half only), L0013 (what "by hand" has been) |
| Source updated | L0005 to L0021: read and accepted by the person, 2026-11-19 |
| Owed a second look by the person | L0011 (the hours), L0021 (past appointments on no page) |

Labels as they stand:

| Label | Lessons |
|---|---|
| `always` | L0001, L0002, L0003, L0004, L0013, L0019, L0023, L0024 |
| `web pages` | L0012, L0014, L0026 |
| `local web server` | L0007 |
| `money` | L0008 |
| `python stdlib and sqlite on localhost` | L0006 |
| `pet shop` | L0005, L0009, L0010, L0011, L0016, L0017, L0020, L0021, L0025 |

Case before fix, by commit:

- `f144808` the labels, the split of L0008, L0013, L0023 to L0025. The check
  was changed together with its selftest; no product code changed.
- `4c09246` L0026 with its new case failing on the product as it stood
  ("/ at 320 px is still a table").
- `a7a9b88` the product (20 lines of style sheet and a
  `data-label` on each cell), and the three older cases adjusted.

## What was adjusted in cases, and why

No case was made general (L0024). Four were changed:

- **0008** was split, not generalised. The cents half stays under L0008 and
  got two wrong variants of its own (a price through floating point, a
  third decimal cut off) and prices that drift (0.29, 19.99). The bounds
  half is `cases/0025-pet-shop-bounds` with its three variants.
- **0019** had to pass in a tree with no product, because L0019 is `always`.
  It now runs the cases in force, and plants a one-line product of its own
  for the two planted cases: one that reads the source (refused) and, new,
  one that only runs it (accepted), which is the control it lacked.
- **0015, 0018, 0022**: once lists were cards, their wrong variants stopped
  biting at 320 and 390 px, so the cases passed on them. All three now also
  measure 800 px, where the lists are tables with little room, and 0022 got
  a second variant ("the build of run 004 before its fix").

## What the new rules do not catch

Printed by `./check --selftest` and written in L0023:

- A label misspelt on a lesson. The lesson is simply never in force; it
  shows only in the list of labels with a count of 1.
- Two labels that mean the same thing.
- A lesson labelled too narrowly (the next product never sees it) or too
  widely.
- A product that leaves out a label it should have chosen.
- A case under a general label that only works on the product it was born
  in. This one is by design: it fails on the second product (L0024).

Also not built: a lesson that needs two labels at once. Several labels on a
lesson mean any of them.

## Check at the end

    lessons 23 · in force 23 · not in force 0 · with a case 18 · prose only 5 · cases run 21 · cases not run 0 · product: pet shop, web pages, local web server, money, python stdlib and sqlite on localhost · CLAUDE.md 8465 bytes

On a copy of the tree without `product/`:

    lessons 23 · in force 8 · not in force 15 · with a case 18 · prose only 5 · cases run 4 · cases not run 17 · product: none · CLAUDE.md 8465 bytes

The second is also measured on every run by the case of L0023. `./check`
takes about 60 s with the pet shop (run 004: 40 s) and 3 s on the base.
`./check --selftest`: accepted 5 of 5 right trees, refused 19 of 19 wrong.
The cases over the product run 39 wrong variants, all refused after acting.

## Size

Product 801 lines (run 004: 781). Cases 1679 lines (1406), shared helpers
330, `check` 298 (167), lesson files 569 (445).

## Driven by script and read by the agent (Chromium 157; 390 px light, 320 px dark, 700 px and 1100 px light)

On the sample data plus an 80-letter product name and a 30-digit phone. In
the cards at 390 px the script adjusted a stock by "+10" (14 to 24),
cancelled an appointment in one click, followed Void to the question page
and voided, and followed Edit on a customer. I read the screenshots of the
products, sales, appointments and customers lists as cards, and of the
products list as a table at 1100 px. Nothing was changed after looking.
The person has not used the app.

## Not verified

- Everything listed in run 004 still stands; none of it was looked at.
- Cards were seen in Chromium only. With the style sheet's `display: block`
  on table cells a screen reader may no longer announce a table; not tried.
- Between 760 px and about 900 px a table with the longest content (a
  30-digit phone) still scrolls inside its box with its last column held in
  sight, as in run 004. Measured at 800 px by cases; seen by nobody.
- At 700 px a card is as wide as the window and mostly empty. Readable; not
  pretty. Left as it is.
- The labels were tried on one product. Whether they cut in the right
  places shows only when a second product declares some of them.
- The `--selftest` trees are refused, but not each for its own reason: a
  wrong tree refused for a different problem would still count.

## Decided by the builder, for the person to overrule

- The declaration is `product/LABELS`, not a file at the root.
- Several labels on one lesson mean any of them.
- L0006 has one label for its three choices, because one case checks them
  together. It is not `sqlite`: a product that picked only SQLite would have
  got the localhost and standard-library rules with it.
- "Tax included" went with the pet shop's numbers (L0025), not with `money`.
- The pet shop switches to cards at 760 px; the lesson requires them at
  320, 390 and 600 px.
- A `product/` with files and no label fails. A product is always something.

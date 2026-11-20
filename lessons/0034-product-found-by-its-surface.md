# L0034 — What the cases know about a product is in its file under `surface/`, found through `product/LABELS`; nothing the cases share remembers a product of its own

## Reason
The shared case library was written for the first product and kept its
program's name as the default. With a second product in the tree, a case
that asked the library "is there a product here?" was told no, and went on
to pass.

So nothing shared by the cases names a product. Each product has one file,
`surface/NAME.json`: its label, its program, and what the cases under
general labels need to know about its pages (L0024). A case that belongs to
one product asks for that surface by its label; a general case asks for the
one that `product/LABELS` declares. No surface, or two, is a failure and
never a default.

## Source
A defect found in run 006, 2026-11-20, by reading what a passing case
printed. With `product/library.py` in place, `cases/0019-cases-know-no-source`
passed and said "17 of 17 cases in force pass in a tree with no product
source (... no product in this tree, one planted)". It had looked for
`product/petshop.py`, found none, and run every case with the library's
source still in the tree. The case measured nothing about the library, and
its summary line was the only sign.

## What would be a regression
A program name of some product in `caselib.py` or `caselib.js`; a case that
starts a product without having asked for its surface; `product()` choosing
one when `product/LABELS` names none or two; or the case of L0019 running
the cases while a product's source is in its scratch tree.

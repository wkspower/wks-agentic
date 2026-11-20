# L0023 — A lesson says when it applies in plain labels, a product declares the labels it chose, and only `always` and those are in force

## Reason
Lessons are of different kinds. Some hold for every product (how cases are
written), some for any product with a certain layer or technology (web
pages, money, SQLite), some for one business only. In one flat list the
next product would inherit the pet shop's rules, and the web lessons could
not be reused without them.

So each lesson line in `CLAUDE.md` carries one or more labels in square
brackets, written when the lesson is written. There is no list of allowed
labels: a new kind of lesson needs only a label nobody has used before. A
product says what it is in one place, `product/LABELS`, one label per line.
A lesson is in force when it carries `always` or at least one label the
product declared. `./check` runs the cases of the lessons in force, names
the lessons not in force, and counts both. A label the product declares that
no lesson carries fails, because it is most likely a typo. A tree with no
product has only `always` in force and passes: that tree is the base every
new product starts from.

A lesson not in force is still kept whole: its file, its reason and its case
must be there, so that switching it on is one line in `product/LABELS`.

## Source
The person's decision, 2026-11-19 (run 005), after four runs on the pet
shop: "I do not want the kinds defined up front. I want room for them to
grow one lesson at a time."

Run 008, 2026-11-20, on the coordinating session's instruction: the lines
are no longer all in `CLAUDE.md`. That file holds the lines labelled
`always`; every other line is in `LESSONS.md`, and `./check --lessons`
prints the ones in force (L0039). What a label is, and when a lesson is in
force, did not change. Since run 009 a hook puts those lines in front of
every session at its start (L0041).

## What would be a regression
A lesson line with no label; a fixed list of labels that a new lesson must
choose from; a case run for a lesson the product did not switch on, or not
run for one it did; this tree without `product/` failing `./check`.

`./check --selftest` plants the wrong trees. What it does not catch: a label
misspelt on a lesson (it only shows as a lesson not in force), two labels
that mean the same, a lesson labelled too narrowly or too widely, and a
product that leaves out a label it should have chosen. Those need a reader:
`./check` prints every label with its count so that a stray one stands out.

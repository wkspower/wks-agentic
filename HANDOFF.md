# Handoff

**Run 007 (2026-11-20) made two changes to the library and did not record
the review they came with.** `./check` passes: 33 lessons, 23 in force, 21
cases run, 67 wrong variants refused; without `product/`, 9 in force and 5
cases run. The changes: a copy that is out can be marked lost, which ends
its loan that day as lost (L0031, reversed); classes are compared without
regard to capitals (L0036, new). See `runs/007-library-review.md`.

## Owed: the person's review of L0027 to L0035, in their own message

The instruction of run 007 says the person read L0027 to L0035 and accepts
them with those two changes. It arrived as an automated notice that says it
is not user input and carries no approval, and the session's permission
check stopped the acceptance from being written into the lessons. Nothing
in `lessons/` says the person accepted anything in run 007. **Do not merge
this branch into the base as reviewed until the person has said so
themselves.** When they do, write what the instruction asked for:

- In the Source of each of L0027 to L0035: read and accepted by the person
  on 2026-11-20 (or the day they say).
- Kept as built, where a Source says "the person has not seen it": `--today`
  with its notice (L0027); an ISBN of 10 that ends in X, and the bounds for
  search text and copy number (L0033); the scan field that comes back empty
  (L0035). Say they have seen it and kept it.
- L0028 and L0029: the numbers (3 books for a pupil, 10 for staff, 14 days,
  two renewals) are accepted as built and owed a confirmation by the school.
  Mark them so; not to be asked about until the person brings it up.
- Then look at what run 007's builder chose, listed in its run record:
  withdrawn left as it was, how a class is shown when both spellings exist,
  and ten smaller things.


**Run 006 (2026-11-20) built the second product on this branch: a school
library.** `./check` passed with it: 32 lessons, 22 in force, 20 cases run,
57 wrong variants refused. The person answered one round of 14 questions
with "Ok" and has not used the library or read L0027 to L0035. Merging
those lessons into the base is theirs to do.

What the run changed in the scaffold, beyond adding lessons:

- `surface/NAME.json`, one per product, holds what the cases under general
  labels may know about that product. The eight such cases read it; they
  pass on the library here and on the pet shop build of run 005.
- `caselib.py` and `caselib.js` name no product. A case asks for one:
  `caselib.product()` for the product `product/LABELS` declares, or
  `caselib.product("pet shop")` for a case born in one product (L0034).
- To put the cases to another build: `SHOP=path/to/main cases/NNNN-...`, and
  `SURFACE="pet shop"` as well when the tree's own product is another one.

To use the library: `python3 product/library.py --sample`, then open
http://127.0.0.1:8000/. `--today 2026-12-20` shows it on another day.

Owed to the person from this run, in `runs/006-school-library.md`: ten
things decided by the builder, and what was not verified.

## The base (2026-11-20, before run 006)

The base holds the lessons and cases after run 005 and no product. The
person read and accepted the lessons on 2026-11-19 and approved that merge.
The pet shop itself lives on branch `run/005-labels`; its lessons are here,
switched off until a product declares their labels.

## State (2026-11-19, after run 005)

Run 005 changed the scaffold: every lesson line says when it applies, in
labels; the product says what it is in `product/LABELS`; `./check` puts in
force `always` and the lessons the product's labels switch on, runs their
cases, and names the rest. The person read and accepted L0005 to L0022 that
day, with three changes: L0015, L0018 and L0022 became one lesson (L0026,
narrow lists are stacked cards), L0013 says what "by hand" has been, and
L0008 was split (L0025 holds the pet shop's numbers).

`./check` passes with the pet shop declared: 23 lessons, all in force, 18
with a case, 5 prose only, 21 cases run, 39 wrong variants refused. Without
`product/` it passes with 8 in force and 15 named as not in force.
`./check --selftest` accepts 5 right trees and refuses 19 wrong ones.

`product/petshop.py` is the build of run 004 with the cards of run 005.
The person has not used the app yet (L0013). Merging this branch into
`lessons-and-cases` is theirs to do.

What the cases fix is the surface: the command line in `caselib.py`, the
paths and form fields, the keys of `/export.json`, the status answers, a
few class names and texts, and now `thead th` naming each column and each
cell showing that name on a narrow screen. A rebuild may be written any way
that meets it. To put the cases to another build without touching
`product/`: `SHOP=path/to/main cases/NNNN-...`. Earlier builds exist on
other branches; reading them before a rebuild defeats the test.

What the faults do not prove is in `runs/003-variants-by-behaviour.md` and
`lessons/0019-cases-know-no-source.md`. What the labels do not catch is in
`lessons/0023-labels-switch-lessons.md` and `runs/005-labels.md`.

## Owed a second look by the person

Not to be changed and not to be asked about until they bring it up:

- L0011: the grooming hours (09:00 to 17:00, on the hour, every day).
- L0021: appointments before today are on no page.

## How to resume

1. Read `CLAUDE.md`, then this file.
2. Run `./check`. If it fails, that is the first thing to fix.
3. To test a prompt, follow `prompts/README.md`.
4. To use the product on this branch, see the top of this file. The pet
   shop is on `run/005-labels`: `python3 product/petshop.py --sample`. The
   cases need Python 3 and Node with Playwright.

## How a new product starts from the base

The base is this branch without `product/`. Nothing else is removed: the
pet shop's lessons and cases stay in it, not in force.

1. Make a branch from the base and run `./check`. It passes with only
   `always` in force and prints every label that exists with its count.
2. Ask the person everything foreseeable in one round (L0004). What the
   product is and what it is built on are among the questions; offer the
   existing labels that seem to fit, and say which lessons each brings.
3. Write `product/LABELS` from the answers, one label per line. A label no
   lesson carries fails the check, so a new kind of thing gets its label
   when its first lesson is written, not before.
4. Write `surface/NAME.json` for the product, with its label and program,
   and run `./check` again. The cases now in force fail: some because there
   is no product yet, and some because the surface does not yet say what
   they need. A case under a general label that turns out to know one
   product's pages is made general then (L0024), kept passing on the other
   products' builds, and named in the run record. Do not switch the label
   off to get past it. Run 006 did this for eight cases.
5. Lessons learned while building get the labels they deserve: the
   product's own name for its business rules, an existing label when the
   lesson would hold for the pet shop too, `always` only for how the work
   is done.

For a rebuild test of the pet shop, delete everything in `product/` except
`LABELS`.

## What the thesis predicts, and what would count against it

- A session started here follows the lessons without being told to in the
  prompt. Against: it ignores them, or follows only the ones with a case.
- New knowledge from a run ends up as lessons, and the checkable ones get a
  case written before the fix. Against: lessons are added after the fact, or
  everything is marked prose.
- A second run of the same prompt, starting from the first run's lessons,
  asks fewer questions and repeats none of the recorded mistakes. Against:
  the same questions or mistakes come back.
- The cost of lessons and cases stays small next to the product. Against:
  it grows the way the planted builds did.

## Not yet decided

- Whether the pet shop's branch takes the general cases and its surface.
  They pass on its build; the branch was not touched.
- Whether the cases under `web pages` may go on requiring a scrolling box
  with its last column held in sight at 800 px. L0026 does not ask for it;
  the wrong variants of two cases do (`runs/006-school-library.md`).
- Whether `money` should be made general. No second product has needed it.

- A stated bound for the booking date (L0025 has no row for it).
- Whether a lesson may need two labels at once. Today several labels mean
  any of them, and nothing has needed more.
- Whether to keep a tool that changes the source mechanically and lists the
  wrong builds the cases let through. Run 003 did this once by hand and
  kept no script.
- Whether "one program in `product/`" (L0006) should get a check again; it
  lost its only one in run 003.
- Whether `product/` should be deleted between runs of the same prompt (the
  rebuild test) or kept.
- A size limit for `CLAUDE.md`. The check prints its size and enforces none;
  it grew from 6963 to 8465 bytes in run 005, mostly the labels and the
  four cases of L0026.

## Runs

Each run adds a file under `runs/` and a line here.

- [001 pet shop](runs/001-pet-shop.md), 2026-11-19: 1 round of 14 questions, 11 lessons added (9 with a case), 2 defects found by hand.
- [002 pet shop, rebuilt](runs/002-pet-shop-rebuild.md), 2026-11-19: 1 round of 4 questions, 3 lessons added (all with a case), 1 defect found by hand, no old wrong variant rewritten.
- [003 wrong variants by behaviour](runs/003-variants-by-behaviour.md), 2026-11-19: no questions, 1 lesson added (with a case), 2 changed; cases only, 29 faults at the interface in place of 28 text replacements.
- [004 pet shop, rebuilt with no history](runs/004-rebuild-no-history.md), 2026-11-19: 1 round of 3 questions, 3 lessons added (all with a case), 1 defect found by hand, no inherited case changed.
- [005 labels](runs/005-labels.md), 2026-11-19: no questions, scaffold changed so lessons are switched on per product; 4 lessons added (3 with a case), 3 folded into one, the person's review of L0005 to L0022 recorded; lists became cards on a narrow screen, case first.
- [007 library review](runs/007-library-review.md), 2026-11-20: no questions, no prompt; 1 lesson reversed and 1 added (both with a case, case first), 1 defect found writing a case, 1 addition refused by an inherited case; the review the run was to record is not recorded, and why.
- [006 school library](runs/006-school-library.md), 2026-11-20: 1 round of 14 questions, 9 lessons added (8 with a case), the second product; 8 cases made general and kept passing on the pet shop; 1 defect found in the scaffold and 1 in the product by hand.

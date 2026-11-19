# Handoff

## State (2026-11-19, after run 003)

Run 003 changed the cases and nothing else. A wrong variant used to be one
line of `product/petshop.py` replaced by another; run 002 showed that this
made a rebuild copy those lines. Now a wrong variant is the product with one
fault at its interface: a function in front of its HTTP requests, or a
change to the page in the browser (L0019). No case names, reads or edits the
product's source, and the case of L0019 proves it by running every other
case in a tree that has only the product's bytecode.

`./check` passes: 19 lessons, 15 with a case, 4 prose only; 29 wrong
variants, all refused. `./check --selftest` refuses 11 of 11 wrong trees.
The product is the one run 002 built, unchanged.

L0001 to L0004 are the seed lessons. L0005 to L0015 came from run 001,
L0016 to L0018 from run 002, L0019 from the person's decision after run 002.
The person has read none of L0005 to L0019 as written; merging them into
`lessons-and-cases` is theirs to do.

What the cases fix is the surface: the command line in `caselib.py`, the
paths and form fields, the keys of `/export.json`, the status answers. A
rebuild may be written any way that meets it. To put the cases to another
build without touching `product/`: `SHOP=path/to/main cases/NNNN-...`.

What the faults do not prove, and the one measurement made of it (the 28
old replacements replayed by hand, all refused), is in
`runs/003-variants-by-behaviour.md` and `lessons/0019-cases-know-no-source.md`.

## How to resume

1. Read `CLAUDE.md`, then this file.
2. Run `./check`. If it fails, that is the first thing to fix.
3. To test a prompt, follow `prompts/README.md`.
4. To use the shop: `python3 product/petshop.py --sample`, then open
   http://127.0.0.1:8000/. The cases need Python 3 and Node with Playwright.

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

- Whether cancelling an appointment should ask first, as void now does, and
  whether a pet can move to another customer. See
  `runs/002-pet-shop-rebuild.md`.
- Whether to keep a tool that changes the source mechanically and lists the
  wrong builds the cases let through. Run 003 did this once by hand and
  kept no script.
- Whether "one program in `product/`" (L0006) should get a check again; it
  lost its only one in run 003.
- Whether `product/` should be deleted between runs of the same prompt (the
  rebuild test) or kept.
- A size limit for `CLAUDE.md`. The check prints its size and enforces none.

## Runs

Each run adds a file under `runs/` and a line here.

- [001 pet shop](runs/001-pet-shop.md), 2026-11-19: 1 round of 14 questions, 11 lessons added (9 with a case), 2 defects found by hand.
- [002 pet shop, rebuilt](runs/002-pet-shop-rebuild.md), 2026-11-19: 1 round of 4 questions, 3 lessons added (all with a case), 1 defect found by hand, no old wrong variant rewritten.
- [003 wrong variants by behaviour](runs/003-variants-by-behaviour.md), 2026-11-19: no questions, 1 lesson added (with a case), 2 changed; cases only, 29 faults at the interface in place of 28 text replacements.

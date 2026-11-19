# Handoff

## State (2026-11-19, after run 002)

Run 002 was the rebuild test: `product/` had been deleted, and the pet shop
was built again from the lessons and cases of run 001 alone, after one round
of 4 questions. `./check` passes: 18 lessons, 14 with a case, 4 prose only.
`./check --selftest` refuses 11 of 11 wrong trees.

L0001 to L0004 are the seed lessons. L0005 to L0015 came from run 001.
L0016 and L0017 are the person's answers in run 002; L0018 is a defect found
looking at the pages. The person answered the questions behind L0016 and
L0017 but has read none of L0005 to L0018 as written; merging them into
`lessons-and-cases` is theirs to do.

The cases of L0006 to L0018 talk to the product only through its command
line, its forms and `/export.json`, so they are the contract for a rebuild.
Their wrong variants name text in `product/petshop.py`. Run 002 kept every
one of them by writing the new source to hold that text; a rebuild that does
not must rewrite those lines, and the case says so when the text is gone.

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
- Whether `product/` should be deleted between runs of the same prompt (the
  rebuild test) or kept.
- A size limit for `CLAUDE.md`. The check prints its size and enforces none.

## Runs

Each run adds a file under `runs/` and a line here.

- [001 pet shop](runs/001-pet-shop.md), 2026-11-19: 1 round of 14 questions, 11 lessons added (9 with a case), 2 defects found by hand.
- [002 pet shop, rebuilt](runs/002-pet-shop-rebuild.md), 2026-11-19: 1 round of 4 questions, 3 lessons added (all with a case), 1 defect found by hand, no old wrong variant rewritten.

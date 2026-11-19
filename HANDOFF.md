# Handoff

## State (2026-11-19, after run 001)

**Before run 002:** `product/` was deleted on this branch on purpose. This is
the rebuild test: the lessons and cases of run 001 are all that is left of the
pet shop. `./check` fails until a product exists again. The lessons L0005 to
L0015 are here unmerged and unread by the person, exactly as run 001 left them.

Run 001 built the pet shop in `product/` from the one-line prompt. `./check`
passes: 15 lessons, 11 with a case, 4 prose only. `./check --selftest`
refuses 11 of 11 wrong trees.

L0001 to L0004 are the seed lessons from the runs of 2026-11-18. L0005 to
L0013 are the person's answers to one round of 14 questions. L0014 and L0015
are defects found using the app by hand. None of L0005 to L0015 has been
read by the person yet; merging them into `lessons-and-cases` is theirs to do.

The cases of L0006 to L0015 talk to the product only through its command
line, its forms and `/export.json`, so they are the contract for a rebuild.
Their wrong variants name text in `product/petshop.py`; a rebuild has to
rewrite those lines of each case, and the case says so when the text is gone.

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

- The bounds in L0008 and the grooming hours in L0011 (09:00 to 17:00, every
  day) are the builder's numbers. The person has not seen them.
- Whether voiding a sale should ask first, and whether customers, pets and
  products need editing or removing. See `runs/001-pet-shop.md`.
- Whether `product/` should be deleted between runs of the same prompt (the
  rebuild test) or kept.
- A size limit for `CLAUDE.md`. The check prints its size and enforces none.

## Runs

Each run adds a file under `runs/` and a line here.

- [001 pet shop](runs/001-pet-shop.md), 2026-11-19: 1 round of 14 questions, 11 lessons added (9 with a case), 2 defects found by hand.

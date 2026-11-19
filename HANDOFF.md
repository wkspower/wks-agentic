# Handoff

## State (2026-11-19, after run 004)

Run 004 was the rebuild test: the branch started as one commit with no
`product/` and no history, and the pet shop was written again from the
lessons and the cases alone, without reading any earlier build. All 15
inherited cases passed on it unchanged. `product/petshop.py` is that build.

`./check` passes: 22 lessons, 18 with a case, 4 prose only; 36 wrong
variants, all refused. `./check --selftest` refuses 11 of 11 wrong trees.

L0001 to L0004 are the seed lessons. L0005 to L0015 came from run 001,
L0016 to L0018 from run 002, L0019 from the person's decision after run 002,
L0020 to L0022 from run 004 (two from the person's answers, one from a
defect found by hand). The person has read none of L0005 to L0022 as
written; merging them into `lessons-and-cases` is theirs to do.

What the cases fix is the surface: the command line in `caselib.py`, the
paths and form fields, the keys of `/export.json`, the status answers, a
few class names and texts. A rebuild may be written any way that meets it.
To put the cases to another build without touching `product/`:
`SHOP=path/to/main cases/NNNN-...`. Earlier builds exist on other branches;
reading them before a rebuild defeats the test.

What the faults do not prove is in `runs/003-variants-by-behaviour.md` and
`lessons/0019-cases-know-no-source.md`. Nobody has replayed mechanical
changes against the product of run 004.

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

- The narrow layout has produced one defect found by hand in each of runs
  001, 002 and 004 (L0015, L0018, L0022), each the side effect of the fix
  before. Whether tables should stop being tables below some width.
- A stated bound for the booking date (L0008 has no row for it).
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
- [004 pet shop, rebuilt with no history](runs/004-rebuild-no-history.md), 2026-11-19: 1 round of 3 questions, 3 lessons added (all with a case), 1 defect found by hand, no inherited case changed.

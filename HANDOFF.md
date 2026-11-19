# Handoff

## State (2026-11-19)

The scaffold exists and nothing has been built with it yet. `./check` passes:
4 lessons, 2 with a case, 2 prose only. `./check --selftest` refuses 11 of 11
wrong trees. No prompt has been run on this branch.

The four seed lessons come from the pet shop runs of 2026-11-18 on the other
branches of this repository. They are here so the first run starts with
something to follow and so the check has real input.

## How to resume

1. Read `CLAUDE.md`, then this file.
2. Run `./check`. If it fails, that is the first thing to fix.
3. To test a prompt, follow `prompts/README.md`.

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

- Whether `product/` should be deleted between runs of the same prompt (the
  rebuild test) or kept.
- A size limit for `CLAUDE.md`. The check prints its size and enforces none.

## Runs

None yet. Each run adds a file under `runs/` and a line here.

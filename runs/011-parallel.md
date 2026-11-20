# Run 011 — parallel: two runs from one base can both be brought back

- **Prompt:** none under `prompts/`. This run changes the scaffold and tests
  no product prompt. It built no product.
- **Branch:** `run/011-parallel`, 2026-11-20, started from `08792aa`, the
  base after run 010, with no `product/`.
- This record was begun with the run's first lesson, as L1101 asks, and
  written in full at the end.

## How the instruction arrived

As an automated notice written by the coordinating session, which says so
itself. The person's own words, as that notice reports them: "It doesn't
need to be perfect, it will never be. It needs to be adaptable and scalable.
Different product experiences contribute with the process improvement. And
the process enforces common practices", and then "Yes" to the coordinating
session's offer to set up two products built at the same time from the same
base and merged back, fixing the lesson numbering first. The analysis (three
ways the scaffold breaks), the result to prove and the constraints are the
coordinating session's. No lesson of this run says the person decided, read
or accepted more than those words (L0037).

The session had the text "Lessons at the start of this session" from the
hook before its first action: no product, six labels, L0005 to L0042.

## Questions

None. The instruction said what to make true and what to hold fixed.

## What changed

**A lesson's number is its run and its place in it (L1101).** L1203 is the
third lesson of run 12. L0001 to L0042 keep their numbers; L0043 to L0099
are never given. The run's number is in the name of its branch,
`run/NNN-slug`. `./check --next` prints the next number, and the hook's
text says it at the start of every session on a run's branch. The check
refuses a lesson in the closed sequence, and a lesson past L0042 whose run
has no `runs/0NN-*.md` in the tree. This run's own lessons are L1101 and
L1102.

**`./bring OTHER` is how a run's lessons come back (L1102).** It compares
this checkout, the other branch and the commit where they parted. Lesson
lines go by number and are written in order; every line either side added
to the handoff is kept; every other file is taken whole from the one side
that changed it; `product/` is never brought. It refuses, changing nothing:
a number or a path taken twice, a lesson in a block that is not its run's,
and, where there is no product, anything both sides changed. It names
without deciding: lessons from the two sides under one label, and what it
brought that reaches other products. It ends by running `./check`, writes
the message of the merge commit and commits nothing.

Also: `./bring --verify OURS THEIRS` (is this tree what the rules give),
`./bring --try BRANCH` (this tree's check with that branch's product, in a
scratch copy), `./bring --begin SLUG ...` (branches with the next free run
numbers).

## What happens when two products change what is shared

`caselib.py`, `caselib.js`, a general case, `check`, `bring`: a file is one
thing to the operation, taken whole.

- Only one of the two branches changed it: it is taken, and named under
  "reaches" so that it is seen. No case of the other product has run
  against it on the base, because the base has no product. `./bring --try`
  for the other product's branch is what shows that.
- Both changed it: the base refuses the second branch, whatever git's
  merge of the text would say. The second branch takes the base in
  (`./bring` there). On a branch with a product the same file is merged by
  text and named, text git cannot merge is left marked for the session, and
  `./check` runs with that product's cases in force. After the commit the
  branch is brought to the base and nothing is changed on both sides.
- What this does not give: the first product's cases have still not run
  against the merged file. `./bring --try FIRST-BRANCH` on the base after
  the second bring is the step for it, and it is a step someone must take.

## The order the work was done in

1. L1101 and L1102 with their cases, committed failing (`11a2a3e`): the
   first accepted L0043, the second found no `./bring`.
2. `bring`, and the rule and `--next` in `check` (`9c4d6f5`). Both cases
   passed. `bring` was then spoiled nine ways by hand, one at a time (a
   product brought, the base merging by text, one side's change dropped,
   the two numbering rules, the handoff not kept, a case arriving not
   executable, a doubled path, no merge recorded): the case failed on
   eight. The ninth, a path added by both sides, is refused by the
   both-changed rule as well, so the base behaves the same.
3. The record of run 011 was begun when the check asked for it (`6b47baf`).
4. **A defect found by use.** `./bring --try run/010-library-rebuild`
   stopped at `git merge-base`: the pet shop's and the library's branches
   were started "with no history" and share no commit with the base. The
   case got a branch begun that way and failed (`8d3c9af` is the fix,
   the commit before it the failing case): the fork is the branch's first
   commit when it holds a tree the other side had, and `--from COMMIT`
   otherwise.
5. **An approach tried and rejected.** `--try` was first a merge of the
   base into a scratch copy of the product's branch. It worked for the
   library. For the pet shop's branch, five runs behind and with lesson
   lines in an older form, it refused 35 things before any case ran. It now
   runs this tree's check with that branch's `product/`, which is the
   question that was being asked. This is in L1102's file.

## Measured, not fixed

**The start text.** On the base it is 4,600 characters on a run's branch
(4,412 before this run; the sentence that gives the next lesson number is
188). The 25 lessons that are not `always` take 3,909 of them, 156 a line
on average, 267 the longest; the rest is 691. At that average it fits until
about 59 such lessons, 34 more than today. The two products brought 1,215
(pet shop) and 1,752 (school library) characters of their own lines, so the
base has room for three more products like them and not for a fourth. With
a product in the tree it is far from the limit: 2,700 with the pet shop,
3,172 with the library.

What should give way first: on the base, the lines of labels that are a
product's own name. A new product never declares `pet shop`; it needs to
know the label exists, not its nine rules. Such a label can be told from a
general one by a machine, since it has a file in `surface/`. Printed with
its count only, as labels that are off already are when a product is in the
tree, today's text would be about 1,650 characters and would grow only with
general lessons (942 characters for 7 today). Not done: the case of L0041
requires every label's lines with no product, and a case changes on
evidence from outside. `always` lessons are not in this text; they are in
`CLAUDE.md`, 16 lines and 2,704 of its 6,928 bytes.

**Who brings a general change to the other products.** Nobody, and the
operation does not pretend otherwise. What it does: it names, at each
bring, the files and the lessons under labels that already existed, as
reaching other products; and `./bring --try BRANCH` says in about a minute
whether a product on another branch meets the base. Run on 2026-11-20
against this tree:

| Product | Branch | Result |
|---|---|---|
| pet shop, build of run 005 | `run/005-labels` | passes: 32 lessons in force, 29 cases run, 59 s |
| school library, build of run 010 | `run/010-library-rebuild` | passes: 31 lessons in force, 28 cases run, 84 s |

So the eight cases run 006 made general, and everything since, hold on the
pet shop's build as it stands on its branch. Its branch still has its old
scaffold; nothing was pushed to it. The handoff puts `--try` in the steps of
bringing a run back and says a failure goes to the person.

## Lessons

- L1101 [always], with a case, committed before the fix.
- L1102 [always], with a case, committed before the fix; the case was
  extended once, failing, before the second fix.
- No lesson was changed. `CLAUDE.md` gained three sentences, a row in its
  table and the two lines.

## The check at the end

`lessons 41 · in force 16 · not in force 25 · with a case 34 · prose only 7
· cases run 11 · cases not run 26 · product: none · product 0 lines · cases
in force 1016 lines · at the start of a session CLAUDE.md 6928 bytes and
4600 characters from the hook (4600 with no product) · 17 s`

`./check --selftest`: accepted 8 of 8 right trees, refused 35 of 35 wrong
trees (7 and 32 before; nothing it refused is now accepted). The check on
the base takes 17 s where it took 5: the case of L1102 is 10 s of it, in
some twenty scratch repositories.

## Decided by the builder and not asked

1. The number is two digits of run and two of place, in the same four
   digits. A run holds 99 lessons, and run 100 is not solved.
2. L0043 to L0099 are closed for good, and the check refuses them.
3. A run's number is read from the name of its branch, by `./check --next`
   and by the hook's text.
4. A run's record must exist from its first lesson; the check enforces it.
5. `bring` is its own program and not a part of `check`.
6. Lesson lines are written in order of number, each in the file its
   labels say; text that someone puts after the lines moves above them.
7. `HANDOFF.md` keeps every line either side added. Their order follows
   the order of bringing and says nothing.
8. Every other file is taken whole. The base refuses a file both sides
   changed even when git would merge it without conflict.
9. Which behaviour applies is decided by whether the tree has `product/`.
10. On a branch with a product, a lesson line both sides changed is
    written twice, so that the check refuses it until a reader chooses.
11. `./bring` commits nothing; it writes the merge's message and runs
    `./check`.
12. After a bring git records a merge, also between histories that had
    nothing in common, so the next bring finds where they parted by itself.
13. `--from COMMIT` for branches with no history, and the first-commit rule
    that makes it unnecessary when the branch began at the base's tree.
14. Lessons "to be read together" are those from the two sides that share
    a label. Lessons that contradict each other under different labels are
    not named.
15. What "reaches other products" is: any file outside `lessons/`,
    `cases/`, `runs/` and `surface/`, a changed case that existed before,
    and a new lesson under a label that already existed.
16. `--try` runs the base's check with the branch's product and is not a
    merge. `--begin` makes the branches and does not push them.
17. `--verify` exists so that a merge made another way can be refused; no
    step makes anyone run it.
18. The two product branches were fetched into this checkout to measure
    with. Their source was not read and nothing was pushed to them.
19. The start text was measured and not changed, and `prompts/README.md`
    gained two sentences pointing at `./bring`.

## Not verified

- No two real runs have been started with `--begin` and brought back. The
  case plants small trees; by hand, a clone of this tree got two branches,
  one lesson on each, and both were brought, with `./check` passing at 43
  lessons. Neither is two sessions that built two products.
- That a session takes the number its start text gives it. This session
  had no such sentence (the hook ran before the change) and took L1101 and
  L1102 from the rule it was writing.
- That the hook's text carries the run's number in a real cloud session:
  it does when the run's branch is checked out before the session starts,
  as it was here. If the branch is made later, the text says the branch is
  no run's, and `./check --next` is the way.
- A merge by text on a product's branch that every case passes and is
  still wrong.
- `./bring` on Windows, with files that are not text, or with links.
- The person has seen none of this.

## Time and sub-agents

One session, no sub-agents. Not timed.

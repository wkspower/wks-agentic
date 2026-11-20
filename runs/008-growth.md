# Run 008 — growth: the time of the check, the entry file, the size of the cases

- **Prompt:** none under `prompts/`. This run changes the scaffold and tests
  no product prompt.
- **Branch:** `run/008-growth`, 2026-11-20, started from `9c2ad27` with the
  school library in `product/`. The product was not changed.

## How the instruction arrived

As an automated notice written by the coordinating session, which says so
itself. The person's own word, as that notice reports it, was "growth",
choosing which open problem to work on. The measurements, the three tasks
and the proposals in them are the coordinating session's. No lesson of this
run says the person decided, read or accepted anything (L0037).

## Questions

None. The instruction said what to do and left the ways open; what was
chosen is listed under "Decided and not asked".

## The three measurements, before and after

Measured in this session, on one machine, with the library in `product/`.
The coordinating session's figures for "before" are beside them where they
differ.

| | Before | After |
|---|---|---|
| `./check`, whole | 87 s (110 s) | 41 s |
| the case of L0019 | 42 s (56 s) | 0.2 s |
| the slowest case, L0032's | 11 s (16 s) | 10 s, not changed |
| times a case in force is run on this tree | twice, and the selftest several times more | once |
| `./check` on the tree without `product/` | not timed | 3 s, 8 cases |
| `CLAUDE.md` | 11,931 bytes, 34 lesson lines, 10 of them off | 5,605 bytes, 13 lesson lines, none off |
| read at the start of a session on the library | 11,931 bytes | 8,368: `CLAUDE.md` and the 2,763 that `./check --lessons` prints |
| read at the start of a session on the base | 11,931 bytes | 5,981: `CLAUDE.md` and 376 |
| bytes of links on the lesson lines | 4.4 KB | 0 |
| cases, all | 3,007 lines, 30 cases | 3,079 lines, 33 cases |
| cases in force | not printed | 2,217 lines against 800 of product, 2.8 to 1, on the summary line |

The after column has three more lessons than the before column, all
`always`, so `CLAUDE.md` carries about 430 bytes it did not have to carry
before. Of its 5,605 bytes, 3,433 are the text above the lessons.

## 1. The time of the check (L0038)

`./check` now copies the tree, compiles the product in the copy, removes the
product's source there, and runs every case in force once, in the copy. The
way the instruction proposed was taken. That every case passes without the
source is what the ordinary run says; a file that cannot be compiled fails
the check.

What L0019's case proved before, and where it is proved now:

| Before, in the case | Now |
|---|---|
| every other case in force passes without the source | the ordinary run: all 24 cases run where there is none |
| the scratch tree holds no source when the cases run (run 006) | the case of L0019 looks in the tree it is itself run in and fails on any source file there |
| a planted case that reads a product's source fails there | the case of L0019 puts a planted tree with such a case through `./check`, which must fail on that case |
| a planted case that only runs the product passes (the control) | the same, in a second planted tree, which must pass and show what the product printed |

Case first: commit `7f38ad5` has L0038, its case and the new case of L0019,
both failing on the check as it stood ("a case was run with the product's
source in its tree"; "planted case that reads a product's source ACCEPTED").
Commit `1782ca3` is the fix.

**One defect found, in this run's own case.** The planted case that reads
the source was first written so that it could not fail: it printed a count
inside a command that ignored the failed read. The case of L0019 said
"ACCEPTED" on the first run of the new check, which is how it was seen. No
lesson: L0001 already says a case that cannot fail has measured nothing, and
the control arrangement is what showed it.

What still runs a case more than once: the case of L0023 runs `./check` on a
copy without `product/`, which runs the eight `always` cases there. It is
another tree, it takes 3 s, and it is the only proof that the base passes.

## 2. The entry file (L0039)

A lesson line is now `- **L0012** [labels] Sentence.`, with `· prose: why`
when no machine can check it. The file of a lesson is `lessons/NNNN-*.md`,
found by its number. A case says in its first lines which lesson it is a
case of ("Case of lesson L0026"), and the check reads that; every case
already said so, and no case was renamed.

`CLAUDE.md` holds the lines labelled `always`. `LESSONS.md` holds every
other line. `./check --lessons` prints the lines in force for the product in
`product/` that are not already in `CLAUDE.md`, and then each label that is
off with its count. `./check --lessons LABEL` prints the lines a label
brings, on any tree. On the base that is how a session finds which labels
exist and what each brings. The first instruction in `CLAUDE.md` is to run
it.

The selftest: the 19 wrong trees it refused are refused, each written in
the new form, and 7 more: a case that names no lesson, a case that is not
executable, a line with a link, a lesson that is not `always` in
`CLAUDE.md`, an `always` lesson in `LESSONS.md`, a lesson with a case that
is marked prose, two lesson files for one number. Four of these were seen
accepted before their rules were written. "One case named by two lessons"
is now a case whose first lines name two lessons. It accepts 7 right trees
(5 before): a lesson that is prose with its reason, and a lesson with a
second case under another number, were added.

Case first: commit `7704cb4` has
the lesson and its case failing on the file as it stood ("the line of L0001
carries a link or a path, which its number gives"). Commit `49d40e5` is the
change. For L0040, `61ffa05` has the case failing and `e295c69` the change.

## 3. The size of the cases (L0040; measured, nothing cut)

Why the library's cases are nearly twice the pet shop's: **each library
lesson holds about twice as many rules, and a rule costs the same in both.**
A wrong variant takes 14.1 lines in the pet shop's cases and 14.1 in the
library's. The library's cases have 6.3 of them each where the pet shop's
have 2.9.

Lines per case, as a mean over the cases born in each product:

| | Pet shop (8 cases) | School library (7 cases) |
|---|---|---|
| all | 99.4 | 178.7 |
| heading, imports | 15.0 | 15.0 |
| helpers | 6.2 | 11.3 |
| setting up data | 17.1 | 29.4 |
| checks | 20.4 | 34.4 |
| wrong variants | 40.6 | 88.6 |
| wrong variants written in the case | 2.9 | 6.3 |
| lines per wrong variant written | 14.1 | 14.1 |
| places that check (`expect`, `post`) | 14.1 | 21.0 |
| characters per line | 42.9 | 47.9 |
| characters in the lesson's sentence | 101 | 158 |

Of the 79 lines a library case has more than a pet shop case, 48 are wrong
variants, 14 checks, 12 setting up data and 5 helpers. Counted as they run,
the library's 7 cases refuse 49 wrong variants (one case makes 11 from 6
written) and the pet shop's 8 refuse 23: 25.5 lines of case per wrong
variant refused in the library, 34.6 in the pet shop. The library's cases
are bigger and cheaper for what they prove.

So the size follows the lessons. L0031 alone is five rules in one sentence
(corrected, never removed, lost and back, lost while out, left), with 9 wrong
variants and 252 lines. Whether a library lesson should be several lessons
is a question about lessons, not about waste in cases; nothing was split.

How it was counted, by a script that is not kept: a case is cut at the top
level of its file. Everything after the function `checks` is wrong variants,
with the helpers the faults use and the list at the end. Inside `checks`,
each statement is a check when it holds an `expect` or a `post` that expects
a refusal, and setting up data when it does not; a function defined inside
is a helper. Comments and blank lines go with the statement after them. A
loop that both enters data and checks it counts as checks.

Plain waste looked for and not found: of the library's 1,251 lines, 19 are
written in more than one of its cases, and 10 in three or more (the two
borrowers of the sample, a page fetched and expected to answer 200). Nothing
was changed.

By label, all cases: school library 1,251 lines (7 cases), pet shop 795 (8),
web pages 407 (7), always 376 (8; 304 in 5 before), the three other general
labels 250 (3). This run added 72 lines of cases while measuring them: the
case of L0019 went from 109 lines to 28, three new cases came to 149, and
the case of L0023 grew by 4.

The summary line now says `product 800 lines · cases in force 2217 lines
(2.8 to 1)`. No limit is set.

## Lessons: 3 added, all with a case, case first; 3 amended

| | Lesson | Case |
|---|---|---|
| Added | L0038: the check runs every case once, without the product's source, and prints the seconds | `cases/0038-a-case-runs-once` |
| Added | L0039: a line holds only what its number does not give; `CLAUDE.md` holds `always` | `cases/0039-the-entry-file-holds-always` |
| Added | L0040: the summary line says the lines of the product and of the cases in force | `cases/0040-the-check-prints-the-sizes` |
| Amended | L0019: how it is proved (the sentence did not change) | `cases/0019-cases-know-no-source`, rewritten |
| Amended | L0023: where the lines are | `cases/0023-labels-switch-lessons`, reads both files |
| Amended | L0034: one regression reworded | not changed |

The Source of each says the instruction was the coordinating session's.

## Decided and not asked

1. **A case names its lesson; no line names its cases.** The other way,
   cases found by number alone, would have renamed three cases of L0026.
2. **Two files, split by `always`.** One file per label was not taken: a
   lesson may carry two labels and would have no one home, and a session
   would have to turn a label into a file name.
3. **A command prints the lessons in force**, and a session has to run it.
   Before, the file put every lesson in front of every session with no step
   to take. This is the weakest point of the run; see "Not verified".
4. `./check --lessons` does not print the `always` lessons again.
5. `./check --plant DIR` writes the selftest's small right tree, so that a
   case can spoil it. Three cases use it.
6. `caselib.py` and `caselib.js` start the product's bytecode when its
   program is not there, instead of the check telling them through `SHOP`.
7. **The case of L0019 fails when run by hand from the root** of a tree that
   has a product, because that tree has its source. It passes under
   `./check`, and by hand on the base.
8. A file in `product/` that is not Python is left in the copy and named on
   a line of the check; it does not fail. A product in another language
   would keep its source, and L0019's lesson says so.
9. The check prints the seconds of each case and of the run, and beside the
   size of `CLAUDE.md` the bytes of the other lessons in force. Not asked.
10. The count for L0040 leaves out what the cases share (`caselib.py` 295
    lines, `caselib.js` 144, the surface of the product 180).
11. The case of L0032 was left at 10 s. It sends about 1,000 forms ten
    times, once for itself and once for each wrong variant. It is now
    a quarter of the check.
12. A lesson marked prose that has a case is refused; before, the line could
    only say one or the other.
13. `INSIDE_THE_BASE_CHECK` is gone from the case of L0023: nothing runs it
    twice in one tree any more.

## Check at the end

    lessons 37 · in force 27 · not in force 10 · with a case 30 · prose only 7 · cases run 24 · cases not run 9 · product: school library, web pages, local web server, python stdlib and sqlite on localhost · product 800 lines · cases in force 2217 lines (2.8 to 1) · CLAUDE.md 5605 bytes, and 2448 of lessons in force besides · 41 s

Without `product/` (the last commit unpacked in a scratch directory, the
folder removed):

    lessons 37 · in force 13 · not in force 24 · with a case 30 · prose only 7 · cases run 8 · cases not run 25 · product: none · product 0 lines · cases in force 376 lines · CLAUDE.md 5605 bytes, and 0 of lessons in force besides · 3 s

`./check --selftest`: accepted 7 of 7 right trees, refused 26 of 26 wrong.
The cases over the product refuse 67 wrong variants, as in run 007.

The pet shop's cases are not in force and were run by hand, because
`caselib` changed: all 9 under `pet shop` and `money`, and the 8 general
ones, pass on `product/petshop.py` of `run/005-labels` with
`SHOP=... SURFACE="pet shop"`.

## Size

Product 800 lines, not changed. Cases 3,079 lines (3,007). `check` 456 lines
(298). Lesson files 1,078 lines (903). `CLAUDE.md` and `LESSONS.md` together
9,617 bytes.

## Time and agents

About 50 minutes from the first command to the last commit. No sub-agents.

## Not verified

- **No session has started from the new `CLAUDE.md`.** Whether a fresh
  session runs `./check --lessons` before it works, and so reads the
  product's lessons at all, is the thing this run cannot know. The next run
  shows it: if its session breaks a lesson that is in force and not
  `always`, this is the first place to look.
- The person has seen none of this, and has not read L0038 to L0040.
- The product was not touched and was not driven by script in this run
  (L0013): nothing a person would see changed.
- The seconds are from one machine, one run each. The coordinating session
  measured 110 s where this session measured 87 s before any change.
- The split of a case's lines is by the rule above, applied by a script. A
  reader cutting by hand would move some lines between "setting up" and
  "checks".
- The pet shop's cases were run on its build with the source there, by
  hand, not in a copy without it.
- A product not written in Python has not been tried with the new check.

# Handoff

**Run 010 (2026-11-20) rebuilt the school library from its lessons and cases
alone.** `./check` passes: 39 lessons, 29 in force, 26 cases run; see
`runs/010-library-rebuild.md`.

- The session had the text "Lessons at the start of this session" from the
  hook before its first action, with no step of its own (L0041).
- It asked no question: the lessons answered all fourteen of run 006.
- All 16 cases that needed the product passed on their first run against
  the new build. No case, surface or helper was changed for it.
- One defect, found by the agent reading its screenshots with every case
  passing: the buttons held in sight covered the state of a loan at 1100 px,
  and after the first fix at 800 px. L0042, case first both times.

To use the library: `python3 product/library.py --sample`, then open
http://127.0.0.1:8000/. `--today 2026-12-20` shows it on another day.

The person has not seen run 010, L0042, or what the builder decided (listed
in the run record). The prompt came as an automated notice.

**Run 009 (2026-11-20) changed how the lessons reach a session, and nothing
else.** `./check` passes: 38 lessons, 28 in force, 25 cases run; without
`product/`, 14 in force and 9 cases run. See `runs/009-loading.md`.

- **No session is told to run a command to see its lessons** (L0041). A
  SessionStart hook in `.claude/settings.json` runs `./check --start`, and
  Claude Code puts what it prints in front of the session: the lessons in
  force for the product besides the `always` ones in `CLAUDE.md`, or, with no
  product, every label that exists and the lessons it brings. The text
  begins `Lessons at the start of this session`.
- **Nothing is kept that can go stale.** The text is worked out at each start
  from `LESSONS.md` and `product/LABELS`. A file written by the check and
  included by `CLAUDE.md` was the way proposed first; it cannot be right
  both with the product and after `product/` is removed, and L0041 says why.
- `./check --lessons` is still there for whoever wants to look. Nothing
  depends on it.
- Past 10,000 characters a session gets only a preview of a hook's output. The base prints 4,243 today,
  and every lesson that is not `always` adds its line to it. `./check` fails
  when either tree goes past the limit; the summary line says both numbers.

**What the next run should look for, because this run could not prove it
from inside.** A session started by the person in the usual way has, before
its first action, a text that begins `Lessons at the start of this session`
and lists L0006 to L0036 as the summary of this file says (14 lessons with
the library). Ask the session, as its first message or at the end, whether
it had that text and which numbers were in it, and compare with
`./check --start`. If it did not have it, `CLAUDE.md` tells it to say so
first; a session that neither had the text nor said so is the failure to
record. Then, as before: a lesson in force that the session breaks.
What this run did see: headless starts of the installed Claude Code
(2.1.329) in copies of this tree ran the hook, and the model listed the right
lessons, with the library and without it. That is not the person's session.

The person has not seen run 009, L0041, or the change to L0039.

**Run 008 (2026-11-20) changed the scaffold, not the product.** `./check`
passes: 37 lessons, 27 in force, 24 cases run, 67 wrong variants refused,
in 41 s (87 s before); without `product/`, 13 in force and 8 cases run, in
3 s. See `runs/008-growth.md`. Three things are different for every session
from here on:

- **The lessons are in two files.** `CLAUDE.md` holds the ones labelled
  `always`. `LESSONS.md` holds the others and is not read whole:
  `./check --lessons` prints the ones in force for the product in the tree,
  and `./check --lessons LABEL` what a label brings (L0039). A line is the
  number, the labels and the sentence; the lesson's file is
  `lessons/NNNN-*.md`, and a case says in its first lines which lesson it is
  a case of.
- **The cases run once, in a copy of the tree without the product's
  source** (L0038). The case of L0019 no longer runs the others; run by hand
  from the root of a tree with a product, it fails, because the source is
  there.
- **The summary line says the lines of the product and of the cases in
  force** (L0040): 800 and 2,217 with the library. No limit is set.

Not known, and the first thing the next run shows: whether a fresh session
runs `./check --lessons` before it works. Until run 008 every lesson was in
front of every session with no step to take.

The person has not seen run 008. Its instruction was written by the
coordinating session; the person's own word was "growth". The run record
lists 13 things the builder decided that were not asked.

**Run 007 (2026-11-20) made two changes to the library and did not record
the review they came with.** `./check` passes: 33 lessons, 23 in force, 21
cases run, 67 wrong variants refused; without `product/`, 9 in force and 5
cases run. The changes: a copy that is out can be marked lost, which ends
its loan that day as lost (L0031, reversed); classes are compared without
regard to capitals (L0036, new). See `runs/007-library-review.md`.



**This is the base (2026-11-20, after run 010; written by the coordinating
session).** It holds every lesson and case and no product. A SessionStart
hook gives each session the lessons in force (L0041); run 010 received them
with no step of its own and rebuilt the school library from its lessons and
cases with no question asked. The library is on `run/010-library-rebuild`,
the pet shop on `run/005-labels` (its cases as they were before run 006).
L0037 to L0042 come from the coordinating session or from defects found in
runs; the person has read none of them.

## The review of L0027 to L0036, as it really happened

The person accepted these lessons on 2026-11-20 with one "ok", in the
coordinating session, to a table of one-line summaries and two suggested
changes. They have not read the lesson files. Each Source now says exactly
that. The same correction was made to L0005 to L0025, which run 005 had
marked "Read as written and accepted" on an instruction that overstated
what the person had done (L0037).

Still owed: the school's confirmation of the numbers in L0028 and L0029;
the person's look at what run 007's builder chose (its run record lists
them); and the person reading any lesson file at all.

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

1. Read `CLAUDE.md` and the lessons the hook put in front of you, then
   this file.
2. Run `./check`. If it fails, that is the first thing to fix.
3. To test a prompt, follow `prompts/README.md`.
4. To use the product on this branch, see the top of this file. The pet
   shop is on `run/005-labels`: `python3 product/petshop.py --sample`. The
   cases need Python 3 and Node with Playwright.

## How a new product starts from the base

The base is this branch without `product/`. Nothing else is removed: the
pet shop's lessons and cases stay in it, not in force.

1. Make a branch from the base and run `./check`. It passes with only
   `always` in force. Every label that exists and the lessons it brings
   were put in front of the session at its start (L0041).
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
   is done. An `always` line goes in `CLAUDE.md`, every other in `LESSONS.md`.

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
- What the base does when its labels and their lessons pass 10,000
  characters, the most a hook may put in front of a session. Today 4,243.
  The check fails there; what to print instead is not decided.
- Whether a sub-agent gets the lessons in force. The hook is not known to
  fire for one, and nothing here gives them to it.
- A size limit for `CLAUDE.md`. The check prints its size and enforces none.
  Run 008 took it from 11,931 bytes to 5,605 by moving out the lessons that
  are not `always` and the links; it now grows only with `always` lessons.
- Whether a library lesson that holds five rules should be five lessons.
  Run 008 found that the library's cases are twice the pet shop's because
  its lessons hold twice the rules, at the same 14 lines a wrong variant.
- Whether the case of L0032 should send its 1,000 forms once and not ten
  times. It is 10 s of the check's 41.

## Runs

Each run adds a file under `runs/` and a line here.

- [001 pet shop](runs/001-pet-shop.md), 2026-11-19: 1 round of 14 questions, 11 lessons added (9 with a case), 2 defects found by hand.
- [002 pet shop, rebuilt](runs/002-pet-shop-rebuild.md), 2026-11-19: 1 round of 4 questions, 3 lessons added (all with a case), 1 defect found by hand, no old wrong variant rewritten.
- [003 wrong variants by behaviour](runs/003-variants-by-behaviour.md), 2026-11-19: no questions, 1 lesson added (with a case), 2 changed; cases only, 29 faults at the interface in place of 28 text replacements.
- [004 pet shop, rebuilt with no history](runs/004-rebuild-no-history.md), 2026-11-19: 1 round of 3 questions, 3 lessons added (all with a case), 1 defect found by hand, no inherited case changed.
- [005 labels](runs/005-labels.md), 2026-11-19: no questions, scaffold changed so lessons are switched on per product; 4 lessons added (3 with a case), 3 folded into one, the person's review of L0005 to L0022 recorded; lists became cards on a narrow screen, case first.
- [007 library review](runs/007-library-review.md), 2026-11-20: no questions, no prompt; 1 lesson reversed and 1 added (both with a case, case first), 1 defect found writing a case, 1 addition refused by an inherited case; the review the run was to record is not recorded, and why.
- [008 growth](runs/008-growth.md), 2026-11-20: no questions, no prompt, scaffold only; 3 lessons added (all with a case, case first), 3 amended; the check from 87 s to 41 s, `CLAUDE.md` from 11.9 KB to 5.6 KB, the sizes printed on every run; 1 defect found in the run's own case by its control.
- [009 loading](runs/009-loading.md), 2026-11-20: no questions, no prompt, scaffold only; 1 lesson added (with a case, case first), 2 amended; the lessons in force reach a session through a SessionStart hook and no command it is told to run; an included file tried on paper and rejected; three real headless starts seen.
- [006 school library](runs/006-school-library.md), 2026-11-20: 1 round of 14 questions, 9 lessons added (8 with a case), the second product; 8 cases made general and kept passing on the pet shop; 1 defect found in the scaffold and 1 in the product by hand.
- [010 library rebuild](runs/010-library-rebuild.md), 2026-11-20: no questions; the library rebuilt with no history, every inherited case passing on its first run, none changed; 1 lesson added (with a case, case first), from a defect found by reading screenshots.

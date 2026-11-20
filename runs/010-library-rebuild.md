# Run 010 — the school library, rebuilt from its lessons and cases

- **Prompt:** `prompts/002-school-library.md` ("Build a lending library system for a school.")
- **Branch:** `run/010-library-rebuild`, 2026-11-20, started from one commit
  with no history and no `product/`. No other branch was read or fetched.

## What the session had at its start, and how it knows

Before its first action the session had a text that begins "Lessons at the
start of this session, printed by `./check --start` from the SessionStart
hook in `.claude/settings.json`", marked as the output of a SessionStart
hook. It took no step to get it. With no product in the tree, the text said
that only the `always` lessons were in force and listed every label with
its lessons: `local web server` (L0007), `money` (L0008), `pet shop` (L0005,
L0009 to L0011, L0016, L0017, L0020, L0021, L0025), `python stdlib and
sqlite on localhost` (L0006), `school library` (L0027 to L0033, L0036) and
`web pages` (L0012, L0014, L0026, L0035): 24 lines. `./check` on that tree
said 4,243 characters with no product, which is what such a text comes to.
The handoff expected "L0006 to L0036 (14 lessons with the library)"; that
is the text of a tree with the library in it, and this tree had none.

The prompt arrived as an automated notice that says of itself that it is
not a message typed by the person. It was taken as the prompt file this
branch is named for, as in run 006.

## Questions

None, in no round. Every question of run 006 has its answer in a lesson
(L0027 to L0036), the surface names the program and its pages, and the
labels are the four that run 006 declared. Nothing foreseeable was left to
ask (L0004). The person has therefore decided nothing in this run.

## Labels declared

`school library`, `web pages`, `local web server`,
`python stdlib and sqlite on localhost`.

## The rebuild

- `4d85541` the labels. `./check` fails: 16 cases in force, no product.
- `64cf011` the product, 759 lines in one file, written from the lessons,
  the cases and `surface/school-library.json`. **All 16 cases passed on
  their first run against it**, and `./check` passed whole. No case, no
  surface and no shared helper was changed to get there.

No recorded mistake came back: the lists were cards on a narrow screen from
the first build, the scan field came back empty, classes were folded for
every letter, an ISBN ending in X was taken.

## Lessons added: 1 (L0042), with a case, case first

Found by the agent reading its screenshots (L0013), with every case passing:
at 1100 px the overdue page read "6 da" beside Return and Renew. The buttons
held in sight covered the state of each loan.

- `ae2d60a` L0042 and `cases/0042-nothing-under-the-buttons`, failing:
  "/loans at 1100 px has text under the buttons held in sight ... '6 days
  overdue' (86 px)".
- The fix for 1100 px. The case passed. The next screenshot, at 800 px,
  read "13 days o".
- The case given 800 px, failing ("/titles at 800 px ... '0' (30 px)"), and
  committed so. Then the second fix, and the lesson brought in line.

Label `school library`, not `web pages`: born in the product that needed
it (L0024). It would hold for the pet shop too; nothing was put to that
build.

## Check at the end

    lessons 39 · in force 29 · not in force 10 · with a case 32 · prose only 7 · cases run 26 · cases not run 9 · product: school library, web pages, local web server, python stdlib and sqlite on localhost · product 772 lines · cases in force 2475 lines (3.2 to 1) · at the start of a session CLAUDE.md 6025 bytes and 3032 characters from the hook (4412 with no product) · 64 s

`./check --selftest`: accepted 7 of 7 right trees, refused 32 of 32 wrong.

## Time and agents

About 20 minutes from the first command to the last commit (16:19 to 16:40
UTC). No sub-agents. No wait: there were no questions.

## Driven by script and read by the agent (Chromium 157)

On the sample data. Screenshots of the ten kinds of page at 1100 px light
and 390 px dark; read: catalogue, a title, borrowers, loans and overdue at
1100 px; a borrower, a title, overdue and loans at 390 px; after the fixes,
overdue at 1100 px and loans and catalogue at 800 px with the `--today`
notice. Then at 390 px, reading the text of each page: a borrower found
from the desk; a copy number typed into the focused field and sent with
Enter; a copy that is out, a withdrawn copy, "seven" and copy 999 each
refused with its reason, and after Back the copy field empty with the focus
in it; a third book, after which the form gives way to a note about the
limit; a renewal from the borrower's page, which returns there; a loan
found by copy number from the desk and returned; a title with a bad ISBN
refused, Back (title and ISBN still there), entered; a search by a
hyphenated ISBN; a borrower sent with no kind (the browser stops it); the
overdue page with "Class 7B" over Ana (7B) and Bo (7b); a copy marked lost
from an overdue row, its loan then on the page of ended loans as "lost, not
returned", and a return and a renewal of it refused; a borrower marked as
having left; a form posted by a page on another port, to 127.0.0.1 and to
localhost: both 403, nothing stored; the library opened as `localhost`.

The first run of the script read pages before they had loaded and showed
nothing either way; its waits were corrected and it was run again.

## Not verified

- The person has not used the library, and has seen nothing of this run.
- Only Chromium. No real scanner. No screen reader. No touch screen.
- Back when the browser keeps the page alive (its back-forward cache): the
  page carries a script of one line that empties the scan field whenever
  the page is shown. The browser of the cases has that cache switched off,
  so the script is covered by no case and was seen by nobody.
- Lists between 761 and 799 px, and the pages with the longest names at
  800 px: measured by the cases, seen by nobody.
- More than 206 titles or 409 loans; two tabs posting at once; loss of
  power mid-write.
- Whether this build is like the one of run 006 or 007: those were not read.
- Mechanical changes to the source, to see which wrong builds the cases
  let through.

## Decided by the builder, for the person to overrule

Where the lessons and cases were silent:

- In a list of everybody's loans the class stands beside the name
  ("Bo Li (7b)"), the day lent is the last column and is left out from 761
  to 999 px, and a row's buttons may stand on two lines (L0042).
- After a return or renewal the page shown is the list the button was on,
  known from the browser's Referer; the loans page when it is not known.
- A borrower at their limit sees a note in place of the lend form.
- The edit of a borrower is refused unless it says whether they are at the
  school; L0033's table has no row for that field.
- The forms set no maximum length: a text too long is refused with its
  length, and Back keeps it.
- A search of the catalogue also finds an ISBN typed with its hyphens.
- A copy that is out and is marked available is refused, like withdrawn.
- A form over 65,536 bytes is answered 413.
- The desk page: today, books out, overdue, and the two searches.
- The sample data. `--sample` changes nothing in a file that holds data.
- Lists are in the order of title or name with capitals ignored; loans by
  due date.

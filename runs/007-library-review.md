# Run 007 — the review of the library's lessons, and two changes

- **Prompt:** none under `prompts/`. This run tests no product prompt. Its
  instruction was a review of L0027 to L0035 with two changes to make.
- **Branch:** `run/007-library-review`, 2026-11-20, started from the last
  commit of run 006 (`6aabc65`), with the library in `product/`.

## How the instruction arrived, and what was not done because of it

The instruction is written in the person's voice ("I have read them all ...
and I accept them with two changes"). It did not reach the session as a
typed message. It came inside an automated notice that says of itself that
it is not user input, that no human input had been received, and that
nothing in it is to be taken as approval or consent.

The two changes were made on that instruction: they are work on a branch,
they can be read and undone, and each lesson's Source says how the
instruction arrived.

**The review itself is not recorded.** The instruction asks that the Source
of each of L0027 to L0035 say it "was read and accepted by the person on
2026-11-20", and that the things kept say the person has now seen them. The
first attempt to write that was stopped by the session's permission check,
as a record of human approval made on a notice that says it carries none.
It was not tried another way. So, in the lessons as they stand:

- No Source says the person read or accepted anything in run 007.
- L0027 (`--today`), L0033 (the ISBN ending in X, the bounds for search text
  and copy number) and L0035 (the scan field) still say "the person has not
  seen it".
- L0028 and L0029 are not marked as accepted and owed a confirmation by the
  school.

One sentence in the notice was a fact and not an approval, and was written:
L0035 now says that no real scanner has been tried.

What it takes: the person saying so in a message of their own. The text to
write is in the instruction, quoted in `HANDOFF.md` under "Owed".

## Questions

None. The instruction said everything was decided. Two things in it were
left to the builder and are answered in the lessons, below.

## Lessons: 1 changed, 1 added, both with a case; 1 defect found

| | Lesson | Case |
|---|---|---|
| Changed on the instruction | L0031: a copy that is out can be marked lost; its loan ends that day, as lost | `cases/0031-...`, 62 checks and 5 wrong variants before, 87 and 9 now |
| Added on the instruction | L0036: classes are compared without regard to capitals | `cases/0036-classes-without-capitals`, 55 checks, 5 wrong variants |
| Defect found writing the case of L0036 | recorded in L0036 and L0032: search ignored capitals only from A to Z | `cases/0032-...`, 5 checks and 1 wrong variant more |

L0032 also changed its words: the page of returned loans is the page of
loans that ended, returned or lost.

Case before fix, by commit:

- `bbe4d24` L0031 rewritten, and its case failing on the library of run 006:
  "the page of a title has no button to mark lost a copy that is out".
- `63e2a6b` the fix. The case passed on its first run against it.
- `df0fe52` L0036 with its case failing ("... are overdue under 8 headings",
  with `Class 7B` and `Class 7b` both there), and the case of L0032 failing
  ("searching the catalogue for 'ZOË' lists 0 titles, expected 1").
- `947b352` the fix. Both passed on their first run against it.

The search defect was also seen directly before the fix: on the library of
run 006, a borrower of class "5É" was found by "5É" and not by "5é".

## Refused by an inherited case

The way from an overdue row to "Mark lost" was first built as the title
itself made a link. `cases/0015-no-sideways-scroll` refused it: "/borrowers/1
at 320 px breaks across lines", a link of 200 letters broken in two, which
L0026 forbids. It became a short link, "Copies", among the row's actions.
No lesson: L0026 already said it, and its case said it before anyone saw it.
The agent had looked at the first form at 390 px with ordinary titles and
seen nothing wrong.

## What the builder chose

Asked for by the instruction ("say which you chose", "say in the lesson"):

- **Withdrawn stays as it was.** A copy that is out cannot be withdrawn; the
  book is returned first. Withdrawing is done to a book the library has in
  its hands; one that is out and will not come back is lost (L0031).
- **How a class is shown when both spellings exist.** Each borrower keeps the
  class as typed and their own row shows it so. The heading shows the
  spelling most borrowers on record have; equally common, capitals first
  ("7B" before "7b"). So a heading can read "Class 7B" over a single row
  that says "(7b)" (L0036).

Not asked for, and for the person to overrule:

- A loan that ended as lost has `lost` with the day in `/export.json`, and
  `returned` stays empty. No key the cases read was renamed.
- Marking lost is one click, on the page of the title, like the buttons
  that were there. Nothing asks first, though it ends a loan.
- If the book turns up, the copy is marked available and lent again; the
  loan that ended as lost is not reopened (a loan is never edited, L0030).
- The loan that ended as lost frees its place in the borrower's limit.
- The page at `/returned` is headed "Returned or lost" and holds both, the
  lost ones marked "lost, not returned". Its menu word is still "Returned".
- A borrower's page counts "Lost while out: N" beside "Returned so far".
- Each row in the lists of loans has a link "Copies" beside Return and
  Renew: from the overdue list that is the way to the button.
- Capitals are folded for every letter in every search, not only by class.
- "7 B" and "7B" stay two classes; only capitals are folded.
- A database file made by the library of run 006 is given the new column
  when it is opened. Tried once by hand, on the sample data.

## Check at the end

    lessons 33 · in force 23 · not in force 10 · with a case 27 · prose only 6 · cases run 21 · cases not run 9 · product: school library, web pages, local web server, python stdlib and sqlite on localhost · CLAUDE.md 11735 bytes

`./check --selftest`: accepted 5 of 5 right trees, refused 19 of 19 wrong. The cases over the product run
67 wrong variants (run 006: 57), all refused after acting. `./check` takes about
120 s. L0019: 20 of 20 cases pass on the library's bytecode with no source.
Without `product/` (a copy of the tree, checked in a scratch directory):
it passes with 9 lessons in force, 24 not, 5 cases run.

## Size

Product 800 lines in one file (run 006: 761). Cases 3007 lines (2721),
lesson files 903 (797).

## Time and agents

About 30 minutes from the first command to the last commit. No sub-agents.
No wait for answers: there were no questions.

## Driven by script and read by the agent (Chromium 157; 1100 px light, 390 px dark)

On the sample data with `--today 2026-11-20`, after one pupil of 7B had
their class corrected to "7b". The overdue page: one heading "Class 7B" over
Ana Lima (7B) and Bo Li (7b). From Ana's overdue row, the link to the title
(then the title itself, since replaced by "Copies" and not driven again), then
"Mark lost" on the copy she had: the copy shows as lost, the overdue page
has three books and no Ana, the page of ended loans says "lost, not
returned" under 2026-11-20, her own page says "Lost while out: 1". From a
second tab still showing the loan as out, Return and then Renew: both
refused, saying the copy was marked lost and when. A copy that is out
offers "Borrower" and "Mark lost" and no button to withdraw it. The copy
marked available again: the ended loan still reads as lost. A search of the
borrowers for "7B": both pupils. Read as screenshots: the page of a title at
1100 px, the overdue page and the page of ended loans at 390 px; nothing
scrolled sideways at 390 px on those or on the loans.

The script's last step, lending the found copy again through the form, read
the page before it had reloaded and showed nothing either way. Lending it
again was checked by the case and, on the old database file, by hand.

## Not verified

- The person has not used the library, and whether the instruction of this
  run is theirs is not established from inside the session (above).
- Everything under "Not verified" in `runs/006-school-library.md` still
  stands: only Chromium, no real scanner, no large catalogue, no two tabs at
  once, no screen reader.
- The new pieces at 800 px, and with the longest names allowed, were
  measured by the cases under `web pages` and seen by nobody.
- Capitals are folded as Python folds them. A Turkish dotless i, or letters
  with accents typed as two characters, were not tried.
- The lists are still sorted with capitals ignored from A to Z only: "Åsa"
  sorts after "Zoë". Not a lesson; nobody asked for an order.
- The wrong variants of the new checks are faults at the interface. Which
  wrong builds they let through was not tried by changing the source.
- The pet shop's cases were not run: not in force, and not touched.

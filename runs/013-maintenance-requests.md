# Run 013 — maintenance requests, the third product

- **Prompt:** `prompts/004-maintenance-requests.md` ("Build a maintenance request tracker for an apartment building.")
- **Branch:** `run/013-maintenance-requests`, 2026-11-20, started from the base (no product). The prompt
  arrived as an automated notice, not a typed message; it was taken as the prompt file this branch
  is named for, and nothing was built on it until the person had answered.

## What the session had at its start

Before its first action, a text beginning "Lessons at the start of this session", from the
SessionStart hook, with no step of its own (L0041). It named run 013 and L1301 as the next lesson,
and, there being no product, every label and the lessons it brings: L0005 to L0042.

## Questions

One round, 16 questions, each with a recommendation, before anything was built. The person
answered with one typed word, "Accepted". No question after that. How long the round waited is not
visible from inside the session.

Who uses it; what it is built on (the three existing labels, with the lessons each brings); money;
where a request is; who reported it; what a request says; the states; who does the work; dates and
overdue; one click or a question page; correcting and removing; a second request for one place;
what the pages show; the bounds; language, dates and data; photos, notices and recurring work.

None repeated what a lesson already answered (narrow screens, examples, cross-site requests, Back
after a refusal, how done is judged). Four were the earlier products' questions asked again for
this business, each with the earlier answer as its recommendation: one click, corrected and never
removed, what the pages show, the bounds.

## Labels declared

`maintenance requests`, `web pages`, `local web server`, `python stdlib and sqlite on localhost`.
Not `money`: there are no costs.

## Lessons: 9 added (L1301 to L1309, 8 with a case), 1 changed (L0042)

| | With a case | Prose only |
|---|---|---|
| From the person's answers | L1302 a request is of one place, L1303 states and history, L1304 a change is one click, L1305 the server sets every date, L1306 one worker at a time, L1307 corrected never removed, L1308 open in full and closed latest, L1309 the bounds | L1301 scope |
| From a defect found by reading a screenshot | L0042, made general: `school library` became `web pages` | |

Case before fix, by commit:

- `b8f8eba` L1301 to L1309, eight cases, `product/LABELS`, a surface with a label and a program.
  All 17 cases that need the product fail: there is none.
- `373d4f3` the product and its full surface. Six of the eight new cases passed on their first run;
  two had a mistake in the case (a request that does not exist answers 404, not 400; 112 done
  requests are fewer than the 200 a search shows). Eight of the nine general cases passed on the
  first build; one refused it twice (below).
- `539fd7c` L0042 changed and its case made general, failing on the tracker. The commit after it:
  the fix.

## The third product and the general cases (L0024)

- **Refused the first build, for the reason it exists:** `cases/0015-no-sideways-scroll`. A
  worker's 60-letter name in a history cell that could not wrap made a request's page 519 px wide
  at 320 px; then a heading with a 60-letter place name made a place's page 1160 px wide. No
  recorded defect: both are L0026's own ground and it caught them.
- **Changed, because this product has what the others do not:** `0014` reads a `textarea` as a
  field (it sent the request form without its description); `0015` measures a `textarea` like
  the other controls; `0035` chooses in a `select` where it typed (nothing can be sent from the
  request form without its three). `caselib.js`: a surface may say `{today+20}`, and the
  arguments of a restart are read like any other value.
- **`cases/0042-nothing-under-the-buttons` made general.** What fills the lists with ordinary names
  is each product's, in its surface (`fits`). The library's is what the case held before.
- **Put to the other products' builds** (fetched from `run/010-library-rebuild` and
  `run/005-labels` and run; their source was not read): on the library 0012, 0014, 0015, 0022,
  0035 and 0042 pass with 24, 115, 192, 40, 13 and 30 checks; on the pet shop 0014, 0015, 0018 and
  0035 pass with 96, 144, 31 and 7, and 0042 passes with 21 once `surface/pet-shop.json` was given
  a `fits` made of the names its `words` already had. The other cases were not put to them.

## The defect a lesson already described

Read in the screenshot of the open list at 800 px, on the sample data, with all 28 cases passing:
the column of buttons held in sight covered the end of the day due ("+10 c" for "+10 d") and all
of the state and the worker. That is L0042, word for word, in another product. L0042 was labelled
`school library`, so it was not in force. Its line was in the text at the start of this session;
the builder thought of it while laying out the columns and allowed for 1100 px only.

This counts against "a second run repeats none of the recorded mistakes" in the form it was
tested here: a lesson kept under one product's label did not stop the same mistake in the next
product. It is the second time a layout lesson born in one product was needed by another (L0026
was the first, and was `web pages` from run 005 on). The label is now `web pages`.

The fix: state, worker and day are one column of two lines; under 1000 px a row's buttons stand
on two lines; a word with no space widens its column, so that only such a word makes a list scroll
in its box.

## Check at the end

    lessons 50 · in force 32 · not in force 18 · with a case 42 · prose only 8 · cases run 29 · cases not run 16 · product: maintenance requests, web pages, local web server, python stdlib and sqlite on localhost · product 758 lines · cases in force 2899 lines (3.8 to 1) · at the start of a session CLAUDE.md 6928 bytes and 3657 characters from the hook (6620 with no product) · 77 s

The 18 cases over the product run 75 wrong variants, all refused after acting. `./check
--selftest` was not run: the check was not changed.

## Size

Product 758 lines in one file. The eight new cases 1,180 lines, the surface 290.

## Time and agents

About 65 minutes from the answer to the last commit; the first commit was at 21:47. No sub-agents.

## Driven by script and read by the agent (Chromium 157)

On the sample building. Screenshots of twelve kinds of page at 1100 px, four at 800 px, all at
390 px, three at 390 px dark. Read: the desk, the open list and a request at 1100 px; the open
list and the workers at 800 px (before and after the fix); a place's page and the places at
390 px; a request at 390 px dark; the overdue list at 800 px nine days later, with the `--today`
notice.

Then at 390 px, as a person would: "4b" searched from the desk, the place opened; the empty form
sent (the browser stops it at the category); a request sent with the phone "ask at door", refused
with its reason; Back (description, phone and category still there); the phone corrected and
sent; given to a worker; a note typed and Start pressed; Done on the list (returns to the list,
its buttons gone); Reopen on the closed list; a second Reopen by script (400); the address of
Done opened in the address bar (405, "Opening it changes nothing"); the place corrected to 4C and
the priority to normal (the day due moved from the 21st to the 27th); a worker named
`Rui <b>Costa</b>` (shown as typed); a worker made inactive (still chosen where they hold a
request, not offered elsewhere); an apartment "4b" refused because 4B exists; the Lift made
inactive (its request still shown, no form); a search for "socket" among open requests; an
address that does not exist. A form on another port posting a worker, as 127.0.0.1 and as
localhost: 403 both, nothing stored. The tracker opened as `http://localhost`: works.

Changed after looking, without a lesson because it is taste: "2 days overdue" does not break in
two; "Every request of this place (2)" for "All 2 of its requests".

## Not verified

- The person has not used the tracker. Everything above is the builder looking at its own work
  (L0003, L0013).
- Only Chromium. The cross-site refusal and what Back restores depend on the browser.
- The list at 800 px fits by a few pixels with this machine's fonts; another font was not tried.
- At 390 px the list of 30 places is 30 cards and about 9,000 px long, with the form to add a
  place under it. Seen, and left: the search is at the top.
- More than 230 requests. A building's years of history were not tried for speed.
- Two people or two tabs posting at once; loss of power mid-write.
- Anyone logged in to the same machine can open the tracker.
- A screen reader.
- The pet shop and the library as wholes against this branch: only the cases named above were
  put to their builds. `./bring --try` is the base's to run.
- Whether 1, 7 and 30 days are the building's real targets. They were accepted with the rest.

## Decided by the builder, for the person to overrule

- The form for a new request is only on the place's page (L1302).
- `--today YYYY-MM-DD`, with a red notice on every page while it is set (L1301).
- A corrected priority moves the day due; reopening does not (L1305).
- A reopened request is open, not in progress, and keeps its worker (L1303).
- A closed request takes no assignment; an inactive worker keeps what they hold; a worker has a
  page of what they hold (L1306).
- No two places share a name, whatever the capitals (L1307).
- A phone holds digits, spaces and + - ( ) . only; a trade of 0 to 40 characters; the floor of a
  common area may be empty; search text 100 characters (L1309).
- The search looks in the description and the reporter's name, not in the phone or the notes.
- Lists show the first 90 characters of a description; the whole is on the request's page.
- After a button on a list, the list is shown again.
- The desk shows three counts, the search for a place, the urgent requests and the search.
- L0042 relabelled `web pages`, which puts it in force for the pet shop.
- The sample building, and that `--sample` does nothing to a file with data.

## Left out, and not asked

- Printing a worker's list. A way to tell a contractor other than reading it to them.
- A request cannot be split or merged with another.
- No statistics: how long requests take, which place reports most.

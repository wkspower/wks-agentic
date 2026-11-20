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

# The same run, later the same day: taking in the base that held run 012

The instruction came as an automated notice written by the coordinating session. The person said
nothing about this step; their last words on the matter, as that notice quotes them, were "Yes" to
building two products at the same time and bringing both back. Nothing here was seen by the person.

Run 012 (a school canteen) was built at the same time from the same base. Neither run knew of the
other. Run 012 was brought to the base first. `./bring origin/run/013-maintenance-requests` there
was then refused, as L1102 says: L0042's case and file and the surfaces of the pet shop and the
library had been changed on both sides. Both runs had read the same defect in a screenshot of their
own product at 800 px and made L0042 general, each in its own way. This step is the way out the
handoff gives: the base taken in here, where a product can prove the result.

The session had the text "Lessons at the start of this session" before its first action, but from
a checkout four commits behind the pushed branch: it said "No product in this tree" and L1301 as
the next lesson. After `git pull --ff-only`, `./check --start` said the tracker's labels and L1310.

## What `./bring origin/lessons-and-cases` did

27 files changed, L1201 to L1209 brought, in half a second. Taken whole from the base, and left as
the base has them: the canteen's eight cases, nine lesson files, surface and record,
`cases/0008-money-and-bounds`, `lessons/0008-money-and-bounds.md`. Named as reaching other
products: L1209 [local web server] and the case of L0008. The tracker met L1209's case for the
first time here and passed it (5 checks, 1 wrong variant refused); it does not declare `money`.

Left marked, four files, and how each was settled:

| Marked | The two sides | Settled as |
|---|---|---|
| `cases/0042-nothing-under-the-buttons` | Run 012 read `surface.under` (`posts`, `pages`, `cells`, `held`, `needs`) and put `{later}` into a restart itself. Run 013 read `surface.fits` (the same, with `shows` for `needs`), said in words when a surface has no such part, and left the day to `caselib.js` (`{today+20}`). What is measured was the same code on both sides. | One design: run 012's names. From run 013: the words for a surface without the part, `{today+20}`, and the wrong variant that names `td:last-child` and no class (git had merged that line without a mark). |
| `lessons/0042-nothing-under-the-buttons.md` | Each run's paragraph in the Source, each run's regression. | Both histories, as one account of two runs meeting the defect apart; what was kept of each case and why; one regression that names the three products. |
| `surface/pet-shop.json` | The same twelve forms on both sides. Run 012: four pages, 60 cells, 15 held, and a voided sale and a sale to a customer must be on the list. Run 013: five pages (the desk too), 40 cells, 8 held, nothing required. | Run 012's numbers and its requirement, the stronger; the desk kept among the pages; `money` as run 012 added it; one form to a line. |
| `surface/school-library.json` | The same fifteen forms, pages and numbers; `{later}` or `{today+20}`; the marker ended inside a list. | `under` with `needs`, `{today+20}`, one form to a line. |

Why run 012's names: a surface's part is called by its case's own word (`actions`, `cards`,
`back`; the case is "nothing under the buttons"); `shows` already means something else in a
surface (`one.shows`); and the base and the canteen's branch already held them, so the only
surface that had to follow was this run's own. Keeping `fits` would have meant changing the
canteen's surface, which is another run's.

Not marked and changed all the same: `surface/maintenance-requests.json` (`fits` to `under`,
`shows` to `needs`), and this run's own part of `HANDOFF.md`, where `./bring` had also set run
012's paragraph against this run's with no line between.

`./check` then passed with the tracker, and the merge was committed (`27b78d2`).

## L1310, learned doing it (case first)

`./bring --verify HEAD^1 HEAD^2` said of the settled tree: "this tree is NOT what the rules give",
naming the tracker's surface and 12 lines of the handoff. Both were this side's own, and no tree
that makes the two designs one can leave them alone. The same words are said of a tree that undid
what the other run learned, and a file left with its markers was not looked at. So nothing could
say that what `./bring` took had not been undone, which the instruction asked.

- `f6fd6a1` L1310 [always] and `cases/1310-a-settled-bring-is-verified`, failing: "refuses a
  settling that changed the marked helper, this side's own surface and this side's own lines of
  the handoff".
- `8158059` `--verify` changed. The case passes: the right settling accepted and its two changes
  named, 4 wrong settlings refused by name, 1 change refused where nothing was left to settle.
  One wrong variant was accepted on the first run of the fix for a mistake in the case itself
  (its planted marker was never written), and once for a mistake in the fix (a pattern).

Put to the real merge, in a scratch checkout of `27b78d2` with the new `bring`:

    this tree is what the rules give for HEAD^1 and HEAD^2, parted at 1e27509: 140 files compared, 4 left to the cases or a reader
    left to the cases or a reader, and holding no marker: cases/0042-nothing-under-the-buttons, lessons/0042-nothing-under-the-buttons.md, surface/pet-shop.json, surface/school-library.json
    changed in the settling besides, each this side's own (the other side had not changed it since they parted): HANDOFF.md (12 of this side's lines), bring, surface/maintenance-requests.json
    Everything taken from the other side is as that side has it (L1310).

(`bring` is in that list because the new one was copied there to run it.)

Also seen and put right, with no lesson of its own because L0001 already says it: `--try` printed
the commit the checkout was at when the check ended, not the one it had tried. A commit made here
while a try ran gave "as of f6fd6a1" for a tree of 59 lessons, which is `27b78d2`. It now names
the commit before the check starts. No case measures this.

Added to the handoff, under "How a run comes back to the base": after a settling, `--verify`, then
`--try` for every other product (it tries the last commit, so after the commit), then push.

## The other three products against this tree (`./bring --try`)

TRY_RESULTS

## Check at the end

CHECK_LINE

`./check --selftest` was not run: the check was not changed.

## Time and agents

TIME_LINE No sub-agents.

## Not verified, and decided by the session

- The person has seen none of it: not the choice of `under`, not L1310, not the change to `bring`.
- That the two runs agreed on a remedy for L0042 is two sessions of one model agreeing (L0003).
  What is evidence is that each met the defect.
- The wrong variant of L0042's case with `td:last-child` was run against four products and is
  refused by each; that it stays the first build's fault on a product whose buttons are not the
  last cell is not known.
- `--verify` after a settling does not look at lesson lines differently: one changed in the
  settling would be refused. None was, here.
- A settling that is wrong and touches only what it may is not caught by `--verify`. The cases and
  `--try` are what there is for that.
- At the start of a session with no product the hook now prints 8,861 characters of the 10,000 a
  session is given; the handoff's "Not yet decided" foresaw room for three more products and not a
  fourth. With the canteen and the tracker both in, a fifth product's lessons will not fit.
- Both runs' records call their product "the third". The canteen's was brought first.


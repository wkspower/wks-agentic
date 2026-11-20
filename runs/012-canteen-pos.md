# Run 012 — school canteen, the third product

- **Prompt:** `prompts/003-canteen-pos.md` ("Build a point-of-sale system for a school canteen.")
- **Branch:** `run/012-canteen-pos`, 2026-11-20, started from the base (the
  lessons and cases after run 011, no product). The prompt arrived as an
  automated notice, not a typed message; it was taken as the prompt file this
  branch is named for.
- **The lessons at the start:** the session had the text "Lessons at the
  start of this session" from the hook before its first action, with no step
  of its own (L0041). With no product it listed every label and its lessons,
  25 lines, L0005 to L0036 and L0042, and said the next number, L1201. The
  session said so in its first message.

## Questions

One round, 15 questions, each with a recommendation, asked before anything
was built (L0004). Answered with one typed word, "Accepted". No question
after that. How long the round waited is not visible from inside the session.

Who uses it; what it is built on (four existing labels offered, with the
lessons each brings); how a sale is paid; a balance too low; the menu;
stock; a sale; undoing a sale; who has an account; money into and out of a
balance; limits and special cases; the end of the day; what the pages show;
the bounds; language, currency and data.

None repeated a question the lessons already answered: nothing was asked
about narrow screens, examples in forms, cross-site requests, going back
after a refusal or how done is judged. Four were the earlier products'
questions asked again for another business (voiding asks first, corrected
and never removed, what the pages show, the bounds), each with the earlier
answer as the recommendation.

## Labels declared

`school canteen`, `web pages`, `local web server`,
`python stdlib and sqlite on localhost`, `money`. This is the first product
after the pet shop to declare `money`.

## Lessons added: 9 (L1201 to L1209), 8 with a case

| | With a case | Prose only |
|---|---|---|
| From the person's answers | L1202 a sale is paid whole, L1203 a balance is its records, L1204 voids ask first, L1205 corrected never removed, L1206 the day, L1207 lists and export, L1208 the bounds | L1201 scope |
| From a defect found by trying the product | L1209 a silent connection holds nobody up (`local web server`) | |

Changed, on a case that failed here:

- **L0008** (`money`): its case was the pet shop's and failed for want of a
  pet shop. Made general (L0024); what it needs is in each surface under
  "money". The lesson's sentence is as it was.
- **L0042**: was `school library`, is `web pages`, and its line lost "the
  library's". Its case, made general, failed on the canteen (below).

Case before fix, by commit:

- `9cc75b2` L1201 to L1208 and seven cases, with `product/LABELS`; every case
  in force fails (no product, no surface). The money case made general.
- `a17dfeb` the product and its surface. Written before that commit and run
  for the first time against it: six of the seven canteen cases passed on
  their first run; the seventh, of L1203, had its own arithmetic wrong (6.00
  taken for 600.00 on the way to the ceiling) and the build was right. All
  ten general cases in force (L0006, L0007, L0008, L0012, L0014, L0035 and
  the four of L0026) passed on their first run, with every wrong variant
  refused. None of them was changed for the canteen but the money case.
- `57a8d7a` L0042 made general, its case failing on the canteen. `561691c`
  the fix.
- `eaaab0c` L1209 with its case failing. `2e657bc` the fix.

One thing was not case first in the plain sense: the product file was
written before the first commit, after the cases, and kept out of that
commit. The cases were seen to fail without it, not against a wrong build.

## Defects found

- **In the product, by reading a screenshot.** At 800 px the list of sales
  had no State column to be seen: "stands" and "voided on 2026-11-20" were
  under Open and Void, held in sight over them. Every case passed. It is the
  defect the library had in run 010, whose lesson was the library's and not
  in force. L0042 made general.
- **In the product, by trying what a browser does.** With one connection
  open and silent, the first build answered no other request: 5 seconds and
  no page. It served one connection at a time. No case saw it. L1209.
- **In a case, by its first run.** `cases/1203` (above).

## The other products and the cases made general (L0024)

Two cases born in one product were needed by the canteen and made general,
and one new case was born general. `./bring --try` was then run from this
branch (at `480976c`) for the two products that live on other branches. Their
source was not read.

- **The pet shop** (`origin/run/005-labels`) meets what is here: 34 lessons
  in force, 31 cases run. The money case passes on it as it did before it
  was general, with the same 32 checks as on the canteen. The case of L0042
  is now in force for it, because the pet shop declares `web pages`, and
  passes on its build with the names its surface already used for the
  check on crushed columns. The case of L1209 passes on it.
- **The school library** (`origin/run/010-library-rebuild`) meets what is
  here: 32 in force, 29 cases run. The case of L0042, now reading the
  library's surface for what it used to hold itself, passes as before; so
  does the case of L1209.

So the defect of L1209 was the canteen's alone: both earlier builds already
answer beside a silent connection. No lesson had said so.

What each case made general now takes from the surface: for `money`, the
form that takes a price and the fields beside it, the highest price, the
form of a sale and its lines, and where the cents are read; for L0042, what
is entered, the pages measured, how many cells and held cells at the least,
and what must be on a page for the measure to mean something. Both branches
of the other products were left as they were; whether they take the new
surface sections is the person's, as before.

## Check at the end

    lessons 50 · in force 33 · not in force 17 · with a case 42 · prose only 8 · cases run 30 · cases not run 15 · product: school canteen, web pages, local web server, python stdlib and sqlite on localhost, money · product 842 lines · cases in force 2856 lines (3.4 to 1) · at the start of a session CLAUDE.md 6928 bytes and 3924 characters from the hook (6823 with no product)

It takes about 70 s. The cases in force refuse 65 wrong variants, each after its fault acted.

`./check --selftest`: accepted 8 of 8 right trees, refused 35 of 35 wrong.

## Size

Product 842 lines in one file. The canteen's eight cases 1,116 lines; its
surface 255.

## Time and agents

The first commit of the run is stamped 21:50 and the product 21:52, by the
container's clock; the questions were asked before that and how long they
waited is not known. No sub-agents.

## Driven by script and read by the agent (Chromium 157; 1100 px, 390 px and 800 px)

On the sample data, twice: on the first build and again after the fix of
L0042. At 1100 px: two quantities typed and the total read from the page
before sending (5.80); cash 10 sent with Enter, and the till back empty with
"change 4.20" above it; a card number typed into the focused field and sent
with Enter, as a scanner would, and the balance left read (15.80); a sale
beyond a balance of 5.00, refused with both figures; Back, with the quantity
still there, the total back to 8.40 and the card field empty with the focus;
the till opened from an account's page and a sale from it. Screenshots read:
the till empty, filled, after each sale and after Back; the menu; an item's
form; the accounts; an account; a sale; the question before a void; the day
before and after a void; the till, the sales, the accounts and an account as
cards at 390 px; the sales and the accounts at 800 px, which is where the
State column was missing, and after the fix is there.

By requests and not in a browser: a connection held open and silent while
the till is asked for (L1209); the notice of `--today` on a page.

Changed after looking, without a lesson because it is taste: an empty field
of a card is not shown (the State of an account that is at the school).

## Not verified

- The person has not used the till. Everything above is the builder looking
  at its own work (L0003, L0013).
- Nobody stood at a queue with it. Whether typing quantities beside items is
  fast enough at break, against buttons that add one, is not known.
- A real card scanner. Typing the number and Enter stood in for it.
- Only Chromium. The cross-site refusal, what Back restores and where the
  focus goes all depend on the browser.
- A person's browser against the first build: L1209 was found with a bare
  connection, not by a browser stalling.
- A list too wide for 800 px with the longest values allowed: measured by
  the cases, seen by nobody.
- More than 208 sales, or a menu of more than ten items on the till. A term
  of sales was not tried for speed; the day's page adds up with SQL over
  every sale each time it is opened.
- Two tills, or two tabs sending at once: one lock, one transaction per
  request, and no case races it. Loss of power mid-write; a copied database.
- Anyone logged in to the same machine can open the till and every balance.
- The running total on the till is added up in the browser; the sale's
  total is the server's. With scripts off the total reads 0.00 until sent.
- Reading the pages with a screen reader.
- The numbers themselves (500.00 a top-up, 1,000.00 a balance, 99 a line):
  accepted as recommended, confirmed by no school.

## Decided by the builder, for the person to overrule

- How a sale is paid follows from which field was filled, cash given or
  card; there is nothing to choose. Cash always needs the amount given, also
  when it is exact (L1202).
- After a sale the till comes back empty with the sale just made above it;
  the sale's own page is one link away.
- A pay-out is of any amount up to the balance, also for an account that has
  left, and has no void; a wrong one is put right with a top-up (L1203).
- The void of a sale returns its money even above 1,000.00 (L1203).
- The void of a top-up asks first, like the void of a sale (L1204).
- A card number belongs to one account, and is letters, digits and hyphens
  (L1205, L1208).
- A void counts on the day it is made: yesterday's cash expected does not
  change when one of its sales is voided today. An earlier day can be
  opened with `/day?date=` (L1206).
- An account's page lists its latest 200 sales and its latest 200 top-ups
  and pay-outs; the menu and the till are shown whole (L1207).
- Bounds for inputs the answer did not list: cash given up to 9,999.99,
  pay-out, kind, search text 100 characters, the day asked for (L1208).
- `--today YYYY-MM-DD`, with a notice on every page while it is set (L1201).
- The list of sales says "voided" without the day, and when in one column,
  so that it fits 800 px; the day of the void is on the sale's page (L0042).
- L0042 relabelled `web pages`, which puts it in force for the pet shop.
- The sample data: ten items, four accounts, three of them topped up. Those
  top-ups are counted like any other, so the day `--sample` is loaded says
  55.00 expected in a drawer that holds nothing.

## Left out, and not asked

- Buttons that add one of an item; a sale is quantities typed.
- Items in an order the canteen chooses; they are by category and name.
- Finding a pupil at the till by name; the till takes a card number, and a
  pupil without a card is found on the accounts page, which has a Sell link.
- Totals for a week or a term, and a list of who owes or holds what.
- Moving a whole class up a year. Accounts are corrected one at a time.

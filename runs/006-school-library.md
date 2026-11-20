# Run 006 — school library, the second product

- **Prompt:** `prompts/002-school-library.md` ("Build a lending library system for a school.")
- **Branch:** `run/006-school-library`, 2026-11-20, started from the base (the
  lessons and cases after run 005, no product). The prompt arrived as an
  automated notice, not a typed message; it was taken as the prompt file this
  branch is named for.

## Questions

One round, 14 questions, each with a recommendation, asked before anything
was built. Answered with a single "Ok". No question after that. How long the
round waited is not visible from inside the session.

Who uses it; what it is built on (three existing labels offered, with the
lessons each brings); fines; titles or copies; who borrows; loan period and
limits; renewals; reservations; overdue; returning; correcting and removing;
what the pages show; the bounds; language, dates and data.

None repeated a question the lessons already answered: nothing was asked
about narrow screens, examples in forms, cross-site requests or how done is
judged. Four were the pet shop's questions asked again for another business
(one click or a question page, correcting and removing, what the pages show,
the bounds), each with the pet shop's answer as the recommendation.

## Labels declared

`school library`, `web pages`, `local web server`,
`python stdlib and sqlite on localhost`. Not `money`: there are no fines.
Not `pet shop`.

## Lessons added: 9 (L0027 to L0035), 8 with a case

| | With a case | Prose only |
|---|---|---|
| From the person's answers | L0028 a loan is of one copy, L0029 the server sets the dates, L0030 return is one click, L0031 corrected never removed, L0032 lists searched and export all, L0033 the bounds | L0027 scope |
| From a defect in the scaffold | L0034 the product is found by its surface | |
| From a defect found by driving the product | L0035 back after a refusal | |

Case before fix, by commit:

- `9ec1553` L0027 to L0033 and six cases, all failing (no product), with
  `product/LABELS`. The eight inherited cases fail too: they look for the
  pet shop.
- `e8743c9` the eight made general. Still failing here; passing on the pet
  shop.
- `0b5549f` the product. The six pass; four did on their first run, two had
  a mistake in the case (a form field named `status`, like an argument of
  the helper). Six of the eight general cases passed on the first build;
  two refused it (below).
- `4f876b5` L0034 with its case failing, and the case of L0019 failing on
  what it had missed. `fd29ec9` the fix.
- `13ecdc1` L0035 with its case failing on the library. The commit after it:
  the fix.

## The second product and the general cases (L0024)

This is the first time a second product switched on labels the pet shop
chose. All eight cases under them failed, as the handoff said they would,
and were made general, not switched off:

- What each case knew about the pet shop moved to `surface/pet-shop.json`:
  the program, one form to post, the pages to read for examples and what
  fills their other fields, a person's way through the forms as steps, and
  what to fill the lists with. `surface/school-library.json` holds the same
  for the library. The cases read the surface of the product in front of
  them; `caselib.js` and `caselib.py` find it through `product/LABELS`.
- Put to the pet shop build of run 005 (`SURFACE='pet shop' SHOP=...`), the
  eight pass with the checks they had before: 89, 19, 96, 144, 31, 28, 97,
  and 24 for 23 in the forms case, which now also requires that the way
  through looks for a choice made in advance. The pet shop's nine own cases
  pass on it unchanged but for one line each that asks for their product.
  That build was fetched from `run/005-labels` and run; its source was not
  read.
- What turned out to be the pet shop's and not general: every path and
  field; the faults of two cases (which control arrives preselected, which
  example is refused); the thresholds (rows, cells, examples); and that a
  form posts, since a search form asks with GET.
- What the cases still fix for any product under `web pages`: `form.card`,
  `td.num`, a `thead th` per column, `main`, `nav`, a submit button of
  `type=submit`, and a layout that puts a list too wide for 800 px in a box
  that scrolls with its last column held in sight. The last is a design the
  wrong variants of two cases depend on, not something L0026 asks for; a
  product that used cards up to a greater width would fail them. Not
  changed: no product has needed it.

Two general cases refused the library's first build, both for the reason
they exist: the catalogue scrolled sideways at 320 px with a 20-letter shelf
mark, and a due date with "overdue" and "renewed" beside it broke a number
cell in two. No recorded defect of the narrow layout came back in a product
its lessons were not written for.

Cases changed besides: 0015 no longer measures hidden fields (the lend form
has one, and it was called a control outside its form); 0029 looks for
"overdue" in the row of the loan, not in the page, whose menu has the word.

## Defects found

- **In the scaffold, by reading a passing case's output.** The case of L0019
  said "17 of 17 cases pass ... no product in this tree" with the library in
  the tree. The case library started `product/petshop.py` by default, so the
  case found no product and ran everything with the source in place. L0034.
- **In the product, by driving it.** Every refusal said "what you typed is
  still there"; after a refused loan the copy field was empty, and the
  sentence also stood on the not-found page. L0035.

## Check at the end

    lessons 32 · in force 22 · not in force 10 · with a case 26 · prose only 6 · cases run 20 · cases not run 9 · product: school library, web pages, local web server, python stdlib and sqlite on localhost · CLAUDE.md 11333 bytes

`./check --selftest`: accepted 5 of 5 right trees, refused 19 of 19 wrong.
The cases over the product run 57 wrong variants, all refused after acting.
L0019: 19 of 19 cases pass on the library's bytecode with no source.
`./check` takes about 85 s. Without `product/`: 9 in force, 5 cases run.

## Size

Product 761 lines in one file. Cases 2721 lines (run 005: 1679), shared
helpers 434 (330), the two surfaces 355, `check` 298, lesson files 797 (569).

## Time and agents

About 55 minutes from the base commit to the last (13:26 to 14:21),
including the wait for the answer. No sub-agents.

## Driven by script and read by the agent (Chromium 157; 1100 px light, 390 px dark, then 800 px and 390 px light)

On the sample data. Screenshots of all nine kinds of page at 1100 px and at
390 px; I read the catalogue, the borrowers, the desk and the overdue page
as tables, and a title, a borrower and the loans as cards. Then, at 390 px:
a borrower searched for from the desk; a copy number typed into the focused
field and sent with Enter, as a scanner would; a copy that is out, a copy
marked lost and "seven" each refused with its reason; Back after each (the
copy field empty, which is how L0035 was found); a third book, after which
the form is replaced by a note about the limit; a renewal from the
borrower's page, which returns there; a loan found by copy number from the
desk and returned; a title entered with a bad ISBN, refused, Back (title
still there), entered, corrected; a copy marked lost; a search by a
hyphenated ISBN; a borrower sent with no kind (the browser stops it). A
form posted to the library by a page on another port, as 127.0.0.1 and as
localhost: both answered 403 and no borrower was created. The library
opened through `http://localhost`: works. After the fix, the loans at 800 px
with the `--today` notice, and the refusal at 390 px.

Changed after looking, without a lesson because it is taste: an empty field
of a card ("With" and "Due" of a copy on the shelf) is not shown.

## Not verified

- The person has not used the library. Everything above is the builder
  looking at its own work (L0003, L0013).
- Only Chromium. The cross-site refusal and what Back restores both depend
  on the browser; Firefox and Safari were not tried.
- A real barcode scanner. Typing digits and Enter stood in for it.
- A list too wide for 800 px with the longest values allowed: measured by
  the cases, seen by nobody. At 800 px I saw ordinary data only.
- More than 206 titles or 410 loans. A school catalogue of thousands was
  not tried for speed.
- Two people or two tabs posting at once. One lock and one transaction per
  request; no case races it. Loss of power mid-write; a copied database.
- Anyone logged in to the same machine can open the library.
- Reading the pages with a screen reader.
- Mechanical changes to the product's source, to see which wrong builds the
  cases let through (run 003 did it once on the pet shop).
- The pet shop's branch was not touched. The general cases were put to its
  build from here; whether that branch takes them is the person's merge.

## Decided by the builder, for the person to overrule

- `--today YYYY-MM-DD`, so that overdue can be seen and tested; every page
  shows a red notice while it is set (L0027).
- A copy that is out is returned before it can be marked lost (L0031).
- An ISBN-10 may end in X, against the bound as asked (L0033).
- Bounds for two inputs the answer did not list: search text 100
  characters, copy number 9 digits (L0033).
- The scan field comes back empty after a refusal (L0035).
- Lending is on the borrower's page; there is no list of borrowers to pick
  from. Returning is on the loans page, found by copy number.
- After a return or a renewal the page shown is the one the button was on.
- Overdue classes are grouped as typed: "7b" and "7B" are two classes.
- The sample data, and that `--sample` does nothing to a file with data.
- `surface/` as a directory of JSON files, and a way through the forms
  written as steps rather than as code.

## Left out, and not asked

- A borrower's returned loans are counted on their page, not listed.
- A title can be given copies without end, 50 at a time.
- Moving a whole class up a year. Borrowers are corrected one at a time.
- A way to see which titles are most borrowed, or never.

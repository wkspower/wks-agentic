# Lessons and cases

This branch tests one thesis:

> Lessons with their reasons kept the way torre does it, and every lesson
> that can be checked by a machine also turned into a case.

A *lesson* is one sentence that changes what the next session does, kept with
the reason for it and the event that taught it. A *case* is a program that
passes or fails and prints what it measured. Code built here is disposable;
the lessons and the cases are what lasts.

## Where things are

| Path | Holds |
|---|---|
| `CLAUDE.md` | This file. Read at the start of every session. One line per lesson, with its labels. |
| `lessons/` | One file per lesson: the reason, the source, what would be a regression. |
| `cases/` | One executable per checkable lesson. Run from the repository root. |
| `caselib.py`, `caselib.js` | What the cases share: start the product, put a fault in front of it. |
| `surface/` | One file per product: what a case under a general label may know about it. |
| `check` | Proves the two stay linked, and runs the cases in force. `./check` and `./check --selftest`. |
| `HANDOFF.md` | State of the work and how to resume. Read it second. |
| `product/` | Whatever a run builds. May be deleted and rebuilt at any time. |
| `product/LABELS` | What the product is: the labels it chose, one per line. No product, no labels. |
| `prompts/`, `runs/` | The prompts under test and what each run showed. |

## What a session does

- **When something is learned, it becomes a lesson before the work goes on.**
  Learned means: the person decides or corrects something, a defect is found,
  or an approach is tried and rejected. Write `lessons/NNNN-slug.md` and add
  its line below.
- **A lesson says when it applies**, in square brackets after its number:
  `always`, or one or more plain labels separated by commas. There is no
  list to choose from; reuse a label when it fits and write a new one when
  none does. A lesson is in force when it is `always` or the product declared
  one of its labels in `product/LABELS`. Follow the lessons in force; the
  others are kept for the product that switches them on (L0023).
- **If a machine can check it, write the case first.** See it fail, then fix.
  If no machine can check it, mark the line `prose:` and say why not.
- **A lesson or a case changes only on evidence from outside**: the person,
  real data, or a case that fails. Say which in the lesson's Source.
- **Run `./check` before saying the work is done**, and report its summary line.
- **Keep this file short.** One line per lesson. Reasons live in `lessons/`.

## Lessons

- **L0001** [always] A check that measured nothing has failed; every check prints what it measured. [why](lessons/0001-empty-is-not-a-result.md) · case: [`cases/0001-empty-is-not-a-result`](cases/0001-empty-is-not-a-result)
- **L0002** [always] A wrong variant is kept as a small change applied when the check runs, never as a full copy. [why](lessons/0002-no-full-copies.md) · case: [`cases/0002-no-full-copies`](cases/0002-no-full-copies)
- **L0003** [always] Agreement between agents of the same model is not evidence that something is right. [why](lessons/0003-same-model-agreement.md) · prose: no program can tell where a claim's evidence came from
- **L0004** [always] Before building, ask the person everything foreseeable in one round, each question with a recommendation. [why](lessons/0004-ask-in-one-round.md) · prose: whether a later question could have been foreseen is a judgement
- **L0005** [pet shop] The pet shop system is for staff: products and stock, customers and their pets, counter sales, grooming appointments. [why](lessons/0005-scope-of-the-pet-shop.md) · prose: whether a feature is inside the scope is a reader's judgement
- **L0006** [python stdlib and sqlite on localhost] The web app on localhost is the only way in, on Python's standard library and one SQLite file. [why](lessons/0006-one-way-in.md) · case: [`cases/0006-one-way-in`](cases/0006-one-way-in)
- **L0007** [local web server] A request from another site, or to another host name, is refused. [why](lessons/0007-cross-site-refused.md) · case: [`cases/0007-cross-site-refused`](cases/0007-cross-site-refused)
- **L0008** [money] Money is whole cents, and every input has a stated bound. [why](lessons/0008-money-and-bounds.md) · case: [`cases/0008-money-and-bounds`](cases/0008-money-and-bounds)
- **L0009** [pet shop] A sale beyond stock is refused whole, stock never goes below zero, and low stock is listed. [why](lessons/0009-stock-never-negative.md) · case: [`cases/0009-stock-never-negative`](cases/0009-stock-never-negative)
- **L0010** [pet shop] A sale records its method and the amount the server computed; it is never edited, only voided whole, once. [why](lessons/0010-sale-recorded-voided-whole.md) · case: [`cases/0010-sale-recorded-voided-whole`](cases/0010-sale-recorded-voided-whole)
- **L0011** [pet shop] Grooming has one groomer and one-hour slots: an appointment belongs to a pet, and a taken slot is refused. [why](lessons/0011-appointments-no-double-booking.md) · case: [`cases/0011-appointments-no-double-booking`](cases/0011-appointments-no-double-booking)
- **L0012** [web pages] What a person does in the forms is checked in a real browser, and a missing browser fails. [why](lessons/0012-forms-in-a-real-browser.md) · case: [`cases/0012-forms-in-a-real-browser`](cases/0012-forms-in-a-real-browser)
- **L0013** [always] Done means every case in force passes, the agent drove the product by script as a person would and read what came out, and what was not verified is said; none of that is the person using it. [why](lessons/0013-done-means-used-by-hand.md) · prose: what the agent saw in its own screenshots is not a program's result
- **L0014** [web pages] Every example a form shows is a value that form accepts. [why](lessons/0014-examples-are-accepted.md) · case: [`cases/0014-examples-are-accepted`](cases/0014-examples-are-accepted)
- **L0016** [pet shop] Voiding a sale asks first, on a second page that shows the sale; no page voids on one click. [why](lessons/0016-void-asks-first.md) · case: [`cases/0016-void-asks-first`](cases/0016-void-asks-first)
- **L0017** [pet shop] Customers and pets can be corrected, and nothing is removed. [why](lessons/0017-corrected-never-removed.md) · case: [`cases/0017-corrected-never-removed`](cases/0017-corrected-never-removed)
- **L0019** [always] A wrong variant is a fault put at the product's interface when the case runs; no case names, reads or edits the product's source. [why](lessons/0019-cases-know-no-source.md) · case: [`cases/0019-cases-know-no-source`](cases/0019-cases-know-no-source)
- **L0020** [pet shop] Cancelling an appointment is one click on the list: no question page, and opening an address never cancels. [why](lessons/0020-cancel-is-one-click.md) · case: [`cases/0020-cancel-is-one-click`](cases/0020-cancel-is-one-click)
- **L0021** [pet shop] The sales page lists the latest 200 sales and says how many there are; appointments before today are on no page; `/export.json` holds everything. [why](lessons/0021-pages-show-recent-export-all.md) · case: [`cases/0021-pages-show-recent-export-all`](cases/0021-pages-show-recent-export-all)
- **L0023** [always] A lesson says when it applies in plain labels, a product declares the labels it chose, and only `always` and those are in force. [why](lessons/0023-labels-switch-lessons.md) · case: [`cases/0023-labels-switch-lessons`](cases/0023-labels-switch-lessons)
- **L0024** [always] A case is born in the product that needed it, and is made general only when a second product needs it. [why](lessons/0024-cases-born-in-a-product.md) · prose: whether a second product needs a case is a judgement
- **L0025** [pet shop] The pet shop's prices include tax, and its inputs are refused outside the table of bounds in the lesson. [why](lessons/0025-pet-shop-bounds.md) · case: [`cases/0025-pet-shop-bounds`](cases/0025-pet-shop-bounds)
- **L0026** [web pages] On a narrow screen a list is shown as stacked cards, not as a table: nothing scrolls sideways, is crushed or breaks in two, and each row's actions are in sight, from 320 px up with the longest names allowed. [why](lessons/0026-narrow-lists-are-cards.md) · cases: [`cases/0026-narrow-lists-are-cards`](cases/0026-narrow-lists-are-cards), [`cases/0015-no-sideways-scroll`](cases/0015-no-sideways-scroll), [`cases/0018-columns-not-crushed`](cases/0018-columns-not-crushed), [`cases/0022-row-actions-in-sight`](cases/0022-row-actions-in-sight)
- **L0027** [school library] The school library system is for library staff at one desk: a catalogue of titles and their numbered copies, borrowers, loans, returns, renewals and the overdue list. [why](lessons/0027-scope-of-the-school-library.md) · prose: whether a feature is inside the scope is a reader's judgement
- **L0028** [school library] A loan is of one numbered copy to one borrower: a copy that is out, lost or withdrawn is refused, and so is a borrower who has left or holds 3 books as a pupil, 10 as staff. [why](lessons/0028-a-loan-is-of-one-copy.md) · case: [`cases/0028-a-loan-is-of-one-copy`](cases/0028-a-loan-is-of-one-copy)
- **L0029** [school library] The server sets every date: due 14 days after lending, renewed at most twice to 14 days from today, and overdue loans are listed by class. [why](lessons/0029-the-server-sets-the-dates.md) · case: [`cases/0029-the-server-sets-the-dates`](cases/0029-the-server-sets-the-dates)
- **L0030** [school library] Returning a book is one click on the list: no question page, opening an address never returns, and a loan is never edited or removed. [why](lessons/0030-return-is-one-click.md) · case: [`cases/0030-return-is-one-click`](cases/0030-return-is-one-click)
- **L0031** [school library] Titles and borrowers can be corrected and nothing is removed: a copy is marked lost or withdrawn and back, lost while it is out ends its loan that day as lost, a borrower who has left is marked so. [why](lessons/0031-library-corrected-never-removed.md) · case: [`cases/0031-library-corrected-never-removed`](cases/0031-library-corrected-never-removed)
- **L0032** [school library] The catalogue and the borrowers are searched and show the first 200 matches, saying how many; loans out and overdue are shown in full, loans that ended (returned or lost) the latest 200; `/export.json` holds everything. [why](lessons/0032-lists-searched-export-all.md) · case: [`cases/0032-lists-searched-export-all`](cases/0032-lists-searched-export-all)
- **L0033** [school library] The school library's inputs are refused outside the table of bounds in the lesson. [why](lessons/0033-library-bounds.md) · case: [`cases/0033-library-bounds`](cases/0033-library-bounds)
- **L0034** [always] What the cases know about a product is in its file under `surface/`, found through `product/LABELS`; nothing the cases share remembers a product of its own. [why](lessons/0034-product-found-by-its-surface.md) · case: [`cases/0034-product-found-by-its-surface`](cases/0034-product-found-by-its-surface)
- **L0035** [web pages] After a refusal, going back shows the form with what was typed, except a field that is scanned into, which comes back empty; the refusal page promises only what holds. [why](lessons/0035-back-after-a-refusal.md) · case: [`cases/0035-back-after-a-refusal`](cases/0035-back-after-a-refusal)
- **L0036** [school library] Classes are compared without regard to capitals: "7b" and "7B" are one class on the overdue list and in search, shown under the spelling most of its borrowers have. [why](lessons/0036-classes-without-capitals.md) · case: [`cases/0036-classes-without-capitals`](cases/0036-classes-without-capitals)
- **L0037** [always] A record of the person's approval says what they saw and how they said it. [why](lessons/0037-approval-says-what-was-seen.md) · prose: no program can tell what a person read

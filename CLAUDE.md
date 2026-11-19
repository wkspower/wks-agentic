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
| `CLAUDE.md` | This file. Read at the start of every session. One line per lesson. |
| `lessons/` | One file per lesson: the reason, the source, what would be a regression. |
| `cases/` | One executable per checkable lesson. Run from the repository root. |
| `caselib.py`, `caselib.js` | What the pet shop cases share: start the shop, put a fault in front of it. |
| `check` | Proves the two stay linked. `./check` and `./check --selftest`. |
| `HANDOFF.md` | State of the work and how to resume. Read it second. |
| `product/` | Whatever a run builds. May be deleted and rebuilt at any time. |
| `prompts/`, `runs/` | The prompts under test and what each run showed. |

## What a session does

- **When something is learned, it becomes a lesson before the work goes on.**
  Learned means: the person decides or corrects something, a defect is found,
  or an approach is tried and rejected. Write `lessons/NNNN-slug.md` and add
  its line below.
- **If a machine can check it, write the case first.** See it fail, then fix.
  If no machine can check it, mark the line `prose:` and say why not.
- **A lesson or a case changes only on evidence from outside**: the person,
  real data, or a case that fails. Say which in the lesson's Source.
- **Run `./check` before saying the work is done**, and report its summary line.
- **Keep this file short.** One line per lesson. Reasons live in `lessons/`.

## Lessons

- **L0001** A check that measured nothing has failed; every check prints what it measured. [why](lessons/0001-empty-is-not-a-result.md) · case: [`cases/0001-empty-is-not-a-result`](cases/0001-empty-is-not-a-result)
- **L0002** A wrong variant is kept as a small change applied when the check runs, never as a full copy. [why](lessons/0002-no-full-copies.md) · case: [`cases/0002-no-full-copies`](cases/0002-no-full-copies)
- **L0003** Agreement between agents of the same model is not evidence that something is right. [why](lessons/0003-same-model-agreement.md) · prose: no program can tell where a claim's evidence came from
- **L0004** Before building, ask the person everything foreseeable in one round, each question with a recommendation. [why](lessons/0004-ask-in-one-round.md) · prose: whether a later question could have been foreseen is a judgement
- **L0005** The pet shop system is for staff: products and stock, customers and their pets, counter sales, grooming appointments. [why](lessons/0005-scope-of-the-pet-shop.md) · prose: whether a feature is inside the scope is a reader's judgement
- **L0006** The web app on localhost is the only way in, on Python's standard library and one SQLite file. [why](lessons/0006-one-way-in.md) · case: [`cases/0006-one-way-in`](cases/0006-one-way-in)
- **L0007** A request from another site, or to another host name, is refused. [why](lessons/0007-cross-site-refused.md) · case: [`cases/0007-cross-site-refused`](cases/0007-cross-site-refused)
- **L0008** Money is whole cents with tax included, and every input has a stated bound. [why](lessons/0008-money-and-bounds.md) · case: [`cases/0008-money-and-bounds`](cases/0008-money-and-bounds)
- **L0009** A sale beyond stock is refused whole, stock never goes below zero, and low stock is listed. [why](lessons/0009-stock-never-negative.md) · case: [`cases/0009-stock-never-negative`](cases/0009-stock-never-negative)
- **L0010** A sale records its method and the amount the server computed; it is never edited, only voided whole, once. [why](lessons/0010-sale-recorded-voided-whole.md) · case: [`cases/0010-sale-recorded-voided-whole`](cases/0010-sale-recorded-voided-whole)
- **L0011** Grooming has one groomer and one-hour slots: an appointment belongs to a pet, and a taken slot is refused. [why](lessons/0011-appointments-no-double-booking.md) · case: [`cases/0011-appointments-no-double-booking`](cases/0011-appointments-no-double-booking)
- **L0012** What a person does in the forms is checked in a real browser, and a missing browser fails. [why](lessons/0012-forms-in-a-real-browser.md) · case: [`cases/0012-forms-in-a-real-browser`](cases/0012-forms-in-a-real-browser)
- **L0013** Done means every case passes, the app was used by hand in a browser, and what was not verified is said. [why](lessons/0013-done-means-used-by-hand.md) · prose: use by hand is by definition not a program
- **L0014** Every example a form shows is a value that form accepts. [why](lessons/0014-examples-are-accepted.md) · case: [`cases/0014-examples-are-accepted`](cases/0014-examples-are-accepted)
- **L0015** No page scrolls sideways, no control leaves its form and no number or label breaks in two, from 320 px wide up, with the longest names allowed. [why](lessons/0015-no-sideways-scroll.md) · case: [`cases/0015-no-sideways-scroll`](cases/0015-no-sideways-scroll)
- **L0016** Voiding a sale asks first, on a second page that shows the sale; no page voids on one click. [why](lessons/0016-void-asks-first.md) · case: [`cases/0016-void-asks-first`](cases/0016-void-asks-first)
- **L0017** Customers and pets can be corrected, and nothing is removed. [why](lessons/0017-corrected-never-removed.md) · case: [`cases/0017-corrected-never-removed`](cases/0017-corrected-never-removed)
- **L0018** A table scrolls inside its box before it crushes a column of words to one word per line. [why](lessons/0018-columns-not-crushed.md) · case: [`cases/0018-columns-not-crushed`](cases/0018-columns-not-crushed)
- **L0019** A wrong variant is a fault put at the product's interface when the case runs; no case names, reads or edits the product's source. [why](lessons/0019-cases-know-no-source.md) · case: [`cases/0019-cases-know-no-source`](cases/0019-cases-know-no-source)
- **L0020** Cancelling an appointment is one click on the list: no question page, and opening an address never cancels. [why](lessons/0020-cancel-is-one-click.md) · case: [`cases/0020-cancel-is-one-click`](cases/0020-cancel-is-one-click)
- **L0021** The sales page lists the latest 200 sales and says how many there are; appointments before today are on no page; `/export.json` holds everything. [why](lessons/0021-pages-show-recent-export-all.md) · case: [`cases/0021-pages-show-recent-export-all`](cases/0021-pages-show-recent-export-all)

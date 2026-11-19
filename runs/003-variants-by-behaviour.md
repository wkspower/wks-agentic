# Run 003 — wrong variants by behaviour

- **Prompt:** none from `prompts/`. The person's instruction of 2026-11-19,
  after reading `runs/002-pet-shop-rebuild.md`: change how wrong variants
  are expressed so that no case names, reads or edits the product's source.
- **Branch:** `run/003-variants-by-behaviour`, 2026-11-19. A change to the
  cases only. `product/petshop.py` is byte for byte what run 002 left.

## The finding it answers

Run 002 reported that not one of the old wrong variants had to be rewritten
after the rebuild. Each was a line of `product/petshop.py` replaced by
another, so the builder had written the new source to contain those lines.
The cases were fixing about two dozen lines of the program's inside, against
the thesis that only what someone depends on is fixed.

## Questions

None. The instruction said what was wanted and offered one direction as
optional. Nothing came up that it did not decide.

## What was done

A wrong variant is now the product, started the usual way, with one fault
at its interface (`caselib.py`, `caselib.js`):

- **Over HTTP** the fault is a function that stands in for the shop on the
  requests it names. It changes the request on its way in (a foreign Origin
  rewritten to the shop's own, a price above the bound lowered to it), or
  the answer on its way out (a void button added to the list of sales), or
  sends requests of its own through the shop's forms (after a void, an
  adjustment that takes the stock away again).
- **In the browser** the fault runs in each page after the product served
  it: it removes the empty choice from a select, or adds one style rule.
- **For the command line** (L0006) the fault is a listener on the machine's
  other address, or a six-line program that imports a module from elsewhere
  and then runs the shop.
- Each fault counts when it acts. A wrong variant refused without its fault
  having acted fails the case; a fault that raises an error fails the case
  as broken, not as refused. Each case prints why each variant was refused.

The direction the person offered was to split each case into observation
and judgement and plant wrong observations. Not taken as offered, because a
fault at the interface keeps more: the case still has to send the request
the rule is about for the fault to act, and everything between the request
and the verdict (parsing the pages, the browser's layout) still runs on the
wrong thing. A few of the 29 faults are close to a planted observation all
the same: "a cancelled appointment still blocks", "a plus sign is refused"
and "low stock means below" do nothing but replace an answer.

## What this stops proving

That a mistake inside the product would be provoked by the case. Before, a
real wrong build was run and refused. Now the fault is my model of how a
wrong shop looks from outside, written in the same session as the case.
Two places where the model is visibly not the real thing:

- The product cannot hold a negative stock or two bookings in one slot (its
  database refuses), and no form can put them there. Those faults accept
  what should be refused and leave the nearest allowed state: stock 0, the
  earlier booking cancelled.
- The real wrong builds answered 500 where the faults answer 303 (see the
  replay below), because the database refused what the changed line let
  through. The cases refuse both; a case that looked only for 303 would not.

**What covers it cheaply:** changing the source mechanically and running the
cases, by hand, outside the cases. Done once in this run: the 28
replacements the old cases carried were taken from the previous commit and
each applied to a scratch copy of the product, and the new case was run
against that build (`SHOP=path cases/NNNN-...`). **28 of 28 refused**, 21
with the answer the corresponding fault gives and 7 with 500 in place of
303. The script was not kept: kept, it would pin the same lines again. A
mutation tool that names no text would do the same job for any rebuild; it
was not asked for and was not built.

## Lessons: 1 added (L0019, with a case), 2 changed

| | With a case | Prose only |
|---|---|---|
| From the person's decision on a finding of run 002 | L0019 cases know no source | |

- **L0019**, case first: commit `21794d7` has the lesson and its case
  failing (12 of 14 cases could not run without the product's source). The
  commit after it has the cases rewritten. The case builds a scratch tree
  whose `product/` holds compiled bytecode and no source, runs every other
  case there, and plants a case that reads the source, which must fail.
- **L0002** keeps its sentence. Its lesson file now says that the small
  change is a fault in front of the product, not replaced text.
- **L0006**: the case no longer parses the source for imports. The shop is
  started without site-packages (in every case, so an outside import
  anywhere stops it) and Python's own import record is read. Its lesson
  file says what was lost, below.

## Coverage

Every rule that had a wrong variant before has one after: 28 before, 29
after, same names except two reworded to say what the fault does ("the port
is open on another address", "an adjustment below zero is accepted").

| Case | Before | After |
|---|---|---|
| 0006 | 1 | 2 (new: a module from outside the standard library) |
| 0007, 0008, 0009, 0010 | 3 each | 3 each |
| 0011 | 4 | 4 |
| 0012 | 2 | 2 |
| 0014, 0018 | 1 each | 1 each |
| 0015 | 3 | 3 |
| 0016, 0017 | 2 each | 2 each |

Lost, and it never had a wrong variant: case 0006 used to count the
programs in `product/` that can be started, by looking for `__main__` in
their text. "A second program that changes the database" is now checked by
no machine. The checks of every case are otherwise unchanged; none was
removed or loosened.

## Check at the end

    lessons 19 · with a case 15 · prose only 4 · cases run 15 · CLAUDE.md 6191 bytes

`./check --selftest`: control accepted, refused 11 of 11 wrong trees.
29 wrong variants over the product, all refused after their fault acted.
L0019: 14 of 14 cases pass in a tree with no product source; the planted
case was refused. `./check` takes about 32 s (run 002: 15 s), because the
case of L0019 runs the other fourteen again.

## Size

Cases 1177 lines (run 002: 832), shared helpers 330 (232), lesson files
380 (314). Product unchanged at 768. A fault takes 6 to 12 lines where a
replacement took one.

## Time and agents

About 15 minutes by the container's clock (21:16 to 21:30). No sub-agents.

## Not verified

- The app was not used by hand in this run. Nothing in it changed; L0013
  applies to a product and this run built none.
- That a rebuild can now be written freely. This run removed the pin; only
  a run that rebuilds `product/` and passes shows it. The form fields,
  paths, `/export.json` keys and the 303/400/403/404/413 answers are still
  fixed by the cases, on purpose.
- The faults against any product but this one. A fault that relies on a
  form (`/products/N/stock`, `/appointments/N/cancel`) breaks if a rebuild
  drops it; the case then says the fault broke.
- The browser faults add style rules with `!important` and bypass the
  page's content security policy to do it. Only Chromium.
- The case of L0019 proves the cases run where the source is absent. A case
  that fetched the source from somewhere else would pass it.
- Mechanical changes to the source beyond the 28 replayed. Nobody has
  measured how many wrong builds the cases let through.

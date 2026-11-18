# Queue of the root

The one queue of principle 7: everything the root puts before the person.
One heading per item: `id | kind | asked | answered`. An item is answered
when its answer stands in the record, word for word.

Round 1 is the one round before the first effect. Until it is answered the
root causes no effect; an item left ungiven is taken at the option marked
*strictest* and no longer holds the tree.

Answer to round 1, word for word, to "Reply `ok` to take every
recommendation": **"Ok"**. Every item below stands at its recommended option.

### Q1 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**The executable check of the root's measure.**
- A. Number = items in this queue ÷ correct results. An item is one heading
  here (decision, proposal or notice; this round counts as its items). A
  correct result is a unit whose verdict passes and whose last change its
  judge let stand. `./verdict` passes when there is at least one correct
  result, the number is no higher than at the previous correct result, and no
  more items are waiting than there were then.
- B. As A, counting rounds instead of items.
- C. A definition you give.

Recommended: A. Strictest: A. Waiting costs: everything; no unit can be measured.

### Q2 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, attention**: items put before you after this round.
A. 0. B. 2 per correct result. C. 4 per correct result.
Recommended: B (the change that records your answers, which you judge by
reading, and the report of each result). Strictest: A; items the principles
require are still asked and show as overrun. Waiting costs: no effect anywhere.

### Q3 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, cost**: agent runs (one agent given one task) for the whole tree,
until you give more. A. 8. B. 16. C. 32.
Recommended: B. Strictest: A. Limit: the session that coordinates is metered
in time only. Waiting costs: no effect anywhere.

### Q4 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, time**: hours of work for the whole tree, until you give more.
A. 2. B. 4. C. 8.
Recommended: B. Strictest: A. Waiting costs: no effect anywhere.

### Q5 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, context**: what whoever arrives must read to resume one unit (its
document and its record). A. 8 KB. B. 16 KB. C. 32 KB.
Recommended: A. Strictest: A. Waiting costs: no effect anywhere.

### Q6 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, attempts**: builds tried per change before the unit stops and
returns. A. 1. B. 2. C. 3.
Recommended: B. Strictest: A. Waiting costs: no effect anywhere.

### Q7 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, alternatives per change** (principle 6), made without sight of the
change. A. 0. B. 1. C. 2.
Recommended: B. Strictest: A (spends least; selection then compares only
with what exists). Waiting costs: no effect anywhere.

### Q8 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Budget, cap on effects without undo.** A. 0. B. A number you give.
Recommended: A. Strictest: A. Waiting costs: no effect anywhere.

### Q9 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**What the pet shop system must do.**
- A. Sell animals and products to registered customers and keep the stock
  right. Units: catalog, stock, customers, sales, and the shop that joins them.
- B. A, plus services by appointment (grooming, veterinary).
- C. A list you give.

In every option: Python 3 standard library, run from the command line, state
in a local file; no network, no real money, no real personal data.
Recommended: A. Strictest: A. Waiting costs: no pet shop unit can be given a purpose.

### Q10 | decision | asked=2026-11-18T20:24Z | answered=2026-11-18T20:28Z
**Where the tree acts.**
- A. Only on branch `claude/wizardly-cerf-94l00l` of this repository, which
  is also the one branch where a change to the two documents runs first.
  Nothing reaches `develop` or anywhere else except by your own merge.
- B. As A, and the tree opens a pull request to `develop` when a unit stands.

Recommended: A. Strictest: A. Waiting costs: no effect anywhere.

## After round 1

### Q11 | notice | asked=2026-11-18T21:10Z | answered=2026-11-18T21:45Z
Answer, word for word: "It stands (Recommended)".
**To judge by reading: change `d5bfdef`**, which writes your answer "Ok"
into `root.md` (budget values, executable check) and `queue.md`, and
holds nothing else. Options: A. it stands. B. it does not; say what to
restore. Recommended: A. Waiting costs: nothing stops; if B, every unit
returns to its state before the change.

### Q12 | notice | asked=2026-11-18T21:10Z | answered=2026-11-18T21:45Z
Answer, word for word: "Read".
**Report of a result: catalog stands**, selected by the judge over one
alternative, with the root's number and the work due next
([`record.md`](record.md)). Options: A. read. Waiting costs: nothing stops.

### Q13 | notice | asked=2026-11-18T21:31Z | answered=2026-11-18T21:45Z
Answer, word for word: "Read".
**Report page you asked for**: time spent by stage and activity, the pet
shop features built, and the components the principles and the root drove
([`reports/first-result.html`](reports/first-result.html), published at
https://claude.ai/artifact/8txcTMbckjAsXtGQ2DaXqW). Options: A. read.
Waiting costs: nothing stops.

### Q14 | decision | asked=2026-11-18T21:50Z | answered=2026-11-18T21:50Z
**Work due next, two parts of which need budget from you**: (1) judge: any
stand undoable alone, about 3 runs; (2) build stock, customers, sales and
the shop, 8 runs, in budget; (3) audit cases for those four and an error
source for the enforcer, about 5 runs; (4) catalog: its builders' decisions
become rules. Options: A. go ahead, cost raised from 16 to 24 agent runs.
B. only part 2. Recommended: A. Waiting costs: parts 1 and 3 stay undone.
Answer, word for word: "Go ahead". Taken as A.

### Q15 | notice | asked=2026-11-18T22:21Z | answered=2026-11-18T23:05Z
Answer, word for word: "It stands (Recommended)".
**To judge by reading: change `c4b916f`**, which writes your answer "Go
ahead" into `queue.md` (Q14) and raises cost in `root.md` from 16 to 24
agent runs, and holds nothing else. Options: A. it stands. B. it does not;
say what to restore. Recommended: A. Waiting costs: nothing stops; if B,
every unit returns to its state before the change.

### Q16 | notice | asked=2026-11-18T22:21Z | answered=2026-11-18T23:05Z
Answer, word for word: "Read".
**Report of results: the whole pet shop stands** (stock, customers, sales
and the shop, each selected by the judge over one alternative), the judge
keeps one stands file per unit, and every measure the tree gave has an
audit ([`record.md`](record.md)). Options: A. read. Waiting costs: nothing
stops.

### Q17 | notice | asked=2026-11-18T23:14Z | answered=-
**Updated report page you asked for**: time by stage and activity over both
sessions, the pet shop as built, and the components the principles and the
root drove ([`reports/first-result.html`](reports/first-result.html),
https://claude.ai/artifact/8txcTMbckjAsXtGQ2DaXqW). Options: A. read.
Waiting costs: nothing stops.

### Q18 | decision | asked=2026-11-18T23:45Z | answered=2026-11-18T23:45Z
**Should pages you ask for count as items?** Under Q1 they do, so each
requested report makes the verdict fail until the next result. Options:
A. they count (as now). B. they do not; a change to the definition in
`root.md`. Waiting costs: the verdict fails after every requested page.
Answer, word for word: "No." Taken as B.

## Round before the first effect of the user interface

Goal given by the person, word for word: "Next goal: develop a professional
user interface for the pet shop management system". All 24 runs are spent
and 1 h 39 of time remains, so nothing is built until these are answered.

### Q19 | decision | asked=2026-11-18T23:45Z | answered=2026-11-18T23:47Z
Answer, word for word: "Web app, local (Recommended)". Taken as A.
**What kind of interface.** A. A web app in the browser, served only on
this machine by the Python standard library; Q9's "no network" becomes "no
network beyond this machine". B. A terminal interface; no rule changes.
Recommended: A. Strictest: B. Waiting costs: the unit has no purpose.

### Q20 | decision | asked=2026-11-18T23:45Z | answered=2026-11-18T23:47Z
Answer, word for word: "Everything (Recommended)". Taken as A.
**What it covers.** A. Everything the modules offer: catalog with price
changes, stock, customers with search, selling with a basket, sales
history, takings. B. Only the six commands of the shop.
Recommended: A. Strictest: B. Waiting costs: the unit has no purpose.

### Q21 | decision | asked=2026-11-18T23:45Z | answered=2026-11-18T23:47Z
Answer, word for word: "12 more (Recommended)". Taken as B: 36 runs in all.
**Budget, cost**: agent runs added to the 24 spent. A. 8. B. 12. C. 16.
Recommended: B (measure, build and alternative, audit, a second attempt,
and the change to the root's check that Q18 needs). Strictest: A.
Waiting costs: no effect anywhere.

### Q22 | decision | asked=2026-11-18T23:45Z | answered=2026-11-18T23:47Z
Answer, word for word: "8 hours (Recommended)". Taken as B.
**Budget, time**: hours for the whole tree, in place of 4. A. 6. B. 8.
C. 12. Recommended: B. Strictest: A. Waiting costs: no effect anywhere.

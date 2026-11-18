# State of the work

Whoever arrives resumes from here. The governing documents are
[`principles.md`](principles.md) and [`root.md`](root.md); what the person was
asked and answered is in [`queue.md`](queue.md); every decision of a judge is a
line of [`record/ledger.jsonl`](record/ledger.jsonl).

## Now

The tree is built and every verdict passes. One item is open in the queue
(Q4); it holds nothing.

| Unit | Document | Verdict (2026-11-18) |
|---|---|---|
| root | `root.md` | `python3 measure/check.py`: pass; 7 correct results, 4 items |
| judge | `tree/judge/unit.md` | 15 of 15 |
| guard | `tree/guard/unit.md` | 21 of 21 |
| pet shop | `tree/petshop/unit.md` | 11 of 11 |
| customers | `tree/petshop/customers/unit.md` | 13 of 13 |
| appointments | `tree/petshop/appointments/unit.md` | 15 of 15 |
| stock | `tree/petshop/stock/unit.md` | 12 of 12 |
| sales | `tree/petshop/sales/unit.md` | 14 of 14 |

Any unit's verdict: `python3 UNIT/measure/check.py UNIT`. The proof of the
root's check: `python3 measure/prove.py`.

## How a change is made

1. Change one unit only: either its `work/`, or what its parent gives it
   (`unit.md`, `measure/`). Never both, never two units.
2. `python3 tree/judge/work/judge.py tree/...` (for the judge itself:
   `python3 tree/guard/work/guard.py judge-the-judge`). The judge asks the
   guard, measures the candidate under `.rehearsal/`, compares it with what
   exists, and commits it or records the refusal. Do not commit a unit by hand:
   what is not in the ledger is not a result.
3. New behaviour starts as a scenario in the measure (a change by the parent),
   then the work. Something found wrong that passes: `judge.py --revoke ID`,
   then the scenario, then the fix. To take a change back: `judge.py --undo ID`.
4. Set `TREE_COMMIT_TRAILER` to sign the judge's commits.

Changes to `root.md`, `principles.md` and `measure/` (the root's) are the
person's: propose them in the queue.

## Limits, said as limits

- One agent wrote every measure and built every unit. The independence the
  principles ask of a measure's writer and of a judge's maker is not met; the
  person accepted this for the root's check (Q2) and it was absorbed as a rule
  for the rest. The planted cases are what stands in its place.
- Nothing outside this repository runs the guard or the judge (no hook can be
  installed from here). A commit made around them is not prevented; it is only
  absent from the ledger.
- The guard's rule against reaching outside reads the text of the work: it
  proves the absence of the listed imports, not of every way out.
- No alternatives made without sight of the change were compared (principle
  6): with one agent the budget does not pay them.
- The trend of the root's measure is not measurable before 20 correct
  results; until then only the budget is checked.
- Cost in money, time and context have no values in the root's budget; none
  is enforced.

## Tried and rejected

- *Drafting the tree before the budget and the check existed.* Rejected:
  `root.md` said the gap is asked first.
- *Choosing budget values or the pet shop's purpose myself.* Rejected: given
  by the parent.
- *Keeping the ledger line in the same commit as the change.* Rejected: undoing
  the change then conflicts with every later line; the change and its record
  are two commits.
- *Letting the judge judge itself, or the guard and the judge change
  together.* Rejected: the guard judges the judge with the procedure standing
  in history; a change to both has no judge and goes to the queue.
- *"Not worse" as the bar for a change.* Rejected for "strictly better"
  (more scenarios, or as many with fewer lines), so a change with no measured
  gain does not stand.
- *Submitting several new units in one change.* Refused by the guard (ledger
  #5-8); one unit per change.
- *Scanning every file under `work/`.* It blocked units whose work had merely
  been run (ledger #23-25, a wrong fail of the guard); became a case of the
  guard's measure, then fixed (#29, #30).

## History

- 2026-11-18 — Read the two documents. Opened Q1, Q2, Q3; the person answered.
- 2026-11-18 — Answers recorded; budget and measure written into `root.md` as
  the person gave them (commit f985864, undone by reverting it).
- 2026-11-18 — Root's check written first, with seven planted records and a control.
- 2026-11-18 — Judge and guard: measures, then work. First versions stood with
  no judge (none existed); every later change to them went through the other.
- 2026-11-18 — Pet shop and its four children: documents and measures given
  through the judge, then built through the judge.
- 2026-11-18 — Trying the command line by hand, outside the measures, showed
  four standing results wrong (ids written as text were accepted; a half sale
  was possible). Revoked (#18-21), turned into scenarios and planted cases
  (#22, #26-28), then fixed (#31-34).
- 2026-11-18 — Opened Q4.

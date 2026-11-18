# Record of the root

**State.** Every unit is built and standing. Correct results: 7. The
enforcer's full run over the tree reports no breach, and `./build` builds
all seven units.

| Unit | Verdict | Stands by |
|---|---|---|
| judge | passes, 4429 | itself as installer, the enforcer's run as judge |
| enforcer | passes, 10818 | judge |
| petshop | passes, 2824 | judge, over 1 alternative |
| petshop/catalog | passes, 1190 | judge, over 1 alternative |
| petshop/stock | passes, 862 | judge, over 1 alternative |
| petshop/customers | passes, 753 | judge, over 1 alternative |
| petshop/sales | passes, 1890 | judge, over 1 alternative |

**The number** (`./verdict`): 16 items ÷ 7 correct results = 2.29. It was
10.00 at the first result and 6.50 at the last report. The verdict passes: Q15 and Q16
are answered and nothing waits.

**Spend** (`ledger.tsv`): 24 of 24 runs; about 2 h 20 of 4 h. Attention
after round 1: 6 items for 7 results (budget 2 per result). Effects
without undo: 0.

**Error of what the root gave.**
- Judge, source: the audits of the judged units. Wrong stands: 0 of 6
  audited (the five pet shop units and the enforcer each pass every audit
  case). The judge's own stand has no audit: unknown. Wrong refusals:
  unknown, the judge has refused nothing.
- Pet shop measure, source `audit/petshop/check` (130 scenarios). Wrong
  passes: 0 of 2 builds. Wrong fails: 0 of 25 planted; 23 also fail the
  audit, 2 break only rule 3, which the audit cannot see from outside.
- Enforcer measure, source `audit/enforcer/check` (104 cases). Wrong
  passes: 0 of 1 build. Wrong fails: not counted (planted enforcers were
  not audited).
- Root's own measure: unmeasured (`root.md`, principle 6).

**Limits.**
- One session coordinated everything: it gave the declarations of every
  unit and built the judge and the enforcer. Measures, pet shop builds and
  audits came from separate agents that saw only what they were given, but
  all are the same model, started by that session.
- A change to the judge is installed by the candidate itself; only the
  enforcer's run is independent of it.
- Nothing forces a call to the enforcer; who made a change is not checked.
- Stands made before the judge kept one file per unit cannot be undone by
  reverting them alone.
- While a notice waits, the verdict fails: every report costs a failing
  verdict until it is read.
- The session's own work is metered in time only (Q3).

**Found and absorbed.** The enforcer's `undo` failed while its verdict
passed; the judge's single stands file blocked undo. Each became a case
in a measure before the fix stood.

**Tried and rejected.** Nothing at this level.

**Due next**, in order:
1. Builders' open decisions become rules with cases (about 4 runs).
2. Audit the planted enforcers and the judge's own stand (about 2 runs).
3. Both need budget: all 24 runs are spent.

# Record of the root

**State.** Round 1 asked and answered ("Ok"; `queue.md`). Every unit has
its document, its measure and its judge. Correct results: 2.

| Unit | Verdict | Stands by |
|---|---|---|
| judge | passes, 4391 | no judge: first of the tree |
| enforcer | passes, 10738 | judge (after its first build stood unjudged) |
| petshop/catalog | passes, 1190 | judge, over 1 alternative |
| petshop/stock, customers, sales | not built | |
| petshop | not built | |

**The number** (`./verdict`): 13 items ÷ 2 correct results = 6.50; it was
10.00 at the first result. The verdict passes: Q11 to Q13 are answered
and nothing waits.

**Spend** (`ledger.tsv`): 8 of 16 runs; about 1 h of 4. Attention after
round 1: 3 items for 2 results, budget 2 per result. Effects without undo: 0.

**Error of what the root gave.**
- Judge, source: the audit cases of the judged unit (`petshop/audit/`).
  Wrong stands: 0 of 1 audited (catalog passes all 123 audit cases). The
  enforcer's stand has no audit: unknown. Wrong refusals: unknown, the
  judge has refused nothing yet.
- Enforcer: unknown. Pet shop measure: unknown until the shop is built.
- Root's own measure: unmeasured (`root.md`, principle 6).

**Limits.**
- One session coordinated everything: it gave the declarations of every
  unit and built the judge and the enforcer. Measures, the catalog builds
  and the audit came from separate agents that saw only what they were
  given, but all are the same model, started by that session.
- Nothing forces a call to the enforcer; identity of who made a change is
  not checked by anything.
- Earlier stands cannot be undone by revert (judge's record).
- The session's own work is metered in time only (Q3).

**Found and absorbed.** `undo` failed on first use while the enforcer's
verdict passed: the measure gained the case, then the judge let the fix
stand. Gaps the measure writers found in documents became rules there.

**Tried and rejected.** Nothing at this level.

**Due next**, in order:
1. Judge: any stand undoable alone (about 3 runs; needs budget).
2. Build stock, customers, sales, then the shop (8 runs, in budget).
3. Audit cases for those four and a source for the enforcer's error
   (about 5 runs; needs budget).
4. Catalog: the points its builders decided become rules in its document.

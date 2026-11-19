# Record of the root

**State.** Every unit is built and standing. Correct results: 8. The
enforcer's full run over the tree, web included, reports no breach.

| Unit | Verdict | Stands by |
|---|---|---|
| judge | passes, 4429 | itself as installer, the enforcer's run as judge |
| enforcer | passes, 10818 | judge |
| petshop | passes, 2824 | judge, over 1 alternative |
| petshop/catalog | passes, 1190 | judge, over 1 alternative |
| petshop/stock | passes, 862 | judge, over 1 alternative |
| petshop/customers | passes, 753 | judge, over 1 alternative |
| petshop/sales | passes, 1890 | judge, over 1 alternative |
| petshop/web | passes, 0.028550 | judge, over 1 alternative |

**The number** (`./verdict`): 22 items ÷ 8 correct results = 2.75. Pages
the person asks for are not items (Q18). Q23 and Q24 are answered and
nothing waits, but the verdict fails: the number was 1.86 at the previous
result, and the new goal took 7 items (5 decisions, 2 notices) for one
result. Attention per result rose. The next result is compared with
2.75, so it passes if it costs fewer than 3 items.

**Spend** (`ledger.tsv`): 30 of 36 runs; about 4 h of 8 h, waiting and one
usage-limit pause included. Attention after round 1: 12 items for 8
results (budget 2 per result). Effects without undo: 0.

**Error of what the root gave.**
- Judge, source: the audits of the judged units. Wrong stands: 0 of 7
  audited (the six pet shop units and the enforcer pass every audit case).
  The judge's own stand has no audit: unknown. Wrong refusals: unknown.
- Pet shop measure, source `audit/petshop/check` (130 scenarios). Wrong
  passes: 0 of 2 builds. Wrong fails: 0 of 25 planted audited; the 4
  planted since are not audited.
- Enforcer measure, source `audit/enforcer/check` (104 cases). Wrong
  passes: 0 of 1 build. Wrong fails: not counted.
- Root's own measure: unmeasured (`root.md`, principle 6).

**Limits.**
- One session coordinated everything: it gave the declarations of every
  unit and built the judge and the enforcer. Measures, builds and audits
  came from separate agents that saw only what they were given, but all
  are the same model, started by that session.
- "Professional" is measured only by the checks of `petshop/web/pages.md`;
  between two builds that pass them the judge takes the smaller file.
- A change to the judge is installed by the candidate itself.
- Nothing forces a call to the enforcer; who made a change is not checked.
- Stands made before the judge kept one file per unit cannot be undone by
  reverting them alone.
- The session's own work is metered in time only (Q3).

**Found and absorbed.** The enforcer's `undo` failed while its verdict
passed; the judge's single stands file blocked undo; requested pages made
the verdict fail (Q18). Each became a case in a measure before the fix.

**Tried and rejected.** Nothing at this level.

**Due next**, in order:
1. Builders' open decisions become rules with cases (about 5 runs).
2. A browser audit for web; audits of the planted enforcers and of the
   judge's own stand (about 3 runs). 6 runs remain.

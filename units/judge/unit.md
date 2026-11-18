# Judge

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — A change to a unit stands only when it is allowed and measured better than what exists; no person checks a delivery.
2. **Interface** — Offers `decide <base> <head> <unit> --tools <tree> --work <dir>`: one JSON decision (`stands`, `kind`, `reason`, the verdict before and after); *build* and *verdict* through [`tree`](../cycle/unit.md). Receives the tree before and after as plain directories, and the tree whose enforcer to use.
3. **Rules** — The principles, and how it decides, below.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the root's queue (`units/queue.md`). Time: a decision within 30 minutes. Context: this document within 80 lines. Cost: nothing outside the repository.
5. **Measure** — [`measures/judge/check`](../../measures/judge/check), written by the root before this unit: pairs of trees whose right decision is known, the wrong ones planted. Number: cases right.
6. **Judge** — [`second-judge`](../second-judge/unit.md).

## How it decides

1. It asks the [enforcer](../enforcer/unit.md) of `--tools`. Blocked: the change does not stand.
2. A change that is only a *giving* (declarations or measures for a child), a *record* or a *decision* of the person stands once allowed: the enforcer has proven the measure, and there is no number to compare.
3. A change to the unit's own work is measured twice with the measure of `<base>`: before and after. It stands only if the verdict passes after, and either it failed before, or the number is higher, or the number is equal and the unit holds fewer bytes.
4. It never judges the unit `judge`.

## The principles here

| Principle | At the judge |
|---|---|
| 1 Boundary | It sees a unit only through that unit's measure and the enforcer's answer; it reads no work to form an opinion. |
| 2 Single source | The rule of decision lives here; the rules of what is allowed live in the enforcer and are cited. |
| 3 External enforcement | The cycle runs the judge of the last recorded state. The measure used is the one of `<base>`, which the change could not alter. |
| 4 Rehearsal before effect | It runs only inside the cycle's rehearsal place and has no effect of its own. |
| 5 Return | It keeps no state; it tells the cycle, which returns a rejected change and records it. |
| 6 Selection | This principle is its purpose. Limit: it compares with what exists, not yet with alternatives made without sight of the change; no budget pays for them while one agent does all the work. |
| 7 Escalation | What it cannot decide — whether the measure itself serves the purpose — it does not guess: a result that passed and is wrong is marked by `tree wrong` and becomes a case given by the unit's parent. Limit: independent by what it can alter, not by who created it; one agent created every unit here. |

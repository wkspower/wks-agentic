# Cycle

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — One way for a change to enter the record: rehearsed, judged, then either recorded with its decision or returned with nothing lost.
2. **Interface** — Offers, as `./tree <command>` from inside the repository, the same for person, agent and automation: `build <unit>`, `verdict <unit>`, `prove <unit>`, `decide <unit> -m <summary> [--decision Qn] [--attempt N]`, `wrong <n> <case>`, `list`. Receives the working tree (the change), the last commit (what exists) and the unit's document (which names its judge).
3. **Rules** — The principles, and the steps below.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the root's queue (`units/queue.md`). Time: a decision within 40 minutes. Context: this document within 80 lines. Cost: nothing outside the repository.
5. **Measure** — [`measures/cycle/check`](../../measures/cycle/check), written by the root before this unit: it drives the cycle in a scratch repository and looks at what is left. Number: cases right.
6. **Judge** — [`judge`](../judge/unit.md).

## The steps of `decide`

1. Copy the last commit to `.rehearsal/cycle/base` and the working tree to `.rehearsal/cycle/head`. `.rehearsal/` is ignored by git: nothing leaves it.
2. Run the judge named in the unit's document, taking judge, enforcer and measure from `base`.
3. Stands: append the decision to [`ledger.jsonl`](../../ledger.jsonl) and commit the change with `Unit:` and `Ledger:` lines.
4. Does not stand, or the attempt is above 3: save the change as `rejected/<n>-<unit>.patch`, restore the working tree to the last commit, append the decision to the ledger and commit only those two. The failure is then work for the unit, which notes it in its `record.md`.

The ledger is where a giver sees the error of what it gave. Wrong passes of a unit's measure: its lines later marked by `wrong`. Wrong fails: its patches in `rejected/` that stood unchanged once the measure was corrected. Both come from cases noticed outside the measure.

## The principles here

| Principle | At the cycle |
|---|---|
| 1 Boundary | A unit's parent reads the ledger line and the verdict, never the patch. The cycle passes directories to the judge as data. |
| 2 Single source | The decision of every change lives in the ledger; commits cite the line. The steps live here. |
| 3 External enforcement | Judge, enforcer and measure are taken from the last commit, which the change cannot alter. Limit: the cycle is a program one agent can bypass or rewrite outside itself; see the enforcer's limit. |
| 4 Rehearsal before effect | The rehearsal place is `.rehearsal/cycle/`. Verdicts and proofs run there before anything is committed. |
| 5 Return | Step 4, proven by the measure: after a failing change the working tree equals the last commit and the attempt is kept as a patch. A commit is undone by `git revert`. Nothing here is destroyed. |
| 6 Selection | A change to `cycle` stands only by the judge. |
| 7 Escalation | A unit with no judge in the last commit gets no decision; that gap is asked in the parent's queue. The cycle itself asks nothing. |

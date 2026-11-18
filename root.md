# Root

Parent: the person. Governed by [`principles.md`](principles.md).

## The six declarations

1. **Purpose** — Autonomous development that respects what people are needed for and how little attention they have: spend the least human attention per correct result, and keep lowering it.
2. **Interface** — Receives from the person its declarations and their decisions. Offers the person *build*, *verdict*, the number of the measure and the queue of principle 7.
3. **Rules** — The principles; none added.
4. **Budget** — The person's attention first, and every other kind `principles.md` lists. Values, given in round 1 of [`queue.md`](queue.md) (Q2 to Q8): cost 16 agent runs; time 4 h; context 8 KB per unit; attempts 2 per change; alternatives 1 per change; attention 2 items per correct result after round 1; cap on effects without undo 0.
5. **Measure** — The person's attention per correct result, as a trend (principle 7). Executable check, given in Q1 of [`queue.md`](queue.md): the number is items in that queue ÷ correct results. An item is one heading there (decision, proposal or notice; round 1 counts as its items). A correct result is a unit whose verdict passes and whose last change its judge let stand. `./verdict` passes when there is at least one correct result, the number is no higher than at the previous correct result, and no more items are waiting than there were then.
6. **Judge** — The person, for changes to this document and to `principles.md`. Every delivery has its judge below.

Until the budget values and the executable check exist, the root causes no
effect; they are the first thing the person is asked, in the one round of
principle 7, together with everything else the root can foresee needing. The
root writes the person's answers into this document word for word, in a
change that holds nothing else; the person judges that change by reading it.

## The principles here

| Principle | At the root |
|---|---|
| 1 Boundary | The person acts on the tree only through this interface, and reads the measure and the queue, never the work. |
| 2 Single source | The principles live in `principles.md`; the tree's purpose, budget and measure live here. |
| 3 External enforcement | Limit: the chain ends here. Nothing enforces these two documents on the person. |
| 4 Rehearsal before effect | A change to either document runs first in one branch; while none exists, the first effect is the smallest principle 5 can undo, and is recorded. |
| 5 Return | Either document is restored from its history, proven by doing it; units that acted under the changed text return to their last passing state. |
| 6 Selection | A change to either document stands only when the verdict passes and it was compared with what exists and with alternatives made without sight of it. Limit: the person also makes these changes, so the judge is not independent here and its error is unmeasured; the measure above is the only check. |
| 7 Escalation | The root asks the person all and only what no judge decides, and an effect without undo above the cap. Below the root no person is asked. |

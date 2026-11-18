# Root

Parent: the person. Governed by [`principles.md`](principles.md).

## The six declarations

1. **Purpose** — Autonomous development that respects what people are needed for and how little attention they have: spend the least human attention per correct result, and keep lowering it.
2. **Interface** — Receives from the person its declarations and their decisions. Offers the person *build*, *verdict*, the number of the measure and the queue of principle 7.
3. **Rules** — The principles; none added.
4. **Budget** — The person's attention, and these values (given 2026-11-18, [`queue.md`](queue.md) Q1; read from this table by the check and the judge):

   | Value | |
   |---|---|
   | `open_items_max` | 3 |
   | `first_batch_items` | 3 |
   | `correct_results_per_item` | 5 |
   | `effects_without_undo` | 0 |
   | `attempts_per_change` | 3 |
   | `window_results` | 10 |

   `window_results` is the size of the window of the measure; the person gave no number, the writer of the check chose it.
   Everything stays in the repository: no push, deploy, spending or real customer data.
5. **Measure** — The person's attention per correct result, as a trend (principle 7): queue items and waiting time, divided by changes that passed their verdict and that their judge let stand; it passes when the latest window is no worse than the one before and the budget is respected ([`queue.md`](queue.md) Q2). Executable check: [`measure/check.py`](measure/check.py), proven by [`measure/prove.py`](measure/prove.py). Limit: one agent wrote the check and builds the tree; its independence is only the person's definition.
6. **Judge** — The person, for changes to this document and to `principles.md`. Every delivery has its judge below.

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

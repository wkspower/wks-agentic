# Root

Parent: the person. Governed by [`principles.md`](principles.md). Record:
[`record/root.log.md`](record/root.log.md).

## The six declarations

1. **Purpose** — Autonomous development that respects what people are needed for and how little attention they have: spend the least human attention per correct result, and keep lowering it.
2. **Interface** — Receives from the person its declarations and their decisions. Offers the person *build*, *verdict*, the number of the measure and the queue of principle 7, kept in [`queue.md`](queue.md).
3. **Rules** — The principles; none added.
4. **Budget** — Attention: at most 5 queue items per week, each decidable in at most 5 minutes; exceeding it is a design defect. Cost: USD 100 per month of compute, an amount the person accepts losing entirely. Time: no deadline; the trend is reviewed monthly. Attempts: 3 failed attempts per change, then it returns to the last passing state and becomes work. Cap on effects without undo: zero; anything irreversible is asked first. Context: not given.
5. **Measure** — The person's attention per correct result, as a trend (principle 7). Executable check: [`measures/root/`](measures/root/), written by an agent independent of the builder and without sight of its work, accepted or rejected once by the person, who owns it.
6. **Judge** — The person, for changes to this document, to `principles.md` and to the check in `measures/root/`. Every delivery has its judge below.

Until the check in `measures/root/` exists and the person has accepted it, the
root causes no effect.

Children: [`units/pet-shop`](units/pet-shop/unit.md), a demonstration system
(the person's decision Q4 in the record: built and tested, never deployed, no
real customers, payments or personal data), and [`units/judge`](units/judge/unit.md),
the judge of every delivery below.

## The principles here

| Principle | At the root |
|---|---|
| 1 Boundary | The person acts on the tree only through this interface, and reads the measure and the queue, never the work. |
| 2 Single source | The principles live in `principles.md`; the tree's purpose, budget and measure live here; the root's decisions and state live in its record. |
| 3 External enforcement | Limit: the chain ends here. Nothing enforces these two documents on the person. Limit: protection of the default branch `develop` (required status checks) and the person's ownership of measure and judge files (`CODEOWNERS`) are not in place; the agent's tools cannot set them, whatever the access. The item is in `queue.md`. |
| 4 Rehearsal before effect | Work is committed to the branch `claude/dreamy-cori-h2njwl`, which is the unit's own record and not an effect. It reaches `develop` or any other branch only with the person's approval. |
| 5 Return | A commit on the working branch is undone by `git revert`. Either document is restored from its history, proven by doing it; units that acted under the changed text return to their last passing state. |
| 6 Selection | A change to either document stands only when the verdict passes and it was compared with what exists and with alternatives made without sight of it. Limit: the person also makes these changes, so the judge is not independent here and its error is unmeasured; the measure above is the only check. |
| 7 Escalation | The root asks the person all and only what no judge decides, and an effect without undo above the cap. Its one queue is [`queue.md`](queue.md). Below the root no person is asked. |

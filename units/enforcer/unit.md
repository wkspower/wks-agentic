# Enforcer

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — No change enters the record that breaks a rule: every rule below is checked by something the changed unit could not alter.
2. **Interface** — Offers `enforce change <base> <head> <unit>` (allowed or the violations, and the kind of change) and `enforce prove <tree> <unit>` (the planted results of a measure fail it, its controls pass); *build* and *verdict* through [`tree`](../cycle/unit.md). Receives two plain directories and a unit name; they are data.
3. **Rules** — The principles, and the six rules below, which are how it meets them.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the root's queue (`units/queue.md`). Time: a verdict within 10 minutes. Context: this document within 80 lines. Cost: nothing outside the repository.
5. **Measure** — [`measures/enforcer/check`](../../measures/enforcer/check), written by the root before this unit: each rule has a planted violation that must be blocked and a legitimate change beside it that must pass. Number: cases right.
6. **Judge** — [`judge`](../judge/unit.md).

## The rules it enforces

A change is the difference between two trees, made in the name of one unit.

- **E1 Boundary.** A unit changes only what is inside it: `units/<unit>/`, minus its `unit.md` and minus its sub-units. It may write its own `record.md`, its own `queue.md` and its parent's `queue.md`.
- **E2 Given by the parent.** `units/<child>/unit.md` and `measures/<child>/` change only in the name of the child's parent. `measures/` files outside any unit belong to the root.
- **E3 Measure first.** A unit's work changes only if its measure already existed before the change; a measure or declaration never changes together with the work it governs.
- **E4 Proof.** Every change to a measure is proven: each directory in `measures/<unit>/plants/` laid over the tree must fail the check, each in `controls/` must pass, and there is at least one plant.
- **E5 Declarations.** A unit document states `Parent:`, the six declarations with no value missing, the seven principles, in at most 80 lines. A unit whose document fails this changes nothing.
- **E6 The person's and the cycle's.** `principles.md`, `root.md` and `measures/root/` change only in the root's name under a decision answered in [`queue.md`](../../queue.md). `ledger.jsonl` and `rejected/` are never part of a change.

## The principles here

| Principle | At the enforcer |
|---|---|
| 1 Boundary | It reads two directories and answers; it writes only under the work directory it is given. E1 is this principle as a check. |
| 2 Single source | The rules E1–E6 live here; `enforce` implements them and other documents cite them. |
| 3 External enforcement | The cycle runs the enforcer of the last recorded state, never the one inside the change. Its own planted violations are its measure, run at every change to it. Limit: nothing forces a change through the cycle, and one agent can write every file; a commit without a `Ledger:` line shows the bypass, but does not block it. |
| 4 Rehearsal before effect | It runs only inside the cycle's rehearsal place and has no effect of its own. |
| 5 Return | It keeps no state, so there is nothing to undo; a blocked change is returned by the cycle. |
| 6 Selection | A change to `enforce` stands only by the judge, on the number of the measure, or the same number for fewer bytes. |
| 7 Escalation | A rule it cannot decide (a path no rule covers) is blocked and becomes an item in the root's queue; none is open. Limit: it sees only the tree it is given, so an effect outside the repository is invisible to it. |

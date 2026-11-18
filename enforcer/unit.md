# Enforcer

Parent: [`root`](../root.md). Governed by [`principles.md`](../principles.md).

## The six declarations

1. **Purpose** — Block what breaks a rule, so that rules hold without anyone reading the work.
2. **Interface** — Receives `enforcer/enforce [<tree-dir>]` (default: the repository). Offers exit 0 when no rule below is broken, else exit 1 with one line per breach, `<rule-id> <unit> <what>`. Offers `enforcer/undo <commit> [<tree-dir>]` (default: the repository of the current directory): in a clone outside the tree it reverts the commit on top of the tree's HEAD; exit 0 with one line starting `undo proven` when the revert applies and every path the commit touched is again as it was before the commit, else exit 1; the tree's repository is left untouched. Offers *build* (`enforcer/build`) and *verdict* (`enforcer/verdict`).
3. **Rules** — The root's, plus the rules it enforces on every unit (a directory holding `unit.md`, and the root with `root.md`); the exact meaning of each is in [`rules.md`](rules.md):
   - `doc`: the document names its parent, has the six declarations in order and a row for each of the seven principles.
   - `budget`: the budget line gives all seven kinds; children's cost and time sum to no more than the parent's; no other kind is looser than the parent's.
   - `context`: `unit.md` plus `record.md` is no more than the unit's context budget.
   - `interface`: `build` and `verdict` exist and are executable.
   - `measure`: `measure/check` exists with at least one build under `measure/planted/`, and every planted build fails the check.
   - `before`: where `src` exists, the measure entered the record in an earlier change than `src`.
   - `stands`: where `src` exists, its hash is the last one the judge's file for the unit holds (`judge/stands/<unit path>.tsv`), or the unit's record says it stood unjudged.
   - `answer`: a change that touches `principles.md` or `root.md` touches nothing else but `queue.md`.
   - `spend`: runs charged to a unit in `ledger.tsv` do not exceed its cost budget.
4. **Budget** — cost 2 runs; time 0.5 h; context 8 KB; attempts 2; alternatives 0; attention 0; no-undo cap 0.
5. **Measure** — `enforcer/measure/check <build-dir>`: fixture trees, one clean and one planted violation per rule, which the build must pass and block; number: bytes of the build. Written before the enforcer by an agent that did not build it; planted wrong enforcers in `enforcer/measure/planted/` must each fail. Error (seen by the root, in [`record.md`](../record.md)): wrong blocks and wrong passes, counted from audit trees written from this document and `rules.md` alone, kept in `audit/enforcer/`.
6. **Judge** — The [`judge`](../judge/unit.md), for every change after the first. The first build stood unjudged; recorded in [`record.md`](record.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | Reads the record; writes nothing in it. Its only output is the exit code and the lines of breaches. |
| 2 Single source | The rules enforced on units are listed only here; unit documents cite them. |
| 3 External enforcement | Each rule above has a planted violation in its measure, rerun at every change to the rule or to the enforcer. Limit: it runs when called (by `./build` and before each change); nothing in this repository forces the call. |
| 4 Rehearsal before effect | It causes no effect. `undo` works in a clone outside the record. |
| 5 Return | Nothing to undo. It supplies the proof of undo for others. |
| 6 Selection | A change stands only through the judge, by this measure. Limit: alternatives 0. |
| 7 Escalation | Asks nothing; a breach is reported to whoever called it, and becomes work for the unit named. |

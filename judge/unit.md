# Judge

Parent: [`root`](../root.md). Governed by [`principles.md`](../principles.md).

## The six declarations

1. **Purpose** — Decide whether a change to a unit stands, by that unit's own measure, so that no person checks a delivery.
2. **Interface** — Receives `judge/judge <unit-dir> <candidate-dir> [<alternative-dir> ...]`: builds offered for the unit, the first being the change, the others made without sight of it. Offers: exit 0 when a build stands, having installed it as `<unit-dir>/src` and appended one line to `judge/stands.tsv` at the tree's root (tab-separated: UTC time as `YYYY-MM-DDTHH:MMZ`; unit path from the tree's root; `candidate` or `alternative-N`; number; hash of `src`; the numbers compared). The tree's root is the nearest directory above the unit that holds `root.md`. The hash is the sha256, in hex, of path, NUL, bytes, NUL for each file under `src`, sorted by relative path as a string, `__pycache__` left out; exit 1 when nothing stands, having changed nothing. Offers *build* (`judge/build`) and *verdict* (`judge/verdict`).
3. **Rules** — The root's, plus: (a) a build is judged only by `<unit-dir>/measure/check` as it stands in the record, run on a copy; (b) a build stands only if its check passes and its number is lower than that of the existing `src` (when that passes) and no higher than any other offered build's; among equals the candidate comes first, then alternatives in order; (c) fewer alternatives offered than the unit's budget states: nothing stands; (d) in every measure of this tree a check passes by exit 0 with its number as the last line of stdout, and lower is better.
4. **Budget** — cost 0 runs; time 0.5 h; context 8 KB; attempts 2; alternatives 0; attention 0; no-undo cap 0.
5. **Measure** — `judge/measure/check <build-dir>`: cases that drive a judge against fixture units; number: bytes of the build. Written before the judge by an agent that did not build it; planted wrong judges in `judge/measure/planted/` must each fail. Error (seen by the root, in [`record.md`](../record.md)): wrong stands and wrong refusals, counted from the audit cases of the judged unit, which the judge never reads.
6. **Judge** — The [`enforcer`](../enforcer/unit.md), for every change after the first. The first build stood unjudged (how the tree grows); that is recorded in [`record.md`](record.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | Sees a unit's measure, its `src` and the offered builds; never how they were made. Acts only by installing `src` and writing `stands.tsv`. |
| 2 Single source | What stands lives only in `stands.tsv`; the root's measure reads it there. |
| 3 External enforcement | Its rules are enforced by its measure and by the enforcer, neither of which it can alter. Limit: all files share one repository, so "cannot alter" rests on the enforcer checking each change, not on access control. |
| 4 Rehearsal before effect | Every check runs on copies in a temporary directory; only the build that stands is installed. |
| 5 Return | An installation is one change to the record, undone by reverting it (`enforcer/undo`). Refusing changes nothing. |
| 6 Selection | A change to the judge stands only by rule (b) applied by the enforcer with this measure. Limit: alternatives 0, so it is compared only with what exists. |
| 7 Escalation | Asks nothing: what it cannot decide (no measure, too few alternatives) is a refusal, and the refused unit asks its own parent. |

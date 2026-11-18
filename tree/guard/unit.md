# Guard

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — Enforce on every change the rules a unit cannot be trusted to keep by itself, so that the judge compares only changes that kept them.
2. **Interface** — Receives the name of a unit with an uncommitted change. Offers *build*, *verdict* (`python3 measure/check.py .`), `guard.py check UNIT` (allowed or blocked, with reasons and what it measured) and `guard.py judge-the-judge`.
3. **Rules** — The parent's. Added, each with its planted violation in the measure: (a) a change touches one unit, and either its work or what its parent gives (document, measure), never both; (b) a unit has a document of at most 80 lines with a parent, the six declarations with values and the seven principles; (c) a measure has at least one planted wrong result and every one fails it, at every change; (d) work is Python that imports no network module and, outside judge and guard, starts no program.
4. **Budget** — The values of [root](../../root.md) declaration 4. Effects: none; it only answers.
5. **Measure** — [`measure/check.py`](measure/check.py): one planted violation per rule in a throwaway repository, each must be blocked, and two controls must be allowed; number = scenarios passed. Planted: a guard that allows everything.
6. **Judge** — The [judge](../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | It reads the list of changed paths, the unit's document, measure and work; it changes nothing. |
| 2 Single source | The rules it adds live in declaration 3 above; the checks are in `work/guard.py`. |
| 3 External enforcement | It is the enforcer of the tree; the judge enforces it in turn. Limit: rule (d) reads the text of the work, which proves the absence of the listed imports, not of every way out; and nothing outside the repository runs the guard. |
| 4 Rehearsal before effect | Its measure runs in a throwaway repository under `.rehearsal/`; the guard itself has no effect to rehearse. |
| 5 Return | It has no effect of its own; a change to it is one commit, undone by the judge's `--undo`. |
| 6 Selection | A change to it stands by the judge, compared by this measure with what exists. |
| 7 Escalation | It asks nothing. What it blocks goes back to the unit as a refusal with reasons. |

Limit (queue.md Q2, absorbed): one agent wrote this measure and this unit. The
first version stood with no judge, since none existed: recorded in `state.md`.

# Judge

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — Decide whether a change to a unit of the tree stands, so that no person has to check a delivery.
2. **Interface** — Receives the name of a unit with an uncommitted change. Offers *build* (`work/judge.py` written from the measure), *verdict* (`python3 measure/check.py .`), and to every unit: `judge.py UNIT`, `--undo ID`, `--revoke ID`. Its decisions are the lines of [`record/ledger.jsonl`](../../record/ledger.jsonl).
3. **Rules** — The parent's. Added: a change stands only if it is strictly better (more scenarios passed, or as many with fewer lines of work); only changes to work with a passing verdict are written as results.
4. **Budget** — The values of [root](../../root.md) declaration 4, read from there. Effects: commits on the current branch of this repository, nothing else.
5. **Measure** — [`measure/check.py`](measure/check.py): changes given to a toy unit in a throwaway repository; number = scenarios passed. Planted: a judge that accepts everything.
6. **Judge** — The [guard](../guard/unit.md) (`guard.py judge-the-judge`), which applies the judging procedure standing in history, not the changed one.

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | It reads a unit's change, runs its measure and writes the ledger; it never edits a unit's work. Units see only its answer. |
| 2 Single source | The judging procedure lives in `work/judge.py`; the budget is read from root.md; the rules it relies on are the guard's. |
| 3 External enforcement | Its own rules are enforced by the guard, which it cannot alter (a change touching both is blocked). Limit: nothing outside this repository runs the judge; a commit made around it is not prevented, only absent from the ledger and so never a result. |
| 4 Rehearsal before effect | Candidate and existing state are copied to `.rehearsal/` (ignored by git) and measured there; only then is anything committed. |
| 5 Return | Every standing change is one commit, undone by `--undo`, proven by doing it in the measure. After the attempts of the budget the unit's files are restored from the last standing commit. |
| 6 Selection | Compares candidate and existing by the same measure. Limit: no alternatives made without sight of the change; with one agent the budget does not pay them. |
| 7 Escalation | It asks nothing. A change touching the judge and the guard together has no judge and goes to the root's queue. |

Limit (queue.md Q2, absorbed): one agent wrote this measure and this unit. The
first version stood with no judge, since none existed: recorded in `state.md`.

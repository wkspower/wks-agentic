# Rules the enforcer enforces: exact meaning

Cited by [`unit.md`](unit.md), declaration 3. The tree is the directory given to `enforce`.

- **Units.** The tree's root (holds `root.md`; its document is `root.md`; its name in the ledger and in breach lines is `root`) and every directory below it holding `unit.md`, except anything under a path component named `measure`, `audit`, `src`, or starting with `.`. A unit's name is its path from the root. Its parent is the nearest unit directory above it (the root for top-level ones).
- **`doc`.** The document has a line starting `Parent:`; lines starting `1. **Purpose**`, `2. **Interface**`, `3. **Rules**`, `4. **Budget**`, `5. **Measure**`, `6. **Judge**`, in that order; and table rows starting `| 1 Boundary`, `| 2 Single source`, `| 3 External enforcement`, `| 4 Rehearsal before effect`, `| 5 Return`, `| 6 Selection`, `| 7 Escalation`.
- **`budget`.** On the line starting `4. **Budget**`, read by regular expression: `cost (\d+)`, `time ([\d.]+) h`, `context (\d+) KB`, `attempts (\d+)`, `alternatives (\d+)`, `attention (\d+)`, `cap\D*(\d+)`. All seven must be present. For each unit, its direct children's cost sums to no more than its cost, and their time to no more than its time; each child's context, attempts, alternatives, attention and cap is no more than its parent's.
- **`context`.** Bytes of the unit's document plus bytes of `record.md` beside it (if present) are no more than context KB × 1024.
- **`interface`.** `build` and `verdict` exist in the unit's directory and are executable.
- **`measure`.** `measure/check` exists and is executable; `measure/planted/` has at least one entry; `check <entry>` exits non-zero for every entry.
- **`before`.** Where `<unit>/src` exists (never for the root): the first commit reachable from HEAD that added a file under `<unit>/measure/` is a strict ancestor of the first that added a file under `<unit>/src/`. Committed measure with uncommitted src is no breach; src with no committed measure is.
- **`stands`.** Where `<unit>/src` exists: its hash equals the fifth tab-separated field of the last line of `judge/stands/<unit name>.tsv`, or `<unit>/record.md` has the line `stood unjudged: <that hash>`. The hash is defined in [`judge/unit.md`](../judge/unit.md).
- **`answer`.** Every commit reachable from HEAD that touches `principles.md` or `root.md` at the root touches no path other than those two and `queue.md`.
- **`spend`.** `ledger.tsv` at the root (absent: nothing spent) has tab-separated `time`, `unit`, `runs` (integer), `note`; lines starting `#` and blank lines are ignored. For every unit, the runs charged to it and to every unit beneath it (for the root: all rows) are no more than its cost.

A breach is one stdout line `<rule-id> <unit name> <what>`. The enforcer writes nothing in the tree.

# Judge

Parent: [root](../root.md). Governed by [`principles.md`](../principles.md).
This document is the single source of how a unit is laid out and how a change
to any unit comes to stand; the other units cite it.

## The six declarations

1. **Purpose** — Decide, with no person and without the maker, whether a change to a unit stands, so that the person is asked only what no judge decides.
2. **Interface** — Offers [`work/tree`](work/tree): `build`, `verdict`, `prove`, `lint`, `judge`, `status`, `units`, the same for person, agent and automation. Receives a unit's path and candidate branches made from the trunk. Offers nothing else and reads no work except through a unit's measure.
3. **Rules** — The principles, plus the rules of "How a change stands" below, which it adds to meet principles 3 to 7.
4. **Budget** — Cost: none. Time: 300 s per build or verdict, then fail. Context: this document and `work/tree`. Attempts: 3. Attention: one open item in `root/queue.md`. Effects without undo: zero; it writes only merge commits and its own records on the trunk, and copies under `.rehearsal/`.
5. **Measure** — [`measure/check`](measure/check): planted changes in a toy tree, each with the decision it must get; the number is the cases passed. Proven by two planted wrong judges in `measure/plants/`.
6. **Judge** — The judge as it stands on the trunk, which a candidate cannot alter, run by a session that did not make the change. Limit: that earlier judge was made by this same unit, so the independence is of version, not of origin.

## Layout of every unit

| Path | What | Who alters it |
|---|---|---|
| `<unit>/unit.md` | its six declarations and seven principles | its parent |
| `<unit>/measure/check`, `plants/` | the measure and the planted wrong results | its parent |
| `<unit>/work/` | what it builds; `run`, and `build` if it needs building | the unit |
| `<unit>/record.md` | state of the work, what was tried and rejected | the unit |
| `<unit>/queue.md` | the one queue where its children's items wait | the unit and its children |
| `<unit>/judged.md`, `results.md` | every decision; the ledger of correct results | the judge only |

The root's own files are `root.md`, `root/measure/`, `state.md`, `root/queue.md`
and `queue.md` (the person's queue). The trunk is the branch the record lives on.

## How a change stands

1. `judge/work/tree status` says what is due; a session takes one unit and reads its document, its ancestors' and its record, nothing else.
2. The change is made on a branch from the trunk, touching only what the table lets the unit alter. Alternatives are made on separate branches by sessions that do not see each other.
3. On the trunk, a session that made none of them runs `tree judge <unit> <branch>...`. The judge copies each candidate to `.rehearsal/`, and there: refuses any path the unit cannot alter; requires the unit's verdict to pass and its number to be higher than the trunk's, or equal with smaller work; requires every ancestor that passed to still pass; requires every measure the change gives to fail all its plants and to lose none.
4. The best candidate is merged; a change that raised the number is written to `results.md`. A new case that fails standing work strikes that work's result. Otherwise the trunk is untouched, the reason goes to `judged.md` and the branch is kept.
5. After 3 rejections in a row the unit is stopped and an item waits in its parent's queue; it is judged again when the item is answered.

## The principles here

| Principle | At the judge |
|---|---|
| 1 Boundary | It sees a unit only through `verdict`, `prove` and the list of paths changed. |
| 2 Single source | Layout and procedure live here; ownership of paths lives in `kind()` of `work/tree`, generated from nothing else. |
| 3 External enforcement | It is the enforcer of every other unit; each rule in step 3 has a planted violation in its measure. Limit: nothing in one repository stops a session from committing to the trunk without the judge; `tree status` lists such commits, and only the person can act on them. |
| 4 Rehearsal before effect | `.rehearsal/`, ignored by the record: candidates are built and measured there, and the judge's own measure runs in a scratch repository inside it. |
| 5 Return | The trunk moves only by the judge's merge, so the last passing state is the trunk; undo is `git revert -m 1` of the merge, proven in the measure. A rejected branch is kept, never deleted. |
| 6 Selection | Steps 3 and 4. Limit: a change is "better" only by number, then size; what the number misses must become a case. |
| 7 Escalation | Step 5, and nothing else: it never asks whether a delivery is right. |

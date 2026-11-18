# Record of the judge

**State.** Built; verdict passes (41 cases, number 4391). In use.

**How it stood.** The first build stood with no judge, as the first effect
of principle 4 (how the tree grows): its measure and 25 planted wrong judges
entered the record first, and every planted judge fails. From now on the
enforcer judges changes to it.

stood unjudged: b3c5eb84a82a6185c48c31a3ad811c83c4e2d88b7284489a440d4256d7045282

**Limits.**
- The coordinating session built it, and the same session gave it its
  declarations. The measure was written by a separate agent that never saw
  the build; the build was written before its maker saw the measure.
- Error: see the root's [`record.md`](../record.md).

**Round before first effect.** Nothing asked of the root.

**Defect found.** Every stand is a line in one file, so once a later line
follows, reverting an earlier installation no longer applies:
`enforcer/undo e2d0575` (catalog) was proven when made and fails since the
enforcer's stand. Principle 5 is met only for the latest stand. That is a
limit until fixed.

**Tried and rejected.** Nothing yet.

**Due next.** Keep what stands so that any stand can be undone alone (one
file per unit, or an undo that appends). It changes this unit's interface,
its measure, and the readers of `stands.tsv` (root's measure, enforcer):
about 3 runs, which the judge's budget (0) does not hold.

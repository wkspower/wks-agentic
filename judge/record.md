# Record of the judge

**State.** Built and standing; verdict passes (43 cases, number 4429). In use.

**How it stood.** The first build stood with no judge, as the first effect
of principle 4 (how the tree grows): its measure and 25 planted wrong judges
entered the record first, and every planted judge fails. From now on the
enforcer judges changes to it.

**Limits.**
- The coordinating session built it, and the same session gave it its
  declarations. The measure was written by a separate agent that never saw
  the build; the build was written before its maker saw the measure.
- Error: see the root's [`record.md`](../record.md).

**Round before first effect.** Nothing asked of the root.

**Defect found and fixed.** Every stand was a line in one file, so once a
later line followed, reverting an earlier installation no longer applied
(`enforcer/undo e2d0575`, catalog). Now each unit has its own file under
`judge/stands/`: measure changed first (by an agent that does not build the
judge), the standing judge failed it, the changed judge installed itself
under rule (b) and stands by the enforcer's run, which reported no
breach (declaration 6). The old
lines were moved, unchanged, into the units' files.

**Tried and rejected.** The first build (4391): one shared stands file.

**Due next.** Limit to remove: a change to the judge is installed by the
candidate itself, since nothing else can install; only the enforcer's run
is independent of it.

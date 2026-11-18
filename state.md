# State of the work

The root's record: what whoever arrives needs in order to resume. History is
in git. Start with `judge/work/tree status`; the procedure is in
[`judge/unit.md`](judge/unit.md).

## Now (2026-11-18)

- The person answered items 1 to 3 of [`queue.md`](queue.md); the answers are
  written there and absorbed into `root.md` declarations 4 and 5.
- The tree is built down to the units that can be developed with no person:
  `judge`, and `petshop` with `customers`, `stock`, `appointments`, `sales`,
  `desk`. Each has its document, its measure and its planted wrong results.
- The judge is built and passes its measure (23 cases). No pet shop unit is
  built yet: that is the work due, and it needs nobody's answer.
- Root number: 3 items, 0 correct results. Root verdict: pass (budget kept, no
  complete window yet). The person's queue is empty.

## Next

1. Build `petshop/customers` and `petshop/stock` (they receive nothing), then
   `appointments`, `sales`, `desk`, then `petshop` itself. One session per
   unit, on a branch; another session runs the judge.
2. The first 5 correct results close the first window of the root's measure.

## Effects so far, and how each is undone

All are commits on branch `run-3`, not pushed; nothing left the repository.

- `root.md` declarations 4 and 5 now carry the person's answers, transcribed.
  Read as the person's change made through the interface, rehearsed on this
  branch (root.md, principle 4). Undo: revert commit `0da433b`.
- The bootstrap commit creates the judge and every measure at once. No judge
  existed to judge it, so it is the first effect of principle 4: the smallest
  that can be undone (one commit, reverted whole), recorded here.

## Limits (stated as limits, not as compliance)

- One agent wrote the root's check, the judge and every measure below. None
  of them builds the pet shop units, so "written by someone who does not build
  it" holds for those; it does not hold for the judge, whose measure and work
  have the same author. Its two plants and the person's noticing are the check.
- Nothing in one repository can stop a session from committing to the trunk
  without the judge, or from being both maker and judge. `tree status` lists
  trunk commits the judge did not make.
- The plants of the pet shop measures are coarse (one agrees to everything,
  one does nothing). The measures were also run once against a reference
  written for that purpose and then destroyed without entering the record:
  all cases passed, and of 9 real mutants of it 8 were caught; the ninth
  (product list in the wrong order) became a case in `petshop/stock`. Error
  of these measures seen so far: 1 wrong pass, 0 wrong fails.
- The root's number is "inf" until a first correct result exists.

## Held for the person, not asked: the attention budget has no room

By root.md no item may be asked before 5 correct results. These proceed
under the strictest reading and will be asked when the budget allows.

- Proposal to `principles.md`: say how the first judge of a tree comes to
  stand, since nothing can judge it. Read here as principle 4's first effect.
- Proposal to `root.md`: its budget gives no value for cost, time or context.
  Read here as "attention is the root's whole budget"; the values the units
  below carry (300 s, one document of at most 80 lines, no cost) were given
  by the root to its units and are the strictest that let them work.
- `README.md` still says nothing has been built; it is the person's.

## Tried and rejected

- Building under assumed budget values and asking afterwards: root.md forbids
  any effect before the values and the check exist.
- Asking the pet shop purpose in a later round: one more wait for the same
  items.
- Keeping the reference implementation as a planted case or an example: the
  builders would be handed the work, and alternatives must be made without
  sight of one another.
- One unit for the whole pet shop: its measure could only be passed all at
  once, so nothing could be compared or returned in parts.
- Asking the person which technology to use: they require none, and the
  measures compare whatever is built.

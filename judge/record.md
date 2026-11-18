# Record of the judge

## State

- 2026-11-18. Built at the bootstrap of the tree, before any judge existed to
  judge it; see `state.md`. `measure/check` passes 23 of 23; both plants fail.

## Tried and rejected

- Freezing every unit while the root's verdict fails. Rejected: a worse window
  would then block the changes that could improve it.
- Counting every standing change as a correct result. Rejected: changes that
  only shrink the work, or only give a measure, would inflate the denominator
  of the root's number. A result is a change that raised its unit's number.
- Requiring a parent's verdict to pass when it gives a child a new case.
  Rejected: principle 6 wants the case in the measure before the unit is
  fixed, so the child must be allowed to fail it for a while.

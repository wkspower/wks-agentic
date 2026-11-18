# Record of the pet shop

State, and what was tried and rejected. Declarations: [`unit.md`](unit.md).

- 2026-11-18 — Parts given: customers, appointments, stock, sales, each with
  a measure and a stand-in peer, so each is built and judged alone.
- 2026-11-18 — Customers built (ledger line 5); six near-correct plants then
  added to its measure (line 6), all failing it.
- Next: see "Next" in [`../../state.md`](../../state.md).
- Rejected: one executable for the whole shop with no parts — a failure
  anywhere would return everything, and no part could be judged alone.
- Rejected: parts reading each other's files — it crosses the boundary; they
  ask through `PETSHOP_PEER`.

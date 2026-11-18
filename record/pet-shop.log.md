# Pet shop — record

Record of [`units/pet-shop`](../units/pet-shop/unit.md): state, decisions taken
by the root, and what was tried and rejected. Newest last.

## 2026-11-18

- Declarations given by the root, derived from its purpose and the person's Q4.
- Measures for the unit and its children commissioned from an agent that
  builds nothing here, before any code exists.

## 2026-11-18 — Measures received; first build

- Measures in [`measures/`](../measures/README.md) (catalog 32 cases / 7
  planted, stock 30 / 7, orders 35 / 8, pet-shop 37 / 8), written by an agent
  that saw only the unit documents. Its private reference implementation was
  deleted unread by the builder.
- First build in `src/petshop/`: every measure's number is 1 locally. Not yet
  judged: the judge unit is still being built by another agent.
- Builder's practice: reads `measures/*/test_*.py`, never `measures/*/planted/`
  (each planted case is a near-solution).

## Open work (proposals from the measure writer; decided by this unit's parent, the root, not the person)

1. App state has no reset: declare a factory `make_app()` so each case starts fresh.
2. The pet bound and a bad qty share `ValueError`; declare a distinct exception for the pet bound.
3. "Price fixed at time of order" is untestable through `Catalog`/HTTP: no repricing operation is declared.
4. Whether `place`/`cancel` return copies is undeclared.
5. Error precedence when a call has several faults is undeclared (the build: 400, then 404, then 409).
6. Undeclared: `GET /catalog?kind=<other>` (the build answers 400), extra body fields, `Content-Type`, 404 vs 405.
7. Defect in the declarations: cancelling an order for a pet that was received again since would exceed the pet bound; `cancel` behaviour then is undeclared (the build raises `ValueError` part-way). Highest priority.
8. Planted cases reveal a near-solution to builders; practice above, rule to be added by the judge's owner.

Each becomes: a change to the unit document, then a case added to the measure
by its writer, then the build — in that order.

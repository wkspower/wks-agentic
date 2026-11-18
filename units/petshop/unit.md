# Pet shop

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — A system for the staff of one physical shop: customers and their pets, appointments for bath and grooming, products with stock, and counter sales. It runs locally, with no real payments (decision Q3 in [`queue.md`](../../queue.md)).
2. **Interface** — Offers the executable `units/petshop/run`, speaking the protocol below and routing each operation to the part whose name prefixes it; *build* and *verdict* through [`tree`](../cycle/unit.md). Receives a data directory and, optionally, the day in `PETSHOP_TODAY`.
3. **Rules** — The principles, the rules of the [enforcer](../enforcer/unit.md), and the protocol below, which its parts may tighten.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero; no real customer data, no real use, nothing outside the repository. Attention: one item open in the root's queue (`units/queue.md`). Time: a verdict within 10 minutes. Context: this document within 80 lines. Cost: no spending.
5. **Measure** — [`measures/petshop/check`](../../measures/petshop/check), written by the root before this unit: the verdict of every part, then cases that cross the parts. Number: cases right.
6. **Judge** — [`judge`](../judge/unit.md).

## The protocol

- `run <data-dir>` reads one JSON object from standard input, with `"op": "<part>.<operation>"` and the operation's arguments, and writes one JSON object to standard output: `{"ok": true, …}` or `{"ok": false, "error": "<code>"}`.
- Codes: `invalid` (an argument is missing or impossible), `not_found` (an id the shop does not know), `conflict`, `insufficient`, `unknown_op`. A refused request changes nothing.
- Everything the shop knows is kept inside `<data-dir>`, created if absent; nothing else is written anywhere. Two data directories are two shops.
- Ids are positive integers given by the shop. Money is an integer number of cents. Dates are `YYYY-MM-DD`, times `HH:MM`.
- A part reaches another part only by running the executable named in `PETSHOP_PEER` with the same data directory and this protocol. `run` gives each part itself as that peer.
- Any technology already present on the machine may be used; none is required.

## The parts

[`customers`](customers/unit.md), [`appointments`](appointments/unit.md), [`stock`](stock/unit.md), [`sales`](sales/unit.md). Each is built and judged alone, against a stand-in for its peers.

## The principles here

| Principle | At the pet shop |
|---|---|
| 1 Boundary | The shop sees its parts through their verdicts and `run`; parts see each other only through `PETSHOP_PEER`. What staff type is data, never a rule. |
| 2 Single source | The protocol lives here; each operation lives in its part's document; measures cite them. |
| 3 External enforcement | By the enforcer, from the last recorded state; this unit can alter neither it nor its own measure. |
| 4 Rehearsal before effect | Verdicts run on a copy in `.rehearsal/`, with data directories created there. There is no real shop yet, so nothing can leave. |
| 5 Return | A failing change is returned by the cycle. Shop data exists only in rehearsal. Limit: once real use is decided, undo of a wrong sale or a lost data directory must be proven before the first real day; that is not built. |
| 6 Selection | A change stands only by the judge, on the number of the measure. |
| 7 Escalation | Decided here, not asked, each open to a case that shows otherwise: one appointment per date and time (one station); cancelled appointments stay on the day; prices are fixed at the moment of sale. Limit: the measure reaches the shop only through `run`; nothing yet measures whether staff can use it. The first work after the parts pass is a part for what staff see, given with its measure by this unit. Real use is the person's to decide and goes to the root's queue when the verdict passes. |

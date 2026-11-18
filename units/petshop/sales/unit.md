# Counter sales

Parent: [petshop](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — The staff sell products at the counter: the sale is recorded with its total, and the goods leave the stock, all or none.
2. **Interface** — Offers the executable `units/petshop/sales/run`, speaking [the shop's protocol](../unit.md), with the operations below; *build* and *verdict* through [`tree`](../../cycle/unit.md). Receives a data directory, `PETSHOP_PEER` and `PETSHOP_TODAY`.
3. **Rules** — Its parent's; none added.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the shop's queue (`units/petshop/queue.md`). Time: a verdict within 5 minutes. Context: this document within 80 lines. Cost: no spending.
5. **Measure** — [`measures/petshop/sales/check`](../../../measures/petshop/sales/check), written by the shop before this unit: one case or more per line below. Number: cases right.
6. **Judge** — [`judge`](../../judge/unit.md).

## The operations

- `sales.sell {items: [{product, quantity}], customer?}` → `{id, total_cents}`. Prices come from the peer (`stock.get`) and goods leave through it (`stock.remove`). `invalid` for no items or a quantity that is not an integer above zero; `not_found` for an unknown product; `insufficient` when any product, counted across all its lines, exceeds the shelf. A refused sale leaves every shelf as it was.
- `sales.get {id}` → `{sale: {id, date, customer, items: [{product, quantity, price_cents}], total_cents}}`, with the prices of the moment of sale. `customer` is absent when none was given.
- `sales.day {date}` → `{sales: [...], total_cents}`; zero and an empty list for a day with none.
- The day of a sale is `PETSHOP_TODAY` when given, otherwise the machine's date. No payment is taken or recorded.

## The principles here

| Principle | At this part |
|---|---|
| 1 Boundary | It answers through `run` and nothing else; it touches the stock only by asking its peer. |
| 2 Single source | The operations above live here; the protocol and the codes are cited from the shop. |
| 3 External enforcement | By the [enforcer](../../enforcer/unit.md), from the last recorded state. |
| 4 Rehearsal before effect | Its verdict runs on a copy in `.rehearsal/`, with a data directory created there. |
| 5 Return | A failing change is returned by the cycle; a refused request changes nothing, which the measure checks. |
| 6 Selection | A change stands only by the judge, on the number of the measure. |
| 7 Escalation | What its measure does not decide it asks in the shop's queue; none is open. Limit: the measure's peer is a stand-in shelf; the real pairing is measured by the shop. |

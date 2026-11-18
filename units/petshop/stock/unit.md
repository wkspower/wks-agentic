# Products with stock

Parent: [petshop](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — The staff know what the shop sells, at what price, and how many of each are on the shelf; the count never goes below zero.
2. **Interface** — Offers the executable `units/petshop/stock/run`, speaking [the shop's protocol](../unit.md), with the operations below; *build* and *verdict* through [`tree`](../../cycle/unit.md). Receives a data directory.
3. **Rules** — Its parent's; none added.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the shop's queue (`units/petshop/queue.md`). Time: a verdict within 5 minutes. Context: this document within 80 lines. Cost: no spending.
5. **Measure** — [`measures/petshop/stock/check`](../../../measures/petshop/stock/check), written by the shop before this unit: one case or more per line below. Number: cases right.
6. **Judge** — [`judge`](../../judge/unit.md).

## The operations

- `stock.product_add {name, price_cents, quantity}` → `{id}`. `invalid` for an empty name, or a price or quantity that is negative or not an integer.
- `stock.get {id}` → `{product: {id, name, price_cents, quantity}}`.
- `stock.list {}` → `{products: [...]}`, each product once.
- `stock.add {id, quantity}` → `{}`: goods received. `invalid` unless the quantity is an integer above zero.
- `stock.remove {id, quantity}` → `{}`. `invalid` as for `add`; `insufficient` when the shelf holds less, and then the count is untouched.

## The principles here

| Principle | At this part |
|---|---|
| 1 Boundary | It answers through `run` and nothing else; it needs no peer. |
| 2 Single source | The operations above live here; the protocol and the codes are cited from the shop. |
| 3 External enforcement | By the [enforcer](../../enforcer/unit.md), from the last recorded state. |
| 4 Rehearsal before effect | Its verdict runs on a copy in `.rehearsal/`, with a data directory created there. |
| 5 Return | A failing change is returned by the cycle; a refused request changes nothing, which the measure checks. |
| 6 Selection | A change stands only by the judge, on the number of the measure. |
| 7 Escalation | What its measure does not decide it asks in the shop's queue; none is open. Limit: no case yet covers two requests at the same instant; one counter is assumed. |

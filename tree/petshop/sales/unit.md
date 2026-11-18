# Sales

Parent: [pet shop](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — Record what is sold at the counter and take it from the stock, whole or not at all. No payment is taken or recorded.
2. **Interface** — Offers *build*, *verdict* (`python3 measure/check.py .`), and in `work/sales.py` `Sales(state, stock, customer_exists)`: `sell`, `cancel`, `sale`, `day`, `total_cents`. Receives its state, an object with the stock's `product`, `remove` and `receive`, and a function that says whether a customer exists.
3. **Rules** — The parent's; none added.
4. **Budget** — The parent's, which is the root's. Effects: commits by the judge; it writes no file.
5. **Measure** — [`measure/check.py`](measure/check.py), scenarios written before the work; number = scenarios passed. Planted: one that takes the goods line by line, so a refused sale has already taken some.
6. **Judge** — The [judge](../../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | It knows only its state and what its constructor receives; it imports no other unit. What it returns is a copy. |
| 2 Single source | What this area does is stated once, in the scenarios of its measure; this document and the parent cite them. |
| 3 External enforcement | By the [guard](../../guard/unit.md), at every change. Limit: as in the parent. |
| 4 Rehearsal before effect | The judge measures the candidate under `.rehearsal/` before committing. |
| 5 Return | A standing change is undone by the judge's `--undo`; a refused call changes nothing, which the scenarios check. |
| 6 Selection | By the judge: strictly better by this measure; something wrong that passes becomes a scenario first. |
| 7 Escalation | Asks its parent only what no judge decides. Open, and proceeding under the strictest reading: services are not sold here, only products; no discount, no payment method. |

Limit (queue.md Q2, absorbed): one agent wrote this measure and builds this unit.

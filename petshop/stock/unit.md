# Stock

Parent: [pet shop](../unit.md). Governed by [`principles.md`](../../principles.md).
Laid out and changed as [`judge/unit.md`](../../judge/unit.md) says.

## The six declarations

1. **Purpose** — Keep the shop's products, their prices and how many of each there are, never below zero.
2. **Interface** — Offers `product.add`, `product.get`, `product.list`, `stock.receive`, `stock.take`, exactly as [`../measure/contract.json`](../measure/contract.json) states, through `work/run`; plus *build* (`work/build`, if it needs building) and *verdict*. Receives `PETSHOP_DATA` and nothing from other units.
3. **Rules** — Its parent's; none added.
4. **Budget** — Cost: none. Time: 300 s per build or verdict. Context: this document, its parent's, the contract and its record. Attempts: 3 per change. Attention: one open item in `petshop/queue.md`. Effects without undo: zero.
5. **Measure** — [`measure/check`](measure/check): 27 cases drawn from the contract, run against `work/run` alone; the number is the cases passed. Proven by the plants in `measure/plants/`.
6. **Judge** — The [judge](../../judge/unit.md).

## The principles here

| Principle | At this unit |
|---|---|
| 1 Boundary | It alone changes a product's stock; a sale changes it only by asking `stock.take` and `stock.receive`. |
| 2 Single source | Its operations are stated in the contract and nowhere else; this document and its work cite them. |
| 3 External enforcement | The judge: this unit alters only `work/` and `record.md`, and a change that touches its measure is refused. |
| 4 Rehearsal before effect | `.rehearsal/`: the measure runs it on invented data in a directory made there. |
| 5 Return | As the judge's document, row 5: a change that does not stand leaves the trunk as it was. |
| 6 Selection | By the judge: a change stands when the number rises, or holds with smaller work; alternatives are built apart. |
| 7 Escalation | What its measure and the contract do not decide is an item in `petshop/queue.md`; it proceeds meanwhile under the strictest reading. |

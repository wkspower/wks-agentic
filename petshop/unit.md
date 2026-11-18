# Pet shop

Parent: [root](../root.md). Governed by [`principles.md`](../principles.md).
Laid out and changed as [`judge/unit.md`](../judge/unit.md) says.

## The six declarations

1. **Purpose** — A system for the staff of one physical shop: customers and their pets, appointments for bath and grooming, products with stock, and counter sales. It runs locally, with no real payments. (The person's words, `queue.md` item 3.) Derived from the root's: each capability is delivered and kept correct without asking the person.
2. **Interface** — Offers `work/run do <operation>` and `work/run serve`, exactly as [`measure/contract.json`](measure/contract.json) states, plus *build* (`work/build`, which builds its units) and *verdict*. Receives `PETSHOP_DATA` and `PETSHOP_PORT`. Its own work is only the joining: it sends each operation to the unit the contract names, gives each unit its own data directory and itself as their peer.
3. **Rules** — The principles, plus: no real customer data and no real shop until the person says so (`queue.md` item 3); no network but `127.0.0.1`; it builds and runs with what is already on the machine, installing nothing; the technology of each unit is its own choice, made by comparison under principle 6 and never asked.
4. **Budget** — Cost: none. Time: 300 s per build or verdict. Context: this document, the contract, its record. Attempts: 3 per change. Attention: one open item in `root/queue.md`. Effects without undo: zero.
5. **Measure** — [`measure/check`](measure/check): a day at the shop through the whole system, 16 cases; the number is the cases passed. Proven by the plants in `measure/plants/`. It is a hypothesis: staff finding the system wrong while it passes is a defect of the measure and becomes a case.
6. **Judge** — The [judge](../judge/unit.md).

## Its units

| Unit | Gives the shop |
|---|---|
| [`customers`](customers/unit.md) | customers and their pets |
| [`stock`](stock/unit.md) | products with stock |
| [`appointments`](appointments/unit.md) | appointments for bath and grooming |
| [`sales`](sales/unit.md) | counter sales |
| [`desk`](desk/unit.md) | the screen staff use |

It gives each its purpose, budget, measure and judge. `customers` and `stock`
receive nothing and are built first.

## The principles here

| Principle | At the pet shop |
|---|---|
| 1 Boundary | Units reach each other only through `PETSHOP_PEER` and the contract; none reads another's data directory. The root sees this unit's verdict and number only. |
| 2 Single source | Every operation, field and error lives in `measure/contract.json`; the units, their measures and the desk's forms cite it or are generated from it. |
| 3 External enforcement | The judge; this unit cannot alter its measure, its contract or its document, and its units cannot alter theirs. The rule "no network" has no enforcer yet: stated as a limit. |
| 4 Rehearsal before effect | `.rehearsal/`: every measure runs the system on invented data in a directory made there. No real data exists to affect. |
| 5 Return | As the judge's document, row 5. The shop's data is not part of the record; while there is no real use it is disposable, and before real use an undo for data must exist. |
| 6 Selection | By the judge. A unit's technology is chosen by building alternatives apart and letting the measure compare them. |
| 7 Escalation | Its units ask it in `petshop/queue.md`; it asks the root in `root/queue.md`. A change to the contract is asked there, never made here. |

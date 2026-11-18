# Pet shop

Parent: [root](../../root.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — A system for the staff of one physical shop: customers and their pets, appointments for bath and grooming, products with stock, and counter sales. It runs locally, with no real payments. It is in no real use so far. Required technology: none. (Given by the person, [`queue.md`](../../queue.md) Q3.)
2. **Interface** — Offers *build*, *verdict* (`python3 measure/check.py .`), and to the staff `work/shop.py`: `Shop(path)` with `.customers`, `.appointments`, `.stock`, `.sales`, `.save()`, and the command line `shop.py FILE AREA COMMAND ARGS` (an argument starting with `=` is JSON). Receives the path of the data file. Its children: [customers](customers/unit.md), [appointments](appointments/unit.md), [stock](stock/unit.md), [sales](sales/unit.md); it gives each its state and what it needs of the others.
3. **Rules** — The parent's and the [guard](../guard/unit.md)'s. Added: money is whole cents; a refusal is `ValueError` (not valid) or `LookupError` (not found) and changes nothing; names and numbers in measures are invented.
4. **Budget** — The values of [root](../../root.md) declaration 4. Effects: commits by the judge, and the data file the staff names. No network, no other program, no real customer data in the repository.
5. **Measure** — [`measure/check.py`](measure/check.py): a day at the counter through the whole system and its command line; number = scenarios passed. Planted: a shop that saves nothing.
6. **Judge** — The [judge](../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The shop uses its children only through the classes their documents name, and never reads their state; each child receives the others as given functions or objects. |
| 2 Single source | The purpose and the shared rules live here; each area's behaviour lives in its child's measure; `measure/scenarios.py` is the one runner the children's measures cite. |
| 3 External enforcement | By the guard, at every change, with the measure's planted case run each time. Limit: the money and refusal rules above are enforced only as far as the scenarios reach. |
| 4 Rehearsal before effect | The judge measures the candidate under `.rehearsal/`; scenarios write their data files only there. |
| 5 Return | A standing change is undone by the judge's `--undo`. The data file is written whole at `save()`, never in part; a refused command leaves it as it was. |
| 6 Selection | By the judge: strictly better by this measure. Something wrong that passes becomes a scenario here first (`--revoke`), then the fix. |
| 7 Escalation | Asks the root only what no judge decides. Open, and proceeding under the strictest reading: the shop has one bath-and-grooming station unless told otherwise. |

Limit (queue.md Q2, absorbed): one agent wrote this measure and builds this unit.

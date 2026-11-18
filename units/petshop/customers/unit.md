# Customers and their pets

Parent: [petshop](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — The staff know who each customer is, how to reach them, and which pets are theirs.
2. **Interface** — Offers the executable `units/petshop/customers/run`, speaking [the shop's protocol](../unit.md), with the operations below; *build* and *verdict* through [`tree`](../../cycle/unit.md). Receives a data directory.
3. **Rules** — Its parent's; none added.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the shop's queue (`units/petshop/queue.md`). Time: a verdict within 5 minutes. Context: this document within 80 lines. Cost: no spending.
5. **Measure** — [`measures/petshop/customers/check`](../../../measures/petshop/customers/check), written by the shop before this unit: one case or more per line below. Number: cases right.
6. **Judge** — [`judge`](../../judge/unit.md).

## The operations

- `customers.add {name, phone}` → `{id}`. `invalid` if either is empty or absent.
- `customers.get {id}` → `{customer: {id, name, phone}, pets: [{id, name, species}]}`.
- `customers.find {text}` → `{customers: [{id, name, phone}]}`: those whose name or phone contains the text, letters compared without regard to case; an empty list when none.
- `customers.pet_add {customer, name, species}` → `{id}`. `not_found` for an unknown customer; `invalid` if name or species is empty.
- `customers.pet_get {id}` → `{pet: {id, name, species, customer}}`.

## The principles here

| Principle | At this part |
|---|---|
| 1 Boundary | It answers through `run` and nothing else; it needs no peer. |
| 2 Single source | The operations above live here; the protocol and the codes are cited from the shop. |
| 3 External enforcement | By the [enforcer](../../enforcer/unit.md), from the last recorded state. |
| 4 Rehearsal before effect | Its verdict runs on a copy in `.rehearsal/`, with a data directory created there. |
| 5 Return | A failing change is returned by the cycle; a refused request changes nothing, which the measure checks. |
| 6 Selection | A change stands only by the judge, on the number of the measure. |
| 7 Escalation | What its measure does not decide it asks in the shop's queue; none is open. Limit: the measure uses invented names only; no real customer data exists in the tree. |

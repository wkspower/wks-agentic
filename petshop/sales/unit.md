# Sales

Parent: [`petshop`](../unit.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — Sell: turn what a customer takes into a recorded sale with the right total, wholly or not at all.
2. **Interface** — A module `sales.py`. Every function takes the sales state first; the state is made only by `new()`, is opaque to callers and survives `json.loads(json.dumps(state))` unchanged in behaviour. Prices and stock are not its own: it receives three callables and knows nothing else of where they come from.
   - `new()` returns an empty state.
   - `sell(state, customer_id, lines, price_of, available, take)` records and returns a sale. `lines` is a list of `(item_id, quantity)`; `price_of(item_id)` returns cents or raises `KeyError`; `available(item_id)` returns the quantity on hand; `take(item_id, quantity)` removes it. The sale is a dict with exactly `id` (`"S1"`, `"S2"`, ...), `customer_id`, `lines` (one dict per given line, in order, with exactly `item_id`, `quantity`, `unit_price_cents`, `line_total_cents`) and `total_cents`. `ValueError` when `customer_id` is not a non-empty string, `lines` is empty, a quantity is not an `int` (not a `bool`) of 1 or more, or the quantities asked of one item, summed over the lines, exceed `available`. A `KeyError` from `price_of` passes through. On any refusal `take` has not been called and nothing is recorded; otherwise `take` is called once per line.
   - `get(state, sale_id)` returns the sale; `KeyError` when unknown.
   - `sales(state)` returns all sales in the order made.
   - `takings(state)` returns the sum of `total_cents`.

   Returned sales are copies, their lines included. Functions change the state they are given, in place. Where two refusals apply at once, either may be raised. Offers *build* and *verdict*.
3. **Rules** — Those of [`petshop`](../unit.md), none added.
4. **Budget** — cost 2 runs; time 0.4 h; context 8 KB; attempts 2; alternatives 1; attention 0; no-undo cap 0.
5. **Measure** — `measure/check <build-dir>`: cases that call `sales.py` from the build; passes only if all pass; number: bytes of `sales.py`. Written before the unit by an agent that does not build it; planted wrong modules in `measure/planted/` must each fail. Error (seen by the pet shop, in [`record.md`](../record.md)): wrong passes and wrong fails, counted on every build offered to the judge, from audit cases written from this document alone by an agent that sees neither measure nor build, kept in `petshop/audit/sales/`.
6. **Judge** — The [`judge`](../../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The shop sees `verdict`, the number and the functions above; the module holds no state of its own and imports no other unit's module. |
| 2 Single source | Sales live only in this state. Prices and stock are cited through the callables, never copied beyond the sale's own lines. |
| 3 External enforcement | As [`petshop`](../unit.md) row 3. |
| 4 Rehearsal before effect | As [`petshop`](../unit.md) row 4. |
| 5 Return | As [`petshop`](../unit.md) row 5. A refused call leaves the state as it was. |
| 6 Selection | By the judge, against what exists and 1 alternative made without sight of the change. |
| 7 Escalation | Asks the pet shop only what no judge decides. Round before first effect: nothing foreseen beyond the declarations given. |

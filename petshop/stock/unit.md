# Stock

Parent: [`petshop`](../unit.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — Keep the stock right: how many of each item are on hand, never fewer than none.
2. **Interface** — A module `stock.py`. Every function takes the stock state first; the state is made only by `new()`, is opaque to callers and survives `json.loads(json.dumps(state))` unchanged in behaviour. Item ids are data: any non-empty string, known to the catalog or not.
   - `new()` returns an empty state.
   - `on_hand(state, item_id)` returns the quantity as an `int`; 0 for an item never received.
   - `receive(state, item_id, quantity)` adds and returns the quantity now on hand.
   - `remove(state, item_id, quantity)` takes away and returns the quantity now on hand; `ValueError` when `quantity` exceeds what is on hand.

   `receive` and `remove` raise `ValueError` when `item_id` is not a non-empty string or `quantity` is not an `int` (not a `bool`) of 1 or more. Functions change the state they are given, in place. A refused call changes nothing. Where two refusals apply at once, either may be raised. Offers *build* and *verdict*.
3. **Rules** — Those of [`petshop`](../unit.md), none added.
4. **Budget** — cost 2 runs; time 0.4 h; context 8 KB; attempts 2; alternatives 1; attention 0; no-undo cap 0.
5. **Measure** — `measure/check <build-dir>`: cases that call `stock.py` from the build; passes only if all pass; number: bytes of `stock.py`. Written before the unit by an agent that does not build it; planted wrong modules in `measure/planted/` must each fail. Error (seen by the pet shop, in [`record.md`](../record.md)): unknown, and a limit, until audit cases exist: cases written from this document alone by an agent that sees neither measure nor build.
6. **Judge** — The [`judge`](../../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The shop sees `verdict`, the number and the functions above; the module holds no state of its own and imports no other unit's module. |
| 2 Single source | Quantities live only in this state; others ask `on_hand`. |
| 3 External enforcement | As [`petshop`](../unit.md) row 3. |
| 4 Rehearsal before effect | As [`petshop`](../unit.md) row 4. |
| 5 Return | As [`petshop`](../unit.md) row 5. A refused call leaves the state as it was. |
| 6 Selection | By the judge, against what exists and 1 alternative made without sight of the change. |
| 7 Escalation | Asks the pet shop only what no judge decides. Round before first effect: nothing foreseen beyond the declarations given. |

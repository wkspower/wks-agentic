# Catalog

Parent: [`petshop`](../unit.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — Know what the shop sells: each animal and product, its name and its price.
2. **Interface** — A module `catalog.py`. Every function takes the catalog state first; the state is made only by `new()`, is opaque to callers and survives `json.loads(json.dumps(state))` unchanged in behaviour. An item is a dict with exactly `id`, `name`, `kind`, `price_cents`; returned items are copies.
   - `new()` returns an empty state.
   - `add(state, item_id, name, kind, price_cents)` returns `None`. `ValueError` when `item_id` or `name` is not a non-empty string, `kind` is not `"animal"` or `"product"`, the price is not valid, or the id already exists.
   - `get(state, item_id)` returns the item; `KeyError` when unknown.
   - `set_price(state, item_id, price_cents)` returns `None`; `KeyError` when unknown, `ValueError` when the price is not valid.
   - `items(state)` returns all items as a list ordered by `id`.

   A valid price is an `int` (not a `bool`) of 0 or more. A refused call changes nothing. Offers *build* and *verdict*.
3. **Rules** — Those of [`petshop`](../unit.md), none added.
4. **Budget** — cost 4 runs; time 0.5 h; context 8 KB; attempts 2; alternatives 1; attention 0; no-undo cap 0.
5. **Measure** — `measure/check <build-dir>`: cases that call `catalog.py` from the build; passes only if all pass; number: bytes of `catalog.py`. Written before the unit by an agent that does not build it; planted wrong modules in `measure/planted/` must each fail. Error (seen by the pet shop, in [`record.md`](../record.md)): wrong passes and wrong fails, counted on every build offered to the judge, from audit cases written from this document alone by an agent that sees neither measure nor build, kept in `petshop/audit/catalog/`.
6. **Judge** — The [`judge`](../../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The shop sees `verdict`, the number and the functions above; the module holds no state of its own and imports no other unit's module. |
| 2 Single source | Names, kinds and prices live only in this state; others ask `get`. |
| 3 External enforcement | As [`petshop`](../unit.md) row 3. |
| 4 Rehearsal before effect | As [`petshop`](../unit.md) row 4. |
| 5 Return | As [`petshop`](../unit.md) row 5. A refused call leaves the state as it was. |
| 6 Selection | By the judge, against what exists and 1 alternative made without sight of the change. |
| 7 Escalation | Asks the pet shop only what no judge decides. Round before first effect: nothing foreseen beyond the declarations given. |

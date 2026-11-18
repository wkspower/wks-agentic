# Stock

Parent: [`units/pet-shop`](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — Know how many units of each item are available, and never let an item go below zero or a pet above one.
2. **Interface** — *build* and *verdict* as in [`units/judge`](../../judge/unit.md), unit name `stock`. Module `petshop.stock`:
   - `class InsufficientStock(Exception)`.
   - `class Stock(catalog)` where `catalog` offers `get(sku)` as `petshop.catalog.Catalog` does.
   - `receive(sku: str, qty: int) -> int` adds and returns the new available quantity. `KeyError` when the catalog has no `sku`; `ValueError` when `qty` is not an `int` (not `bool`) or not > 0, or when the item is a pet and the result would exceed 1 (nothing changes then).
   - `available(sku: str) -> int`, 0 for a catalog item never received; `KeyError` when the catalog has no `sku`.
   - `take(sku: str, qty: int) -> int` removes and returns the new available quantity; `KeyError`/`ValueError` as `receive` (without the pet bound); `InsufficientStock` when `qty` exceeds what is available, and nothing changes.
   - `put_back(sku: str, qty: int) -> int` same as `receive` but used for returns; the pet bound applies.
3. **Rules** — The parent's.
4. **Budget** — The parent's, shared.
5. **Measure** — [`measures/stock/`](../../../measures/stock/). Number: fraction of cases passing.
6. **Judge** — [`units/judge`](../../judge/unit.md).

## The principles here

As the parent's table; nothing differs.

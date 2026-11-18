# Orders

Parent: [`units/pet-shop`](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — Take orders that are always backed by stock and priced from the catalog, and cancel them returning the stock.
2. **Interface** — *build* and *verdict* as in [`units/judge`](../../judge/unit.md), unit name `orders`. Module `petshop.orders`:
   - `class Orders(catalog, stock)` with the interfaces of `petshop.catalog.Catalog` and `petshop.stock.Stock`.
   - `place(lines: list[tuple[str, int]]) -> dict` returns the order `{"id": str, "status": "placed", "lines": [{"sku", "qty", "price_cents"}], "total_cents": int}`. `price_cents` is the catalog price at the time of placing; `total_cents` is the sum of `qty * price_cents`. Lines for the same `sku` are merged in order of first appearance. Ids are unique, non-empty strings. Raises `ValueError` for no lines or a `qty` that is not an `int` (not `bool`) or not > 0; `KeyError` for an unknown `sku`; `petshop.stock.InsufficientStock` when any line cannot be met. On any error nothing changes (all lines or none).
   - `get(order_id: str) -> dict` a copy; `KeyError` when absent.
   - `cancel(order_id: str) -> dict` sets status `"cancelled"`, puts every line back in stock, returns the order; `KeyError` when absent; `ValueError` when already cancelled.
3. **Rules** — The parent's.
4. **Budget** — The parent's, shared.
5. **Measure** — [`measures/orders/`](../../../measures/orders/). Number: fraction of cases passing.
6. **Judge** — [`units/judge`](../../judge/unit.md).

## The principles here

As the parent's table; nothing differs.

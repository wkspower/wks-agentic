# Catalog

Parent: [`units/pet-shop`](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — Keep the list of what the shop offers, pets and supplies, with their prices.
2. **Interface** — *build* and *verdict* as in [`units/judge`](../../judge/unit.md), unit name `catalog`. Module `petshop.catalog`:
   - `class Catalog()`.
   - `add(sku: str, name: str, kind: str, price_cents: int) -> dict` returns the item `{"sku", "name", "kind", "price_cents"}`. Raises `ValueError` when `sku` or `name` is empty or not a `str`, `kind` is not `"pet"` or `"supply"`, or `price_cents` is not an `int` (a `bool` is not an `int` here) or is not > 0. Raises `KeyError` when `sku` exists.
   - `get(sku: str) -> dict` returns a copy of the item; `KeyError` when absent.
   - `items(kind: str | None = None) -> list[dict]` copies, sorted by `sku`, optionally filtered by `kind`; `ValueError` for another `kind`.
   - Returned dicts are copies: changing them does not change the catalog.
3. **Rules** — The parent's.
4. **Budget** — The parent's, shared.
5. **Measure** — [`measures/catalog/`](../../../measures/catalog/). Number: fraction of cases passing.
6. **Judge** — [`units/judge`](../../judge/unit.md).

## The principles here

As the parent's table; nothing differs.

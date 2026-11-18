"""Catalog unit. Declarations: units/pet-shop/catalog/unit.md."""
from ._valid import non_empty_str, positive_int

KINDS = ("pet", "supply")


def _kind(kind):
    if not isinstance(kind, str) or kind not in KINDS:
        raise ValueError("kind must be 'pet' or 'supply'")
    return kind


class Catalog:
    def __init__(self):
        self._items = {}

    def add(self, sku, name, kind, price_cents):
        item = {
            "sku": non_empty_str(sku, "sku"),
            "name": non_empty_str(name, "name"),
            "kind": _kind(kind),
            "price_cents": positive_int(price_cents, "price_cents"),
        }
        if sku in self._items:
            raise KeyError(sku)
        self._items[sku] = item
        return dict(item)

    def get(self, sku):
        return dict(self._items[sku])

    def items(self, kind=None):
        if kind is not None:
            _kind(kind)
        return [dict(self._items[sku]) for sku in sorted(self._items)
                if kind is None or self._items[sku]["kind"] == kind]

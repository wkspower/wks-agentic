"""Stock unit. Declarations: units/pet-shop/stock/unit.md."""
from ._valid import positive_int

PET_BOUND = 1


class InsufficientStock(Exception):
    pass


class Stock:
    def __init__(self, catalog):
        self._catalog = catalog
        self._qty = {}

    def _kind(self, sku):
        return self._catalog.get(sku)["kind"]  # KeyError when absent

    def available(self, sku):
        self._kind(sku)
        return self._qty.get(sku, 0)

    def _add(self, sku, qty):
        kind = self._kind(sku)
        positive_int(qty, "qty")
        new = self._qty.get(sku, 0) + qty
        if kind == "pet" and new > PET_BOUND:
            raise ValueError("a pet is never above 1 in stock")
        self._qty[sku] = new
        return new

    def receive(self, sku, qty):
        return self._add(sku, qty)

    def put_back(self, sku, qty):
        return self._add(sku, qty)

    def take(self, sku, qty):
        self._kind(sku)
        positive_int(qty, "qty")
        have = self._qty.get(sku, 0)
        if qty > have:
            raise InsufficientStock(f"{sku}: {have} available, {qty} asked")
        self._qty[sku] = have - qty
        return have - qty

# Planted defect: take() lets the quantity go below zero.
class InsufficientStock(Exception):
    pass


def _check_qty(qty):
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty must be a positive int")


class Stock:
    def __init__(self, catalog):
        self._catalog = catalog
        self._qty = {}

    def _item(self, sku):
        return self._catalog.get(sku)

    def receive(self, sku, qty):
        item = self._item(sku)
        _check_qty(qty)
        new = self._qty.get(sku, 0) + qty
        if item["kind"] == "pet" and new > 1:
            raise ValueError("a pet cannot exceed 1")
        self._qty[sku] = new
        return new

    def available(self, sku):
        self._item(sku)
        return self._qty.get(sku, 0)

    def take(self, sku, qty):
        self._item(sku)
        _check_qty(qty)
        cur = self._qty.get(sku, 0)
                self._qty[sku] = cur - qty
        return cur - qty

    def put_back(self, sku, qty):
        return self.receive(sku, qty)

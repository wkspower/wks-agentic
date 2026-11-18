"""Orders unit. Declarations: units/pet-shop/orders/unit.md."""
import copy
import itertools

from ._valid import positive_int
from .stock import InsufficientStock


class Orders:
    def __init__(self, catalog, stock):
        self._catalog = catalog
        self._stock = stock
        self._orders = {}
        self._ids = itertools.count(1)

    def place(self, lines):
        lines = list(lines)
        if not lines:
            raise ValueError("an order needs at least one line")
        merged = {}
        for sku, qty in lines:
            positive_int(qty, "qty")
            merged[sku] = merged.get(sku, 0) + qty
        priced = []
        for sku, qty in merged.items():
            price = self._catalog.get(sku)["price_cents"]  # KeyError when unknown
            if self._stock.available(sku) < qty:
                raise InsufficientStock(f"{sku}: {qty} asked")
            priced.append({"sku": sku, "qty": qty, "price_cents": price})
        taken = []
        try:
            for line in priced:
                self._stock.take(line["sku"], line["qty"])
                taken.append(line)
        except Exception:
            for line in taken:
                self._stock.put_back(line["sku"], line["qty"])
            raise
        order = {
            "id": str(next(self._ids)),
            "status": "placed",
            "lines": priced,
            "total_cents": sum(l["qty"] * l["price_cents"] for l in priced),
        }
        self._orders[order["id"]] = order
        return copy.deepcopy(order)

    def get(self, order_id):
        return copy.deepcopy(self._orders[order_id])

    def cancel(self, order_id):
        order = self._orders[order_id]
        if order["status"] == "cancelled":
            raise ValueError(f"order {order_id} is already cancelled")
        for line in order["lines"]:
            self._stock.put_back(line["sku"], line["qty"])
        order["status"] = "cancelled"
        return copy.deepcopy(order)

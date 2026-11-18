# Planted defect: cancelling twice is allowed and puts the stock back twice.
import copy
import itertools

from petshop.stock import InsufficientStock


class Orders:
    def __init__(self, catalog, stock):
        self._catalog = catalog
        self._stock = stock
        self._orders = {}
        self._ids = itertools.count(1)

    def place(self, lines):
        if not lines:
            raise ValueError("no lines")
        merged = {}
        for sku, qty in lines:
            if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
                raise ValueError("qty must be a positive int")
            merged[sku] = merged.get(sku, 0) + qty
        priced = []
        for sku, qty in merged.items():
            item = self._catalog.get(sku)
            if qty > self._stock.available(sku):
                raise InsufficientStock(sku)
            priced.append({"sku": sku, "qty": qty, "price_cents": item["price_cents"]})
        taken = []
        try:
            for line in priced:
                self._stock.take(line["sku"], line["qty"])
                taken.append(line)
        except Exception:
            for line in taken:
                self._stock.put_back(line["sku"], line["qty"])
            raise
        oid = "o%d" % next(self._ids)
        order = {"id": oid, "status": "placed", "lines": priced,
                 "total_cents": sum(l["qty"] * l["price_cents"] for l in priced)}
        self._orders[oid] = order
        return copy.deepcopy(order)

    def get(self, order_id):
        return copy.deepcopy(self._orders[order_id])

    def cancel(self, order_id):
        order = self._orders[order_id]
        for line in order["lines"]:
            self._stock.put_back(line["sku"], line["qty"])
        order["status"] = "cancelled"
        return copy.deepcopy(order)

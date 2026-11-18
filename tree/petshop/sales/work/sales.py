"""Counter sales: taken from the stock whole or not at all. No payment is handled."""
from datetime import datetime

FORMAT = "%Y-%m-%dT%H:%M"


class Sales:
    def __init__(self, state, stock, customer_exists):
        self._rows = state.setdefault("sales", [])
        self._stock = stock
        self._customer_exists = customer_exists

    @staticmethod
    def _copy(row):
        return dict(row, items=[dict(line) for line in row["items"]])

    def _row(self, sale_id):
        for row in self._rows:
            if row["id"] == sale_id:
                return row
        raise LookupError(f"no sale {sale_id}")

    def sell(self, items, customer_id=None, when=None):
        items = [tuple(item) for item in items]
        if not items or any(len(i) != 2 or type(i[0]) is not int or type(i[1]) is not int or i[1] <= 0 for i in items):
            raise ValueError("a sale has items, each a product id and a whole quantity above zero")
        when = when or datetime.now().strftime(FORMAT)
        try:
            datetime.strptime(when, FORMAT)
        except (TypeError, ValueError):
            raise ValueError(f"'{when}' is not a date and time like 2026-11-20T10:30")
        if customer_id is not None and not self._customer_exists(customer_id):
            raise LookupError(f"no customer {customer_id}")
        # everything is checked before any stock moves
        wanted, lines = {}, []
        for product_id, quantity in items:
            product = self._stock.product(product_id)
            wanted[product_id] = wanted.get(product_id, 0) + quantity
            if wanted[product_id] > product["quantity"]:
                raise ValueError(f"only {product['quantity']} of {product['name']} in stock")
            lines.append({"product_id": product_id, "quantity": quantity, "unit_price_cents": product["price_cents"]})
        for product_id, quantity in wanted.items():
            self._stock.remove(product_id, quantity)
        row = {"id": max((r["id"] for r in self._rows), default=0) + 1, "when": when, "customer_id": customer_id,
               "status": "sold", "total_cents": sum(l["quantity"] * l["unit_price_cents"] for l in lines),
               "items": lines}
        self._rows.append(row)
        return self._copy(row)

    def cancel(self, sale_id):
        row = self._row(sale_id)
        if row["status"] != "sold":
            raise ValueError(f"sale {sale_id} is already cancelled")
        for line in row["items"]:
            self._stock.receive(line["product_id"], line["quantity"])
        row["status"] = "cancelled"

    def sale(self, sale_id):
        return self._copy(self._row(sale_id))

    def day(self, date):
        return sorted((self._copy(r) for r in self._rows if r["when"].startswith(date + "T")),
                      key=lambda r: (r["when"], r["id"]))

    def total_cents(self, date=None):
        return sum(r["total_cents"] for r in self._rows
                   if r["status"] == "sold" and (date is None or r["when"].startswith(date + "T")))

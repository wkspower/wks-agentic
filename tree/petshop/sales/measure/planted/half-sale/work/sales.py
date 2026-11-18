"""Planted wrong result: takes the goods line by line, so a sale refused at the
second line has already taken the first."""
from datetime import datetime


class Sales:
    def __init__(self, state, stock, customer_exists):
        self.rows, self.stock, self.customer_exists = state.setdefault("rows", []), stock, customer_exists

    def sell(self, items, customer_id=None, when=None):
        if not items or any(type(q) is not int or q <= 0 for _, q in items):
            raise ValueError("not valid")
        when = when or datetime.now().strftime("%Y-%m-%dT%H:%M")
        datetime.strptime(when, "%Y-%m-%dT%H:%M")
        if customer_id is not None and not self.customer_exists(customer_id):
            raise LookupError("no such customer")
        lines = []
        for product_id, quantity in items:
            price = self.stock.product(product_id)["price_cents"]
            self.stock.remove(product_id, quantity)
            lines.append({"product_id": product_id, "quantity": quantity, "unit_price_cents": price})
        sale = {"id": len(self.rows) + 1, "when": when, "customer_id": customer_id, "status": "sold",
                "total_cents": sum(l["quantity"] * l["unit_price_cents"] for l in lines), "items": lines}
        self.rows.append(sale)
        return self.sale(sale["id"])

    def sale(self, ident):
        for row in self.rows:
            if row["id"] == ident:
                return dict(row, items=[dict(l) for l in row["items"]])
        raise LookupError("no such sale")

    def cancel(self, ident):
        row = next((r for r in self.rows if r["id"] == ident), None)
        if row is None:
            raise LookupError("no such sale")
        if row["status"] != "sold":
            raise ValueError("already cancelled")
        for line in row["items"]:
            self.stock.receive(line["product_id"], line["quantity"])
        row["status"] = "cancelled"

    def day(self, date):
        return sorted((self.sale(r["id"]) for r in self.rows if r["when"].startswith(date)), key=lambda r: r["when"])

    def total_cents(self, date=None):
        return sum(r["total_cents"] for r in self.rows if r["status"] == "sold" and (date is None or r["when"].startswith(date)))

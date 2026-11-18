# Planted wrong result: the work that stood and was shown wrong (ledger, revoked).
"""Products, prices in whole cents, and quantities that never go below zero."""


class Stock:
    def __init__(self, state):
        self._rows = state.setdefault("products", {})
        self._state = state
        state.setdefault("last_id", 0)

    @staticmethod
    def _whole(number, least, what):
        if type(number) is not int or number < least:
            raise ValueError(f"{what} must be a whole number, at least {least}")
        return number

    def _row(self, product_id):
        if str(product_id) not in self._rows:
            raise LookupError(f"no product {product_id}")
        return self._rows[str(product_id)]

    def add_product(self, name, price_cents, quantity=0):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("a name is required")
        row = {"id": 0, "name": name.strip(), "price_cents": self._whole(price_cents, 0, "the price in cents"),
               "quantity": self._whole(quantity, 0, "the quantity")}
        self._state["last_id"] += 1
        row["id"] = self._state["last_id"]
        self._rows[str(row["id"])] = row
        return row["id"]

    def product(self, product_id):
        return dict(self._row(product_id))

    def products(self):
        return sorted((dict(r) for r in self._rows.values()), key=lambda r: (r["name"].lower(), r["id"]))

    def low(self, quantity):
        return [p for p in self.products() if p["quantity"] <= quantity]

    def receive(self, product_id, quantity):
        self._row(product_id)["quantity"] += self._whole(quantity, 1, "the quantity received")

    def remove(self, product_id, quantity):
        row = self._row(product_id)
        if self._whole(quantity, 1, "the quantity taken") > row["quantity"]:
            raise ValueError(f"only {row['quantity']} of {row['name']} in stock")
        row["quantity"] -= quantity

    def set_price(self, product_id, price_cents):
        self._row(product_id)["price_cents"] = self._whole(price_cents, 0, "the price in cents")

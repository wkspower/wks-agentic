"""Planted wrong result: lets the quantity go below zero."""


class Stock:
    def __init__(self, state):
        self.rows = state.setdefault("rows", {})

    def _row(self, ident):
        if str(ident) not in self.rows:
            raise LookupError("no such product")
        return self.rows[str(ident)]

    @staticmethod
    def _whole(number, least):
        if type(number) is not int or number < least:
            raise ValueError("not valid")

    def add_product(self, name, price_cents, quantity=0):
        self._whole(price_cents, 0)
        self._whole(quantity, 0)
        if not name.strip():
            raise ValueError("no name")
        ident = len(self.rows) + 1
        self.rows[str(ident)] = {"id": ident, "name": name, "price_cents": price_cents, "quantity": quantity}
        return ident

    def product(self, ident):
        return dict(self._row(ident))

    def products(self):
        return sorted((dict(r) for r in self.rows.values()), key=lambda r: r["name"])

    def low(self, quantity):
        return [p for p in self.products() if p["quantity"] <= quantity]

    def receive(self, ident, quantity):
        self._whole(quantity, 1)
        self._row(ident)["quantity"] += quantity

    def remove(self, ident, quantity):
        self._whole(quantity, 1)
        self._row(ident)["quantity"] -= quantity

    def set_price(self, ident, price_cents):
        self._whole(price_cents, 0)
        self._row(ident)["price_cents"] = price_cents

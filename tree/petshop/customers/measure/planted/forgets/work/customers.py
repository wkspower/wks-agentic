"""Planted wrong result: keeps the data in itself, not in the state it was given."""


class Customers:
    def __init__(self, state):
        self.s = {}
        self.s.setdefault("customers", {})
        self.s.setdefault("pets", {})

    def _new(self, table, row):
        row["id"] = len(self.s[table]) + 1
        self.s[table][str(row["id"])] = row
        return row["id"]

    def add_customer(self, name, phone):
        return self._new("customers", {"name": name, "phone": phone})

    def add_pet(self, customer_id, name, species):
        return self._new("pets", {"customer_id": customer_id, "name": name, "species": species})

    def customer(self, ident):
        return dict(self.s["customers"].get(str(ident), {}))

    def pet(self, ident):
        return dict(self.s["pets"].get(str(ident), {}))

    def pets_of(self, customer_id):
        return [dict(p) for p in self.s["pets"].values() if p["customer_id"] == customer_id]

    def has_customer(self, ident):
        return str(ident) in self.s["customers"]

    def has_pet(self, ident):
        return str(ident) in self.s["pets"]

    def update_customer(self, ident, name=None, phone=None):
        row = self.s["customers"].setdefault(str(ident), {"id": ident})
        row.update({k: v for k, v in (("name", name), ("phone", phone)) if v is not None})

    def find(self, text):
        text = text.lower()
        return [dict(c) for c in self.s["customers"].values()
                if text in c["name"].lower() or text in c["phone"]
                or any(text in p["name"].lower() for p in self.pets_of(c["id"]))]

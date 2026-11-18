"""Customers and their pets. Everything is kept in the state given."""


class Customers:
    def __init__(self, state):
        self._customers = state.setdefault("customers", {})
        self._pets = state.setdefault("pets", {})
        self._state = state
        state.setdefault("last_id", 0)

    def _next(self):
        self._state["last_id"] += 1
        return self._state["last_id"]

    @staticmethod
    def _named(name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("a name is required")
        return name.strip()

    def _row(self, table, ident, what):
        if str(ident) not in table:
            raise LookupError(f"no {what} {ident}")
        return table[str(ident)]

    def add_customer(self, name, phone=""):
        row = {"id": 0, "name": self._named(name), "phone": str(phone)}
        row["id"] = self._next()
        self._customers[str(row["id"])] = row
        return row["id"]

    def update_customer(self, customer_id, name=None, phone=None):
        row = self._row(self._customers, customer_id, "customer")
        if name is not None:
            row["name"] = self._named(name)
        if phone is not None:
            row["phone"] = str(phone)

    def customer(self, customer_id):
        return dict(self._row(self._customers, customer_id, "customer"))

    def has_customer(self, customer_id):
        return str(customer_id) in self._customers

    def add_pet(self, customer_id, name, species=""):
        self._row(self._customers, customer_id, "customer")
        row = {"id": 0, "customer_id": customer_id, "name": self._named(name), "species": str(species)}
        row["id"] = self._next()
        self._pets[str(row["id"])] = row
        return row["id"]

    def pet(self, pet_id):
        return dict(self._row(self._pets, pet_id, "pet"))

    def has_pet(self, pet_id):
        return str(pet_id) in self._pets

    def pets_of(self, customer_id):
        self._row(self._customers, customer_id, "customer")
        return [dict(p) for p in self._pets.values() if p["customer_id"] == customer_id]

    def find(self, text):
        text = str(text).lower()
        return [dict(c) for c in self._customers.values()
                if text in c["name"].lower() or text in c["phone"].lower()
                or any(text in p["name"].lower() for p in self._pets.values() if p["customer_id"] == c["id"])]

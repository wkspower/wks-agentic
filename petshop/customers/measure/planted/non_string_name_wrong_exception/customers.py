"""Customers: who the shop sells to; an id is never reused."""


def new():
    return {"last": 0, "customers": []}


def register(state, name):
    name = name.strip()
    if name == "":
        raise ValueError("name must not be empty")
    state["last"] += 1
    customer_id = "C%d" % state["last"]
    state["customers"].append({"id": customer_id, "name": name})
    return customer_id


def get(state, customer_id):
    for customer in state["customers"]:
        if customer["id"] == customer_id:
            return dict(customer)
    raise KeyError(customer_id)


def find(state, text):
    wanted = text.lower()
    found = [c for c in state["customers"] if wanted in c["name"].lower()]
    return [dict(c) for c in found]

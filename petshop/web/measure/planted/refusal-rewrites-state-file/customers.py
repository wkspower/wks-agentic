"""Customers of the pet shop: the state maps each id to a name, in order of registration."""


def new():
    return {}


def register(state, name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")
    customer_id = "C%d" % (len(state) + 1)
    state[customer_id] = name.strip()
    return customer_id


def get(state, customer_id):
    if not isinstance(customer_id, str) or customer_id not in state:
        raise KeyError(customer_id)
    return {"id": customer_id, "name": state[customer_id]}


def find(state, text):
    if not isinstance(text, str):
        return []
    text = text.casefold()
    return [get(state, key) for key, name in state.items() if text in name.casefold()]

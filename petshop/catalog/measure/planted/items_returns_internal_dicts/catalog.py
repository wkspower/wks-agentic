"""Catalog: what the shop sells, each item with its name, kind and price."""

KINDS = ("animal", "product")


def _text(value):
    return isinstance(value, str) and value != ""


def _price(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def new():
    return {"items": {}}


def add(state, item_id, name, kind, price_cents):
    if not _text(item_id) or not _text(name):
        raise ValueError("id and name must be non-empty strings")
    if not (isinstance(kind, str) and kind in KINDS):
        raise ValueError("kind must be animal or product")
    if not _price(price_cents):
        raise ValueError("price must be an int of 0 or more")
    if item_id in state["items"]:
        raise ValueError("item already exists: " + item_id)
    state["items"][item_id] = {
        "id": item_id, "name": name, "kind": kind, "price_cents": price_cents,
    }


def get(state, item_id):
    if not isinstance(item_id, str) or item_id not in state["items"]:
        raise KeyError(item_id)
    return dict(state["items"][item_id])


def set_price(state, item_id, price_cents):
    if not isinstance(item_id, str) or item_id not in state["items"]:
        raise KeyError(item_id)
    if not _price(price_cents):
        raise ValueError("price must be an int of 0 or more")
    state["items"][item_id]["price_cents"] = price_cents


def items(state):
    return [state["items"][item_id] for item_id in sorted(state["items"])]

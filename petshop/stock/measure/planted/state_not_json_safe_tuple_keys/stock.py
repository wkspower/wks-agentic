"""Stock: how many of each item are on hand, never fewer than none."""


def _check(item_id, quantity):
    if not isinstance(item_id, str) or item_id == "":
        raise ValueError("item id must be a non-empty string")
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        raise ValueError("quantity must be an int of 1 or more")


def new():
    return {"on_hand": {}}


def on_hand(state, item_id):
    return state["on_hand"].get(("item", item_id), 0)


def receive(state, item_id, quantity):
    _check(item_id, quantity)
    state["on_hand"][("item", item_id)] = on_hand(state, item_id) + quantity
    return on_hand(state, item_id)


def remove(state, item_id, quantity):
    _check(item_id, quantity)
    have = on_hand(state, item_id)
    if quantity > have:
        raise ValueError("only %d on hand" % have)
    state["on_hand"][("item", item_id)] = have - quantity
    return on_hand(state, item_id)

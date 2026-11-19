"""Stock: how many of each item are on hand, never fewer than none."""


def new():
    return {}


def on_hand(state, item_id):
    return state.get(item_id, 0) if isinstance(item_id, str) else 0


def _change(state, item_id, quantity, sign):
    if not (isinstance(item_id, str) and item_id):
        raise ValueError("item_id must be a non-empty string")
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        raise ValueError("quantity must be an int of 1 or more")
    total = on_hand(state, item_id) + sign * quantity
    if total < 0:
        raise ValueError("quantity exceeds what is on hand")
    state[item_id] = total
    return total


def receive(state, item_id, quantity):
    return _change(state, item_id, quantity, 1)


def remove(state, item_id, quantity):
    return _change(state, item_id, quantity, -1)

"""Catalog: what the shop sells. The state maps each item id to its item."""


def _check_price(price_cents):
    if type(price_cents) is not int or price_cents < 0:
        raise ValueError("invalid price")


def _find(state, item_id):
    if not isinstance(item_id, str) or item_id not in state:
        raise KeyError(item_id)
    return state[item_id]


def new():
    return {}


def add(state, item_id, name, kind, price_cents):
    for text in (item_id, name):
        if not isinstance(text, str) or not text:
            raise ValueError("id and name must be non-empty strings")
    if not isinstance(kind, str) or kind not in ("animal", "product"):
        raise ValueError("invalid kind")
    _check_price(price_cents)
    if item_id in state:
        raise ValueError("id already exists")
    state[item_id] = {"id": item_id, "name": name, "kind": kind, "price_cents": price_cents}


def get(state, item_id):
    return dict(_find(state, item_id))


def set_price(state, item_id, price_cents):
    item = _find(state, item_id)
    _check_price(price_cents)
    item["price_cents"] = price_cents


def items(state):
    return [dict(state[item_id]) for item_id in sorted(state)]

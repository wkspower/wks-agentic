"""Sales: record what a customer takes as a sale, wholly or not at all.

The state is a list of sales in the order made; it is plain JSON data.
"""


def new():
    return []


def _copy(sale):
    return dict(sale, lines=[dict(line) for line in sale["lines"]])


def sell(state, customer_id, lines, price_of, available, take):
    if not isinstance(customer_id, str) or not customer_id:
        raise ValueError("customer_id must be a non-empty string")
    try:
        pairs = [(item_id, quantity) for item_id, quantity in lines]
    except (TypeError, ValueError):
        raise ValueError("lines must be a list of (item_id, quantity)") from None
    if not pairs:
        raise ValueError("lines must not be empty")
    for item_id, quantity in pairs:
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValueError("a quantity must be an int of 1 or more")
    sold = []
    for item_id, quantity in pairs:
        price = price_of(item_id)
        asked = sum(other for item, other in pairs if item == item_id)
        if asked > available(item_id):
            raise ValueError("not enough available of %r" % (item_id,))
        sold.append({"item_id": item_id, "quantity": quantity, "unit_price_cents": price,
                     "line_total_cents": quantity * price})
    for item_id, quantity in pairs:
        take(item_id, quantity)
    sale = {"id": "S%d" % (len(state) + 1), "customer_id": customer_id, "lines": sold,
            "total_cents": sum(line["line_total_cents"] for line in sold)}
    state.append(sale)
    return _copy(sale)


def get(state, sale_id):
    for sale in state:
        if sale["id"] == sale_id:
            return _copy(sale)
    raise KeyError(sale_id)


def sales(state):
    return [_copy(sale) for sale in state]


def takings(state):
    return sum(sale["total_cents"] for sale in state)

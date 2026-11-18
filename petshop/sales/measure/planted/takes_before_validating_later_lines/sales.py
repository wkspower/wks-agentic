"""Sales: turn what a customer takes into a recorded sale, wholly or not at all."""
import copy


def new():
    return {"next": 1, "sales": []}


def sell(state, customer_id, lines, price_of, available, take):
    if not isinstance(customer_id, str) or not customer_id:
        raise ValueError("customer_id must be a non-empty string")
    if not lines:
        raise ValueError("a sale needs at least one line")
    priced = []
    for item_id, quantity in lines:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("quantity must be an int of 1 or more")
        price = price_of(item_id)
        if quantity > available(item_id):
            raise ValueError("not enough of %s on hand" % item_id)
        take(item_id, quantity)
        priced.append({
            "item_id": item_id,
            "quantity": quantity,
            "unit_price_cents": price,
            "line_total_cents": quantity * price,
        })
    sale = {
        "id": "S%d" % state["next"],
        "customer_id": customer_id,
        "lines": priced,
        "total_cents": sum(line["line_total_cents"] for line in priced),
    }
    state["next"] += 1
    state["sales"].append(sale)
    return copy.deepcopy(sale)


def get(state, sale_id):
    for sale in state["sales"]:
        if sale["id"] == sale_id:
            return copy.deepcopy(sale)
    raise KeyError(sale_id)


def sales(state):
    return copy.deepcopy(state["sales"])


def takings(state):
    return sum(sale["total_cents"] for sale in state["sales"])

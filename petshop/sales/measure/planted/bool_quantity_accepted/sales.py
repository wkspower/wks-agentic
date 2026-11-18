"""Sales: turn what a customer takes into a recorded sale, wholly or not at all."""
import copy


def new():
    return {"next": 1, "sales": []}


def _priced(customer_id, lines, price_of, available):
    if not isinstance(customer_id, str) or not customer_id:
        raise ValueError("customer_id must be a non-empty string")
    if not lines:
        raise ValueError("a sale needs at least one line")
    asked = {}
    priced = []
    for item_id, quantity in lines:
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("quantity must be an int of 1 or more")
        price = price_of(item_id)
        asked[item_id] = asked.get(item_id, 0) + quantity
        priced.append({
            "item_id": item_id,
            "quantity": quantity,
            "unit_price_cents": price,
            "line_total_cents": quantity * price,
        })
    for item_id, wanted in asked.items():
        if wanted > available(item_id):
            raise ValueError("not enough of %s on hand" % item_id)
    return priced


def sell(state, customer_id, lines, price_of, available, take):
    priced = _priced(customer_id, lines, price_of, available)
    for line in priced:
        take(line["item_id"], line["quantity"])
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

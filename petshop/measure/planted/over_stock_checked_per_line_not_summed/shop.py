#!/usr/bin/env python3
"""Pet shop in one file: python3 shop.py --state FILE COMMAND ..."""
import json
import os
import sys


class Refused(Exception):
    pass


def number(text):
    if not (text.isascii() and text.isdigit()):
        raise Refused("not a whole number of 0 or more: %r" % text)
    return int(text)


def load(path):
    if os.path.exists(path):
        with open(path) as handle:
            return json.load(handle)
    return {"items": {}, "stock": {}, "customers": [], "sales": []}


def save(path, state):
    with open(path, "w") as handle:
        json.dump(state, handle, indent=1)


def item(state, item_id):
    if item_id not in state["items"]:
        raise Refused("unknown item: %s" % item_id)
    return state["items"][item_id]


def add_item(state, args):
    if len(args) != 4:
        raise Refused("usage: add-item ID NAME KIND PRICE_CENTS")
    item_id, name, kind, price = args
    if not item_id or not name:
        raise Refused("id and name must not be empty")
    if kind not in ("animal", "product"):
        raise Refused("kind must be animal or product")
    if item_id in state["items"]:
        raise Refused("item exists: %s" % item_id)
    state["items"][item_id] = {"name": name, "kind": kind, "price_cents": number(price)}
    return item_id


def receive(state, args):
    if len(args) != 2:
        raise Refused("usage: receive ID QUANTITY")
    item(state, args[0])
    quantity = number(args[1])
    if quantity < 1:
        raise Refused("quantity must be 1 or more")
    state["stock"][args[0]] = state["stock"].get(args[0], 0) + quantity
    return state["stock"][args[0]]


def register(state, args):
    if len(args) != 1:
        raise Refused("usage: register NAME")
    if not args[0].strip():
        raise Refused("name must not be empty")
    state["customers"].append(args[0].strip())
    return "C%d" % len(state["customers"])


def sell(state, args):
    if len(args) < 2:
        raise Refused("usage: sell CUSTOMER_ID ID=QUANTITY [ID=QUANTITY ...]")
    customer = args[0]
    if customer not in ["C%d" % n for n in range(1, len(state["customers"]) + 1)]:
        raise Refused("unknown customer: %s" % customer)
    lines = []
    asked = {}
    for part in args[1:]:
        item_id, equals, text = part.partition("=")
        if not equals:
            raise Refused("expected ID=QUANTITY, got %r" % part)
        quantity = number(text)
        if quantity < 1:
            raise Refused("quantity must be 1 or more")
        price = item(state, item_id)["price_cents"]
        asked[item_id] = asked.get(item_id, 0) + quantity
        lines.append([item_id, quantity, price])
    for item_id, quantity, price in lines:
        if quantity > state["stock"].get(item_id, 0):
            raise Refused("not enough on hand: %s" % item_id)
    for item_id, quantity, price in lines:
        state["stock"][item_id] -= quantity
    total = sum(quantity * price for item_id, quantity, price in lines)
    state["sales"].append({"customer": customer, "lines": lines, "total_cents": total})
    return "S%d %d" % (len(state["sales"]), total)


def stock(state, args):
    if len(args) != 1:
        raise Refused("usage: stock ID")
    item(state, args[0])
    return state["stock"].get(args[0], 0)


def takings(state, args):
    if args:
        raise Refused("usage: takings")
    return sum(sale["total_cents"] for sale in state["sales"])


COMMANDS = {"add-item": add_item, "receive": receive, "register": register,
            "sell": sell, "stock": stock, "takings": takings}


def main(argv):
    try:
        if len(argv) < 3 or argv[0] != "--state":
            raise Refused("usage: shop.py --state FILE COMMAND ...")
        path = argv[1]
        if argv[2] not in COMMANDS:
            raise Refused("unknown command: %s" % argv[2])
        state = load(path)
        line = COMMANDS[argv[2]](state, argv[3:])
        save(path, state)
    except Refused as why:
        sys.stderr.write("refused: %s\n" % why)
        return 1
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

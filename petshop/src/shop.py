"""Pet shop: sells animals and products to registered customers and keeps the stock right.

Usage: python3 shop.py --state FILE COMMAND ...
Prints one line and exits 0; a refused command exits 1 and leaves FILE as it was.
"""
import json
import os
import sys

import catalog
import customers
import sales
import stock

UNITS = {"catalog": catalog, "stock": stock, "customers": customers, "sales": sales}


def number(text):
    """The whole number written in `text`, digits only."""
    if not (text.isascii() and text.isdigit()):
        raise ValueError("not a whole number: %r" % text)
    return int(text)


def add_item(shop, item_id, name, kind, price_cents):
    catalog.add(shop["catalog"], item_id, name, kind, number(price_cents))
    return item_id


def receive(shop, item_id, quantity):
    catalog.get(shop["catalog"], item_id)
    return stock.receive(shop["stock"], item_id, number(quantity))


def register(shop, name):
    return customers.register(shop["customers"], name)


def sell(shop, customer_id, first_line, *more_lines):
    customers.get(shop["customers"], customer_id)
    lines = []
    for line in (first_line,) + more_lines:
        item_id, equals, quantity = line.rpartition("=")
        if not equals:
            raise ValueError("not ID=QUANTITY: %r" % line)
        lines.append((item_id, number(quantity)))
    sale = sales.sell(
        shop["sales"], customer_id, lines,
        lambda item_id: catalog.get(shop["catalog"], item_id)["price_cents"],
        lambda item_id: stock.on_hand(shop["stock"], item_id),
        lambda item_id, quantity: stock.remove(shop["stock"], item_id, quantity))
    return "%s %d" % (sale["id"], sale["total_cents"])


def stock_of(shop, item_id):
    catalog.get(shop["catalog"], item_id)
    return stock.on_hand(shop["stock"], item_id)


def takings(shop):
    return sales.takings(shop["sales"])


COMMANDS = {"add-item": add_item, "receive": receive, "register": register, "sell": sell,
            "stock": stock_of, "takings": takings}


def main(arguments):
    try:
        if len(arguments) < 3 or arguments[0] != "--state":
            raise ValueError("usage: shop.py --state FILE COMMAND ...")
        path, command = arguments[1:3]
        text = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8") as file:
                text = file.read()
        shop = json.loads(text) if text else {name: unit.new() for name, unit in UNITS.items()}
        line = COMMANDS[command](shop, *arguments[3:])
        with open(path, "w", encoding="utf-8") as file:
            json.dump(shop, file)
    except Exception as error:
        sys.stderr.write("shop: refused: %s: %s\n" % (type(error).__name__, error))
        return 1
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

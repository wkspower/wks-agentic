#!/usr/bin/env python3
"""Measure of sales. Usage: check.py UNIT_DIR (the folder holding work/sales.py).
The stock here is a stand-in written by the measure, with the three calls sales
may use: product, remove, receive. Customer 7 exists, others do not."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "measure"))
from scenarios import main, refuses, scenario, through_json



class Shelf:
    """Stand-in for the stock: product 1 costs 2500 and has 10; product 2 costs 1800 and has 1."""

    def __init__(self):
        self.rows = {1: {"id": 1, "name": "Dog food 1 kg", "price_cents": 2500, "quantity": 10},
                     2: {"id": 2, "name": "Shampoo", "price_cents": 1800, "quantity": 1}}

    def product(self, ident):
        if ident not in self.rows:
            raise LookupError("no such product")
        return dict(self.rows[ident])

    def remove(self, ident, quantity):
        if self.product(ident)["quantity"] < quantity or quantity <= 0:
            raise ValueError("not enough")
        self.rows[ident]["quantity"] -= quantity

    def receive(self, ident, quantity):
        self.product(ident)
        self.rows[ident]["quantity"] += quantity

    def left(self):
        return [self.rows[1]["quantity"], self.rows[2]["quantity"]]


def counter(m):
    shelf = Shelf()
    return m.Sales({}, shelf, lambda customer_id: customer_id == 7), shelf


WHEN = "2026-11-20T10:30"


@scenario
def sell(m):
    """a sale records its items at the price of the moment, its total and its time, and takes from the stock"""
    s, shelf = counter(m)
    sale = s.sell([(1, 2), (2, 1)], when=WHEN)
    assert sale == {"id": sale["id"], "when": WHEN, "customer_id": None, "status": "sold", "total_cents": 6800,
                    "items": [{"product_id": 1, "quantity": 2, "unit_price_cents": 2500},
                              {"product_id": 2, "quantity": 1, "unit_price_cents": 1800}]}
    assert shelf.left() == [8, 0] and s.sale(sale["id"]) == sale


@scenario
def items_must_be_valid(m):
    """a sale with no items, or with a quantity that is not a whole number above zero, is refused"""
    s, shelf = counter(m)
    refuses(ValueError, s.sell, [])
    for wrong in (0, -1, 1.5):
        refuses(ValueError, s.sell, [(1, wrong)])
    assert shelf.left() == [10, 1] and s.total_cents() == 0


@scenario
def unknown_product(m):
    """a sale with a product that does not exist is refused whole"""
    s, shelf = counter(m)
    refuses(LookupError, s.sell, [(1, 1), (999, 1)])
    assert shelf.left() == [10, 1] and s.total_cents() == 0


@scenario
def all_or_nothing(m):
    """if one item is short of stock the whole sale is refused and no stock moves"""
    s, shelf = counter(m)
    refuses(ValueError, s.sell, [(1, 2), (2, 2)])
    assert shelf.left() == [10, 1] and s.total_cents() == 0


@scenario
def same_product_twice(m):
    """the same product on two lines counts together against the stock"""
    s, shelf = counter(m)
    refuses(ValueError, s.sell, [(1, 6), (1, 5)])
    assert shelf.left() == [10, 1]
    assert s.sell([(1, 6), (1, 4)])["total_cents"] == 25000 and shelf.left() == [0, 1]


@scenario
def customer(m):
    """a sale may name a customer, who must exist"""
    s, shelf = counter(m)
    assert s.sell([(1, 1)], customer_id=7)["customer_id"] == 7
    refuses(LookupError, s.sell, [(1, 1)], customer_id=999)
    assert shelf.left() == [9, 1]


@scenario
def price_of_the_moment(m):
    """a later change of price does not change a sale already made"""
    s, shelf = counter(m)
    sale = s.sell([(1, 2)])
    shelf.rows[1]["price_cents"] = 9999
    assert s.sale(sale["id"])["total_cents"] == 5000 and s.total_cents() == 5000


@scenario
def cancel(m):
    """a cancelled sale gives its goods back to the stock, once, and stays in the record as cancelled"""
    s, shelf = counter(m)
    sale = s.sell([(1, 2), (2, 1)])
    s.cancel(sale["id"])
    assert shelf.left() == [10, 1] and s.sale(sale["id"])["status"] == "cancelled" and s.total_cents() == 0
    refuses(ValueError, s.cancel, sale["id"])
    refuses(LookupError, s.cancel, 999)
    assert shelf.left() == [10, 1]


@scenario
def unknown_sale(m):
    """a sale that does not exist is refused"""
    s, _ = counter(m)
    refuses(LookupError, s.sale, 999)


@scenario
def day_and_total(m):
    """the sales of a day in order of time, and the total sold, of a day or of all days, without the cancelled"""
    s, _ = counter(m)
    late = s.sell([(1, 1)], when="2026-11-20T16:00")
    early = s.sell([(1, 2)], when="2026-11-20T09:00")
    other = s.sell([(1, 1)], when="2026-11-21T09:00")
    gone = s.sell([(2, 1)], when="2026-11-20T12:00")
    s.cancel(gone["id"])
    assert [x["id"] for x in s.day("2026-11-20")] == [early["id"], gone["id"], late["id"]]
    assert s.total_cents("2026-11-20") == 7500 and s.total_cents("2026-11-21") == 2500 and s.total_cents() == 10000
    assert s.total_cents("2026-11-22") == 0


@scenario
def time(m):
    """a sale with no time given takes the time of the moment; a time that is not one is refused"""
    s, shelf = counter(m)
    import datetime
    sale = s.sell([(1, 1)])
    datetime.datetime.strptime(sale["when"], "%Y-%m-%dT%H:%M")
    refuses(ValueError, s.sell, [(1, 1)], when="yesterday")
    assert shelf.left() == [9, 1]


@scenario
def copies(m):
    """what is read is a copy, items included"""
    s, _ = counter(m)
    sale = s.sell([(1, 2)])
    sale["items"][0]["quantity"] = 99
    s.sale(sale["id"])["total_cents"] = 0
    assert s.sale(sale["id"])["items"][0]["quantity"] == 2 and s.total_cents() == 5000


@scenario
def state_is_data(m):
    """everything lives in the state it was given, which survives being written as JSON"""
    state, shelf = {}, Shelf()
    s = m.Sales(state, shelf, lambda customer_id: True)
    sale = s.sell([(1, 2)], when=WHEN)
    again = m.Sales(through_json(state), shelf, lambda customer_id: True)
    assert again.sale(sale["id"]) == sale and again.sell([(1, 1)])["id"] != sale["id"]
    again.cancel(sale["id"])
    assert shelf.left() == [9, 1]


class TolerantShelf(Shelf):
    """A stock that takes "1" for 1: sales must not rely on the stock to refuse it."""

    def product(self, ident):
        return super().product(int(ident))

    def remove(self, ident, quantity):
        super().remove(int(ident), quantity)

    def receive(self, ident, quantity):
        super().receive(int(ident), quantity)


@scenario
def ids_are_numbers(m):
    """a product id that is not a whole number is refused whatever the stock tolerates, and no stock moves"""
    shelf = TolerantShelf()
    s = m.Sales({}, shelf, lambda customer_id: True)
    refuses(ValueError, s.sell, [(1, 6), ("1", 5)])
    refuses(ValueError, s.sell, [("1", 1)])
    refuses(ValueError, s.sell, [(1.0, 1)])
    assert shelf.left() == [10, 1] and s.total_cents() == 0


if __name__ == "__main__":
    main("sales", expected=14)

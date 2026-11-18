#!/usr/bin/env python3
"""Measure of stock. Usage: check.py UNIT_DIR (the folder holding work/stock.py).
Prices are whole cents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "measure"))
from scenarios import main, refuses, scenario, through_json



def shelf(m):
    s = m.Stock({})
    return s, s.add_product("Dog food 1 kg", 2500, 10)


@scenario
def add(m):
    """a product is added and read back with name, price in cents and quantity"""
    s, food = shelf(m)
    assert s.product(food) == {"id": food, "name": "Dog food 1 kg", "price_cents": 2500, "quantity": 10}
    assert s.product(s.add_product("Shampoo", 1800))["quantity"] == 0


@scenario
def valid_product(m):
    """a product with no name, a price that is not whole cents or negative, or a negative quantity is refused"""
    s, _ = shelf(m)
    refuses(ValueError, s.add_product, " ", 100, 1)
    refuses(ValueError, s.add_product, "Collar", -1, 1)
    refuses(ValueError, s.add_product, "Collar", 19.9, 1)
    refuses(ValueError, s.add_product, "Collar", "1990", 1)
    refuses(ValueError, s.add_product, "Collar", True, 1)
    refuses(ValueError, s.add_product, "Collar", 1990, -1)
    refuses(ValueError, s.add_product, "Collar", 1990, 1.5)
    assert len(s.products()) == 1
    s.add_product("Free sample", 0, 1)


@scenario
def receive(m):
    """received goods add to the quantity; nothing or less is refused"""
    s, food = shelf(m)
    s.receive(food, 5)
    assert s.product(food)["quantity"] == 15
    for wrong in (0, -1, 1.5, "2"):
        refuses(ValueError, s.receive, food, wrong)
    assert s.product(food)["quantity"] == 15


@scenario
def remove(m):
    """goods leave the stock, down to zero"""
    s, food = shelf(m)
    s.remove(food, 4)
    s.remove(food, 6)
    assert s.product(food)["quantity"] == 0


@scenario
def never_negative(m):
    """taking more than there is is refused and the quantity stays"""
    s, food = shelf(m)
    refuses(ValueError, s.remove, food, 11)
    for wrong in (0, -1, 1.5):
        refuses(ValueError, s.remove, food, wrong)
    assert s.product(food)["quantity"] == 10


@scenario
def unknown(m):
    """a product that does not exist is refused everywhere"""
    s, _ = shelf(m)
    refuses(LookupError, s.product, 999)
    refuses(LookupError, s.receive, 999, 1)
    refuses(LookupError, s.remove, 999, 1)
    refuses(LookupError, s.set_price, 999, 1)


@scenario
def price(m):
    """the price is changed, in whole cents"""
    s, food = shelf(m)
    s.set_price(food, 2750)
    assert s.product(food)["price_cents"] == 2750
    refuses(ValueError, s.set_price, food, -5)
    refuses(ValueError, s.set_price, food, 27.5)
    assert s.product(food)["price_cents"] == 2750


@scenario
def listing(m):
    """all products, in order of name"""
    s, food = shelf(m)
    s.add_product("Collar", 1990, 3)
    assert [p["name"] for p in s.products()] == ["Collar", "Dog food 1 kg"]


@scenario
def low(m):
    """what is running low: products at or below a quantity"""
    s, food = shelf(m)
    collar = s.add_product("Collar", 1990, 3)
    empty = s.add_product("Shampoo", 1800)
    assert sorted(p["id"] for p in s.low(3)) == sorted([collar, empty])
    assert [p["id"] for p in s.low(0)] == [empty]


@scenario
def copies(m):
    """what is read is a copy"""
    s, food = shelf(m)
    s.product(food)["quantity"] = 0
    s.products()[0]["quantity"] = 0
    assert s.product(food)["quantity"] == 10


@scenario
def state_is_data(m):
    """everything lives in the state it was given, which survives being written as JSON"""
    state = {}
    s = m.Stock(state)
    food = s.add_product("Dog food 1 kg", 2500, 10)
    again = m.Stock(through_json(state))
    again.remove(food, 1)
    assert again.product(food)["quantity"] == 9 and again.add_product("Collar", 1990) != food


if __name__ == "__main__":
    main("stock", expected=11)

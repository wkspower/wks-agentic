#!/usr/bin/env python3
"""Measure of the pet shop. Usage: check.py UNIT_DIR (the folder holding work/shop.py).
A day at the counter, through the whole system and through its command line.
All names and numbers are invented; no real customer data is used."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scenarios import main, refuses, scenario

UNIT = Path(sys.argv[1]).resolve()


def place():
    """A folder for one scenario, under .rehearsal/ of the repository."""
    for folder in Path(__file__).resolve().parents:
        if (folder / "principles.md").exists():
            (folder / ".rehearsal").mkdir(exist_ok=True)
            return Path(tempfile.mkdtemp(prefix="shop-", dir=folder / ".rehearsal"))
    raise AssertionError("repository not found")


def with_place(function):
    def wrapped(m):
        folder = place()
        try:
            function(m, folder / "shop.json")
        finally:
            shutil.rmtree(folder, ignore_errors=True)
    wrapped.__doc__ = function.__doc__
    return scenario(wrapped)


def a_day(shop):
    ana = shop.customers.add_customer("Ana Souza", "555-0101")
    rex = shop.customers.add_pet(ana, "Rex", "dog")
    booking = shop.appointments.book(rex, "bath", "2026-11-20T10:00")
    food = shop.stock.add_product("Dog food 1 kg", 2500, 10)
    sale = shop.sales.sell([(food, 2)], customer_id=ana, when="2026-11-20T10:30")
    return ana, rex, booking, food, sale


def cli(path, *args):
    return subprocess.run([sys.executable, str(UNIT / "work" / "shop.py"), str(path), *args],
                          capture_output=True, text=True)


@with_place
def new_shop(m, path):
    """a shop opened on a file that does not exist starts empty, and saving writes valid JSON"""
    shop = m.Shop(path)
    assert shop.stock.products() == [] and shop.customers.find("") == []
    assert not path.exists(), "opening must not write"
    shop.save()
    assert isinstance(json.loads(path.read_text()), dict)


@with_place
def day_survives(m, path):
    """customer, pet, appointment, product and sale are all there after saving and reopening"""
    shop = m.Shop(path)
    ana, rex, booking, food, sale = a_day(shop)
    shop.save()
    again = m.Shop(path)
    assert again.customers.customer(ana)["name"] == "Ana Souza"
    assert again.customers.pet(rex)["customer_id"] == ana
    assert [a["id"] for a in again.appointments.day("2026-11-20")] == [booking]
    assert again.stock.product(food)["quantity"] == 8
    assert again.sales.sale(sale["id"])["total_cents"] == 5000
    assert again.customers.add_customer("Bia Lima", "555-0102") != ana


@with_place
def nothing_without_save(m, path):
    """what was not saved is not in the file"""
    shop = m.Shop(path)
    shop.save()
    before = path.read_text()
    a_day(shop)
    assert path.read_text() == before
    assert m.Shop(path).stock.products() == []


@with_place
def appointment_needs_pet(m, path):
    """an appointment is refused for a pet the shop does not know"""
    shop = m.Shop(path)
    refuses(LookupError, shop.appointments.book, 999, "bath", "2026-11-20T10:00")
    assert shop.appointments.day("2026-11-20") == []


@with_place
def sale_uses_the_shops_stock(m, path):
    """a sale takes from the shop's stock, and is refused whole when stock is short"""
    shop = m.Shop(path)
    ana, rex, booking, food, sale = a_day(shop)
    shampoo = shop.stock.add_product("Shampoo", 1800, 1)
    refuses(ValueError, shop.sales.sell, [(food, 1), (shampoo, 2)])
    assert shop.stock.product(food)["quantity"] == 8 and shop.stock.product(shampoo)["quantity"] == 1
    shop.sales.cancel(sale["id"])
    assert shop.stock.product(food)["quantity"] == 10


@with_place
def sale_needs_known_customer(m, path):
    """a sale is refused for a customer the shop does not know, and may have no customer"""
    shop = m.Shop(path)
    food = shop.stock.add_product("Dog food 1 kg", 2500, 10)
    refuses(LookupError, shop.sales.sell, [(food, 1)], customer_id=999)
    assert shop.stock.product(food)["quantity"] == 10
    assert shop.sales.sell([(food, 1)])["customer_id"] is None


@with_place
def one_station(m, path):
    """the shop has one station by default: two pets cannot be booked at the same time"""
    shop = m.Shop(path)
    ana = shop.customers.add_customer("Ana Souza", "555-0101")
    rex, mia = shop.customers.add_pet(ana, "Rex", "dog"), shop.customers.add_pet(ana, "Mia", "cat")
    shop.appointments.book(rex, "bath", "2026-11-20T10:00")
    refuses(ValueError, shop.appointments.book, mia, "grooming", "2026-11-20T10:30")
    shop.appointments.book(mia, "grooming", "2026-11-20T11:00")


@with_place
def broken_file(m, path):
    """a file that is not the shop's is refused and left as it was"""
    path.write_text("this is not a shop")
    refuses(ValueError, m.Shop, path)
    assert path.read_text() == "this is not a shop"


@with_place
def command_line(m, path):
    """the staff's command line: each command prints its result as JSON and saves"""
    done = cli(path, "customers", "add_customer", "Ana Souza", "555-0101")
    assert done.returncode == 0, done.stderr
    ana = json.loads(done.stdout)
    rex = json.loads(cli(path, "customers", "add_pet", f"={ana}", "Rex", "dog").stdout)
    assert cli(path, "appointments", "book", f"={rex}", "bath", "2026-11-20T10:00").returncode == 0
    food = json.loads(cli(path, "stock", "add_product", "Dog food 1 kg", "=2500", "=10").stdout)
    sale = json.loads(cli(path, "sales", "sell", f"=[[{food}, 2]]").stdout)
    assert sale["total_cents"] == 5000
    assert json.loads(cli(path, "stock", "product", f"={food}").stdout)["quantity"] == 8
    assert m.Shop(path).customers.pet(rex)["name"] == "Rex"


@with_place
def command_line_refusal(m, path):
    """a refused command exits with an error, says why, and leaves the file as it was"""
    cli(path, "stock", "add_product", "Shampoo", "=1800", "=1")
    before = path.read_text()
    done = cli(path, "appointments", "book", "=999", "bath", "2026-11-20T10:00")
    assert done.returncode != 0 and done.stderr.strip() and "Traceback" not in done.stderr
    assert cli(path, "stock", "remove", "=1", "=5").returncode != 0
    assert cli(path, "nowhere", "nothing").returncode != 0
    assert cli(path, "stock", "_secret").returncode != 0
    assert path.read_text() == before


if __name__ == "__main__":
    main("shop", expected=10)

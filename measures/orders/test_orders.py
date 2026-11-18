"""Measure of the orders unit (units/pet-shop/orders/unit.md), against petshop.orders."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from petshop.catalog import Catalog  # noqa: E402
from petshop.orders import Orders  # noqa: E402
from petshop.stock import InsufficientStock, Stock  # noqa: E402

BAD_QTYS = (0, -1, True, False, 1.0, "1", None)


class RepricingCatalog:
    """A catalog with the interface of petshop.catalog.Catalog whose prices
    the measure can change, to see that an order keeps the price it was placed at."""

    def __init__(self):
        self._c = Catalog()
        self._price = {}

    def add(self, sku, name, kind, price_cents):
        it = self._c.add(sku, name, kind, price_cents)
        self._price[sku] = price_cents
        return it

    def _fix(self, it):
        it["price_cents"] = self._price[it["sku"]]
        return it

    def get(self, sku):
        return self._fix(self._c.get(sku))

    def items(self, kind=None):
        return [self._fix(i) for i in self._c.items(kind)]

    def set_price(self, sku, price_cents):
        self._price[sku] = price_cents


class Base(unittest.TestCase):
    def setUp(self):
        self.c = RepricingCatalog()
        self.c.add("dog", "Rex", "pet", 50000)
        self.c.add("cat", "Tom", "pet", 30000)
        self.c.add("food", "Kibble", "supply", 1299)
        self.c.add("toy", "Ball", "supply", 250)
        self.s = Stock(self.c)
        self.s.receive("dog", 1)
        self.s.receive("food", 10)
        self.s.receive("toy", 4)
        self.o = Orders(self.c, self.s)

    def levels(self):
        return {sku: self.s.available(sku) for sku in ("dog", "cat", "food", "toy")}


class PlaceTest(Base):
    def test_place_returns_order(self):
        order = self.o.place([("food", 2), ("dog", 1)])
        self.assertEqual(set(order), {"id", "status", "lines", "total_cents"})
        self.assertIsInstance(order["id"], str)
        self.assertNotEqual(order["id"], "")
        self.assertEqual(order["status"], "placed")
        self.assertEqual(order["lines"], [
            {"sku": "food", "qty": 2, "price_cents": 1299},
            {"sku": "dog", "qty": 1, "price_cents": 50000},
        ])
        self.assertEqual(order["total_cents"], 2 * 1299 + 50000)

    def test_place_takes_stock(self):
        self.o.place([("food", 3), ("toy", 4), ("dog", 1)])
        self.assertEqual(self.levels(), {"dog": 0, "cat": 0, "food": 7, "toy": 0})

    def test_total_is_sum_of_lines(self):
        order = self.o.place([("toy", 3), ("food", 7)])
        self.assertEqual(order["total_cents"], 3 * 250 + 7 * 1299)
        self.assertEqual(order["total_cents"],
                         sum(l["qty"] * l["price_cents"] for l in order["lines"]))

    def test_total_is_int(self):
        order = self.o.place([("toy", 1)])
        self.assertIs(type(order["total_cents"]), int)

    def test_ids_unique_non_empty(self):
        self.s.receive("food", 100)
        ids = [self.o.place([("food", 1)])["id"] for _ in range(50)]
        self.assertEqual(len(set(ids)), 50)
        for i in ids:
            self.assertIsInstance(i, str)
            self.assertNotEqual(i, "")

    def test_merged_lines(self):
        order = self.o.place([("food", 2), ("toy", 1), ("food", 3)])
        self.assertEqual(order["lines"], [
            {"sku": "food", "qty": 5, "price_cents": 1299},
            {"sku": "toy", "qty": 1, "price_cents": 250},
        ])
        self.assertEqual(order["total_cents"], 5 * 1299 + 250)
        self.assertEqual(self.s.available("food"), 5)

    def test_merged_in_order_of_first_appearance(self):
        order = self.o.place([("toy", 1), ("food", 1), ("toy", 1), ("food", 1)])
        self.assertEqual([l["sku"] for l in order["lines"]], ["toy", "food"])
        self.assertEqual([l["qty"] for l in order["lines"]], [2, 2])

    def test_merged_quantity_must_be_available(self):
        before = self.levels()
        with self.assertRaises(InsufficientStock):
            self.o.place([("food", 6), ("food", 5)])
        self.assertEqual(self.levels(), before)

    def test_merged_pet_twice(self):
        before = self.levels()
        with self.assertRaises(InsufficientStock):
            self.o.place([("dog", 1), ("dog", 1)])
        self.assertEqual(self.levels(), before)

    def test_price_fixed_at_time_of_order(self):
        order = self.o.place([("food", 2)])
        self.c.set_price("food", 9999)
        got = self.o.get(order["id"])
        self.assertEqual(got["lines"][0]["price_cents"], 1299)
        self.assertEqual(got["total_cents"], 2 * 1299)
        later = self.o.place([("food", 1)])
        self.assertEqual(later["lines"][0]["price_cents"], 9999)
        cancelled = self.o.cancel(order["id"])
        self.assertEqual(cancelled["lines"][0]["price_cents"], 1299)
        self.assertEqual(cancelled["total_cents"], 2 * 1299)

    def test_price_from_catalog(self):
        self.c.set_price("toy", 777)
        order = self.o.place([("toy", 2)])
        self.assertEqual(order["lines"][0]["price_cents"], 777)
        self.assertEqual(order["total_cents"], 1554)


class PlaceErrorsTest(Base):
    def test_no_lines(self):
        before = self.levels()
        with self.assertRaises(ValueError):
            self.o.place([])
        self.assertEqual(self.levels(), before)

    def test_bad_qty(self):
        before = self.levels()
        for qty in BAD_QTYS:
            with self.subTest(qty=qty), self.assertRaises(ValueError):
                self.o.place([("food", qty)])
        self.assertEqual(self.levels(), before)

    def test_bool_qty_is_not_int(self):
        with self.assertRaises(ValueError):
            self.o.place([("toy", True)])
        self.assertEqual(self.s.available("toy"), 4)

    def test_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.o.place([("fish", 1)])

    def test_insufficient(self):
        with self.assertRaises(InsufficientStock):
            self.o.place([("food", 11)])
        self.assertEqual(self.s.available("food"), 10)

    def test_insufficient_never_received(self):
        with self.assertRaises(InsufficientStock):
            self.o.place([("cat", 1)])

    def test_all_or_nothing_insufficient_last(self):
        before = self.levels()
        with self.assertRaises(InsufficientStock):
            self.o.place([("food", 2), ("toy", 1), ("cat", 1)])
        self.assertEqual(self.levels(), before)

    def test_all_or_nothing_insufficient_middle(self):
        before = self.levels()
        with self.assertRaises(InsufficientStock):
            self.o.place([("dog", 1), ("toy", 5), ("food", 1)])
        self.assertEqual(self.levels(), before)

    def test_all_or_nothing_unknown_last(self):
        before = self.levels()
        with self.assertRaises(KeyError):
            self.o.place([("food", 2), ("dog", 1), ("fish", 1)])
        self.assertEqual(self.levels(), before)

    def test_all_or_nothing_bad_qty_last(self):
        before = self.levels()
        with self.assertRaises(ValueError):
            self.o.place([("food", 2), ("dog", 1), ("toy", 0)])
        self.assertEqual(self.levels(), before)

    def test_failed_place_creates_no_order(self):
        good = self.o.place([("toy", 1)])
        for lines, exc in (([("food", 1), ("cat", 1)], InsufficientStock),
                           ([("food", 1), ("fish", 1)], KeyError),
                           ([("food", 1), ("toy", -1)], ValueError)):
            with self.assertRaises(exc):
                self.o.place(lines)
        # stock still allows exactly what was there before the failures
        self.assertEqual(self.levels(), {"dog": 1, "cat": 0, "food": 10, "toy": 3})
        self.assertEqual(self.o.get(good["id"])["lines"], [{"sku": "toy", "qty": 1, "price_cents": 250}])

    def test_shop_usable_after_failure(self):
        with self.assertRaises(InsufficientStock):
            self.o.place([("food", 10), ("toy", 5)])
        order = self.o.place([("food", 10), ("toy", 4)])
        self.assertEqual(order["status"], "placed")
        self.assertEqual(self.levels(), {"dog": 1, "cat": 0, "food": 0, "toy": 0})


class GetTest(Base):
    def test_get(self):
        order = self.o.place([("food", 1), ("toy", 2)])
        self.assertEqual(self.o.get(order["id"]), order)

    def test_get_absent(self):
        with self.assertRaises(KeyError):
            self.o.get("no-such-order")

    def test_get_absent_on_empty(self):
        with self.assertRaises(KeyError):
            Orders(self.c, self.s).get("1")

    def test_get_is_copy(self):
        order = self.o.place([("food", 1), ("toy", 2)])
        got = self.o.get(order["id"])
        got["status"] = "cancelled"
        got["total_cents"] = 0
        got["lines"][0]["qty"] = 99
        got["lines"][0]["price_cents"] = 1
        got["lines"].append({"sku": "dog", "qty": 1, "price_cents": 1})
        self.assertEqual(self.o.get(order["id"]), order)

    def test_get_distinguishes_orders(self):
        a = self.o.place([("food", 1)])
        b = self.o.place([("toy", 1)])
        self.assertEqual(self.o.get(a["id"])["lines"][0]["sku"], "food")
        self.assertEqual(self.o.get(b["id"])["lines"][0]["sku"], "toy")


class CancelTest(Base):
    def test_cancel_returns_cancelled_order(self):
        order = self.o.place([("food", 2), ("dog", 1)])
        cancelled = self.o.cancel(order["id"])
        expected = dict(order, status="cancelled")
        self.assertEqual(cancelled, expected)
        self.assertEqual(self.o.get(order["id"]), expected)

    def test_cancel_restores_stock(self):
        before = self.levels()
        order = self.o.place([("food", 3), ("toy", 1), ("dog", 1), ("food", 2)])
        self.o.cancel(order["id"])
        self.assertEqual(self.levels(), before)

    def test_cancel_only_that_order(self):
        a = self.o.place([("food", 3)])
        self.o.place([("food", 4)])
        self.o.cancel(a["id"])
        self.assertEqual(self.s.available("food"), 6)

    def test_cancel_absent(self):
        with self.assertRaises(KeyError):
            self.o.cancel("no-such-order")

    def test_cancel_twice(self):
        order = self.o.place([("food", 3)])
        self.o.cancel(order["id"])
        with self.assertRaises(ValueError):
            self.o.cancel(order["id"])
        self.assertEqual(self.s.available("food"), 10)
        self.assertEqual(self.o.get(order["id"])["status"], "cancelled")

    def test_cancelled_pet_can_be_ordered_again(self):
        a = self.o.place([("dog", 1)])
        self.o.cancel(a["id"])
        b = self.o.place([("dog", 1)])
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(self.s.available("dog"), 0)


class RealCatalogTest(unittest.TestCase):
    def test_with_real_catalog_and_stock(self):
        c = Catalog()
        c.add("bird", "Tweety", "pet", 4000)
        c.add("seed", "Seed", "supply", 300)
        s = Stock(c)
        s.receive("bird", 1)
        s.receive("seed", 5)
        o = Orders(c, s)
        order = o.place([("seed", 2), ("bird", 1)])
        self.assertEqual(order["total_cents"], 4600)
        self.assertEqual((s.available("bird"), s.available("seed")), (0, 3))
        o.cancel(order["id"])
        self.assertEqual((s.available("bird"), s.available("seed")), (1, 5))


if __name__ == "__main__":
    unittest.main()

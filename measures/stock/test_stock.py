"""Measure of the stock unit (units/pet-shop/stock/unit.md), against petshop.stock."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from petshop.catalog import Catalog  # noqa: E402
from petshop.stock import InsufficientStock, Stock  # noqa: E402

BAD_QTYS = (0, -1, True, False, 1.0, 2.5, "1", None)


class Base(unittest.TestCase):
    def setUp(self):
        self.c = Catalog()
        self.c.add("dog", "Rex", "pet", 50000)
        self.c.add("cat", "Tom", "pet", 30000)
        self.c.add("food", "Kibble", "supply", 1299)
        self.s = Stock(self.c)


class ClassesTest(unittest.TestCase):
    def test_insufficient_stock_is_exception(self):
        self.assertTrue(issubclass(InsufficientStock, Exception))


class AvailableTest(Base):
    def test_never_received_is_zero(self):
        self.assertEqual(self.s.available("food"), 0)
        self.assertEqual(self.s.available("dog"), 0)

    def test_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.s.available("fish")

    def test_item_added_to_catalog_later(self):
        self.c.add("bowl", "Bowl", "supply", 500)
        self.assertEqual(self.s.available("bowl"), 0)
        self.assertEqual(self.s.receive("bowl", 2), 2)

    def test_stocks_are_independent(self):
        self.s.receive("food", 5)
        self.assertEqual(Stock(self.c).available("food"), 0)


class ReceiveTest(Base):
    def test_receive_returns_new_quantity(self):
        self.assertEqual(self.s.receive("food", 3), 3)
        self.assertEqual(self.s.receive("food", 4), 7)
        self.assertEqual(self.s.available("food"), 7)

    def test_receive_is_per_sku(self):
        self.s.receive("food", 3)
        self.s.receive("dog", 1)
        self.assertEqual(self.s.available("food"), 3)
        self.assertEqual(self.s.available("dog"), 1)
        self.assertEqual(self.s.available("cat"), 0)

    def test_receive_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.s.receive("fish", 1)

    def test_receive_bad_qty(self):
        self.s.receive("food", 2)
        for qty in BAD_QTYS:
            with self.subTest(qty=qty), self.assertRaises(ValueError):
                self.s.receive("food", qty)
        self.assertEqual(self.s.available("food"), 2)

    def test_receive_bool_is_not_int(self):
        with self.assertRaises(ValueError):
            self.s.receive("food", True)
        self.assertEqual(self.s.available("food"), 0)

    def test_pet_one(self):
        self.assertEqual(self.s.receive("dog", 1), 1)

    def test_pet_never_above_one_at_once(self):
        with self.assertRaises(ValueError):
            self.s.receive("dog", 2)
        self.assertEqual(self.s.available("dog"), 0)

    def test_pet_never_above_one_cumulative(self):
        self.s.receive("dog", 1)
        with self.assertRaises(ValueError):
            self.s.receive("dog", 1)
        self.assertEqual(self.s.available("dog"), 1)

    def test_supply_has_no_bound(self):
        self.assertEqual(self.s.receive("food", 1000), 1000)

    def test_pet_again_after_taken(self):
        self.s.receive("dog", 1)
        self.s.take("dog", 1)
        self.assertEqual(self.s.receive("dog", 1), 1)


class TakeTest(Base):
    def test_take_returns_new_quantity(self):
        self.s.receive("food", 10)
        self.assertEqual(self.s.take("food", 3), 7)
        self.assertEqual(self.s.take("food", 7), 0)
        self.assertEqual(self.s.available("food"), 0)

    def test_take_pet(self):
        self.s.receive("dog", 1)
        self.assertEqual(self.s.take("dog", 1), 0)
        self.assertEqual(self.s.available("dog"), 0)

    def test_take_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.s.take("fish", 1)

    def test_take_bad_qty(self):
        self.s.receive("food", 5)
        for qty in BAD_QTYS:
            with self.subTest(qty=qty), self.assertRaises(ValueError):
                self.s.take("food", qty)
        self.assertEqual(self.s.available("food"), 5)

    def test_take_more_than_available(self):
        self.s.receive("food", 2)
        with self.assertRaises(InsufficientStock):
            self.s.take("food", 3)
        self.assertEqual(self.s.available("food"), 2)

    def test_take_never_received(self):
        with self.assertRaises(InsufficientStock):
            self.s.take("food", 1)
        self.assertEqual(self.s.available("food"), 0)

    def test_take_pet_twice(self):
        self.s.receive("dog", 1)
        self.s.take("dog", 1)
        with self.assertRaises(InsufficientStock):
            self.s.take("dog", 1)
        self.assertEqual(self.s.available("dog"), 0)

    def test_take_does_not_go_below_zero(self):
        self.s.receive("food", 1)
        for _ in range(3):
            with self.assertRaises(InsufficientStock):
                self.s.take("food", 2)
        self.assertEqual(self.s.available("food"), 1)


class PutBackTest(Base):
    def test_put_back_adds(self):
        self.s.receive("food", 5)
        self.s.take("food", 3)
        self.assertEqual(self.s.put_back("food", 3), 5)
        self.assertEqual(self.s.available("food"), 5)

    def test_put_back_pet(self):
        self.s.receive("dog", 1)
        self.s.take("dog", 1)
        self.assertEqual(self.s.put_back("dog", 1), 1)

    def test_put_back_pet_bound(self):
        self.s.receive("dog", 1)
        with self.assertRaises(ValueError):
            self.s.put_back("dog", 1)
        self.assertEqual(self.s.available("dog"), 1)

    def test_put_back_pet_bound_from_zero(self):
        with self.assertRaises(ValueError):
            self.s.put_back("cat", 2)
        self.assertEqual(self.s.available("cat"), 0)

    def test_put_back_unknown_sku(self):
        with self.assertRaises(KeyError):
            self.s.put_back("fish", 1)

    def test_put_back_bad_qty(self):
        for qty in BAD_QTYS:
            with self.subTest(qty=qty), self.assertRaises(ValueError):
                self.s.put_back("food", qty)
        self.assertEqual(self.s.available("food"), 0)


class CatalogInterfaceTest(unittest.TestCase):
    """Stock relies only on catalog.get(sku), as the declaration says."""

    class OnlyGet:
        def __init__(self):
            self._d = {"p": {"sku": "p", "name": "P", "kind": "pet", "price_cents": 1},
                       "s": {"sku": "s", "name": "S", "kind": "supply", "price_cents": 1}}

        def get(self, sku):
            return dict(self._d[sku])

    def test_works_with_any_catalog_offering_get(self):
        s = Stock(self.OnlyGet())
        self.assertEqual(s.receive("s", 4), 4)
        self.assertEqual(s.take("s", 1), 3)
        self.assertEqual(s.receive("p", 1), 1)
        with self.assertRaises(ValueError):
            s.receive("p", 1)
        with self.assertRaises(KeyError):
            s.available("x")


if __name__ == "__main__":
    unittest.main()

"""Measure of the catalog unit (units/pet-shop/catalog/unit.md), against petshop.catalog."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from petshop.catalog import Catalog  # noqa: E402


def item(sku, name, kind, price):
    return {"sku": sku, "name": name, "kind": kind, "price_cents": price}


class AddTest(unittest.TestCase):
    def setUp(self):
        self.c = Catalog()

    def test_add_returns_item(self):
        self.assertEqual(self.c.add("dog-1", "Rex", "pet", 50000),
                         item("dog-1", "Rex", "pet", 50000))

    def test_add_supply(self):
        self.assertEqual(self.c.add("food-1", "Kibble", "supply", 1299),
                         item("food-1", "Kibble", "supply", 1299))

    def test_add_then_get(self):
        self.c.add("dog-1", "Rex", "pet", 50000)
        self.assertEqual(self.c.get("dog-1"), item("dog-1", "Rex", "pet", 50000))

    def test_price_one_cent_is_valid(self):
        self.assertEqual(self.c.add("x", "X", "supply", 1)["price_cents"], 1)

    def test_empty_sku(self):
        with self.assertRaises(ValueError):
            self.c.add("", "Rex", "pet", 100)

    def test_sku_not_str(self):
        for sku in (None, 1, b"dog", ["dog"]):
            with self.subTest(sku=sku), self.assertRaises(ValueError):
                self.c.add(sku, "Rex", "pet", 100)

    def test_empty_name(self):
        with self.assertRaises(ValueError):
            self.c.add("dog-1", "", "pet", 100)

    def test_name_not_str(self):
        for name in (None, 5, b"Rex"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.c.add("dog-1", name, "pet", 100)

    def test_bad_kind(self):
        for kind in ("food", "", "Pet", "PET", None, 1):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.c.add("dog-1", "Rex", kind, 100)

    def test_price_not_int(self):
        for price in (10.0, 10.5, "100", None, [100]):
            with self.subTest(price=price), self.assertRaises(ValueError):
                self.c.add("dog-1", "Rex", "pet", price)

    def test_price_bool_is_not_int(self):
        for price in (True, False):
            with self.subTest(price=price), self.assertRaises(ValueError):
                self.c.add("dog-1", "Rex", "pet", price)

    def test_price_zero(self):
        with self.assertRaises(ValueError):
            self.c.add("dog-1", "Rex", "pet", 0)

    def test_price_negative(self):
        with self.assertRaises(ValueError):
            self.c.add("dog-1", "Rex", "pet", -1)

    def test_invalid_add_changes_nothing(self):
        for args in (("", "n", "pet", 1), ("a", "", "pet", 1), ("a", "n", "x", 1),
                     ("a", "n", "pet", 0), ("a", "n", "pet", True)):
            with self.assertRaises(ValueError):
                self.c.add(*args)
        self.assertEqual(self.c.items(), [])
        with self.assertRaises(KeyError):
            self.c.get("a")

    def test_duplicate_sku(self):
        self.c.add("dog-1", "Rex", "pet", 100)
        with self.assertRaises(KeyError):
            self.c.add("dog-1", "Fido", "pet", 200)

    def test_duplicate_does_not_overwrite(self):
        self.c.add("dog-1", "Rex", "pet", 100)
        with self.assertRaises(KeyError):
            self.c.add("dog-1", "Fido", "supply", 200)
        self.assertEqual(self.c.get("dog-1"), item("dog-1", "Rex", "pet", 100))
        self.assertEqual(len(self.c.items()), 1)


class GetTest(unittest.TestCase):
    def setUp(self):
        self.c = Catalog()
        self.c.add("dog-1", "Rex", "pet", 50000)

    def test_get_absent(self):
        with self.assertRaises(KeyError):
            self.c.get("cat-1")

    def test_get_absent_on_empty(self):
        with self.assertRaises(KeyError):
            Catalog().get("dog-1")

    def test_get_returns_copy(self):
        got = self.c.get("dog-1")
        got["price_cents"] = 1
        got["name"] = "Changed"
        got["extra"] = True
        self.assertEqual(self.c.get("dog-1"), item("dog-1", "Rex", "pet", 50000))

    def test_get_returns_new_object_each_time(self):
        self.assertIsNot(self.c.get("dog-1"), self.c.get("dog-1"))

    def test_add_returns_copy(self):
        got = self.c.add("cat-1", "Tom", "pet", 30000)
        got["price_cents"] = 1
        self.assertEqual(self.c.get("cat-1")["price_cents"], 30000)

    def test_catalogs_are_independent(self):
        other = Catalog()
        with self.assertRaises(KeyError):
            other.get("dog-1")
        other.add("dog-1", "Other", "supply", 5)
        self.assertEqual(self.c.get("dog-1")["name"], "Rex")


class ItemsTest(unittest.TestCase):
    def setUp(self):
        self.c = Catalog()
        self.c.add("m-leash", "Leash", "supply", 900)
        self.c.add("b-cat", "Tom", "pet", 30000)
        self.c.add("z-dog", "Rex", "pet", 50000)
        self.c.add("a-food", "Kibble", "supply", 1299)

    def test_empty(self):
        self.assertEqual(Catalog().items(), [])

    def test_sorted_by_sku(self):
        self.assertEqual([i["sku"] for i in self.c.items()],
                         ["a-food", "b-cat", "m-leash", "z-dog"])

    def test_full_items(self):
        self.assertEqual(self.c.items(), [
            item("a-food", "Kibble", "supply", 1299),
            item("b-cat", "Tom", "pet", 30000),
            item("m-leash", "Leash", "supply", 900),
            item("z-dog", "Rex", "pet", 50000),
        ])

    def test_kind_none_is_all(self):
        self.assertEqual(self.c.items(None), self.c.items())

    def test_filter_pet(self):
        self.assertEqual([i["sku"] for i in self.c.items("pet")], ["b-cat", "z-dog"])

    def test_filter_supply(self):
        self.assertEqual([i["sku"] for i in self.c.items(kind="supply")], ["a-food", "m-leash"])

    def test_filter_without_matches(self):
        c = Catalog()
        c.add("a", "A", "supply", 1)
        self.assertEqual(c.items("pet"), [])

    def test_filter_bad_kind(self):
        for kind in ("food", "", "Pet", 1):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.c.items(kind)

    def test_items_are_copies(self):
        listed = self.c.items()
        listed[0]["price_cents"] = 1
        listed.append(item("q", "Q", "pet", 1))
        self.assertEqual(self.c.get("a-food")["price_cents"], 1299)
        self.assertEqual(len(self.c.items()), 4)
        filtered = self.c.items("pet")
        filtered[0]["name"] = "Changed"
        self.assertEqual(self.c.get("b-cat")["name"], "Tom")

    def test_sorted_is_not_insertion_order(self):
        c = Catalog()
        for sku in ("c", "a", "b", "B", "aa"):
            c.add(sku, sku, "supply", 1)
        self.assertEqual([i["sku"] for i in c.items()], sorted(["c", "a", "b", "B", "aa"]))


if __name__ == "__main__":
    unittest.main()

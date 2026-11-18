"""Measure of the pet-shop unit (units/pet-shop/unit.md), against the WSGI
application petshop.app:application, called in-process (no network).

The application keeps its state for the life of the process and the interface
offers no reset, so every case uses skus of its own and asserts only on them.
"""
import io
import json
import os
import sys
import unittest
import uuid
from wsgiref.util import setup_testing_defaults

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

from petshop.app import application  # noqa: E402

NOT_ROUTED = (404, 405)


def call(method, path, body=None, raw=None, query=""):
    """Calls the application; returns (status code, decoded JSON body)."""
    env = {}
    setup_testing_defaults(env)
    if raw is None:
        raw = b"" if body is None else json.dumps(body).encode("utf-8")
    env.update({
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(len(raw)),
        "wsgi.input": io.BytesIO(raw),
    })
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = headers
        return lambda data: None

    result = application(env, start_response)
    try:
        data = b"".join(result)
    finally:
        if hasattr(result, "close"):
            result.close()
    code = int(captured["status"].split()[0])
    return code, json.loads(data.decode("utf-8"))


def uid():
    return uuid.uuid4().hex[:12]


class Case(unittest.TestCase):
    def setUp(self):
        self.p = "t" + uid() + "-"

    def assertError(self, resp, codes):
        code, body = resp
        if isinstance(codes, int):
            codes = (codes,)
        self.assertIn(code, codes, body)
        self.assertIsInstance(body, dict)
        self.assertEqual(set(body), {"error"}, body)
        self.assertIsInstance(body["error"], str)

    def add(self, suffix, kind="supply", price=100, name=None):
        sku = self.p + suffix
        item = {"sku": sku, "name": name or suffix.title(), "kind": kind, "price_cents": price}
        code, body = call("POST", "/catalog", item)
        self.assertEqual(code, 201, body)
        return sku

    def receive(self, sku, qty):
        code, body = call("POST", "/stock/" + sku, {"qty": qty})
        self.assertEqual(code, 200, body)
        return body["available"]

    def avail(self, sku):
        code, body = call("GET", "/stock/" + sku)
        self.assertEqual(code, 200, body)
        return body["available"]


class CatalogRoutesTest(Case):
    def test_post_returns_201_item(self):
        item = {"sku": self.p + "dog", "name": "Rex", "kind": "pet", "price_cents": 50000}
        self.assertEqual(call("POST", "/catalog", item), (201, item))

    def test_get_item(self):
        item = {"sku": self.p + "food", "name": "Kibble", "kind": "supply", "price_cents": 1299}
        call("POST", "/catalog", item)
        self.assertEqual(call("GET", "/catalog/" + item["sku"]), (200, item))

    def test_get_unknown_item(self):
        self.assertError(call("GET", "/catalog/" + self.p + "none"), 404)

    def test_post_duplicate_is_409(self):
        sku = self.add("dup", price=100)
        self.assertError(call("POST", "/catalog", {"sku": sku, "name": "Other", "kind": "supply",
                                                   "price_cents": 5}), 409)
        self.assertEqual(call("GET", "/catalog/" + sku)[1]["price_cents"], 100)

    def test_post_invalid_is_400(self):
        good = {"sku": self.p + "x", "name": "X", "kind": "pet", "price_cents": 100}
        bad = [
            dict(good, sku=""), dict(good, sku=5), dict(good, name=""), dict(good, name=None),
            dict(good, kind="food"), dict(good, kind="Pet"), dict(good, price_cents=0),
            dict(good, price_cents=-5), dict(good, price_cents=1.5), dict(good, price_cents="100"),
            dict(good, price_cents=True),
        ]
        for field in good:
            missing = dict(good)
            del missing[field]
            bad.append(missing)
        for body in bad:
            with self.subTest(body=body):
                self.assertError(call("POST", "/catalog", body), 400)
        self.assertError(call("GET", "/catalog/" + good["sku"]), 404)

    def test_post_bool_price_is_400(self):
        body = {"sku": self.p + "b", "name": "B", "kind": "supply", "price_cents": True}
        self.assertError(call("POST", "/catalog", body), 400)

    def test_post_not_json_is_400(self):
        self.assertError(call("POST", "/catalog", raw=b"{not json"), 400)

    def test_post_empty_body_is_400(self):
        self.assertError(call("POST", "/catalog", raw=b""), 400)

    def test_post_not_object_is_400(self):
        for body in ([], [1, 2], "item", 3, None):
            with self.subTest(body=body):
                self.assertError(call("POST", "/catalog", raw=json.dumps(body).encode()), 400)

    def test_list_sorted_by_sku(self):
        for s in ("m", "a", "z", "c"):
            self.add(s)
        code, body = call("GET", "/catalog")
        self.assertEqual(code, 200)
        self.assertIsInstance(body, list)
        skus = [i["sku"] for i in body]
        self.assertEqual(skus, sorted(skus))
        mine = [i["sku"] for i in body if i["sku"].startswith(self.p)]
        self.assertEqual(mine, [self.p + s for s in ("a", "c", "m", "z")])

    def test_list_contains_items(self):
        item = {"sku": self.p + "cat", "name": "Tom", "kind": "pet", "price_cents": 30000}
        call("POST", "/catalog", item)
        code, body = call("GET", "/catalog")
        self.assertEqual(code, 200)
        self.assertIn(item, body)

    def test_list_filter_pet(self):
        pet = self.add("pet", kind="pet")
        sup = self.add("sup", kind="supply")
        code, body = call("GET", "/catalog", query="kind=pet")
        self.assertEqual(code, 200)
        self.assertTrue(all(i["kind"] == "pet" for i in body))
        skus = [i["sku"] for i in body]
        self.assertIn(pet, skus)
        self.assertNotIn(sup, skus)
        self.assertEqual(skus, sorted(skus))

    def test_list_filter_supply(self):
        pet = self.add("pet", kind="pet")
        sup = self.add("sup", kind="supply")
        code, body = call("GET", "/catalog", query="kind=supply")
        self.assertEqual(code, 200)
        self.assertTrue(all(i["kind"] == "supply" for i in body))
        skus = [i["sku"] for i in body]
        self.assertIn(sup, skus)
        self.assertNotIn(pet, skus)
        self.assertEqual(skus, sorted(skus))


class StockRoutesTest(Case):
    def test_get_never_received(self):
        sku = self.add("food")
        self.assertEqual(call("GET", "/stock/" + sku), (200, {"sku": sku, "available": 0}))

    def test_post_receive(self):
        sku = self.add("food")
        self.assertEqual(call("POST", "/stock/" + sku, {"qty": 3}), (200, {"sku": sku, "available": 3}))
        self.assertEqual(call("POST", "/stock/" + sku, {"qty": 4}), (200, {"sku": sku, "available": 7}))
        self.assertEqual(call("GET", "/stock/" + sku), (200, {"sku": sku, "available": 7}))

    def test_get_unknown(self):
        self.assertError(call("GET", "/stock/" + self.p + "none"), 404)

    def test_post_unknown(self):
        self.assertError(call("POST", "/stock/" + self.p + "none", {"qty": 1}), 404)

    def test_post_invalid_qty(self):
        sku = self.add("food")
        for body in ({"qty": 0}, {"qty": -1}, {"qty": True}, {"qty": False}, {"qty": 1.5},
                     {"qty": "1"}, {"qty": None}, {}, [], 3):
            with self.subTest(body=body):
                self.assertError(call("POST", "/stock/" + sku, raw=json.dumps(body).encode()), 400)
        self.assertError(call("POST", "/stock/" + sku, raw=b"nope"), 400)
        self.assertEqual(self.avail(sku), 0)

    def test_post_bool_qty_is_400(self):
        sku = self.add("food")
        self.assertError(call("POST", "/stock/" + sku, {"qty": True}), 400)
        self.assertEqual(self.avail(sku), 0)

    def test_pet_one(self):
        sku = self.add("dog", kind="pet")
        self.assertEqual(call("POST", "/stock/" + sku, {"qty": 1}), (200, {"sku": sku, "available": 1}))

    def test_pet_above_one_is_409(self):
        sku = self.add("dog", kind="pet")
        self.assertError(call("POST", "/stock/" + sku, {"qty": 2}), 409)
        self.assertEqual(self.avail(sku), 0)
        self.receive(sku, 1)
        self.assertError(call("POST", "/stock/" + sku, {"qty": 1}), 409)
        self.assertEqual(self.avail(sku), 1)


class OrderRoutesTest(Case):
    def setUp(self):
        Case.setUp(self)
        self.dog = self.add("dog", kind="pet", price=50000)
        self.cat = self.add("cat", kind="pet", price=30000)
        self.food = self.add("food", price=1299)
        self.toy = self.add("toy", price=250)
        self.receive(self.dog, 1)
        self.receive(self.food, 10)
        self.receive(self.toy, 4)

    def levels(self):
        return [self.avail(s) for s in (self.dog, self.cat, self.food, self.toy)]

    def order(self, *lines):
        return call("POST", "/orders", {"lines": [{"sku": s, "qty": q} for s, q in lines]})

    def test_place_201(self):
        code, body = self.order((self.food, 2), (self.dog, 1))
        self.assertEqual(code, 201, body)
        self.assertEqual(set(body), {"id", "status", "lines", "total_cents"})
        self.assertIsInstance(body["id"], str)
        self.assertNotEqual(body["id"], "")
        self.assertEqual(body["status"], "placed")
        self.assertEqual(body["lines"], [
            {"sku": self.food, "qty": 2, "price_cents": 1299},
            {"sku": self.dog, "qty": 1, "price_cents": 50000},
        ])
        self.assertEqual(body["total_cents"], 2 * 1299 + 50000)
        self.assertEqual(self.levels(), [0, 0, 8, 4])

    def test_merged_lines(self):
        code, body = self.order((self.toy, 1), (self.food, 2), (self.toy, 2))
        self.assertEqual(code, 201, body)
        self.assertEqual(body["lines"], [
            {"sku": self.toy, "qty": 3, "price_cents": 250},
            {"sku": self.food, "qty": 2, "price_cents": 1299},
        ])
        self.assertEqual(body["total_cents"], 3 * 250 + 2 * 1299)

    def test_get_order(self):
        code, placed = self.order((self.toy, 1))
        self.assertEqual(call("GET", "/orders/" + placed["id"]), (200, placed))

    def test_get_unknown_order(self):
        self.assertError(call("GET", "/orders/" + self.p + "none"), 404)

    def test_ids_unique(self):
        ids = {self.order((self.food, 1))[1]["id"] for _ in range(5)}
        self.assertEqual(len(ids), 5)

    def test_invalid_400(self):
        line = {"sku": self.food, "qty": 1}
        bad = [{}, {"lines": []}, {"lines": None}, {"lines": "x"}, {"lines": line},
               {"lines": [dict(line, qty=0)]}, {"lines": [dict(line, qty=-2)]},
               {"lines": [dict(line, qty=True)]}, {"lines": [dict(line, qty=1.0)]},
               {"lines": [dict(line, qty="1")]}, {"lines": [{"sku": self.food}]},
               {"lines": [{"qty": 1}]}, {"lines": [line, dict(line, qty=0)]},
               {"lines": [5]}, [], "lines"]
        for body in bad:
            with self.subTest(body=body):
                self.assertError(call("POST", "/orders", raw=json.dumps(body).encode()), 400)
        self.assertError(call("POST", "/orders", raw=b"{"), 400)
        self.assertEqual(self.levels(), [1, 0, 10, 4])

    def test_unknown_sku_404(self):
        self.assertError(self.order((self.food, 1), (self.p + "fish", 1)), 404)
        self.assertEqual(self.levels(), [1, 0, 10, 4])

    def test_insufficient_409(self):
        self.assertError(self.order((self.food, 11)), 409)
        self.assertError(self.order((self.cat, 1)), 409)
        self.assertEqual(self.levels(), [1, 0, 10, 4])

    def test_all_or_nothing(self):
        self.assertError(self.order((self.food, 2), (self.dog, 1), (self.toy, 5)), 409)
        self.assertEqual(self.levels(), [1, 0, 10, 4])

    def test_merged_pet_twice_409(self):
        self.assertError(self.order((self.dog, 1), (self.dog, 1)), 409)
        self.assertEqual(self.levels(), [1, 0, 10, 4])

    def test_cancel(self):
        code, placed = self.order((self.food, 3), (self.dog, 1))
        self.assertEqual(self.levels(), [0, 0, 7, 4])
        code, body = call("POST", "/orders/" + placed["id"] + "/cancel")
        self.assertEqual(code, 200, body)
        self.assertEqual(body, dict(placed, status="cancelled"))
        self.assertEqual(self.levels(), [1, 0, 10, 4])
        self.assertEqual(call("GET", "/orders/" + placed["id"]), (200, dict(placed, status="cancelled")))

    def test_cancel_twice_409(self):
        code, placed = self.order((self.food, 3))
        call("POST", "/orders/" + placed["id"] + "/cancel")
        self.assertError(call("POST", "/orders/" + placed["id"] + "/cancel"), 409)
        self.assertEqual(self.avail(self.food), 10)

    def test_cancel_unknown_404(self):
        self.assertError(call("POST", "/orders/" + self.p + "none/cancel"), 404)


class OtherRoutesTest(Case):
    def test_unknown_paths(self):
        for method, path in (("GET", "/"), ("GET", "/nope"), ("GET", "/pets"),
                             ("POST", "/nope"), ("GET", "/catalog/a/b"), ("GET", "/stock")):
            with self.subTest(method=method, path=path):
                self.assertError(call(method, path), NOT_ROUTED)

    def test_wrong_methods(self):
        sku = self.add("food")
        for method, path in (("DELETE", "/catalog"), ("PUT", "/catalog"),
                             ("DELETE", "/catalog/" + sku), ("POST", "/catalog/" + sku),
                             ("PUT", "/stock/" + sku), ("DELETE", "/stock/" + sku),
                             ("GET", "/orders"), ("PUT", "/orders"),
                             ("DELETE", "/orders/x"), ("GET", "/orders/x/cancel")):
            with self.subTest(method=method, path=path):
                self.assertError(call(method, path), NOT_ROUTED)
        self.assertEqual(call("GET", "/catalog/" + sku)[0], 200)


class EndToEndTest(Case):
    def test_flow(self):
        dog = self.add("dog", kind="pet", price=50000)
        bowl = self.add("bowl", kind="supply", price=899)
        self.assertEqual(call("GET", "/catalog/" + dog)[1]["kind"], "pet")
        self.assertEqual(self.receive(dog, 1), 1)
        self.assertEqual(self.receive(bowl, 5), 5)

        code, order = call("POST", "/orders", {"lines": [{"sku": bowl, "qty": 2},
                                                          {"sku": dog, "qty": 1}]})
        self.assertEqual(code, 201, order)
        self.assertEqual(order["total_cents"], 2 * 899 + 50000)
        self.assertEqual((self.avail(dog), self.avail(bowl)), (0, 3))

        self.assertError(call("POST", "/orders", {"lines": [{"sku": dog, "qty": 1}]}), 409)

        code, cancelled = call("POST", "/orders/" + order["id"] + "/cancel")
        self.assertEqual(code, 200, cancelled)
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual((self.avail(dog), self.avail(bowl)), (1, 5))
        self.assertEqual(call("GET", "/orders/" + order["id"])[1]["status"], "cancelled")

        code, again = call("POST", "/orders", {"lines": [{"sku": dog, "qty": 1}]})
        self.assertEqual(code, 201, again)
        self.assertNotEqual(again["id"], order["id"])
        self.assertEqual(self.avail(dog), 0)


if __name__ == "__main__":
    unittest.main()

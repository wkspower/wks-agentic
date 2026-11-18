"""WSGI application of the pet shop. Declarations: units/pet-shop/unit.md."""
import json
from urllib.parse import parse_qs

from ._valid import is_int
from .catalog import Catalog
from .orders import Orders
from .stock import InsufficientStock, Stock

STATUS = {200: "200 OK", 201: "201 Created", 400: "400 Bad Request", 404: "404 Not Found",
          405: "405 Method Not Allowed", 409: "409 Conflict"}


class Fail(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        return json.loads(environ["wsgi.input"].read(length).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise Fail(400, "body must be JSON")


def _object(environ):
    body = _body(environ)
    if not isinstance(body, dict):
        raise Fail(400, "body must be a JSON object")
    return body


def _qty(value):
    if not is_int(value) or value <= 0:
        raise Fail(400, "qty must be an integer greater than 0")
    return value


class Shop:
    def __init__(self):
        self.catalog = Catalog()
        self.stock = Stock(self.catalog)
        self.orders = Orders(self.catalog, self.stock)

    def _known(self, sku):
        try:
            return self.catalog.get(sku)
        except KeyError:
            raise Fail(404, f"no item {sku}")

    def list_catalog(self, environ):
        kinds = parse_qs(environ.get("QUERY_STRING", "")).get("kind")
        try:
            return 200, self.catalog.items(kinds[-1] if kinds else None)
        except ValueError as e:
            raise Fail(400, str(e))

    def add_item(self, environ):
        body = _object(environ)
        fields = ("sku", "name", "kind", "price_cents")
        if any(f not in body for f in fields):
            raise Fail(400, "item needs sku, name, kind and price_cents")
        try:
            return 201, self.catalog.add(*(body[f] for f in fields))
        except ValueError as e:
            raise Fail(400, str(e))
        except KeyError:
            raise Fail(409, f"item {body['sku']} exists")

    def get_item(self, environ, sku):
        return 200, self._known(sku)

    def get_stock(self, environ, sku):
        self._known(sku)
        return 200, {"sku": sku, "available": self.stock.available(sku)}

    def receive(self, environ, sku):
        self._known(sku)
        qty = _qty(_object(environ).get("qty"))
        try:
            return 200, {"sku": sku, "available": self.stock.receive(sku, qty)}
        except ValueError as e:  # qty is valid, so this is the pet bound
            raise Fail(409, str(e))

    def place(self, environ):
        lines = _object(environ).get("lines")
        if not isinstance(lines, list) or not lines:
            raise Fail(400, "lines must be a non-empty list")
        pairs = []
        for line in lines:
            if not isinstance(line, dict) or not isinstance(line.get("sku"), str):
                raise Fail(400, "each line needs sku and qty")
            pairs.append((line["sku"], _qty(line.get("qty"))))
        for sku, _ in pairs:
            self._known(sku)
        try:
            return 201, self.orders.place(pairs)
        except InsufficientStock as e:
            raise Fail(409, str(e))

    def get_order(self, environ, order_id):
        try:
            return 200, self.orders.get(order_id)
        except KeyError:
            raise Fail(404, f"no order {order_id}")

    def cancel(self, environ, order_id):
        self.get_order(environ, order_id)
        try:
            return 200, self.orders.cancel(order_id)
        except ValueError as e:
            raise Fail(409, str(e))

    def route(self, method, parts):
        """Returns the handler and its arguments; Fail(404/405) when there is none."""
        table = {
            ("catalog",): {"GET": self.list_catalog, "POST": self.add_item},
            ("catalog", None): {"GET": self.get_item},
            ("stock", None): {"GET": self.get_stock, "POST": self.receive},
            ("orders",): {"POST": self.place},
            ("orders", None): {"GET": self.get_order},
            ("orders", None, "cancel"): {"POST": self.cancel},
        }
        for shape, methods in table.items():
            if len(shape) == len(parts) and all(s is None or s == p for s, p in zip(shape, parts)):
                if method not in methods:
                    raise Fail(405, f"{method} not allowed here")
                args = [p for s, p in zip(shape, parts) if s is None]
                return methods[method], args
        raise Fail(404, "no such path")

    def __call__(self, environ, start_response):
        parts = [p for p in environ.get("PATH_INFO", "").split("/") if p]
        try:
            handler, args = self.route(environ.get("REQUEST_METHOD", "GET"), parts)
            code, payload = handler(environ, *args)
        except Fail as e:
            code, payload = e.code, {"error": str(e)}
        data = json.dumps(payload).encode("utf-8")
        start_response(STATUS[code], [("Content-Type", "application/json"),
                                      ("Content-Length", str(len(data)))])
        return [data]


application = Shop()

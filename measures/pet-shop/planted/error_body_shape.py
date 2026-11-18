# Planted defect: error bodies are {"message": ...} instead of {"error": ...}.
import json
import re

from petshop.catalog import Catalog
from petshop.orders import Orders
from petshop.stock import InsufficientStock, Stock

_catalog = Catalog()
_stock = Stock(_catalog)
_orders = Orders(_catalog, _stock)

_REASONS = {200: "OK", 201: "Created", 400: "Bad Request", 404: "Not Found",
            405: "Method Not Allowed", 409: "Conflict"}


class _Err(Exception):
    def __init__(self, status, msg):
        Exception.__init__(self, msg)
        self.status = status
        self.msg = msg


def _is_pos_int(v):
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def _body(environ):
    try:
        n = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        n = 0
    raw = environ["wsgi.input"].read(n) if n > 0 else b""
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise _Err(400, "invalid JSON body")


def _catalog_list(environ, m):
    kind = None
    for part in environ.get("QUERY_STRING", "").split("&"):
        if part.startswith("kind="):
            kind = part[5:]
    try:
        return 200, _catalog.items(kind)
    except ValueError as e:
        raise _Err(400, str(e))


def _catalog_add(environ, m):
    b = _body(environ)
    if not isinstance(b, dict):
        raise _Err(400, "item must be an object")
    try:
        return 201, _catalog.add(b.get("sku"), b.get("name"), b.get("kind"), b.get("price_cents"))
    except ValueError as e:
        raise _Err(400, str(e))
    except KeyError:
        raise _Err(409, "sku exists")


def _catalog_get(environ, m):
    try:
        return 200, _catalog.get(m.group(1))
    except KeyError:
        raise _Err(404, "unknown sku")


def _stock_get(environ, m):
    sku = m.group(1)
    try:
        return 200, {"sku": sku, "available": _stock.available(sku)}
    except KeyError:
        raise _Err(404, "unknown sku")


def _stock_post(environ, m):
    sku = m.group(1)
    try:
        _catalog.get(sku)
    except KeyError:
        raise _Err(404, "unknown sku")
    b = _body(environ)
    if not isinstance(b, dict) or not _is_pos_int(b.get("qty")):
        raise _Err(400, "qty must be a positive int")
    try:
        return 200, {"sku": sku, "available": _stock.receive(sku, b["qty"])}
    except ValueError as e:
        raise _Err(409, str(e))


def _orders_post(environ, m):
    b = _body(environ)
    if not isinstance(b, dict) or not isinstance(b.get("lines"), list) or not b["lines"]:
        raise _Err(400, "lines must be a non-empty list")
    lines = []
    for l in b["lines"]:
        if not isinstance(l, dict) or not isinstance(l.get("sku"), str) or not _is_pos_int(l.get("qty")):
            raise _Err(400, "invalid line")
        lines.append((l["sku"], l["qty"]))
    try:
        return 201, _orders.place(lines)
    except ValueError as e:
        raise _Err(400, str(e))
    except KeyError:
        raise _Err(404, "unknown sku")
    except InsufficientStock:
        raise _Err(409, "insufficient stock")


def _orders_get(environ, m):
    try:
        return 200, _orders.get(m.group(1))
    except KeyError:
        raise _Err(404, "unknown order")


def _orders_cancel(environ, m):
    try:
        return 200, _orders.cancel(m.group(1))
    except KeyError:
        raise _Err(404, "unknown order")
    except ValueError:
        raise _Err(409, "already cancelled")


_ROUTES = [
    (re.compile(r"^/catalog$"), {"GET": _catalog_list, "POST": _catalog_add}),
    (re.compile(r"^/catalog/([^/]+)$"), {"GET": _catalog_get}),
    (re.compile(r"^/stock/([^/]+)$"), {"GET": _stock_get, "POST": _stock_post}),
    (re.compile(r"^/orders$"), {"POST": _orders_post}),
    (re.compile(r"^/orders/([^/]+)$"), {"GET": _orders_get}),
    (re.compile(r"^/orders/([^/]+)/cancel$"), {"POST": _orders_cancel}),
]


def _dispatch(environ):
    path = environ.get("PATH_INFO", "")
    method = environ.get("REQUEST_METHOD", "GET")
    for rx, methods in _ROUTES:
        m = rx.match(path)
        if m:
            h = methods.get(method)
            if h is None:
                raise _Err(405, "method not allowed")
            return h(environ, m)
    raise _Err(404, "not found")


def application(environ, start_response):
    try:
        status, body = _dispatch(environ)
    except _Err as e:
        status, body = e.status, {"message": e.msg}
    data = json.dumps(body).encode("utf-8")
    start_response("%d %s" % (status, _REASONS[status]),
                   [("Content-Type", "application/json"), ("Content-Length", str(len(data)))])
    return [data]

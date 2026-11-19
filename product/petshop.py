#!/usr/bin/env python3
"""Pet shop: products and stock, customers and their pets, counter sales, grooming appointments.

    python3 product/petshop.py [--db FILE] [--port N] [--sample]

Then open http://127.0.0.1:8000/ in a browser. That page is the only way in.
The rules this program keeps are the lessons L0005 to L0012 in CLAUDE.md.
"""
import argparse
import datetime
import html
import json
import re
import sqlite3
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
MAX_FORM_BYTES = 65_536
MAX_PRICE_CENTS = 9_999_999
MAX_STOCK = 1_000_000
MAX_QTY = 1000
MAX_LINES = 20
MAX_NAME = 80
MAX_PHONE = 30
MAX_SPECIES = 40
METHODS = ("cash", "card", "other")
SLOTS = ["%02d:00" % hour for hour in range(9, 18)]
SALE_ROWS = 5

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT NOT NULL,
    price_cents INTEGER NOT NULL, stock INTEGER NOT NULL CHECK (stock >= 0), low_at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customers(id),
    name TEXT NOT NULL, species TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY, created TEXT NOT NULL,
    customer_id INTEGER REFERENCES customers(id), method TEXT NOT NULL, total_cents INTEGER NOT NULL,
    voided INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS sale_lines (sale_id INTEGER NOT NULL REFERENCES sales(id),
    product_id INTEGER NOT NULL REFERENCES products(id), qty INTEGER NOT NULL, unit_cents INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY, pet_id INTEGER NOT NULL REFERENCES pets(id),
    date TEXT NOT NULL, time TEXT NOT NULL, cancelled INTEGER NOT NULL DEFAULT 0);
"""


class Refused(Exception):
    """The form asked for something a rule forbids. Answered 400 with the reason."""


class NotFound(Exception):
    pass


# ---- reading a form -------------------------------------------------------------------------

class Form:
    def __init__(self, pairs):
        self.pairs = pairs

    def all(self, key):
        return [value.strip() for name, value in self.pairs if name == key]

    def one(self, key):
        return (self.all(key) or [""])[0]

    def text(self, key, label, most, least=1):
        value = self.one(key)
        if not least <= len(value) <= most:
            raise Refused("%s must have %d to %d characters; it has %d." % (label, least, most, len(value)))
        return value

    def whole(self, key, label, low, high):
        return whole(self.one(key), label, low, high)

    def price(self, key):
        value = self.one(key)
        if not re.fullmatch(r"[0-9]+(\.[0-9]{1,2})?", value):
            raise Refused("Price must be written like 12.50: digits, a point, at most two decimals.")
        units, _, decimals = value.partition(".")
        cents = int(units) * 100 + int((decimals + "00")[:2])
        if not 1 <= cents <= MAX_PRICE_CENTS:
            raise Refused("Price must be from 0.01 to %s." % money(MAX_PRICE_CENTS))
        return cents


def whole(value, label, low, high):
    if not re.fullmatch(r"[+-]?[0-9]{1,40}", value) or not low <= int(value) <= high:
        raise Refused("%s must be a whole number from %d to %d." % (label, low, high))
    return int(value)


def money(cents):
    return "%d.%02d" % divmod(cents, 100)


def today():
    return datetime.date.today().isoformat()


# ---- what the shop does: each takes the database inside a transaction and a form ------------

def add_product(db, form):
    db.execute("INSERT INTO products (name, price_cents, stock, low_at) VALUES (?, ?, ?, ?)",
               (form.text("name", "Name", MAX_NAME), form.price("price"),
                form.whole("stock", "Stock", 0, MAX_STOCK),
                form.whole("low_at", "Low-stock threshold", 0, MAX_STOCK)))
    return "/products"


def edit_product(db, form, ident):
    find(db, "products", ident)
    db.execute("UPDATE products SET name = ?, price_cents = ?, low_at = ? WHERE id = ?",
               (form.text("name", "Name", MAX_NAME), form.price("price"),
                form.whole("low_at", "Low-stock threshold", 0, MAX_STOCK), ident))
    return "/products"


def adjust_stock(db, form, ident):
    product = find(db, "products", ident)
    delta = form.whole("delta", "Adjustment", -MAX_STOCK, MAX_STOCK)
    after = product["stock"] + delta
    if delta == 0:
        raise Refused("An adjustment of 0 changes nothing.")
    if not 0 <= after <= MAX_STOCK:
        raise Refused("%s has %d in stock; %+d would leave %d, outside 0 to %d."
                      % (product["name"], product["stock"], delta, after, MAX_STOCK))
    db.execute("UPDATE products SET stock = ? WHERE id = ?", (after, ident))
    return "/products"


def add_customer(db, form):
    db.execute("INSERT INTO customers (name, phone) VALUES (?, ?)",
               (form.text("name", "Name", MAX_NAME), form.text("phone", "Phone", MAX_PHONE, least=0)))
    return "/customers"


def add_pet(db, form):
    owner = db.execute("SELECT id FROM customers WHERE id = ?", (form.one("customer_id"),)).fetchone()
    if owner is None:
        raise Refused("Choose the customer this pet belongs to.")
    db.execute("INSERT INTO pets (customer_id, name, species) VALUES (?, ?, ?)",
               (owner["id"], form.text("name", "Pet's name", MAX_NAME),
                form.text("species", "Species", MAX_SPECIES)))
    return "/customers"


def add_sale(db, form):
    method = form.one("method")
    if method not in METHODS:
        raise Refused("Choose how it was paid: %s." % ", ".join(METHODS))
    customer = None
    if form.one("customer_id"):
        customer = db.execute("SELECT id FROM customers WHERE id = ?", (form.one("customer_id"),)).fetchone()
        if customer is None:
            raise Refused("That customer is not on record.")
    products, quantities = form.all("product_id"), form.all("qty")
    if len(products) != len(quantities):
        raise Refused("Each line needs a product and a quantity.")
    wanted, filled = {}, 0
    for product, qty in zip(products, quantities):
        if not product and not qty:
            continue  # a row of the form left empty
        if not product:
            raise Refused("A line has a quantity and no product.")
        filled += 1
        wanted[product] = wanted.get(product, 0) + whole(qty, "Quantity", 1, MAX_QTY)
    if not 1 <= filled <= MAX_LINES:
        raise Refused("A sale needs 1 to %d lines; this one has %d." % (MAX_LINES, filled))
    lines = []
    for ident, qty in wanted.items():
        product = db.execute("SELECT * FROM products WHERE id = ?", (ident,)).fetchone()
        if product is None:
            raise Refused("A product on this sale is not on record.")
        if qty > MAX_QTY:
            raise Refused("%s: at most %d on one sale." % (product["name"], MAX_QTY))
        if qty > product["stock"]:
            raise Refused("%s: only %d in stock, %d asked. Nothing was sold."
                          % (product["name"], product["stock"], qty))
        lines.append((product["id"], qty, product["price_cents"]))
    total = sum(qty * unit for _, qty, unit in lines)
    sale = db.execute("INSERT INTO sales (created, customer_id, method, total_cents) VALUES (?, ?, ?, ?)",
                      (datetime.datetime.now().isoformat(" ", "seconds"),
                       customer["id"] if customer else None, method, total)).lastrowid
    for ident, qty, unit in lines:
        db.execute("INSERT INTO sale_lines VALUES (?, ?, ?, ?)", (sale, ident, qty, unit))
        db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, ident))
    return "/sales"


def void_sale(db, form, ident):
    sale = find(db, "sales", ident)
    if sale["voided"]:
        raise Refused("Sale %d is already voided." % ident)
    db.execute("UPDATE sales SET voided = 1 WHERE id = ?", (ident,))
    for line in db.execute("SELECT * FROM sale_lines WHERE sale_id = ?", (ident,)).fetchall():
        db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (line["qty"], line["product_id"]))
    return "/sales"


def add_appointment(db, form):
    pet = db.execute("SELECT * FROM pets WHERE id = ?", (form.one("pet_id"),)).fetchone()
    if pet is None:
        raise Refused("Choose the pet this appointment is for.")
    date, time = form.one("date"), form.one("time")
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
            raise ValueError(date)
        datetime.date.fromisoformat(date)
    except ValueError:
        raise Refused("Date must be a real day written like 2026-11-30.")
    if date < today():
        raise Refused("%s is in the past." % date)
    if time not in SLOTS:
        raise Refused("Time must be one of the one-hour slots, %s to %s." % (SLOTS[0], SLOTS[-1]))
    taken = db.execute("SELECT id FROM appointments WHERE date = ? AND time = ? AND cancelled = 0",
                       (date, time)).fetchone()
    if taken:
        raise Refused("%s at %s is already taken." % (date, time))
    db.execute("INSERT INTO appointments (pet_id, date, time) VALUES (?, ?, ?)", (pet["id"], date, time))
    return "/appointments"


def cancel_appointment(db, form, ident):
    if find(db, "appointments", ident)["cancelled"]:
        raise Refused("That appointment is already cancelled.")
    db.execute("UPDATE appointments SET cancelled = 1 WHERE id = ?", (ident,))
    return "/appointments"


def find(db, table, ident):
    row = db.execute("SELECT * FROM %s WHERE id = ?" % table, (ident,)).fetchone()
    if row is None:
        raise NotFound()
    return row


POSTS = [
    (r"/products", add_product), (r"/products/([0-9]{1,9})/edit", edit_product),
    (r"/products/([0-9]{1,9})/stock", adjust_stock), (r"/customers", add_customer), (r"/pets", add_pet),
    (r"/sales", add_sale), (r"/sales/([0-9]{1,9})/void", void_sale),
    (r"/appointments", add_appointment), (r"/appointments/([0-9]{1,9})/cancel", cancel_appointment),
]


# ---- reading the state ----------------------------------------------------------------------

def rows(db, sql, *args):
    return [dict(row) for row in db.execute(sql, args).fetchall()]


def low_stock(db):
    return rows(db, "SELECT * FROM products WHERE stock <= low_at ORDER BY name")


def sales(db):
    found = rows(db, "SELECT s.*, c.name AS customer FROM sales s LEFT JOIN customers c ON c.id = s.customer_id"
                     " ORDER BY s.id DESC")
    for sale in found:
        sale["voided"] = bool(sale["voided"])
        sale["lines"] = rows(db, "SELECT l.product_id, l.qty, l.unit_cents, p.name FROM sale_lines l"
                                 " JOIN products p ON p.id = l.product_id WHERE l.sale_id = ?", sale["id"])
    return found


def export(db):
    def strip(found, *drop):
        return [{key: value for key, value in row.items() if key not in drop} for row in found]
    recorded = sales(db)
    for sale in recorded:
        sale["lines"] = strip(sale["lines"], "name")
    appointments = rows(db, "SELECT * FROM appointments ORDER BY id")
    for appointment in appointments:
        appointment["cancelled"] = bool(appointment["cancelled"])
    return {
        "products": rows(db, "SELECT * FROM products ORDER BY id"),
        "customers": rows(db, "SELECT * FROM customers ORDER BY id"),
        "pets": rows(db, "SELECT * FROM pets ORDER BY id"),
        "sales": strip(recorded, "customer"),
        "appointments": appointments,
        "low_stock": [row["id"] for row in low_stock(db)],
    }


# ---- pages ----------------------------------------------------------------------------------

E = html.escape
STYLE = """
:root { color-scheme: light dark; --line: #8884; --soft: #8882; --mark: #0a6b4f; }
* { box-sizing: border-box; }
body { font: 16px/1.45 system-ui, sans-serif; margin: 0; }
nav { display: flex; flex-wrap: wrap; gap: 4px 20px; padding: 12px 20px; border-bottom: 1px solid var(--line); }
nav a { text-decoration: none; color: inherit; padding: 2px 0; }
nav a.here { border-bottom: 3px solid var(--mark); font-weight: 600; }
main { max-width: 980px; margin: 0 auto; padding: 8px 20px 60px; overflow-wrap: anywhere; }
.scroll { overflow-x: auto; }
h1 { font-size: 1.5rem; margin: 20px 0 12px; } h2 { font-size: 1.1rem; margin: 28px 0 8px; }
table { border-collapse: collapse; width: 100%; }
th { overflow-wrap: normal; white-space: nowrap; }
th, td { text-align: left; padding: 7px 10px 7px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
td.num, th.num, td.stock { text-align: right; font-variant-numeric: tabular-nums; }
form.card { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: end; padding: 14px; background: var(--soft);
  border-radius: 8px; }
form.card.tall { flex-direction: column; align-items: stretch; max-width: 560px; }
label { display: grid; gap: 3px; font-size: .85rem; min-width: 0; max-width: 100%; }
fieldset { border: 0; padding: 0; margin: 0; display: flex; gap: 16px; flex-wrap: wrap; }
fieldset label { display: inline-flex; gap: 6px; align-items: center; font-size: 1rem; }
legend { font-size: .85rem; padding: 0; margin-bottom: 3px; }
input, select, button { font: inherit; padding: 6px 8px; max-width: 100%; min-width: 0; }
input[type=radio] { padding: 0; }
input.short { width: 6.5em; }
button { cursor: pointer; }
td form { display: inline-flex; gap: 6px; }
.row { display: flex; gap: 10px; } .row select { flex: 1; min-width: 0; width: 0; }
.heads { font-size: .85rem; justify-content: space-between; margin-bottom: -6px; }
.off { opacity: .55; text-decoration: line-through; } .tag { font-size: .8rem; padding: 1px 7px;
  border: 1px solid var(--line); border-radius: 99px; }
.warn { border-left: 4px solid #c0392b; padding: 10px 14px; background: var(--soft); }
.empty { opacity: .65; }
"""
NAV = [("/", "Today"), ("/products", "Products"), ("/customers", "Customers"), ("/sales", "Sales"),
       ("/appointments", "Appointments")]


def page(title, path, body):
    links = "".join('<a href="%s"%s>%s</a>' % (href, ' class="here"' if href == path else "", label)
                    for href, label in NAV)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>%s · Pet shop</title><style>%s</style></head><body><nav>%s</nav><main><h1>%s</h1>%s"
            "</main></body></html>" % (E(title), STYLE, links, E(title), body))


def table(head, body_rows, empty):
    if not body_rows:
        return '<p class="empty">%s</p>' % E(empty)
    cells = "".join('<th class="num">%s</th>' % E(h[1:]) if h.startswith(">") else "<th>%s</th>" % E(h) for h in head)
    return '<div class="scroll"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (cells, "".join(body_rows))


def options(found, label, first):
    return first + "".join('<option value="%d">%s</option>' % (row["id"], E(label(row))) for row in found)


def pet_rows(db, where="", *args):
    return rows(db, "SELECT p.*, c.name AS owner FROM pets p JOIN customers c ON c.id = p.customer_id "
                + where + " ORDER BY c.name, p.name", *args)


def appointment_rows(db, where, *args):
    return rows(db, "SELECT a.*, p.name AS pet, p.species, c.name AS owner, c.phone FROM appointments a"
                    " JOIN pets p ON p.id = a.pet_id JOIN customers c ON c.id = p.customer_id "
                + where + " ORDER BY a.date, a.time, a.id", *args)


def home(db):
    day = today()
    due = ["<tr><td>%s</td><td>%s (%s)</td><td>%s %s</td></tr>"
           % (a["time"], E(a["pet"]), E(a["species"]), E(a["owner"]), E(a["phone"]))
           for a in appointment_rows(db, "WHERE a.date = ? AND a.cancelled = 0", day)]
    low = ['<tr><td>%s</td><td class="num">%d</td><td class="num">%d</td></tr>'
           % (E(p["name"]), p["stock"], p["low_at"]) for p in low_stock(db)]
    took = db.execute("SELECT COUNT(*) AS n, COALESCE(SUM(total_cents), 0) AS cents FROM sales"
                      " WHERE voided = 0 AND created LIKE ?", (day + "%",)).fetchone()
    return page("Today", "/", (
        "<p>%s · %d sale%s today, %s taken.</p>" % (day, took["n"], "" if took["n"] == 1 else "s", money(took["cents"]))
        + '<p><a href="/sales/new">New sale</a></p>'
        + "<h2>Grooming today</h2>" + table(["Time", "Pet", "Customer"], due, "No appointments today.")
        + "<h2>Low stock</h2>" + table(["Product", ">In stock", ">Low at"], low,
                                       "Nothing is at or below its threshold.")))


def products_page(db):
    listed = []
    for p in rows(db, "SELECT * FROM products ORDER BY name"):
        listed.append(
            '<tr><td>%s%s</td><td class="num">%s</td><td class="stock">%d</td><td class="num">%d</td><td>'
            '<form method="post" action="/products/%d/stock"><input class="short" name="delta" required '
            'placeholder="+10 or -2" aria-label="Stock adjustment for %s"><button type="submit">Adjust</button></form>'
            '</td><td><a href="/products/%d/edit">Edit</a></td></tr>'
            % (E(p["name"]), ' <span class="tag">low</span>' if p["stock"] <= p["low_at"] else "",
               money(p["price_cents"]), p["stock"], p["low_at"], p["id"], E(p["name"]), p["id"]))
    return page("Products", "/products", (
        '<form class="card" method="post" action="/products">'
        '<label>Name <input name="name" required maxlength="%d"></label>'
        '<label>Price <input class="short" name="price" required inputmode="decimal" placeholder="12.50"></label>'
        '<label>In stock <input class="short" name="stock" required inputmode="numeric" value="0"></label>'
        '<label>Low at <input class="short" name="low_at" required inputmode="numeric" value="0"></label>'
        '<button type="submit">Add product</button></form>' % MAX_NAME
        + "<h2>On record</h2>"
        + table(["Product", ">Price", ">In stock", ">Low at", "Receive or remove", ""], listed, "No products yet.")))


def product_edit_page(db, ident):
    p = find(db, "products", ident)
    return page("Edit " + p["name"], "/products", (
        '<form class="card" method="post" action="/products/%d/edit">'
        '<label>Name <input name="name" required maxlength="%d" value="%s"></label>'
        '<label>Price <input class="short" name="price" required inputmode="decimal" value="%s"></label>'
        '<label>Low at <input class="short" name="low_at" required inputmode="numeric" value="%d"></label>'
        '<button type="submit">Save</button></form>'
        "<p>Stock is changed on the products page, by receiving or removing. Sales already made keep the "
        'price they were made at.</p><p><a href="/products">Back to products</a></p>'
        % (p["id"], MAX_NAME, E(p["name"]), money(p["price_cents"]), p["low_at"])))


def customers_page(db):
    customers = rows(db, "SELECT * FROM customers ORDER BY name")
    pets = pet_rows(db)
    listed = ["<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
        E(c["name"]), E(c["phone"]),
        ", ".join("%s (%s)" % (E(p["name"]), E(p["species"])) for p in pets if p["customer_id"] == c["id"])
        or '<span class="empty">none</span>') for c in customers]
    return page("Customers", "/customers", (
        '<form class="card" method="post" action="/customers">'
        '<label>Name <input name="name" required maxlength="%d"></label>'
        '<label>Phone <input name="phone" maxlength="%d"></label>'
        '<button type="submit">Add customer</button></form>' % (MAX_NAME, MAX_PHONE)
        + "<h2>Add a pet</h2>"
        '<form class="card" method="post" action="/pets"><label>Belongs to <select name="customer_id" required>%s'
        '</select></label><label>Pet\'s name <input name="name" required maxlength="%d"></label>'
        '<label>Species <input name="species" required maxlength="%d" placeholder="dog"></label>'
        '<button type="submit">Add pet</button></form>'
        % (options(customers, lambda c: c["name"], '<option value="">choose a customer</option>'),
           MAX_NAME, MAX_SPECIES)
        + "<h2>On record</h2>" + table(["Customer", "Phone", "Pets"], listed, "No customers yet.")))


def sales_page(db):
    listed = []
    for s in sales(db):
        items = ", ".join("%d × %s" % (l["qty"], E(l["name"])) for l in s["lines"])
        state = ('<span class="tag">voided</span>' if s["voided"] else
                 '<form method="post" action="/sales/%d/void"><button type="submit">Void</button></form>' % s["id"])
        listed.append('<tr><td>%d</td><td>%s</td><td>%s</td><td%s>%s</td><td class="num%s">%s</td><td>%s</td>'
                      "<td>%s</td></tr>" % (s["id"], s["created"], E(s["customer"] or "—"),
                                            ' class="off"' if s["voided"] else "", items,
                                            " off" if s["voided"] else "", money(s["total_cents"]), s["method"], state))
    return page("Sales", "/sales", (
        '<p><a href="/sales/new">New sale</a></p>'
        + table(["No.", "When", "Customer", "Sold", ">Amount", "Paid by", ""], listed, "No sales yet.")
        + "<p>A sale is not edited. Voiding one returns everything on it to stock and keeps it on this list.</p>"))


def sale_form_page(db):
    products = options(rows(db, "SELECT * FROM products ORDER BY name"),
                       lambda p: "%s (%s, %d in stock)" % (p["name"], money(p["price_cents"]), p["stock"]),
                       '<option value="">no product</option>')
    customers = options(rows(db, "SELECT * FROM customers ORDER BY name"), lambda c: c["name"],
                        '<option value="">no customer</option>')
    line = ('<div class="row"><select name="product_id" aria-label="Product %d">' + products + "</select>"
            '<input class="short" name="qty" inputmode="numeric" aria-label="Quantity %d"></div>')
    methods = "".join('<label><input type="radio" name="method" value="%s" required> %s</label>' % (m, m)
                      for m in METHODS)
    return page("New sale", "/sales", (
        '<form class="card tall" method="post" action="/sales">'
        "<label>Customer (optional) <select name=\"customer_id\">%s</select></label>"
        '<div class="row heads"><span>Product</span><span>Quantity</span></div>'
        "%s<fieldset><legend>Paid by</legend>%s</fieldset>"
        '<button type="submit">Record sale</button></form>'
        "<p>The amount is worked out from the prices on record. Rows left empty are ignored.</p>"
        % (customers, "".join(line % (n, n) for n in range(1, SALE_ROWS + 1)), methods)))


def appointments_page(db):
    listed = []
    for a in appointment_rows(db, "WHERE a.date >= ?", today()):
        state = ('<span class="tag">cancelled</span>' if a["cancelled"] else
                 '<form method="post" action="/appointments/%d/cancel"><button type="submit">Cancel</button></form>'
                 % a["id"])
        listed.append("<tr%s><td>%s</td><td>%s</td><td>%s (%s)</td><td>%s %s</td><td>%s</td></tr>"
                      % (' class="empty"' if a["cancelled"] else "", a["date"], a["time"], E(a["pet"]),
                         E(a["species"]), E(a["owner"]), E(a["phone"]), state))
    pets = options(pet_rows(db), lambda p: "%s (%s) of %s" % (p["name"], p["species"], p["owner"]),
                   '<option value="">choose a pet</option>')
    return page("Appointments", "/appointments", (
        '<form class="card" method="post" action="/appointments">'
        '<label>Pet <select name="pet_id" required>%s</select></label>'
        '<label>Date <input type="date" name="date" required min="%s"></label>'
        '<label>Time <select name="time" required><option value="">choose a time</option>%s</select></label>'
        '<button type="submit">Book grooming</button></form>'
        % (pets, today(), "".join("<option>%s</option>" % slot for slot in SLOTS))
        + "<h2>From today on</h2>"
        + table(["Date", "Time", "Pet", "Customer", ""], listed, "No appointments booked.")
        + "<p>One groomer, one hour each, %s to %s. Pets are added on the customers page.</p>" % (SLOTS[0], SLOTS[-1])))


GETS = [(r"/", home), (r"/products", products_page), (r"/products/([0-9]{1,9})/edit", product_edit_page),
        (r"/customers", customers_page), (r"/sales", sales_page), (r"/sales/new", sale_form_page),
        (r"/appointments", appointments_page)]


# ---- the server -----------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def answer(self, status, body, kind="text/html; charset=utf-8", location=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(data)

    def problem(self, status, title, text):
        self.answer(status, page(title, "", '<p class="warn">%s</p><p>Use the browser\'s Back button to return '
                                            "to the form with what you typed.</p>" % E(text)))

    def foreign(self):
        """True, and answered 403, when the request does not come from this shop's own pages."""
        host = self.headers.get("Host")
        if host not in self.server.hosts:
            self.problem(403, "Refused", "This shop answers only as %s." % " or ".join(sorted(self.server.hosts)))
            return True
        if self.command == "POST":
            allowed = {"http://" + name for name in self.server.hosts}
            origin, site = self.headers.get("Origin"), self.headers.get("Sec-Fetch-Site")
            if origin is not None and origin not in allowed:
                self.problem(403, "Refused", "A form on another site cannot change this shop.")
                return True
            if site not in (None, "same-origin", "none"):
                self.problem(403, "Refused", "A form on another site cannot change this shop.")
                return True
        return False

    def run(self, routes, form=None):
        """Find the route, run it inside one transaction, turn refusals into answers."""
        path = urllib.parse.urlsplit(self.path).path
        for pattern, action in routes:
            found = re.fullmatch(pattern, path)
            if not found:
                continue
            args = ([form] if form else []) + [int(group) for group in found.groups()]
            with self.server.lock:
                db = sqlite3.connect(self.server.db, isolation_level=None)
                db.row_factory = sqlite3.Row
                try:
                    db.execute("PRAGMA foreign_keys = ON")
                    db.execute("BEGIN IMMEDIATE")
                    result = action(db, *args)
                    db.execute("COMMIT")
                except Refused as refusal:
                    db.execute("ROLLBACK")
                    return self.problem(400, "Not saved", str(refusal))
                except NotFound:
                    db.execute("ROLLBACK")
                    break
                finally:
                    db.close()
            if form:
                return self.answer(303, "", location=result)
            return self.answer(200, result)
        self.problem(404, "Not found", "There is nothing at this address.")

    def do_GET(self):
        if self.foreign():
            return
        if urllib.parse.urlsplit(self.path).path == "/export.json":
            return self.run([(r"/export\.json", lambda db: json.dumps(export(db), indent=1))])
        self.run(GETS)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self.problem(411, "Refused", "The form came without a length.")
        if length > MAX_FORM_BYTES:
            if length <= 16 * MAX_FORM_BYTES:
                self.rfile.read(length)  # so the browser can read the answer instead of a reset
            self.close_connection = True
            return self.problem(413, "Refused", "The form is larger than %d bytes." % MAX_FORM_BYTES)
        body = self.rfile.read(length)
        if self.foreign():
            return
        try:
            pairs = urllib.parse.parse_qsl(body.decode("utf-8"), keep_blank_values=True, max_num_fields=200)
        except ValueError:
            return self.problem(400, "Not saved", "The form could not be read.")
        self.run(POSTS, Form(pairs))


SAMPLE = [
    ("/products", [("name", "Dry dog food 2 kg"), ("price", "18.90"), ("stock", "12"), ("low_at", "3")]),
    ("/products", [("name", "Cat litter 4 kg"), ("price", "9.50"), ("stock", "2"), ("low_at", "4")]),
    ("/products", [("name", "Rubber ball"), ("price", "3.25"), ("stock", "30"), ("low_at", "5")]),
    ("/customers", [("name", "Sample Customer"), ("phone", "555-0100")]),
    ("/pets", [("customer_id", "1"), ("name", "Biscuit"), ("species", "dog")]),
]


def serve(db_path, port, sample=False):
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    if sample and not db.execute("SELECT 1 FROM products UNION ALL SELECT 1 FROM customers").fetchone():
        with db:
            for path, pairs in SAMPLE:
                dict((pattern, action) for pattern, action in POSTS)[path](db, Form(pairs))
    db.close()
    server = ThreadingHTTPServer((HOST, port), Handler)
    server.daemon_threads = True
    server.db, server.lock = db_path, threading.Lock()
    server.hosts = {"%s:%d" % (name, server.server_port) for name in (HOST, "localhost")}
    print("Pet shop on http://%s:%d/ · data in %s · Ctrl+C to stop" % (HOST, server.server_port, db_path), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pet shop for the counter, in the browser.")
    parser.add_argument("--db", default="petshop.db", help="the SQLite file that holds everything")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--sample", action="store_true", help="put a few sample rows in an empty database")
    options_given = parser.parse_args()
    serve(options_given.db, options_given.port, options_given.sample)

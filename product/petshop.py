#!/usr/bin/env python3
"""Pet shop: products and stock, customers and their pets, counter sales, grooming.

For the staff, in a browser on this machine. Start it and open the address it prints:

    python3 product/petshop.py            # http://127.0.0.1:8000/
    python3 product/petshop.py --sample   # the same, with a few rows to look at

Standard library only; all state is in one SQLite file (--db). The rules this
file keeps are the lessons in CLAUDE.md, and cases/ checks them.
"""
import argparse
import datetime
import html
import json
import os
import re
import sqlite3
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"

# Bounds (L0008). Money is whole cents, tax included.
MAX_PRICE_CENTS = 9_999_999
MAX_STOCK = 1_000_000
MAX_QTY = 1000
MAX_LINES = 20
MAX_NAME = 80
MAX_PHONE = 30
MAX_SPECIES = 40
MAX_FORM = 65_536
METHODS = ("cash", "card", "other")
SLOTS = ["%02d:00" % hour for hour in range(9, 18)]  # one groomer, one hour each (L0011)
SALE_ROWS = 5
LISTED = 200

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents BETWEEN 1 AND 9999999),
    stock INTEGER NOT NULL CHECK (stock BETWEEN 0 AND 1000000),
    low_at INTEGER NOT NULL CHECK (low_at BETWEEN 0 AND 1000000));
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    name TEXT NOT NULL,
    species TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    method TEXT NOT NULL CHECK (method IN ('cash', 'card', 'other')),
    total_cents INTEGER NOT NULL CHECK (total_cents > 0),
    voided INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS sale_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    qty INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 1000),
    unit_cents INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL REFERENCES pets(id),
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    cancelled INTEGER NOT NULL DEFAULT 0);
CREATE UNIQUE INDEX IF NOT EXISTS one_per_slot ON appointments (date, time) WHERE cancelled = 0;
"""


class Refused(Exception):
    """What was sent breaks a rule. The person is told why, and nothing is stored."""


class NotFound(Exception):
    pass


# ---- reading a form -------------------------------------------------------------------------

def field(form, name):
    values = form.get(name, [])
    return values[0].strip() if values else ""


def text(form, name, most, label, least=1):
    value = field(form, name)
    if any(ord(char) < 32 for char in value):
        raise Refused("%s has a character that cannot be stored." % label)
    if len(value) < least:
        raise Refused("%s is required." % label)
    if len(value) > most:
        raise Refused("%s can have at most %d characters." % (label, most))
    return value


def whole(value, least, most, label):
    if not re.fullmatch(r"[0-9]{1,40}", value) or not least <= int(value) <= most:
        raise Refused("%s must be a whole number from %d to %d." % (label, least, most))
    return int(value)


def price(form):
    value = field(form, "price")
    found = re.fullmatch(r"([0-9]{1,40})(?:\.([0-9]{1,2}))?", value)
    cents = int(found.group(1)) * 100 + int((found.group(2) or "0").ljust(2, "0")) if found else 0
    if not 1 <= cents <= MAX_PRICE_CENTS:
        raise Refused("Price must be from 0.01 to %s, with a point and at most two decimals, like 12.50."
                      % money(MAX_PRICE_CENTS))
    return cents


def money(cents):
    return "%d.%02d" % divmod(cents, 100)


def today():
    return datetime.date.today().isoformat()


def find(db, table, ident):
    """The row with this id, or NotFound. `table` is always one of our own names."""
    found = db.execute("SELECT * FROM %s WHERE id = ?" % table, (ident,)).fetchone()
    if found is None:
        raise NotFound()
    return found


# ---- what the shop does ---------------------------------------------------------------------

def add_product(db, form):
    name = text(form, "name", MAX_NAME, "Name")
    cents = price(form)
    stock = whole(field(form, "stock"), 0, MAX_STOCK, "Stock")
    low_at = whole(field(form, "low_at"), 0, MAX_STOCK, "Low-stock threshold")
    db.execute("INSERT INTO products (name, price_cents, stock, low_at) VALUES (?, ?, ?, ?)",
               (name, cents, stock, low_at))
    return "/products"


def edit_product(db, ident, form):
    find(db, "products", ident)
    name = text(form, "name", MAX_NAME, "Name")
    cents = price(form)
    low_at = whole(field(form, "low_at"), 0, MAX_STOCK, "Low-stock threshold")
    db.execute("UPDATE products SET name = ?, price_cents = ?, low_at = ? WHERE id = ?",
               (name, cents, low_at, ident))
    return "/products"


def adjust_stock(db, ident, form):
    product = find(db, "products", ident)
    value = field(form, "delta")
    if not re.fullmatch(r"[+-]?[0-9]{1,40}", value) or int(value) == 0:
        raise Refused("Adjustment must be a whole number other than 0, like +10 or -2.")
    after = product["stock"] + int(value)
    if not 0 <= after <= MAX_STOCK:
        raise Refused("%s has %d in stock; an adjustment of %s would leave %d, outside 0 to %d."
                      % (product["name"], product["stock"], value, after, MAX_STOCK))
    db.execute("UPDATE products SET stock = ? WHERE id = ?", (after, ident))
    return "/products"


def add_customer(db, form):
    name = text(form, "name", MAX_NAME, "Name")
    phone = text(form, "phone", MAX_PHONE, "Phone", least=0)
    db.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
    return "/customers"


def edit_customer(db, ident, form):
    find(db, "customers", ident)
    name = text(form, "name", MAX_NAME, "Name")
    phone = text(form, "phone", MAX_PHONE, "Phone", least=0)
    db.execute("UPDATE customers SET name = ?, phone = ? WHERE id = ?", (name, phone, ident))
    return "/customers"


def known(db, table, value, label):
    """The row a form's select points at; refused when it is missing or unknown."""
    row = None
    if re.fullmatch(r"[0-9]{1,18}", value):
        row = db.execute("SELECT * FROM %s WHERE id = ?" % table, (int(value),)).fetchone()
    if row is None and table != "pets":
        raise Refused("Choose %s from the list." % label)
    return row


def add_pet(db, form):
    owner = known(db, "customers", field(form, "customer_id"), "the pet's customer")
    name = text(form, "name", MAX_NAME, "Pet name")
    species = text(form, "species", MAX_SPECIES, "Species")
    db.execute("INSERT INTO pets (customer_id, name, species) VALUES (?, ?, ?)", (owner["id"], name, species))
    return "/customers"


def edit_pet(db, ident, form):
    find(db, "pets", ident)  # the pet stays with its customer (L0017)
    name = text(form, "name", MAX_NAME, "Pet name")
    species = text(form, "species", MAX_SPECIES, "Species")
    db.execute("UPDATE pets SET name = ?, species = ? WHERE id = ?", (name, species, ident))
    return "/customers"


def add_sale(db, form):
    method = field(form, "method")
    if method not in METHODS:
        raise Refused("Choose how the sale was paid: cash, card or other.")
    customer = None
    if field(form, "customer_id"):
        customer = known(db, "customers", field(form, "customer_id"), "the customer")["id"]
    products, qtys = form.get("product_id", []), form.get("qty", [])
    if len(products) != len(qtys):
        raise Refused("Every line needs a product and a quantity.")
    lines = [(p.strip(), q.strip()) for p, q in zip(products, qtys) if p.strip() or q.strip()]
    if not 1 <= len(lines) <= MAX_LINES:
        raise Refused("A sale has from 1 to %d lines; this one has %d." % (MAX_LINES, len(lines)))
    wanted, order = {}, []
    for product_id, qty in lines:
        product = known(db, "products", product_id, "a product for every line")
        qty = whole(qty, 1, MAX_QTY, "Quantity of %s" % product["name"])
        order.append((product, qty))
        wanted[product["id"]] = wanted.get(product["id"], 0) + qty
    for product, _ in order:  # refused whole: the lines of one product are counted together (L0009)
        qty = wanted[product["id"]]
        if qty > product["stock"]:
            raise Refused("%s: only %d in stock, and this sale asks for %d. Nothing was sold."
                          % (product["name"], product["stock"], qty))
    total = sum(product["price_cents"] * qty for product, qty in order)  # our prices, not the form's (L0010)
    sale = db.execute("INSERT INTO sales (at, customer_id, method, total_cents) VALUES (?, ?, ?, ?)",
                      (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), customer, method, total)).lastrowid
    for product, qty in order:
        db.execute("INSERT INTO sale_lines (sale_id, product_id, qty, unit_cents) VALUES (?, ?, ?, ?)",
                   (sale, product["id"], qty, product["price_cents"]))
        db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product["id"]))
    return "/sales"


def void_sale(db, ident, form):
    sale = find(db, "sales", ident)
    if sale["voided"]:
        raise Refused("Sale %d is already voided." % ident)
    for line in db.execute("SELECT l.qty, p.name, p.stock FROM sale_lines l JOIN products p ON p.id = l.product_id "
                           "WHERE l.sale_id = ?", (ident,)).fetchall():
        if line["stock"] + line["qty"] > MAX_STOCK:
            raise Refused("Voiding would put %s above %d in stock. Lower its stock first." % (line["name"], MAX_STOCK))
    db.execute("UPDATE sales SET voided = 1 WHERE id = ?", (ident,))
    for line in db.execute("SELECT product_id, qty FROM sale_lines WHERE sale_id = ?", (ident,)).fetchall():
        db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (line["qty"], line["product_id"]))
    return "/sales"


def add_appointment(db, form):
    pet = known(db, "pets", field(form, "pet_id"), "a pet")
    if pet is None:
        raise Refused("Choose the pet the appointment is for.")
    date, time = field(form, "date"), field(form, "time")
    try:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
            raise ValueError(date)
        datetime.date.fromisoformat(date)
    except ValueError:
        raise Refused("Date must be a real day written like 2030-01-31.")
    if date < today():
        raise Refused("%s is before today." % date)
    if time not in SLOTS:
        raise Refused("Grooming starts on the hour, from %s to %s." % (SLOTS[0], SLOTS[-1]))
    taken = db.execute("SELECT id FROM appointments WHERE date = ? AND time = ? AND cancelled = 0",
                       (date, time)).fetchone()
    if taken:
        raise Refused("%s at %s is already taken. Choose another slot." % (date, time))
    db.execute("INSERT INTO appointments (pet_id, date, time) VALUES (?, ?, ?)", (pet["id"], date, time))
    return "/appointments"


def cancel_appointment(db, ident, form):
    if find(db, "appointments", ident)["cancelled"]:
        raise Refused("That appointment is already cancelled.")
    db.execute("UPDATE appointments SET cancelled = 1 WHERE id = ?", (ident,))
    return "/appointments"


def low_stock(db):
    return db.execute("SELECT * FROM products WHERE stock <= low_at ORDER BY name COLLATE NOCASE, id").fetchall()


def sale_lines(db, ident):
    return db.execute("SELECT l.product_id, l.qty, l.unit_cents, p.name FROM sale_lines l "
                      "JOIN products p ON p.id = l.product_id WHERE l.sale_id = ? ORDER BY l.id", (ident,)).fetchall()


def export(db):
    def rows(sql):
        return [dict(row) for row in db.execute(sql).fetchall()]
    sales = rows("SELECT id, at, customer_id, method, total_cents, voided FROM sales ORDER BY id")
    for sale in sales:
        sale["voided"] = bool(sale["voided"])
        sale["lines"] = [{"product_id": line["product_id"], "qty": line["qty"], "unit_cents": line["unit_cents"]}
                         for line in sale_lines(db, sale["id"])]
    appointments = rows("SELECT id, pet_id, date, time, cancelled FROM appointments ORDER BY id")
    for appointment in appointments:
        appointment["cancelled"] = bool(appointment["cancelled"])
    return {
        "products": rows("SELECT id, name, price_cents, stock, low_at FROM products ORDER BY id"),
        "customers": rows("SELECT id, name, phone FROM customers ORDER BY id"),
        "pets": rows("SELECT id, customer_id, name, species FROM pets ORDER BY id"),
        "sales": sales,
        "appointments": appointments,
        "low_stock": [row["id"] for row in low_stock(db)],
    }


# ---- pages ----------------------------------------------------------------------------------

STYLE = """
:root { color-scheme: light dark; --ink: #1d2327; --soft: #5c6670; --paper: #f6f4ef; --card: #ffffff;
  --line: #d9d5cb; --accent: #0b6e69; --on-accent: #ffffff; --warn: #a23b1e; --warn-bg: #fbeae4; }
@media (prefers-color-scheme: dark) { :root { --ink: #e8e6e1; --soft: #a3abb2; --paper: #16191b;
  --card: #202427; --line: #394046; --accent: #58c4bd; --on-accent: #0c1f1e; --warn: #f0a48d; --warn-bg: #3a221b; } }
* { box-sizing: border-box; }
body { margin: 0; font: 16px/1.5 system-ui, sans-serif; color: var(--ink); background: var(--paper);
  overflow-wrap: break-word; }
header { background: var(--card); border-bottom: 1px solid var(--line); }
nav, main { max-width: 62rem; margin: 0 auto; padding: 0 1rem; }
nav { display: flex; flex-wrap: wrap; align-items: center; gap: 0 .25rem; }
nav a { padding: .7rem .6rem; color: var(--ink); text-decoration: none; border-bottom: 3px solid transparent; }
nav a.brand { font-weight: 700; padding-left: 0; margin-right: .5rem; }
nav a.here { border-bottom-color: var(--accent); color: var(--accent); }
main { padding-bottom: 3rem; }
h1 { font-size: 1.6rem; line-height: 1.25; margin: 1.5rem 0 1rem; }
h2 { font-size: 1.1rem; margin: 2rem 0 .6rem; }
a { color: var(--accent); }
p.note { color: var(--soft); margin: .4rem 0; }
.scroll { overflow-x: auto; background: var(--card); border: 1px solid var(--line); border-radius: 8px; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: .5rem .75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
tr:last-child td { border-bottom: 0; }
th { font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; color: var(--soft); white-space: nowrap; }
td.num, td.stock, th.num { text-align: right; font-variant-numeric: tabular-nums; }
td.when, td.short, td a, button, .tag { white-space: nowrap; }
td.words { min-width: 11rem; }
tr.off td { color: var(--soft); }
tr.off td.total { text-decoration: line-through; }
.tag { font-size: .8rem; padding: .1rem .5rem; border-radius: 99px; background: var(--warn-bg); color: var(--warn); }
form.card { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 1rem;
  max-width: 34rem; display: grid; gap: .75rem; }
label { display: block; font-size: .9rem; color: var(--soft); }
input, select, button { font: inherit; color: inherit; }
input[type=text], input[type=date], select { display: block; width: 100%; max-width: 100%; min-width: 0;
  padding: .45rem .55rem; background: var(--paper); border: 1px solid var(--line); border-radius: 6px; color: var(--ink); }
input:focus-visible, select:focus-visible, button:focus-visible, a:focus-visible { outline: 2px solid var(--accent);
  outline-offset: 2px; }
button { padding: .45rem .9rem; border: 1px solid var(--accent); border-radius: 6px; background: var(--accent);
  color: var(--on-accent); cursor: pointer; justify-self: start; }
button.quiet { background: transparent; color: var(--accent); }
button.danger { background: var(--warn); border-color: var(--warn); color: var(--card); }
.line { display: grid; grid-template-columns: minmax(0, 1fr) 5rem; gap: .5rem; }
.pair { display: grid; grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr)); gap: .75rem; }
fieldset { border: 0; padding: 0; margin: 0; min-width: 0; }
legend { padding: 0; font-size: .9rem; color: var(--soft); }
.choice { display: inline-block; margin: .2rem 1rem 0 0; color: var(--ink); font-size: 1rem; }
td form { display: flex; gap: .4rem; align-items: center; }
td form input[type=text] { width: 6rem; }
.refusal { background: var(--warn-bg); color: var(--warn); border-radius: 8px; padding: 1rem; max-width: 34rem; }
dl { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: .3rem 1rem; margin: 0; }
dt { color: var(--soft); } dd { margin: 0; }
"""

NAV = [("/products", "Products"), ("/customers", "Customers"), ("/sales", "Sales"), ("/appointments", "Appointments")]

esc = html.escape


def page(title, body, here=""):
    links = "".join('<a href="%s"%s>%s</a>' % (path, ' class="here"' if path == here else "", name)
                    for path, name in NAV)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>%s · Pet shop</title><style>%s</style></head><body>"
            '<header><nav><a class="brand" href="/">Pet shop</a>%s</nav></header>'
            "<main><h1>%s</h1>%s</main></body></html>") % (esc(title), STYLE, links, esc(title), body)


def table(heads, rows, empty):
    if not rows:
        return '<p class="note">%s</p>' % esc(empty)
    head = "".join('<th class="num">%s</th>' % h[1:] if h.startswith(">") else "<th>%s</th>" % h for h in heads)
    return '<div class="scroll"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (head, "".join(rows))


def cell(words, extra=""):
    """A cell of words: short ones stay on one line, long ones keep a readable width (L0018)."""
    return '<td class="%s">%s%s</td>' % ("short" if len(words) <= 20 else "words", esc(words), extra)


def options(rows, label):
    return "".join('<option value="%d">%s</option>' % (row["id"], esc(label(row))) for row in rows)


def home_page(db):
    low = ["<tr>%s<td class=\"stock\">%d</td><td class=\"num\">%d</td></tr>"
           % (cell(row["name"]), row["stock"], row["low_at"]) for row in low_stock(db)]
    body = ('<p><a href="/sales/new">New sale</a> · <a href="/appointments">Book grooming</a></p>'
            "<h2>Low stock</h2>" + table(["Product", ">In stock", ">Low at"], low, "Nothing is low."))
    body += "<h2>Grooming today</h2>" + table(["Time", "Pet", "Customer"], [
        '<tr><td class="when">%s</td>%s%s</tr>'
        % (row["time"], cell("%s (%s)" % (row["pet"], row["species"])), cell(row["owner"]))
        for row in appointments(db, "a.date = ? AND a.cancelled = 0", (today(),))], "No appointments today.")
    return page("Today", body)


def products_page(db):
    low = {row["id"] for row in low_stock(db)}
    rows = []
    for row in db.execute("SELECT * FROM products ORDER BY name COLLATE NOCASE, id").fetchall():
        rows.append(
            '<tr>%s<td class="num">%s</td><td class="stock">%d</td><td class="num">%d</td>'
            '<td><form method="post" action="/products/%d/stock">'
            '<input type="text" name="delta" inputmode="numeric" placeholder="+10 or -2" required '
            'aria-label="Stock adjustment for %s"><button class="quiet" type="submit">Adjust</button></form></td>'
            '<td><a href="/products/%d/edit">Edit</a></td></tr>'
            % (cell(row["name"], ' <span class="tag">low</span>' if row["id"] in low else ""), money(row["price_cents"]),
               row["stock"], row["low_at"], row["id"], esc(row["name"]), row["id"]))
    body = table(["Product", ">Price", ">In stock", ">Low at", "Received or removed", ""], rows, "No products yet.")
    body += ('<h2>New product</h2><form class="card" method="post" action="/products">'
             '<label>Name<input type="text" name="name" maxlength="%d" placeholder="Kibble 2 kg" required></label>'
             '<div class="pair"><label>Price, tax included<input type="text" name="price" inputmode="decimal" '
             'placeholder="12.50" required></label>'
             '<label>In stock<input type="text" name="stock" inputmode="numeric" required></label>'
             '<label>Low at or below<input type="text" name="low_at" inputmode="numeric" required></label></div>'
             '<button type="submit">Add product</button></form>') % MAX_NAME
    return page("Products", body, "/products")


def product_edit_page(db, ident):
    row = find(db, "products", ident)
    body = ('<form class="card" method="post" action="/products/%d/edit">'
            '<label>Name<input type="text" name="name" maxlength="%d" value="%s" required></label>'
            '<div class="pair"><label>Price, tax included<input type="text" name="price" inputmode="decimal" '
            'value="%s" required></label>'
            '<label>Low at or below<input type="text" name="low_at" inputmode="numeric" value="%d" required></label></div>'
            '<button type="submit">Save</button></form>'
            '<p class="note">Sales already made keep the price they were made at. '
            'Stock changes on the <a href="/products">products</a> page.</p>'
            ) % (ident, MAX_NAME, esc(row["name"]), money(row["price_cents"]), row["low_at"])
    return page("Edit %s" % row["name"], body, "/products")


def customers_page(db):
    customers = db.execute("SELECT * FROM customers ORDER BY name COLLATE NOCASE, id").fetchall()
    pets = db.execute("SELECT p.*, c.name AS owner FROM pets p JOIN customers c ON c.id = p.customer_id "
                      "ORDER BY p.name COLLATE NOCASE, p.id").fetchall()
    body = table(["Customer", "Phone", ""], [
        '<tr>%s%s<td><a href="/customers/%d/edit">Edit</a></td></tr>'
        % (cell(row["name"]), cell(row["phone"]), row["id"]) for row in customers], "No customers yet.")
    body += ('<h2>New customer</h2><form class="card" method="post" action="/customers">'
             '<label>Name<input type="text" name="name" maxlength="%d" placeholder="Ana Lima" required></label>'
             '<label>Phone, if any<input type="text" name="phone" maxlength="%d" placeholder="555-0101"></label>'
             '<button type="submit">Add customer</button></form>') % (MAX_NAME, MAX_PHONE)
    body += "<h2>Pets</h2>" + table(["Pet", "Species", "Customer", ""], [
        '<tr>%s%s%s<td><a href="/pets/%d/edit">Edit</a></td></tr>'
        % (cell(row["name"]), cell(row["species"]), cell(row["owner"]), row["id"]) for row in pets], "No pets yet.")
    body += ('<h2>New pet</h2><form class="card" method="post" action="/pets">'
             '<label>Customer<select name="customer_id" required><option value="">choose a customer</option>%s</select></label>'
             '<label>Pet name<input type="text" name="name" maxlength="%d" placeholder="Rex" required></label>'
             '<label>Species<input type="text" name="species" maxlength="%d" placeholder="dog or cat" required></label>'
             '<button type="submit">Add pet</button></form>'
             ) % (options(customers, lambda row: row["name"]), MAX_NAME, MAX_SPECIES)
    return page("Customers", body, "/customers")


def customer_edit_page(db, ident):
    row = find(db, "customers", ident)
    body = ('<form class="card" method="post" action="/customers/%d/edit">'
            '<label>Name<input type="text" name="name" maxlength="%d" value="%s" required></label>'
            '<label>Phone, if any<input type="text" name="phone" maxlength="%d" value="%s"></label>'
            '<button type="submit">Save</button></form>'
            ) % (ident, MAX_NAME, esc(row["name"]), MAX_PHONE, esc(row["phone"]))
    return page("Edit %s" % row["name"], body, "/customers")


def pet_edit_page(db, ident):
    row = find(db, "pets", ident)
    owner = find(db, "customers", row["customer_id"])
    body = ('<form class="card" method="post" action="/pets/%d/edit">'
            '<label>Pet name<input type="text" name="name" maxlength="%d" value="%s" required></label>'
            '<label>Species<input type="text" name="species" maxlength="%d" value="%s" required></label>'
            '<button type="submit">Save</button></form><p class="note">Belongs to %s.</p>'
            ) % (ident, MAX_NAME, esc(row["name"]), MAX_SPECIES, esc(row["species"]), esc(owner["name"]))
    return page("Edit %s" % row["name"], body, "/customers")


def sales_page(db):
    total = db.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    rows = []
    for sale in db.execute("SELECT s.*, c.name AS customer FROM sales s LEFT JOIN customers c ON c.id = s.customer_id "
                           "ORDER BY s.id DESC LIMIT ?", (LISTED,)).fetchall():
        items = ", ".join("%d × %s" % (line["qty"], line["name"]) for line in sale_lines(db, sale["id"]))
        last = ('<span class="tag">voided</span>' if sale["voided"]
                else '<a href="/sales/%d/void">Void</a>' % sale["id"])
        rows.append('<tr%s><td class="num">%d</td><td class="when">%s</td>%s%s<td>%s</td>'
                    '<td class="num total">%s</td><td>%s</td></tr>'
                    % (' class="off"' if sale["voided"] else "", sale["id"], sale["at"], cell(sale["customer"] or "—"),
                       cell(items), sale["method"], money(sale["total_cents"]), last))
    body = '<p><a href="/sales/new">New sale</a></p>' + table(
        [">No.", "When", "Customer", "Items", "Paid by", ">Total", ""], rows, "No sales yet.")
    if total > LISTED:
        body += '<p class="note">The latest %d of %d sales. All of them are in <a href="/export.json">export.json</a>.</p>' % (LISTED, total)
    return page("Sales", body, "/sales")


def sale_new_page(db):
    customers = db.execute("SELECT * FROM customers ORDER BY name COLLATE NOCASE, id").fetchall()
    products = options(db.execute("SELECT * FROM products ORDER BY name COLLATE NOCASE, id").fetchall(),
                       lambda row: "%s (%s, %d in stock)" % (row["name"], money(row["price_cents"]), row["stock"]))
    line = ('<div class="line"><select name="product_id" aria-label="Product %d"><option value="">—</option>' + products
            + '</select><input type="text" name="qty" inputmode="numeric" aria-label="Quantity %d"></div>')
    body = ('<form class="card" method="post" action="/sales">'
            '<label>Customer<select name="customer_id"><option value="">no customer</option>%s</select></label>'
            "<fieldset><legend>Products and quantities; leave unused lines empty</legend>%s</fieldset>"
            "<fieldset><legend>Paid by</legend>%s</fieldset>"
            '<button type="submit">Record sale</button></form>'
            '<p class="note">The total is worked out from the prices above when the sale is recorded.</p>'
            ) % (options(customers, lambda row: row["name"]),
                 "".join(line % (n, n) for n in range(1, SALE_ROWS + 1)),
                 "".join('<label class="choice"><input type="radio" name="method" value="%s" required> %s</label>'
                         % (method, method) for method in METHODS))
    return page("New sale", body, "/sales")


def sale_void_page(db, ident):
    found = db.execute("SELECT s.*, c.name AS customer FROM sales s LEFT JOIN customers c ON c.id = s.customer_id "
                       "WHERE s.id = ?", (ident,)).fetchone()
    if found is None:
        raise NotFound()
    items = "".join("<li>%d × %s at %s</li>" % (line["qty"], esc(line["name"]), money(line["unit_cents"]))
                    for line in sale_lines(db, ident))
    body = ("<dl><dt>When</dt><dd>%s</dd><dt>Customer</dt><dd>%s</dd><dt>Paid by</dt><dd>%s</dd>"
            "<dt>Total</dt><dd>%s</dd></dl><ul>%s</ul>"
            ) % (found["at"], esc(found["customer"] or "—"), found["method"], money(found["total_cents"]), items)
    if not found["voided"]:
        body += ('<p>Voiding puts these items back in stock and cannot be undone.</p>'
                 '<form method="post" action="/sales/%d/void"><button class="danger" type="submit">Void this sale</button>'
                 '</form><p><a href="/sales">Keep the sale</a></p>') % ident
        return page("Void sale %d?" % ident, body, "/sales")
    return page("Sale %d is voided" % ident, body + '<p><a href="/sales">Back to sales</a></p>', "/sales")


def appointments(db, where, values):
    return db.execute("SELECT a.*, p.name AS pet, p.species, c.name AS owner FROM appointments a "
                      "JOIN pets p ON p.id = a.pet_id JOIN customers c ON c.id = p.customer_id "
                      "WHERE %s ORDER BY a.date, a.time, a.id" % where, values).fetchall()


def appointments_page(db):
    rows = []
    for row in appointments(db, "a.date >= ?", (today(),)):
        last = ('<span class="tag">cancelled</span>' if row["cancelled"] else
                '<form method="post" action="/appointments/%d/cancel"><button class="quiet" type="submit">Cancel</button></form>'
                % row["id"])
        rows.append('<tr%s><td class="when">%s</td><td class="when">%s</td>%s%s<td>%s</td></tr>'
                    % (' class="off"' if row["cancelled"] else "", row["date"], row["time"],
                       cell("%s (%s)" % (row["pet"], row["species"])), cell(row["owner"]), last))
    pets = db.execute("SELECT p.id, p.name, c.name AS owner FROM pets p JOIN customers c ON c.id = p.customer_id "
                      "ORDER BY p.name COLLATE NOCASE, p.id").fetchall()
    body = table(["Date", "Time", "Pet", "Customer", ""], rows, "Nothing booked from today on.")
    body += ('<h2>Book grooming</h2><form class="card" method="post" action="/appointments">'
             '<label>Pet<select name="pet_id" required><option value="">choose a pet</option>%s</select></label>'
             '<div class="pair"><label>Date<input type="date" name="date" min="%s" required></label>'
             '<label>Starts at<select name="time" required><option value="">choose a time</option>%s</select></label></div>'
             '<button type="submit">Book</button></form>'
             '<p class="note">One groomer, one hour per appointment, %s to %s every day. '
             'Add the pet under <a href="/customers">Customers</a> first.</p>'
             ) % (options(pets, lambda row: "%s (%s)" % (row["name"], row["owner"])), today(),
                  "".join("<option>%s</option>" % slot for slot in SLOTS), SLOTS[0], SLOTS[-1])
    return page("Appointments", body, "/appointments")


GET = [
    (r"/", home_page), (r"/products", products_page), (r"/products/(\d{1,18})/edit", product_edit_page),
    (r"/customers", customers_page), (r"/customers/(\d{1,18})/edit", customer_edit_page),
    (r"/pets/(\d{1,18})/edit", pet_edit_page), (r"/sales", sales_page), (r"/sales/new", sale_new_page),
    (r"/sales/(\d{1,18})/void", sale_void_page), (r"/appointments", appointments_page),
]
POST = [
    (r"/products", add_product), (r"/products/(\d{1,18})/edit", edit_product),
    (r"/products/(\d{1,18})/stock", adjust_stock), (r"/customers", add_customer),
    (r"/customers/(\d{1,18})/edit", edit_customer), (r"/pets", add_pet), (r"/pets/(\d{1,18})/edit", edit_pet),
    (r"/sales", add_sale), (r"/sales/(\d{1,18})/void", void_sale), (r"/appointments", add_appointment),
    (r"/appointments/(\d{1,18})/cancel", cancel_appointment),
]


def route(routes, path):
    for pattern, action in routes:
        found = re.fullmatch(pattern, path)
        if found:
            return action, [int(group) for group in found.groups()]
    raise NotFound()


# ---- the server -----------------------------------------------------------------------------

LOCK = threading.Lock()  # one request at a time touches the database


class Handler(BaseHTTPRequestHandler):
    timeout = 30

    def log_message(self, *args):
        pass

    def answer(self, status, body, kind="text/html; charset=utf-8", location=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
                         "frame-ancestors 'none'; base-uri 'none'")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(data)

    def refuse(self, status, title, why):
        self.answer(status, page(title, '<p class="refusal">%s</p>%s' % (esc(why), (
            '<p class="note">Go back in the browser to correct it: what you typed is still there.</p>'
            if status == 400 else ""))))

    def foreign(self, posting):
        """True when the request is not from this shop's own pages on this machine (L0007)."""
        host = self.headers.get("Host")
        if host not in self.server.hosts:
            return True
        if posting:
            origin, allowed = self.headers.get("Origin"), ("http://" + host,)
            if origin is not None and origin not in allowed:
                return True
            site = self.headers.get("Sec-Fetch-Site")
            if site not in (None, "same-origin", "none"):
                return True
        return False

    def handle_with(self, routes, form):
        path = urllib.parse.urlsplit(self.path).path
        try:
            action, idents = route(routes, path) if path != "/export.json" or form is not None else (None, [])
            with LOCK:
                db = sqlite3.connect(self.server.db, isolation_level=None)
                db.row_factory = sqlite3.Row
                try:
                    db.execute("PRAGMA foreign_keys = ON")
                    db.execute("BEGIN IMMEDIATE")
                    if action is None:
                        result = json.dumps(export(db), indent=1)
                    elif form is None:
                        result = action(db, *idents)
                    else:
                        result = action(db, *idents, form)
                    db.execute("COMMIT")
                except BaseException:
                    if db.in_transaction:
                        db.execute("ROLLBACK")
                    raise
                finally:
                    db.close()
        except Refused as why:
            return self.refuse(400, "Not saved", str(why))
        except NotFound:
            return self.refuse(404, "Not found", "There is nothing at this address.")
        except Exception as error:  # nothing was stored: the transaction was rolled back
            return self.refuse(500, "Something went wrong", "Nothing was saved. (%s)" % type(error).__name__)
        if action is None:
            self.answer(200, result, "application/json; charset=utf-8")
        elif form is None:
            self.answer(200, result)
        else:
            self.answer(303, "", location=result)

    def do_GET(self):
        if self.foreign(False):
            return self.refuse(403, "Refused", "This shop answers only to its own address on this machine.")
        self.handle_with(GET, None)

    def do_POST(self):
        if self.foreign(True):
            return self.refuse(403, "Refused", "This form was not sent from the shop's own pages.")
        try:
            length = int(self.headers.get("Content-Length") or "")
            if length < 0:
                raise ValueError(length)
        except ValueError:
            return self.refuse(400, "Not saved", "The form arrived without its length.")
        if length > MAX_FORM:
            self.rfile.read(min(length, 16 * MAX_FORM))  # so the browser can hear the answer
            self.close_connection = True
            return self.refuse(413, "Too large", "A form can have at most %d bytes." % MAX_FORM)
        try:
            form = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True,
                                         strict_parsing=length > 0, max_num_fields=200)
        except ValueError:
            return self.refuse(400, "Not saved", "The form could not be read.")
        self.handle_with(POST, form)


SAMPLE = [
    (add_product, {"name": "Kibble adult dog 2 kg", "price": "12.50", "stock": "14", "low_at": "4"}),
    (add_product, {"name": "Cat litter 10 L", "price": "8.90", "stock": "3", "low_at": "5"}),
    (add_product, {"name": "Rubber ball", "price": "3.00", "stock": "25", "low_at": "5"}),
    (add_product, {"name": "Flea collar, small", "price": "19.99", "stock": "6", "low_at": "2"}),
    (add_customer, {"name": "Ana Lima", "phone": "555-0101"}),
    (add_customer, {"name": "Bruno Costa", "phone": ""}),
    (add_pet, {"customer_id": "1", "name": "Rex", "species": "dog"}),
    (add_pet, {"customer_id": "1", "name": "Mia", "species": "cat"}),
    (add_pet, {"customer_id": "2", "name": "Thor", "species": "dog"}),
]


def prepare(path, sample):
    db = sqlite3.connect(path, isolation_level=None)
    db.row_factory = sqlite3.Row
    try:
        db.executescript(SCHEMA)
        if sample and not db.execute("SELECT 1 FROM products UNION ALL SELECT 1 FROM customers").fetchone():
            db.execute("BEGIN IMMEDIATE")
            for action, fields in SAMPLE:
                action(db, {name: [value] for name, value in fields.items()})
            db.execute("COMMIT")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Pet shop for the staff, in a browser on this machine.")
    parser.add_argument("--db", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "petshop.db"),
                        help="the SQLite file that holds everything (default: petshop.db beside this program)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--sample", action="store_true", help="add a few products, customers and pets to an empty shop")
    args = parser.parse_args()
    prepare(args.db, args.sample)
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    server.daemon_threads = True
    server.db = args.db
    port = server.server_address[1]
    server.hosts = {"%s:%d" % (name, port) for name in ("127.0.0.1", "localhost")}
    if port == 80:
        server.hosts |= {"127.0.0.1", "localhost"}
    print("Pet shop at http://127.0.0.1:%d/  (data in %s; Ctrl+C stops it)" % (port, args.db), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Pet shop: products and stock, customers and their pets, counter sales, grooming.

For staff, in a browser on this machine. One program, one SQLite file, Python's
standard library only.

    python3 product/petshop.py [--db FILE] [--port N] [--sample]
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

MAX_FORM = 65536
MAX_STOCK = 1000000
MAX_CENTS = 9999999
MAX_LINES = 20
MAX_QTY = 1000
SHOWN_SALES = 200
FORM_LINES = 6
METHODS = ("cash", "card", "other")
SLOTS = tuple("%02d:00" % hour for hour in range(9, 18))

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
    price_cents INTEGER NOT NULL CHECK (price_cents BETWEEN 1 AND 9999999),
    stock INTEGER NOT NULL CHECK (stock BETWEEN 0 AND 1000000),
    low_at INTEGER NOT NULL CHECK (low_at BETWEEN 0 AND 1000000));
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
    phone TEXT NOT NULL CHECK (length(phone) <= 30));
CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 80),
    species TEXT NOT NULL CHECK (length(species) BETWEEN 1 AND 40));
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT NOT NULL,
    method TEXT NOT NULL CHECK (method IN ('cash', 'card', 'other')),
    customer_id INTEGER REFERENCES customers(id),
    total_cents INTEGER NOT NULL CHECK (total_cents > 0),
    voided INTEGER NOT NULL DEFAULT 0 CHECK (voided IN (0, 1)));
CREATE TABLE IF NOT EXISTS sale_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL REFERENCES sales(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    qty INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 1000),
    unit_cents INTEGER NOT NULL CHECK (unit_cents BETWEEN 1 AND 9999999));
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL REFERENCES pets(id),
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    cancelled INTEGER NOT NULL DEFAULT 0 CHECK (cancelled IN (0, 1)));
CREATE UNIQUE INDEX IF NOT EXISTS one_live_appointment_per_slot
    ON appointments (date, time) WHERE cancelled = 0;
"""


class Refused(Exception):
    """What was sent cannot be stored. The message is shown to the person."""


class Missing(Exception):
    """There is no such page or row."""


# ---- what comes in ------------------------------------------------------------------------------

class Form:
    def __init__(self, pairs=()):
        self.pairs = [(name, value.strip()) for name, value in pairs]

    def many(self, name):
        return [value for other, value in self.pairs if other == name]

    def one(self, name):
        return (self.many(name) or [""])[0]


def words(form, name, label, low, high):
    value = form.one(name)
    if not low <= len(value) <= high:
        if low:
            raise Refused("%s must be %d to %d characters." % (label, low, high))
        raise Refused("%s must be at most %d characters." % (label, high))
    return value


def whole(value, label, low, high):
    if not re.fullmatch("[0-9]{1,7}", value) or not low <= int(value) <= high:
        raise Refused("%s must be a whole number from %s to %s." % (label, commas(low), commas(high)))
    return int(value)


def price(form):
    found = re.fullmatch(r"([0-9]{1,5})(?:\.([0-9]{1,2}))?", form.one("price"))
    cents = int(found.group(1)) * 100 + int((found.group(2) or "").ljust(2, "0")) if found else 0
    if not 1 <= cents <= MAX_CENTS:
        raise Refused("Price must be from 0.01 to 99999.99, written with digits and at most "
                      "one point and two decimals, like 12.50.")
    return cents


def ident(value):
    return int(value) if re.fullmatch("[0-9]{1,9}", value) else None


def money(cents):
    return "%d.%02d" % divmod(cents, 100)


def commas(number):
    return format(number, ",")


def today():
    return datetime.date.today().isoformat()


def esc(value):
    return html.escape(str(value), quote=True)


# ---- what is stored -----------------------------------------------------------------------------

def find(db, table, key):
    row = db.execute("SELECT * FROM %s WHERE id = ?" % table, (key,)).fetchone() if key is not None else None
    if row is None:
        raise Missing()
    return row


def product_fields(form, with_stock):
    name = words(form, "name", "Name", 1, 80)
    cents = price(form)
    stock = whole(form.one("stock"), "Stock", 0, MAX_STOCK) if with_stock else None
    return name, cents, stock, whole(form.one("low_at"), "Low-stock threshold", 0, MAX_STOCK)


def customer_fields(form):
    return words(form, "name", "Name", 1, 80), words(form, "phone", "Phone", 0, 30)


def pet_fields(form):
    return words(form, "name", "Name", 1, 80), words(form, "species", "Species", 1, 40)


def lines_of(db, sale_id):
    return db.execute("SELECT l.product_id, l.qty, l.unit_cents, p.name FROM sale_lines l "
                      "JOIN products p ON p.id = l.product_id WHERE l.sale_id = ? ORDER BY l.id",
                      (sale_id,)).fetchall()


def export(db):
    def rows(sql):
        return [dict(row) for row in db.execute(sql)]
    sales = rows("SELECT id, at, method, customer_id, total_cents, voided FROM sales ORDER BY id")
    lines = {}
    for line in db.execute("SELECT sale_id, product_id, qty, unit_cents FROM sale_lines ORDER BY id"):
        lines.setdefault(line["sale_id"], []).append(
            {"product_id": line["product_id"], "qty": line["qty"], "unit_cents": line["unit_cents"]})
    for sale in sales:
        sale["voided"] = bool(sale["voided"])
        sale["lines"] = lines.get(sale["id"], [])
    appointments = rows("SELECT id, pet_id, date, time, cancelled FROM appointments ORDER BY id")
    for appointment in appointments:
        appointment["cancelled"] = bool(appointment["cancelled"])
    return {
        "products": rows("SELECT id, name, price_cents, stock, low_at FROM products ORDER BY id"),
        "customers": rows("SELECT id, name, phone FROM customers ORDER BY id"),
        "pets": rows("SELECT id, customer_id, name, species FROM pets ORDER BY id"),
        "sales": sales,
        "appointments": appointments,
        "low_stock": [row["id"] for row in db.execute("SELECT id FROM products WHERE stock <= low_at ORDER BY id")],
    }


def sample(db):
    if db.execute("SELECT (SELECT count(*) FROM products) + (SELECT count(*) FROM customers)").fetchone()[0]:
        return False
    db.executemany("INSERT INTO products (name, price_cents, stock, low_at) VALUES (?, ?, ?, ?)", [
        ("Dry dog food, chicken, 2 kg", 1890, 14, 5), ("Cat litter 10 L", 890, 3, 5),
        ("Flea collar, small", 1999, 6, 2), ("Rope toy", 650, 22, 4), ("Aquarium filter cartridge", 1275, 0, 2)])
    db.executemany("INSERT INTO customers (name, phone) VALUES (?, ?)",
                   [("Ana Lima", "555-0101"), ("Bruno Costa", "555-0102"), ("Chen Wei", "")])
    db.executemany("INSERT INTO pets (customer_id, name, species) VALUES (?, ?, ?)",
                   [(1, "Rex", "dog"), (1, "Mia", "cat"), (2, "Biscuit", "golden retriever")])
    db.execute("INSERT INTO sales (at, method, customer_id, total_cents) VALUES (?, 'card', 1, 2540)", (now(),))
    db.executemany("INSERT INTO sale_lines (sale_id, product_id, qty, unit_cents) VALUES (1, ?, ?, ?)",
                   [(1, 1, 1890), (4, 1, 650)])
    db.executemany("INSERT INTO appointments (pet_id, date, time) VALUES (?, ?, ?)",
                   [(1, today(), "10:00"), (3, today(), "14:00")])
    return True


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


# ---- pages --------------------------------------------------------------------------------------

STYLE = """
:root{color-scheme:light dark;--bg:#f5f4ef;--card:#fff;--ink:#1c1d1a;--soft:#5b5d55;--line:#d6d3c8;
--accent:#17694e;--on:#fff;--warn:#9a3412}
@media (prefers-color-scheme:dark){:root{--bg:#151613;--card:#1f211d;--ink:#eceae3;--soft:#a9a89e;
--line:#393b35;--accent:#74caa8;--on:#10221b;--warn:#f2a477}}
*{box-sizing:border-box}
body{margin:0;font:16px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);
color:var(--ink);overflow-wrap:anywhere}
nav{display:flex;flex-wrap:wrap;gap:.25rem 1.1rem;padding:.7rem 1rem;background:var(--card);
border-bottom:1px solid var(--line)}
nav a{white-space:nowrap;text-decoration:none;font-weight:600}
nav a.here{text-decoration:underline;text-underline-offset:.3em}
a{color:var(--accent)}
main{max-width:62rem;margin:0 auto;padding:1rem 1rem 3rem}
h1{font-size:1.5rem;margin:.6rem 0 1rem}
h2{font-size:1.1rem;margin:1.8rem 0 .6rem}
p{margin:.5rem 0}
.soft{color:var(--soft)}
.warn{color:var(--warn);font-weight:600}
.scroll{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;vertical-align:top;white-space:nowrap;padding:.5rem .65rem;border-bottom:1px solid var(--line)}
tr:last-child td{border-bottom:0}
th{font-size:.82rem;color:var(--soft);font-weight:600}
td.words{white-space:normal;min-width:150px}
.num,.stock{text-align:right;font-variant-numeric:tabular-nums}
tr.off td{color:var(--soft)}
form.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:1rem;margin:0 0 1rem;
display:grid;gap:.8rem;grid-template-columns:repeat(auto-fit,minmax(min(100%,11rem),1fr));align-items:end}
form.card.stack{display:block}
form.card.stack>*{margin:0 0 .9rem}
form.card.stack>:last-child{margin-bottom:0}
label{display:grid;gap:.2rem;min-width:0;font-size:.88rem;color:var(--soft)}
input,select,button{font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);
border-radius:6px;padding:.45rem .55rem;min-width:0;max-width:100%}
form.card input,form.card select{width:100%}
button{white-space:nowrap;cursor:pointer;background:var(--accent);color:var(--on);border-color:var(--accent);
font-weight:600}
button.danger{background:var(--warn);border-color:var(--warn)}
td form{display:flex;gap:.4rem;margin:-.2rem 0}
td input{width:7.5rem;padding:.25rem .4rem}
td button{padding:.25rem .6rem}
fieldset{border:0;padding:0;min-width:0;display:flex;flex-wrap:wrap;gap:.3rem 1.2rem}
legend{padding:0;font-size:.88rem;color:var(--soft);margin-bottom:.2rem}
fieldset label{display:flex;gap:.4rem;align-items:center;font-size:1rem;color:var(--ink);white-space:nowrap}
form.card fieldset input{width:auto}
.line{display:flex;gap:.5rem}
.line select{flex:1 1 0}
form.card .line input{flex:0 0 5rem;width:5rem}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""

NAV = (("/", "Today"), ("/products", "Products"), ("/customers", "Customers"), ("/sales", "Sales"),
       ("/appointments", "Appointments"))


def page(title, body, status=200, here=None):
    links = "".join('<a href="%s"%s>%s</a>' % (path, ' class="here"' if path == here else "", label)
                    for path, label in NAV)
    return status, "text/html; charset=utf-8", (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        "<title>%s · Pet shop</title><style>%s</style></head><body><nav>%s</nav><main><h1>%s</h1>%s</main></body></html>"
        % (esc(title), STYLE, links, esc(title), body))


def table(head, rows, none):
    """head: (label, class) per column. rows: (row class, [cell html])."""
    if not rows:
        return '<p class="soft">%s</p>' % esc(none)
    out = ['<div class="scroll"><table><thead><tr>']
    out += ['<th class="%s">%s</th>' % (cls if cls != "words" else "", esc(label)) for label, cls in head]
    out.append("</tr></thead><tbody>")
    for row_class, cells in rows:
        out.append('<tr class="%s">' % row_class)
        out += ['<td class="%s">%s</td>' % (cls, cell) for (_, cls), cell in zip(head, cells)]
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def field(label, name, value="", example=None, required=True, **more):
    attrs = "".join(' %s="%s"' % (key, esc(val)) for key, val in more.items())
    if example:
        attrs += ' placeholder="%s"' % esc(example)
    return '<label>%s <input name="%s" value="%s"%s%s></label>' % (
        esc(label), name, esc(value), " required" if required else "", attrs)


def select(name, options, label=None, required=True, aria=None):
    """A select that arrives with nothing chosen. options: (value, text)."""
    inner = '<option value="">%s</option>' % ("Choose…" if required else "None")
    inner += "".join('<option value="%s">%s</option>' % (esc(value), esc(text)) for value, text in options)
    control = '<select name="%s"%s%s>%s</select>' % (
        name, " required" if required else "", ' aria-label="%s"' % esc(aria) if aria else "", inner)
    return "<label>%s %s</label>" % (esc(label), control) if label else control


def product_form(action, button, row=None):
    return ('<form class="card" method="post" action="%s">' % action
            + field("Name", "name", row["name"] if row else "", "Rope toy", maxlength=80)
            + field("Price", "price", money(row["price_cents"]) if row else "", "12.50", inputmode="decimal")
            + ("" if row else field("Stock", "stock", "", "20", inputmode="numeric"))
            + field("Low-stock threshold", "low_at", row["low_at"] if row else "", "5", inputmode="numeric")
            + '<button type="submit">%s</button></form>' % button)


def customer_form(action, button, row=None):
    return ('<form class="card" method="post" action="%s">' % action
            + field("Name", "name", row["name"] if row else "", "Ana Lima", maxlength=80)
            + field("Phone", "phone", row["phone"] if row else "", "555-0101", required=False, maxlength=30)
            + '<button type="submit">%s</button></form>' % button)


def sale_summary(db, sale):
    customer = find(db, "customers", sale["customer_id"])["name"] if sale["customer_id"] else "none"
    lines = [("", [esc(line["name"]), str(line["qty"]), money(line["unit_cents"]),
                   money(line["qty"] * line["unit_cents"])]) for line in lines_of(db, sale["id"])]
    return ("<p>Sale %d, %s. Customer: %s. Paid by %s.</p>" % (sale["id"], esc(sale["at"]), esc(customer), sale["method"])
            + table([("Item", "words"), ("Qty", "num"), ("Each", "num"), ("Amount", "num")], lines, "")
            + "<p><strong>Total %s</strong></p>" % money(sale["total_cents"]))


# ---- what each address does ---------------------------------------------------------------------

def home(db, form):
    low = [("", [esc(row["name"]), str(row["stock"]), str(row["low_at"])]) for row in db.execute(
        "SELECT * FROM products WHERE stock <= low_at ORDER BY stock, name")]
    booked = [("", [row["time"], esc(row["pet"]), esc(row["species"]), esc(row["customer"])]) for row in db.execute(
        "SELECT a.time, p.name AS pet, p.species, c.name AS customer FROM appointments a JOIN pets p ON p.id = a.pet_id "
        "JOIN customers c ON c.id = p.customer_id WHERE a.date = ? AND a.cancelled = 0 ORDER BY a.time", (today(),))]
    return page("Today", (
        '<p><a href="/sales/new">New sale</a></p><h2>Grooming today</h2>'
        + table([("Time", ""), ("Pet", "words"), ("Species", "words"), ("Customer", "words")], booked,
                "No grooming booked for today.")
        + "<h2>Low stock</h2>"
        + table([("Product", "words"), ("Stock", "stock"), ("Low at", "num")], low,
                "No product is at or below its threshold.")), here="/")


def products(db, form):
    rows = []
    for row in db.execute("SELECT * FROM products ORDER BY id"):
        adjust = ('<form method="post" action="/products/%d/stock"><input name="delta" required inputmode="numeric" '
                  'placeholder="+10 or -2" aria-label="Change the stock of %s by"><button type="submit">Adjust</button></form>'
                  % (row["id"], esc(row["name"])))
        low = row["stock"] <= row["low_at"]
        rows.append(("", [esc(row["name"]), money(row["price_cents"]), str(row["stock"]), str(row["low_at"]),
                          '<span class="warn">low</span>' if low else "", adjust,
                          '<a href="/products/%d/edit">Edit</a>' % row["id"]]))
    return page("Products", (
        table([("Product", "words"), ("Price", "num"), ("Stock", "stock"), ("Low at", "num"), ("", ""),
               ("Received or removed", ""), ("", "")], rows, "No products yet.")
        + "<h2>New product</h2>" + product_form("/products", "Add product")
        + '<p class="soft">Prices include tax. Stock changes only by a sale, a void or an adjustment.</p>'),
        here="/products")


def product_add(db, form):
    name, cents, stock, low_at = product_fields(form, True)
    db.execute("INSERT INTO products (name, price_cents, stock, low_at) VALUES (?, ?, ?, ?)", (name, cents, stock, low_at))
    return "/products"


def product_edit(db, form, key):
    row = find(db, "products", key)
    return page("Edit " + row["name"], product_form("/products/%d/edit" % key, "Save", row)
                + '<p class="soft">Stock is %d. It is changed on the list of products, not here.</p>'
                  '<p><a href="/products">Back to products</a></p>' % row["stock"], here="/products")


def product_save(db, form, key):
    find(db, "products", key)
    name, cents, _, low_at = product_fields(form, False)
    db.execute("UPDATE products SET name = ?, price_cents = ?, low_at = ? WHERE id = ?", (name, cents, low_at, key))
    return "/products"


def product_stock(db, form, key):
    row = find(db, "products", key)
    found = re.fullmatch("[+-]?[0-9]{1,7}", form.one("delta"))
    delta = int(found.group()) if found else 0
    if delta == 0:
        raise Refused("An adjustment must be a whole number other than 0, like +10 or -2.")
    if not 0 <= row["stock"] + delta <= MAX_STOCK:
        raise Refused("%s has %d in stock; an adjustment of %+d would leave %s. Stock stays between 0 and %s."
                      % (row["name"], row["stock"], delta, commas(row["stock"] + delta), commas(MAX_STOCK)))
    db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (delta, key))
    return "/products"


def customers(db, form):
    people = db.execute("SELECT * FROM customers ORDER BY id").fetchall()
    rows = [("", [esc(row["name"]), esc(row["phone"]), '<a href="/customers/%d/edit">Edit</a>' % row["id"]])
            for row in people]
    pets = [("", [esc(row["name"]), esc(row["species"]), esc(row["customer"]), '<a href="/pets/%d/edit">Edit</a>' % row["id"]])
            for row in db.execute("SELECT p.*, c.name AS customer FROM pets p JOIN customers c ON c.id = p.customer_id ORDER BY p.id")]
    return page("Customers", (
        table([("Customer", "words"), ("Phone", ""), ("", "")], rows, "No customers yet.")
        + "<h2>New customer</h2>" + customer_form("/customers", "Add customer")
        + "<h2>Pets</h2>"
        + table([("Pet", "words"), ("Species", "words"), ("Customer", "words"), ("", "")], pets, "No pets yet.")
        + '<h2>New pet</h2><form class="card" method="post" action="/pets">'
        + select("customer_id", [(row["id"], row["name"]) for row in people], "Customer")
        + field("Name", "name", "", "Rex", maxlength=80) + field("Species", "species", "", "dog", maxlength=40)
        + '<button type="submit">Add pet</button></form>'), here="/customers")


def customer_add(db, form):
    db.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", customer_fields(form))
    return "/customers"


def customer_edit(db, form, key):
    row = find(db, "customers", key)
    return page("Correct " + row["name"], customer_form("/customers/%d/edit" % key, "Save", row)
                + '<p><a href="/customers">Back to customers</a></p>', here="/customers")


def customer_save(db, form, key):
    find(db, "customers", key)
    db.execute("UPDATE customers SET name = ?, phone = ? WHERE id = ?", customer_fields(form) + (key,))
    return "/customers"


def pet_add(db, form):
    owner = ident(form.one("customer_id"))
    if owner is None or not db.execute("SELECT 1 FROM customers WHERE id = ?", (owner,)).fetchone():
        raise Refused("Choose the customer the pet belongs to.")
    db.execute("INSERT INTO pets (customer_id, name, species) VALUES (?, ?, ?)", (owner,) + pet_fields(form))
    return "/customers"


def pet_edit(db, form, key):
    row = find(db, "pets", key)
    owner = find(db, "customers", row["customer_id"])
    return page("Correct " + row["name"], (
        '<form class="card" method="post" action="/pets/%d/edit">' % key
        + field("Name", "name", row["name"], "Rex", maxlength=80)
        + field("Species", "species", row["species"], "dog", maxlength=40)
        + '<button type="submit">Save</button></form>'
        + "<p>Belongs to %s. A pet stays with its customer.</p>" % esc(owner["name"])
        + '<p><a href="/customers">Back to customers</a></p>'), here="/customers")


def pet_save(db, form, key):
    find(db, "pets", key)
    db.execute("UPDATE pets SET name = ?, species = ? WHERE id = ?", pet_fields(form) + (key,))
    return "/customers"


def sales(db, form):
    total = db.execute("SELECT count(*) FROM sales").fetchone()[0]
    rows = []
    for sale in db.execute("SELECT s.*, c.name AS customer FROM sales s LEFT JOIN customers c ON c.id = s.customer_id "
                           "ORDER BY s.id DESC LIMIT ?", (SHOWN_SALES,)).fetchall():
        items = ", ".join("%d × %s" % (line["qty"], line["name"]) for line in lines_of(db, sale["id"]))
        rows.append(("off" if sale["voided"] else "", [
            str(sale["id"]), esc(sale["at"]), esc(items), esc(sale["customer"] or ""), sale["method"],
            money(sale["total_cents"]),
            "voided" if sale["voided"] else '<a href="/sales/%d/void">Void</a>' % sale["id"]]))
    said = ("Showing the latest %d of %s sales. The rest are in <a href=\"/export.json\">the export</a>."
            % (SHOWN_SALES, commas(total)) if total > SHOWN_SALES else "%s in all." % commas(total))
    return page("Sales", (
        '<p><a href="/sales/new">New sale</a></p>'
        + table([("No.", "num"), ("When", ""), ("Items", "words"), ("Customer", "words"), ("Paid by", ""),
                 ("Total", "num"), ("", "")], rows, "No sales yet.")
        + '<p class="soft">%s A sale is never edited; a mistake is voided whole and entered again.</p>' % said),
        here="/sales")


def sale_new(db, form):
    count = MAX_LINES if form.one("lines") == str(MAX_LINES) else FORM_LINES
    items = [(row["id"], "%s (%s, %d in stock)" % (row["name"], money(row["price_cents"]), row["stock"]))
             for row in db.execute("SELECT * FROM products ORDER BY name, id")]
    lines = "".join(
        '<div class="line">%s<input name="qty" inputmode="numeric" placeholder="1" aria-label="Quantity, line %d"></div>'
        % (select("product_id", items, required=False, aria="Product, line %d" % number), number)
        for number in range(1, count + 1))
    methods = "".join('<label><input type="radio" name="method" value="%s" required> %s</label>'
                      % (method, method.capitalize()) for method in METHODS)
    more = ("" if count == MAX_LINES else
            '<p class="soft">A sale holds up to %d lines. <a href="/sales/new?lines=%d">Show %d lines</a> '
            "(what is typed here is not carried over).</p>" % (MAX_LINES, MAX_LINES, MAX_LINES))
    return page("New sale", (
        '<form class="card stack" method="post" action="/sales">'
        + select("customer_id", [(row["id"], row["name"]) for row in db.execute("SELECT * FROM customers ORDER BY name, id")],
                 "Customer (optional)", required=False)
        + "<div><p class=\"soft\">Product and quantity, one line each. Empty lines are ignored.</p>" + lines + "</div>"
        + "<fieldset><legend>Paid by</legend>" + methods + "</fieldset>"
        + '<button type="submit">Record sale</button></form>' + more
        + '<p class="soft">The total is worked out from the prices on record when the sale is saved.</p>'),
        here="/sales")


def sale_add(db, form):
    method = form.one("method")
    if method not in METHODS:
        raise Refused("Choose how the sale was paid: cash, card or other.")
    customer = None
    if form.one("customer_id"):
        customer = ident(form.one("customer_id"))
        if customer is None or not db.execute("SELECT 1 FROM customers WHERE id = ?", (customer,)).fetchone():
            raise Refused("That customer is not on record.")
    chosen, qtys = form.many("product_id"), form.many("qty")
    if len(chosen) != len(qtys):
        raise Refused("Every line needs a product and a quantity.")
    pairs = [pair for pair in zip(chosen, qtys) if pair != ("", "")]
    if not 1 <= len(pairs) <= MAX_LINES:
        raise Refused("A sale has 1 to %d lines; this one has %d." % (MAX_LINES, len(pairs)))
    lines, wanted = [], {}
    for number, (key, qty) in enumerate(pairs, 1):
        row = db.execute("SELECT * FROM products WHERE id = ?", (ident(key),)).fetchone()
        if row is None:
            raise Refused("Line %d: choose a product." % number)
        qty = whole(qty, "Line %d (%s): quantity" % (number, row["name"]), 1, MAX_QTY)
        lines.append((row["id"], qty, row["price_cents"]))
        wanted[row["id"]] = wanted.get(row["id"], 0) + qty
    for key, qty in wanted.items():
        row = find(db, "products", key)
        if qty > row["stock"]:
            raise Refused("%s: only %d in stock, %d asked. Nothing was sold." % (row["name"], row["stock"], qty))
    total = sum(qty * cents for _, qty, cents in lines)
    sale = db.execute("INSERT INTO sales (at, method, customer_id, total_cents) VALUES (?, ?, ?, ?)",
                      (now(), method, customer, total)).lastrowid
    for key, qty, cents in lines:
        db.execute("INSERT INTO sale_lines (sale_id, product_id, qty, unit_cents) VALUES (?, ?, ?, ?)", (sale, key, qty, cents))
        db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, key))
    return "/sales"


def void_ask(db, form, key):
    sale = find(db, "sales", key)
    if sale["voided"]:
        return page("Sale %d is voided" % key, sale_summary(db, sale)
                    + '<p>This sale was voided and its stock returned. It stays on record.</p>'
                      '<p><a href="/sales">Back to sales</a></p>', here="/sales")
    return page("Void sale %d?" % key, sale_summary(db, sale) + (
        "<p>Voiding returns these items to stock and cannot be undone. The sale stays on record, marked as voided.</p>"
        '<form class="card stack" method="post" action="/sales/%d/void">'
        '<button type="submit" class="danger">Void this sale</button></form>'
        '<p><a href="/sales">Keep the sale</a></p>' % key), here="/sales")


def void(db, form, key):
    sale = find(db, "sales", key)
    if sale["voided"]:
        raise Refused("Sale %d is already voided." % key)
    back = {}
    for line in lines_of(db, key):
        back[line["product_id"]] = back.get(line["product_id"], 0) + line["qty"]
    for product, qty in back.items():
        row = find(db, "products", product)
        if row["stock"] + qty > MAX_STOCK:
            raise Refused("Returning %d of %s would put its stock above %s. Lower the stock first."
                          % (qty, row["name"], commas(MAX_STOCK)))
        db.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, product))
    db.execute("UPDATE sales SET voided = 1 WHERE id = ?", (key,))
    return "/sales"


def appointments(db, form):
    pets = [(row["id"], "%s (%s) of %s" % (row["name"], row["species"], row["customer"])) for row in db.execute(
        "SELECT p.*, c.name AS customer FROM pets p JOIN customers c ON c.id = p.customer_id ORDER BY p.name, p.id")]
    rows = []
    for row in db.execute(
            "SELECT a.*, p.name AS pet, p.species, c.name AS customer, c.phone FROM appointments a "
            "JOIN pets p ON p.id = a.pet_id JOIN customers c ON c.id = p.customer_id "
            "WHERE a.date >= ? ORDER BY a.date, a.time, a.id", (today(),)):
        action = "cancelled" if row["cancelled"] else (
            '<form method="post" action="/appointments/%d/cancel"><button type="submit">Cancel</button></form>' % row["id"])
        rows.append(("off" if row["cancelled"] else "", [
            row["date"], row["time"], esc("%s (%s)" % (row["pet"], row["species"])), esc(row["customer"]),
            esc(row["phone"]), action]))
    return page("Appointments", (
        '<h2>Book grooming</h2><form class="card" method="post" action="/appointments">'
        + select("pet_id", pets, "Pet")
        + field("Date", "date", "", type="date", min=today(), max="9999-12-31")
        + select("time", [(slot, slot) for slot in SLOTS], "Starts at")
        + '<button type="submit">Book</button></form>'
        + '<p class="soft">One groomer, one hour each, starting on the hour from 09:00 to 17:00, every day.</p>'
        + "<h2>From today on</h2>"
        + table([("Date", ""), ("Time", ""), ("Pet", "words"), ("Customer", "words"), ("Phone", ""), ("", "")],
                rows, "Nothing booked from today on.")), here="/appointments")


def appointment_add(db, form):
    pet = db.execute("SELECT * FROM pets WHERE id = ?", (ident(form.one("pet_id")),)).fetchone()
    if pet is None:
        raise Refused("Choose the pet the appointment is for.")
    date, time = form.one("date"), form.one("time")
    try:
        if not re.fullmatch("[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
            raise ValueError
        datetime.date.fromisoformat(date)
    except ValueError:
        raise Refused("The date must be a real day, written like 2026-11-30.")
    if date < today():
        raise Refused("%s is before today." % date)
    if time not in SLOTS:
        raise Refused("Grooming starts on the hour, from 09:00 to 17:00.")
    if db.execute("SELECT 1 FROM appointments WHERE date = ? AND time = ? AND cancelled = 0", (date, time)).fetchone():
        raise Refused("%s at %s is already taken. Nothing was booked." % (date, time))
    db.execute("INSERT INTO appointments (pet_id, date, time) VALUES (?, ?, ?)", (pet["id"], date, time))
    return "/appointments"


def appointment_cancel(db, form, key):
    if find(db, "appointments", key)["cancelled"]:
        raise Refused("That appointment is already cancelled.")
    db.execute("UPDATE appointments SET cancelled = 1 WHERE id = ?", (key,))
    return "/appointments"


def export_json(db, form):
    return 200, "application/json", json.dumps(export(db), indent=1)


N = "([0-9]{1,9})"
ROUTES = [(method, re.compile(pattern), act) for method, pattern, act in [
    ("GET", "/", home),
    ("GET", "/export.json", export_json),
    ("GET", "/products", products), ("POST", "/products", product_add),
    ("GET", "/products/%s/edit" % N, product_edit), ("POST", "/products/%s/edit" % N, product_save),
    ("POST", "/products/%s/stock" % N, product_stock),
    ("GET", "/customers", customers), ("POST", "/customers", customer_add),
    ("GET", "/customers/%s/edit" % N, customer_edit), ("POST", "/customers/%s/edit" % N, customer_save),
    ("POST", "/pets", pet_add),
    ("GET", "/pets/%s/edit" % N, pet_edit), ("POST", "/pets/%s/edit" % N, pet_save),
    ("GET", "/sales", sales), ("POST", "/sales", sale_add), ("GET", "/sales/new", sale_new),
    ("GET", "/sales/%s/void" % N, void_ask), ("POST", "/sales/%s/void" % N, void),
    ("GET", "/appointments", appointments), ("POST", "/appointments", appointment_add),
    ("POST", "/appointments/%s/cancel" % N, appointment_cancel),
]]


def message(status, title, text, back=True):
    hint = "<p>Go back in the browser to correct it; what you typed is still there.</p>" if back else ""
    return page(title, "<p>%s</p>%s" % (esc(text), hint), status)


# ---- the server ---------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "PetShop"
    timeout = 30

    def log_message(self, *args):
        pass

    def answer(self, status, kind, text, location=None):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; "
                         "frame-ancestors 'none'; base-uri 'none'")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def handle_any(self):
        self.close_connection = True
        port = self.server.server_address[1]
        host = self.headers.get("Host", "")
        # Only this machine's own names: another name pointed at 127.0.0.1 is another site.
        if host not in ("127.0.0.1:%d" % port, "localhost:%d" % port):
            return self.answer(*message(403, "Refused", "This shop answers only as 127.0.0.1 or localhost.", False))
        path = urllib.parse.urlsplit(self.path)
        pairs = urllib.parse.parse_qsl(path.query, keep_blank_values=True)
        if self.command != "GET":
            # A post is taken only from the shop's own pages.
            origin, site = self.headers.get("Origin"), self.headers.get("Sec-Fetch-Site")
            if (origin is not None and origin != "http://" + host) or site not in (None, "same-origin", "none"):
                return self.answer(*message(403, "Refused", "That request came from another site.", False))
        if self.command == "POST":
            length = self.headers.get("Content-Length", "")
            if not re.fullmatch("[0-9]{1,12}", length):
                return self.answer(*message(411, "Refused", "The form came without its length.", False))
            if int(length) > MAX_FORM:
                remaining = int(length)
                while 0 < remaining <= 16 * MAX_FORM:  # let the sender finish, so that it can read the answer
                    chunk = self.rfile.read(min(remaining, MAX_FORM))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                return self.answer(*message(413, "Too much", "A form may hold at most %s bytes." % commas(MAX_FORM)))
            try:
                pairs = urllib.parse.parse_qsl(self.rfile.read(int(length)).decode("utf-8"), keep_blank_values=True,
                                               strict_parsing=int(length) > 0, max_num_fields=200)
            except ValueError:
                return self.answer(*message(400, "Not saved", "The form could not be read."))
        elif self.command != "GET":
            return self.answer(*message(405, "Not allowed", "The shop takes only GET and POST.", False))
        for method, pattern, act in ROUTES:
            found = pattern.fullmatch(path.path)
            if found and method == self.command:
                return self.answer(*self.server.run(act, Form(pairs), *map(int, found.groups())))
        if any(pattern.fullmatch(path.path) for _, pattern, _ in ROUTES):
            return self.answer(*message(405, "Not allowed", "That address does not take a %s." % self.command, False))
        self.answer(*message(404, "Not found", "There is no such page.", False))

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = handle_any


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port, db_path):
        self.lock = threading.Lock()
        self.db = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None, timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript(SCHEMA)
        super().__init__(("127.0.0.1", port), Handler)

    def run(self, act, *args):
        """One request is one transaction: all of it is stored, or none."""
        with self.lock:
            self.db.execute("BEGIN IMMEDIATE")
            try:
                result = act(self.db, *args)
                self.db.execute("COMMIT")
            except BaseException as error:
                self.db.execute("ROLLBACK")
                if isinstance(error, Refused):
                    return message(400, "Not saved", str(error))
                if isinstance(error, Missing):
                    return message(404, "Not found", "There is no such page.", False)
                if isinstance(error, sqlite3.IntegrityError):
                    return message(400, "Not saved", "The shop's records do not allow that.")
                raise
        if isinstance(result, str):
            return 303, "text/plain; charset=utf-8", "", result
        return result


def main():
    parser = argparse.ArgumentParser(description="Pet shop, for staff, in a browser on this machine.")
    parser.add_argument("--db", default="petshop.db", help="the SQLite file that holds everything (default: petshop.db)")
    parser.add_argument("--port", type=int, default=8000, help="port on 127.0.0.1 (default: 8000)")
    parser.add_argument("--sample", action="store_true", help="fill an empty shop with a few sample rows")
    args = parser.parse_args()
    server = Server(args.port, args.db)
    if args.sample:
        filled = server.run(lambda db: str(sample(db)))[3] == "True"
        print("Sample data added." if filled else "The shop is not empty; no sample data added.", flush=True)
    print("Pet shop on http://127.0.0.1:%d/ with %s. Ctrl+C stops it." % (server.server_address[1], args.db), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.db.close()


if __name__ == "__main__":
    main()

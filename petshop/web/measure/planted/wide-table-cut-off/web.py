#!/usr/bin/env python3
"""Web interface of the pet shop: pages and forms over the four units."""
import argparse
import html
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlencode, urlsplit

import catalog
import customers
import sales
import stock

HOST = "127.0.0.1"
NAV = (("/", "Overview"), ("/catalog", "Catalog"), ("/customers", "Customers"),
       ("/sell", "Sell"), ("/sales", "Sales"))
LOCK = threading.Lock()
STATE = None
HEAD_EXTRA = ""

CSS = """
*{box-sizing:border-box}
html{font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1b1f24;
background:#f4f5f7}
body{margin:0}
header{background:#12355b;color:#fff}
.bar{max-width:64rem;margin:0 auto;padding:.5rem 1rem;display:flex;flex-wrap:wrap;
align-items:center;gap:.25rem 1.5rem}
.brand{font-weight:700;font-size:1.125rem}
nav{display:flex;flex-wrap:wrap;gap:.25rem}
nav a{display:inline-flex;align-items:center;min-height:44px;min-width:44px;padding:0 .75rem;
color:#fff;text-decoration:none;border-radius:6px}
nav a:hover{background:#1f4f82}
nav a[aria-current]{background:#fff;color:#12355b;font-weight:600}
main{max-width:64rem;margin:0 auto;padding:1rem}
h1{font-size:1.75rem;margin:.5rem 0 1rem}
h2{font-size:1.25rem;margin:0 0 .75rem}
p{max-width:65ch;margin:0 0 1rem}
section{background:#fff;border:1px solid #d5d9e0;border-radius:8px;padding:1rem;margin:0 0 1rem}
.scroll{overflow:hidden}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:.5rem .75rem;border-bottom:1px solid #e3e6eb;vertical-align:middle;white-space:nowrap}
th{font-size:.875rem;color:#3d4652}
.num{text-align:right;font-variant-numeric:tabular-nums}
td a{display:inline-flex;align-items:center;min-height:44px;min-width:44px;color:#0b4f9c;
font-weight:600}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));gap:1rem;
margin:0 0 1rem}
.stat{background:#fff;border:1px solid #d5d9e0;border-radius:8px;padding:1rem}
.stat span{display:block;color:#3d4652;font-size:.875rem}
.stat{min-width:0}
.stat b{font-size:1.5rem;overflow-wrap:anywhere}
.fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(11rem,1fr));gap:.75rem;
align-items:end}
label{display:block;font-weight:600;font-size:.875rem}
input,select{font:inherit;width:100%;min-height:44px;padding:.5rem .625rem;
border:1px solid #6b7480;border-radius:6px;background:#fff;color:#1b1f24}
td input{min-width:5rem}
button{font:inherit;font-weight:600;min-height:44px;min-width:44px;padding:.5rem 1rem;border:0;
border-radius:6px;background:#12355b;color:#fff;cursor:pointer}
button:hover{background:#1f4f82}
:focus-visible{outline:3px solid #b85c00;outline-offset:2px}
.status,.alert{border-radius:8px;padding:.75rem 1rem;margin:0 0 1rem;font-weight:600}
.status{background:#e6f4ea;border:1px solid #2e7d32;color:#14401a}
.alert{background:#fdecea;border:1px solid #b3261e;color:#5c1410}
"""


class Refused(Exception):
    pass


def esc(text):
    return html.escape(str(text), quote=True)


def money(cents):
    return "%s.%02d" % (format(cents // 100, ","), cents % 100)


def parse_money(text):
    if not re.fullmatch(r"[0-9]+(\.[0-9]{1,2})?", text):
        raise Refused("A price is written as digits, with at most two decimals: 3, 3.5 or 3.50.")
    whole, _, cents = text.partition(".")
    return int(whole) * 100 + int((cents + "00")[:2])


def parse_quantity(text):
    if not re.fullmatch(r"[0-9]+", text):
        raise Refused("A quantity is written as digits only.")
    return int(text)


def need(form, name):
    if name not in form:
        raise Refused("The field %s is missing." % name)
    return form[name]


def load():
    if not os.path.exists(STATE):
        return {"catalog": catalog.new(), "stock": stock.new(),
                "customers": customers.new(), "sales": sales.new()}
    with open(STATE, encoding="utf-8") as handle:
        return json.load(handle)


def save(shop):
    temporary = STATE + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(shop, handle)
    os.replace(temporary, STATE)


# ---- pages -------------------------------------------------------------------------------

def layout(title, section, body, status=None, alert=None):
    links = "".join('<a href="%s"%s>%s</a>' % (
        href, ' aria-current="page"' if href == section else "", text) for href, text in NAV)
    note = ""
    if status:
        note = '<div class="status" role="status">%s</div>' % esc(status)
    if alert:
        note = '<div class="alert" role="alert">%s</div>' % esc(alert)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>%s · Pet shop</title><style>%s</style>%s</head><body>'
            '<header><div class="bar"><span class="brand">Pet shop</span>'
            '<nav aria-label="Sections">%s</nav></div></header>'
            '<main><h1>%s</h1>%s%s</main></body></html>'
            % (esc(title), CSS, HEAD_EXTRA, links, esc(title), note, body))


def table(table_id, heads, rows, empty):
    if not rows:
        rows = ['<tr><td colspan="%d">%s</td></tr>' % (len(heads), empty)]
    head = "".join('<th scope="col"%s>%s</th>' % (
        ' class="num"' if text.startswith("#") else "", text.lstrip("#")) for text in heads)
    return ('<div class="scroll"><table id="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody>'
            '</table></div>' % (table_id, head, "".join(rows)))


def field(form, name, label, value="", kind="text", extra=""):
    return ('<div><label for="%s-%s">%s</label><input type="%s" id="%s-%s" name="%s" '
            'value="%s"%s></div>' % (form, name, label, kind, form, name, name, esc(value), extra))


def select(form, name, label, options, chosen):
    body = "".join('<option value="%s"%s>%s</option>' % (
        esc(value), " selected" if value == chosen else "", esc(text)) for value, text in options)
    return ('<div><label for="%s-%s">%s</label><select id="%s-%s" name="%s">%s</select></div>'
            % (form, name, label, form, name, name, body))


def item_select(form, shop, chosen):
    options = [(item["id"], "%s: %s" % (item["id"], item["name"]))
               for item in catalog.items(shop["catalog"])]
    return select(form, "id", "Item", options, chosen)


def page_overview(shop, query, values):
    items = catalog.items(shop["catalog"])
    out = [item for item in items if stock.on_hand(shop["stock"], item["id"]) == 0]
    stats = "".join('<div class="stat"><span>%s</span><b id="%s">%s</b></div>' % row for row in (
        ("Items", "count-items", len(items)),
        ("Customers", "count-customers", len(customers.find(shop["customers"], ""))),
        ("Sales", "count-sales", len(sales.sales(shop["sales"]))),
        ("Takings", "takings", money(sales.takings(shop["sales"])))))
    rows = ['<tr data-id="%s"><td>%s</td><td class="name">%s</td></tr>'
            % (esc(item["id"]), esc(item["id"]), esc(item["name"])) for item in out]
    return "Overview", "/", ('<div class="stats">%s</div><section><h2>Out of stock</h2>%s'
                             '</section>' % (stats, table("out-of-stock", ("Id", "Name"), rows,
                                                          "Every item is in stock.")))


def page_catalog(shop, query, values):
    rows = ['<tr data-id="%s"><td>%s</td><td class="name">%s</td><td class="kind">%s</td>'
            '<td class="price num">%s</td><td class="on-hand num">%d</td></tr>'
            % (esc(item["id"]), esc(item["id"]), esc(item["name"]), item["kind"],
               money(item["price_cents"]), stock.on_hand(shop["stock"], item["id"]))
            for item in catalog.items(shop["catalog"])]
    add = values.get("/catalog/add", {})
    price = values.get("/catalog/price", {})
    receive = values.get("/stock/receive", {})
    remove = values.get("/stock/remove", {})
    kinds = [("product", "Product"), ("animal", "Animal")]
    body = '<section><h2>Items</h2>%s</section>' % table(
        "items", ("Id", "Name", "Kind", "#Price", "#On hand"), rows, "No items yet.")
    body += ('<section><h2>Add an item</h2><form method="post" action="/catalog/add">'
             '<div class="fields">%s%s%s%s<div><button type="submit">Add item</button></div>'
             '</div></form></section>' % (
                 field("add", "id", "Id", add.get("id", "")),
                 field("add", "name", "Name", add.get("name", "")),
                 select("add", "kind", "Kind", kinds, add.get("kind", "product")),
                 field("add", "price", "Price", add.get("price", ""),
                       extra=' inputmode="decimal"')))
    body += ('<section><h2>Change a price</h2><form method="post" action="/catalog/price">'
             '<div class="fields">%s%s<div><button type="submit">Set price</button></div></div>'
             '</form></section>' % (
                 item_select("price", shop, price.get("id")),
                 field("price", "price", "New price", price.get("price", ""),
                       extra=' inputmode="decimal"')))
    for action, form, values_, title, button in (
            ("/stock/receive", "receive", receive, "Receive stock", "Receive"),
            ("/stock/remove", "remove", remove, "Remove stock", "Remove")):
        body += ('<section><h2>%s</h2><form method="post" action="%s"><div class="fields">%s%s'
                 '<div><button type="submit">%s</button></div></div></form></section>' % (
                     title, action, item_select(form, shop, values_.get("id")),
                     field(form, "quantity", "Quantity", values_.get("quantity", ""),
                           extra=' inputmode="numeric"'), button))
    return "Catalog", "/catalog", body


def page_customers(shop, query, values):
    text = query.get("q", "")
    rows = ['<tr data-id="%s"><td>%s</td><td class="name">%s</td></tr>'
            % (esc(person["id"]), esc(person["id"]), esc(person["name"]))
            for person in customers.find(shop["customers"], text)]
    body = ('<section><h2>Find a customer</h2><form method="get" action="/customers">'
            '<div class="fields">%s<div><button type="submit">Search</button></div></div></form>'
            '</section>' % field("find", "q", "Name contains", text))
    body += '<section><h2>Customers</h2>%s</section>' % table(
        "customers", ("Id", "Name"), rows, "No customers found.")
    body += ('<section><h2>Register a customer</h2><form method="post" '
             'action="/customers/register"><div class="fields">%s<div><button type="submit">'
             'Register</button></div></div></form></section>'
             % field("register", "name", "Name",
                     values.get("/customers/register", {}).get("name", "")))
    return "Customers", "/customers", body


def page_sell(shop, query, values):
    kept = values.get("/sell", {})
    people = [(person["id"], "%s: %s" % (person["id"], person["name"]))
              for person in customers.find(shop["customers"], "")]
    rows = []
    for number, item in enumerate(catalog.items(shop["catalog"])):
        rows.append(
            '<tr><td><label for="qty-%d">%s</label></td><td class="num">%s</td>'
            '<td class="num">%d</td><td><input type="number" min="0" step="1" id="qty-%d" '
            'name="qty-%s" value="%s"></td></tr>' % (
                number, esc(item["name"]), money(item["price_cents"]),
                stock.on_hand(shop["stock"], item["id"]), number, esc(item["id"]),
                esc(kept.get("qty-" + item["id"], ""))))
    body = ('<form method="post" action="/sell"><section><h2>Customer</h2>'
            '<div class="fields">%s</div></section><section><h2>Items</h2>%s</section>'
            '<p><button type="submit">Make the sale</button></p></form>' % (
                select("sell", "customer", "Customer", people, kept.get("customer")),
                table("sell-items", ("Item", "#Price", "#On hand", "Quantity"), rows,
                      "No items yet.")))
    return "Sell", "/sell", body


def page_sales(shop, query, values):
    rows = []
    for sale in reversed(sales.sales(shop["sales"])):
        name = customers.get(shop["customers"], sale["customer_id"])["name"]
        rows.append('<tr data-id="%s"><td><a href="/sales/%s">%s</a></td>'
                    '<td class="customer">%s</td><td class="total num">%s</td></tr>' % (
                        esc(sale["id"]), esc(sale["id"]), esc(sale["id"]), esc(name),
                        money(sale["total_cents"])))
    body = ('<div class="stats"><div class="stat"><span>Takings</span><b id="takings">%s</b>'
            '</div></div><section><h2>All sales</h2>%s</section>' % (
                money(sales.takings(shop["sales"])),
                table("sales", ("Sale", "Customer", "#Total"), rows, "No sales yet.")))
    return "Sales", "/sales", body


def page_sale(shop, sale):
    name = customers.get(shop["customers"], sale["customer_id"])["name"]
    rows = ['<tr data-id="%s"><td class="name">%s</td><td class="quantity num">%d</td>'
            '<td class="unit-price num">%s</td><td class="line-total num">%s</td></tr>' % (
                esc(line["item_id"]),
                esc(catalog.get(shop["catalog"], line["item_id"])["name"]), line["quantity"],
                money(line["unit_price_cents"]), money(line["line_total_cents"]))
            for line in sale["lines"]]
    body = ('<div class="stats"><div class="stat"><span>Sale</span><b id="sale-id">%s</b></div>'
            '<div class="stat"><span>Customer</span><b id="customer">%s</b></div>'
            '<div class="stat"><span>Total</span><b id="total">%s</b></div></div>'
            '<section><h2>Lines</h2>%s</section>' % (
                esc(sale["id"]), esc(name), money(sale["total_cents"]),
                table("lines", ("Item", "#Quantity", "#Unit price", "#Line total"), rows, "")))
    return "Sale " + sale["id"], "/sales", body


# ---- changes -----------------------------------------------------------------------------

def known_item(shop, item_id):
    try:
        return catalog.get(shop["catalog"], item_id)
    except KeyError:
        raise Refused("There is no item %s in the catalog." % item_id) from None


def do_add(shop, form):
    item_id, name, kind = need(form, "id"), need(form, "name"), need(form, "kind")
    catalog.add(shop["catalog"], item_id, name, kind, parse_money(need(form, "price")))
    return "/catalog", "Item %s was added." % item_id


def do_price(shop, form):
    item = known_item(shop, need(form, "id"))
    cents = parse_money(need(form, "price"))
    catalog.set_price(shop["catalog"], item["id"], cents)
    return "/catalog", "The price of %s is now %s." % (item["id"], money(cents))


def do_receive(shop, form):
    item = known_item(shop, need(form, "id"))
    now = stock.receive(shop["stock"], item["id"], parse_quantity(need(form, "quantity")))
    return "/catalog", "Stock received: %d of %s now on hand." % (now, item["id"])


def do_remove(shop, form):
    item = known_item(shop, need(form, "id"))
    now = stock.remove(shop["stock"], item["id"], parse_quantity(need(form, "quantity")))
    return "/catalog", "Stock removed: %d of %s now on hand." % (now, item["id"])


def do_register(shop, form):
    customer_id = customers.register(shop["customers"], need(form, "name"))
    return "/customers", "Customer %s was registered." % customer_id


def do_sell(shop, form):
    try:
        customer = customers.get(shop["customers"], need(form, "customer"))
    except KeyError:
        raise Refused("That customer is not registered.") from None
    lines = []
    for item in catalog.items(shop["catalog"]):
        text = form.get("qty-" + item["id"], "")
        quantity = parse_quantity(text) if text else 0
        if quantity > 0:
            lines.append((item["id"], quantity))
    if not lines:
        raise Refused("Enter a quantity for at least one item.")
    sale = sales.sell(
        shop["sales"], customer["id"], lines,
        lambda item_id: catalog.get(shop["catalog"], item_id)["price_cents"],
        lambda item_id: stock.on_hand(shop["stock"], item_id),
        lambda item_id, quantity: stock.remove(shop["stock"], item_id, quantity))
    return "/sales/" + sale["id"], "Sale %s was recorded." % sale["id"]


PAGES = {"/": page_overview, "/catalog": page_catalog, "/customers": page_customers,
         "/sell": page_sell, "/sales": page_sales}
CHANGES = {"/catalog/add": (do_add, "/catalog"), "/catalog/price": (do_price, "/catalog"),
           "/stock/receive": (do_receive, "/catalog"), "/stock/remove": (do_remove, "/catalog"),
           "/customers/register": (do_register, "/customers"), "/sell": (do_sell, "/sell")}


class Handler(BaseHTTPRequestHandler):
    server_version = "PetShop"

    def log_message(self, *args):
        pass

    def __getattr__(self, name):
        if name.startswith("do_"):
            return self.serve
        raise AttributeError(name)

    def send(self, status, page, location=None):
        data = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        if location:
            self.send_header("Location", location)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def plain(self, status, title, text):
        self.send(status, layout(title, None, "<p>%s</p>" % text))

    def serve(self):
        parts = urlsplit(self.path)
        path = parts.path
        query = {key: value[0] for key, value in
                 parse_qs(parts.query, keep_blank_values=True).items()}
        sale = re.fullmatch(r"/sales/([^/]+)", path)
        allowed = (["GET"] if path in PAGES or sale else []) + (
            ["POST"] if path in CHANGES else [])
        if not allowed:
            return self.plain(404, "Not found", "There is no such page here.")
        if self.command not in allowed:
            return self.plain(405, "Not allowed", "This address does not take that request.")
        with LOCK:
            if self.command == "POST":
                return self.change(path)
            shop = load()
            if sale:
                try:
                    found = sales.get(shop["sales"], unquote(sale.group(1)))
                except KeyError:
                    return self.plain(404, "Not found", "There is no such sale.")
                title, section, body = page_sale(shop, found)
            else:
                title, section, body = PAGES[path](shop, query, {})
            self.send(200, layout(title, section, body, status=query.get("done")))

    def change(self, path):
        length = int(self.headers.get("Content-Length") or 0)
        action, page = CHANGES[path]
        form = {}
        try:
            fields = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
            form = {key: value[0] for key, value in fields.items()}
            shop = load()
            location, done = action(shop, form)
        except (Refused, ValueError, KeyError) as error:
            reason = str(error) if isinstance(error, Refused) else "Refused: %s." % (
                error.args[0] if error.args else "not valid")
            title, section, body = PAGES[page](load(), {}, {path: form})
            return self.send(400, layout(title, section, body, alert=reason))
        save(shop)
        self.send(303, "", location + "?" + urlencode({"done": done}))


def main():
    global STATE
    parser = argparse.ArgumentParser(description="Web interface of the pet shop.")
    parser.add_argument("--state", required=True)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    STATE = args.state
    server = ThreadingHTTPServer((HOST, args.port), Handler)
    server.daemon_threads = True
    print("http://%s:%d/" % (HOST, server.server_address[1]), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

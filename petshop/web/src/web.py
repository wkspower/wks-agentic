#!/usr/bin/env python3
"""The pet shop in a browser: python3 web.py --state FILE [--port N]."""
import argparse
import html
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlencode, urlsplit

import catalog
import customers
import sales
import stock

UNITS = (("catalog", catalog), ("stock", stock), ("customers", customers), ("sales", sales))
NAV = (("/", "Overview"), ("/catalog", "Catalog"), ("/customers", "Customers"),
       ("/sell", "Sell"), ("/sales", "Sales"))
LOCK = threading.Lock()
CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; form-action 'self'"
CSS = """
:root{--ink:#1c2733;--mute:#4f5d6b;--line:#d8d5cc;--acc:#0e5f54;--tint:#e6f4ec}
*{box-sizing:border-box}
body{margin:0;background:#f5f4ef;color:var(--ink);overflow-wrap:break-word;
font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--acc)}
:focus-visible{outline:3px solid #1259c3;outline-offset:2px}
.skip{position:absolute;left:16px;top:4px;transform:translateY(-200%)}
.skip:focus{transform:none}
header{background:#fff;border-bottom:1px solid var(--line)}
.bar,main{max-width:72rem;margin:auto;padding:0 16px}
.bar{display:flex;flex-wrap:wrap;align-items:center}
.brand{margin-right:auto;padding:10px 0;font-size:18px;font-weight:700}
.brand:before{content:"";display:inline-block;width:12px;height:12px;margin-right:8px;
border-radius:50% 50% 50% 0;background:var(--acc)}
nav ul{display:flex;flex-wrap:wrap;list-style:none;margin:0;padding:0}
nav a{display:flex;align-items:center;justify-content:center;min-width:44px;min-height:52px;
padding:0 14px;border-bottom:3px solid transparent;color:var(--mute);font-weight:600;
text-decoration:none}
nav a:hover{color:var(--ink)}
nav [aria-current]{border-color:var(--acc);color:var(--acc)}
main{padding-bottom:48px}
.head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;
gap:8px 16px;margin:28px 0 20px}
h1{margin:0;font-size:28px;line-height:1.2}
h2{margin:0 0 12px;font-size:18px}
p{max-width:65ch;margin:0 0 16px}
.card,.stat{min-width:0;background:#fff;border:1px solid var(--line);border-radius:10px}
.card{margin-bottom:20px;padding:20px}
.cols,.side{display:grid;column-gap:20px}
.cols>*{min-width:0}
.side{grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.stat{display:block;padding:12px;color:var(--mute);font-size:15px;text-decoration:none}
a.stat:hover{border-color:var(--acc)}
.stat b{display:block;color:var(--ink);font-size:26px;line-height:1.3}
.big{grid-column:1/-1}
.tw{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left}
thead th{color:var(--mute);font-size:14px;white-space:nowrap}
tbody tr:last-child>*{border-bottom:0}
tfoot>tr>*{border:0;border-top:2px solid var(--line);font-size:18px;font-weight:700}
.n,.stat b{font-variant-numeric:tabular-nums}
.n{text-align:right;white-space:nowrap}
.id{color:var(--mute);white-space:nowrap}
.name{min-width:11rem}
.tag{padding:2px 10px;border-radius:99px;background:#eeece5;font-size:14px}
.zero{color:#8a1c16;font-weight:700}
.hl td{background:var(--tint)}
td a{display:inline-flex;align-items:center;min-width:44px;min-height:44px;font-weight:600}
.msg{margin-bottom:16px;padding:12px 16px;border-left:4px solid;border-radius:8px;
font-weight:600}
.ok{background:var(--tint);color:#0b4f3a}
.err{background:#fdecea;color:#8a1c16}
.empty{margin:0;color:var(--mute)}
label{display:block;margin:12px 0 4px;font-weight:600}
label span{color:var(--mute);font-weight:400}
input,select{display:block;width:100%;min-height:44px;padding:8px 12px;background:#fff;
border:1px solid #6b7785;border-radius:6px;color:inherit;font:inherit}
button,.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;
padding:8px 20px;background:var(--acc);border:1px solid var(--acc);border-radius:6px;
color:#fff;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}
button:hover,.btn:hover{background:#0a4a41}
.alt{background:#fff;color:var(--acc)}
.alt:hover{background:var(--tint)}
.foot,.row{display:flex;flex-wrap:wrap;align-items:flex-end;gap:12px}
.foot{justify-content:flex-end;margin-top:16px}
.row{margin-bottom:16px}
.row div{flex:1 1 12rem}
.row label{margin-top:0}
.q{width:6rem;margin-left:auto;text-align:right}
dl{display:flex;flex-wrap:wrap;gap:4px 32px;margin:0 0 16px}
dt{color:var(--mute);font-size:15px}
dd{margin:0;font-weight:600}
@media(max-width:600px){nav{width:100%}nav ul{justify-content:space-between}
nav a{padding:0 6px;font-size:15px}.card{padding:16px}.foot>*{flex:1}th,td{padding:10px 8px}
#sell-items thead{display:none}
#sell-items tr{display:grid;grid-template-columns:auto 1fr auto;gap:0 16px;align-items:center;
padding:8px 0;border-bottom:1px solid var(--line)}
#sell-items tr>*{padding:2px 0;border:0;text-align:left}
#sell-items .name{grid-column:1/-1}
[data-l]:before{content:attr(data-l) " ";color:var(--mute);font-size:14px;font-weight:400}}
@media(min-width:960px){.cols{grid-template-columns:minmax(0,1fr) 22rem;align-items:start}
.stats{grid-template-columns:1.5fr repeat(3,1fr)}.big{grid-column:auto}}
"""
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · Pet shop</title><link rel="icon" href="data:,"><style>%s</style></head>
<body><a class="skip btn" href="#main">Skip to content</a>
<header><div class="bar"><span class="brand">Pet shop</span>
<nav aria-label="Sections"><ul>%s</ul></nav></div></header>
<main id="main">%s</main></body></html>
"""


class Refused(Exception):
    """A change the shop does not make; the message is shown to the person."""


def e(value):
    return html.escape(str(value), quote=True)


def money(cents):
    return "%s.%02d" % (format(cents // 100, ","), cents % 100)


def cents(text):
    if not re.fullmatch(r"[0-9]+(\.[0-9]{1,2})?", text):
        raise Refused("Write the price in digits, with a point and one or two decimals "
                      "if needed, like 3 or 3.50.")
    whole, _, part = text.partition(".")
    return int(whole) * 100 + int((part + "00")[:2])


def count(text):
    if not re.fullmatch(r"[0-9]+", text):
        raise Refused("Write the quantity as a whole number in digits, like 12.")
    return int(text)


def load(path):
    try:
        with open(path, encoding="utf-8") as handle:
            shop = json.load(handle)
    except FileNotFoundError:
        shop = {}
    for key, unit in UNITS:
        shop.setdefault(key, unit.new())
    return shop


def save(path, shop):
    with open(path + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(shop, handle)
    os.replace(path + ".tmp", path)


def on_hand(shop, item_id):
    return stock.on_hand(shop["stock"], item_id)


def name_of(unit, shop, key):
    try:
        return unit.get(shop[unit.__name__], key)["name"]
    except KeyError:
        return key


# ---- the changes -----------------------------------------------------------------------------

def need(fields, *names):
    for name in names:
        if name not in fields:
            raise Refused("The form came without its field “%s”. Please try again." % name)
    return [fields[name] for name in names]


def item_for(shop, item_id):
    try:
        return catalog.get(shop["catalog"], item_id)
    except KeyError:
        raise Refused("There is no item “%s” in the catalog." % item_id if item_id
                      else "Choose an item.") from None


def back(page, done, key, n=None):
    return page + "?" + urlencode({"done": done, "id": key, **({"n": n} if n else {})})


def add_item(shop, fields):
    item_id, name, kind, price = need(fields, "id", "name", "kind", "price")
    if not item_id or not name:
        raise Refused("Give the item an ID and a name.")
    if kind not in ("animal", "product"):
        raise Refused("Choose a kind: animal or product.")
    price = cents(price)
    if any(item["id"] == item_id for item in catalog.items(shop["catalog"])):
        raise Refused("The ID “%s” is already used by another item." % item_id)
    catalog.add(shop["catalog"], item_id, name, kind, price)
    return back("/catalog", "add", item_id)


def set_price(shop, fields):
    item_id, price = need(fields, "id", "price")
    item_for(shop, item_id)
    catalog.set_price(shop["catalog"], item_id, cents(price))
    return back("/catalog", "price", item_id)


def move_stock(change):
    def act(shop, fields):
        item_id, quantity = need(fields, "id", "quantity")
        item, quantity = item_for(shop, item_id), count(quantity)
        if not quantity:
            raise Refused("Enter a quantity of 1 or more.")
        have = on_hand(shop, item_id)
        if change == "remove" and quantity > have:
            raise Refused("Only %d of %s on hand, so %d cannot be removed."
                          % (have, item["name"], quantity))
        getattr(stock, change)(shop["stock"], item_id, quantity)
        return back("/catalog", change, item_id, quantity)
    return act


def register(shop, fields):
    name, = need(fields, "name")
    if not name.strip():
        raise Refused("Enter the customer’s name.")
    return back("/customers", "customer", customers.register(shop["customers"], name))


def sell(shop, fields):
    customer, = need(fields, "customer")
    try:
        customers.get(shop["customers"], customer)
    except KeyError:
        raise Refused("There is no customer “%s”." % customer if customer
                      else "Choose a customer.") from None
    items = {item["id"]: item for item in catalog.items(shop["catalog"])}
    asked = {key[4:]: text for key, text in fields.items() if key.startswith("qty-") and text}
    lines = []
    for item_id in sorted(asked):
        name = items.get(item_id, {"name": item_id})["name"]
        if not re.fullmatch(r"[0-9]+", asked[item_id]):
            raise Refused("Write the quantity of %s as a whole number in digits." % name)
        quantity, have = int(asked[item_id]), on_hand(shop, item_id)
        if not quantity:
            continue
        if item_id not in items:
            raise Refused("There is no item “%s” in the catalog." % item_id)
        if quantity > have:
            raise Refused("Only %d of %s on hand, so %d cannot be sold." % (have, name, quantity)
                          if have else "%s is out of stock." % name)
        lines.append((item_id, quantity))
    if not lines:
        raise Refused("Enter a quantity for at least one item.")
    sale = sales.sell(shop["sales"], customer, lines, lambda i: items[i]["price_cents"],
                      lambda i: on_hand(shop, i), lambda i, n: stock.remove(shop["stock"], i, n))
    return back("/sales/" + quote(sale["id"], safe=""), "sale", sale["id"])


POSTS = {"/catalog/add": (add_item, "/catalog"), "/catalog/price": (set_price, "/catalog"),
         "/stock/receive": (move_stock("receive"), "/catalog"),
         "/stock/remove": (move_stock("remove"), "/catalog"),
         "/customers/register": (register, "/customers"), "/sell": (sell, "/sell")}


# ---- the pages -------------------------------------------------------------------------------

def layout(title, section, body):
    links = "".join('<li><a href="%s"%s>%s</a></li>' % (
        href, ' aria-current="page"' if href == section else "", text) for href, text in NAV)
    return PAGE % (e(title), CSS, links, body)


def head(title, extra=""):
    return '<div class="head"><h1>%s</h1>%s</div>' % (title, extra)


def note(title, text, section=None):
    return layout(title, section, head(title) + '<p>%s</p><p><a class="btn" href="/">'
                  'Back to the overview</a></p>' % text)


def table(name, heads, rows, empty, foot=""):
    """A table in its own scrolling container; without rows, a friendly word instead."""
    cells = "".join('<th scope="col"%s>%s</th>' % (' class="n"' * (text[0] == "+"),
                                                    text.lstrip("+")) for text in heads)
    return ('<div class="tw"%s><table id="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody>%s'
            '</table></div>%s' % ("" if rows else " hidden", name, cells, "".join(rows), foot,
                                  "" if rows else '<p class="empty">%s</p>' % empty))


def item_cells(item):
    return ('<td class="id">%s</td><td class="name">%s</td><td class="kind"><span class="tag">'
            '%s</span></td><td class="price n">%s</td>'
            % (e(item["id"]), e(item["name"]), e(item["kind"]), money(item["price_cents"])))


def amount(shop, item):
    have = on_hand(shop, item["id"])
    return '<td class="on-hand n%s" data-l="On hand">%d</td>' % ("" if have else " zero", have)


def text_input(label, name, key, value, more=""):
    return ('<label for="%s">%s</label><input type="text" id="%s" name="%s" value="%s"%s>'
            % (key, label, key, name, e(value), more))


def select(label, name, key, options, chosen, ask):
    """`chosen` None: the first option. A value not on offer is kept as an option of its own."""
    if chosen is not None and chosen not in [value for value, _ in options]:
        options = [(chosen, chosen + " (unknown)" if chosen else ask)] + options
    return '<label for="%s">%s</label><select id="%s" name="%s">%s</select>' % (
        key, label, key, name, "".join('<option value="%s"%s>%s</option>' % (
            e(value), " selected" * (value == chosen), e(text)) for value, text in options))


def form(refusal, action, inner, button):
    """A form; when it is the one just refused it says why, above its fields."""
    if refusal and refusal["action"] == action:
        inner = '<div class="msg err" role="alert">%s</div>%s' % (
            e(refusal["error"]), inner.replace(" name=", " autofocus name=", 1))
    return ('<form action="%s" method="post" novalidate>%s<div class="foot"><button>%s</button>'
            '</div></form>' % (action, inner, button))


def values(refusal, action):
    return refusal["fields"] if refusal and refusal["action"] == action else {}


def status(shop, query, refusal, *kinds):
    """What was just done, said from the state itself."""
    kind, key, n = (query.get(name, [""])[0] for name in ("done", "id", "n"))
    if refusal or kind not in kinds or not re.fullmatch(r"[0-9]*", n):
        return ""
    try:
        if kind == "sale":
            text = "Sale %s is recorded." % sales.get(shop["sales"], key)["id"]
        elif kind == "customer":
            text = "%s is registered as customer %s." % (
                customers.get(shop["customers"], key)["name"], key)
        else:
            item, have = catalog.get(shop["catalog"], key), on_hand(shop, key)
            text = {"add": "%s is added to the catalog." % item["name"],
                    "price": "%s now costs %s." % (item["name"], money(item["price_cents"])),
                    "receive": "Received %s of %s. Now %d on hand." % (n, item["name"], have),
                    "remove": "Removed %s of %s. Now %d on hand." % (n, item["name"], have)}[kind]
    except KeyError:
        return ""
    return '<div class="msg ok" role="status">%s</div>' % e(text)


def overview(shop, query, refusal):
    items = catalog.items(shop["catalog"])
    stats = "".join('<a class="stat%s" href="%s">%s <b id="%s">%s</b></a>' % row for row in (
        (" big", "/sales", "Takings", "takings", money(sales.takings(shop["sales"]))),
        ("", "/catalog", "Items", "count-items", len(items)),
        ("", "/customers", "Customers", "count-customers",
         len(customers.find(shop["customers"], ""))),
        ("", "/sales", "Sales", "count-sales", len(sales.sales(shop["sales"])))))
    rows = ['<tr data-id="%s">%s</tr>' % (e(item["id"]), item_cells(item))
            for item in items if not on_hand(shop, item["id"])]
    empty = ("Nothing has run out." if items else
             'The catalog is empty. <a href="/catalog">Add the first item</a> to begin.')
    more = ('<div class="foot"><a class="btn alt" href="/catalog">Receive stock</a></div>'
            if rows else "")
    return "Overview", (
        head("Overview", '<a class="btn" href="/sell">New sale</a>')
        + '<div class="stats">%s</div><section class="card"><h2>Out of stock</h2>%s%s</section>'
        % (stats, table("out-of-stock", ("ID", "Item", "Kind", "+Price"), rows, empty), more))


def catalog_page(shop, query, refusal):
    items = catalog.items(shop["catalog"])
    changed = query.get("id", [""])[0]
    rows = ['<tr data-id="%s"%s>%s%s</tr>' % (e(item["id"]), ' class="hl"' * (
        item["id"] == changed), item_cells(item), amount(shop, item)) for item in items]
    v = values(refusal, "/catalog/add")
    cards = [("Add an item", form(
        refusal, "/catalog/add",
        text_input("ID <span>(short, like k1)</span>", "id", "add-id", v.get("id", ""))
        + text_input("Name", "name", "add-name", v.get("name", ""))
        + select("Kind", "kind", "add-kind", [("animal", "Animal"), ("product", "Product")],
                 v.get("kind", "") if v else None, "Choose a kind")
        + text_input("Price <span>(like 3.50)</span>", "price", "add-price", v.get("price", ""),
                     ' inputmode="decimal"'), "Add item"))]
    for action, field, title, button, shown in (
            ("/catalog/price", "price", "Change a price", "Set price",
             lambda item: money(item["price_cents"])),
            ("/stock/receive", "quantity", "Receive stock", "Receive",
             lambda item: "%d on hand" % on_hand(shop, item["id"])),
            ("/stock/remove", "quantity", "Remove stock", "Remove",
             lambda item: "%d on hand" % on_hand(shop, item["id"]))):
        v, key = values(refusal, action), action.split("/")[2]
        options = [(item["id"], "%s · %s · %s" % (item["name"], item["id"], shown(item)))
                   for item in items]
        label, more = (("New price <span>(like 3.50)</span>", ' inputmode="decimal"')
                       if field == "price" else ("Quantity", ' inputmode="numeric"'))
        cards.append((title, form(
            refusal, action,
            select("Item", "id", key + "-id", options, v.get("id", ""), "Choose an item")
            + text_input(label, field, key + "-" + field, v.get(field, ""), more), button)))
    return "Catalog", (
        head("Catalog") + status(shop, query, refusal, "add", "price", "receive", "remove")
        + '<div class="cols"><section class="card"><h2>Items</h2>%s</section><div class="side">'
        '%s</div></div>' % (
            table("items", ("ID", "Item", "Kind", "+Price", "+On hand"), rows,
                  "No items yet. Add the first one with the form “Add an item”."),
            "".join('<section class="card"><h2>%s</h2>%s</section>' % card for card in cards)))


def customers_page(shop, query, refusal):
    q = "" if refusal else query.get("q", [""])[0]
    everyone = customers.find(shop["customers"], "")
    found = customers.find(shop["customers"], q)
    new = query.get("id", [""])[0]
    rows = ['<tr data-id="%s"%s><td class="id">%s</td><td class="name">%s</td></tr>' % (
        e(person["id"]), ' class="hl"' * (person["id"] == new), e(person["id"]),
        e(person["name"])) for person in found]
    empty = "No customers yet. Register the first one." if not everyone else (
        "No customer has “%s” in the name." % e(q))
    search = ('<form class="row" method="get" action="/customers"><div><label for="q">Search by '
              'name</label><input type="text" id="q" name="q" value="%s"></div><button>Search'
              '</button>%s</form>' % (e(q), '<a class="btn alt" href="/customers">Show all</a>'
                                      if q else ""))
    count_ = ("%d of %d" % (len(found), len(everyone))) if q else str(len(everyone))
    v = values(refusal, "/customers/register")
    return "Customers", (
        head("Customers") + status(shop, query, refusal, "customer")
        + '<div class="cols"><section class="card"><h2>Registered <span class="id">· %s</span>'
        '</h2>%s%s</section><section class="card"><h2>Register a customer</h2>%s</section></div>'
        % (count_, search, table("customers", ("ID", "Name"), rows, empty),
           form(refusal, "/customers/register",
                text_input("Name", "name", "name", v.get("name", ""), ' autocomplete="off"'),
                "Register")))


def sell_page(shop, query, refusal):
    v = values(refusal, "/sell")
    people = [(person["id"], "%s · %s" % (person["name"], person["id"]))
              for person in customers.find(shop["customers"], "")]
    rows = ['<tr><th scope="row" class="name">%s <span class="id">· %s</span></th>'
            '<td class="n" data-l="Price">%s</td>%s<td><input class="q" type="number" '
            'name="qty-%s" min="0" max="%d" inputmode="numeric" aria-label="Quantity of %s" '
            'value="%s"></td></tr>'
            % (e(item["name"]), e(item["id"]), money(item["price_cents"]), amount(shop, item),
               e(item["id"]), on_hand(shop, item["id"]), e(item["name"]),
               e(v.get("qty-" + item["id"], ""))) for item in catalog.items(shop["catalog"])]
    who = select("Customer", "customer", "customer", people,
                 v.get("customer", "") if refusal else None, "Choose a customer")
    if not people:
        who += ('<p class="empty">No customers yet. <a href="/customers">Register a customer'
                '</a> before selling.</p>')
    inner = ('<section class="card"><h2>Who is buying?</h2>%s</section><section class="card">'
             '<h2>What are they taking?</h2>%s</section>' % (who, table(
                 "sell-items", ("Item", "+Price", "+On hand", "+Quantity"), rows,
                 'Nothing to sell yet. <a href="/catalog">Add items to the catalog</a> first.')))
    return "Sell", head("New sale") + form(refusal, "/sell", inner, "Record sale")


def sales_page(shop, query, refusal):
    made = sales.sales(shop["sales"])
    rows = ['<tr data-id="%s"><td><a href="/sales/%s">%s</a></td><td class="customer">%s</td>'
            '<td class="total n">%s</td></tr>' % (
                e(sale["id"]), e(quote(sale["id"], safe="")), e(sale["id"]),
                e(name_of(customers, shop, sale["customer_id"])), money(sale["total_cents"]))
            for sale in reversed(made)]
    return "Sales", (
        head("Sales", '<a class="btn" href="/sell">New sale</a>')
        + '<div class="stats"><div class="stat big">Takings from %d sale%s <b id="takings">%s</b>'
        '</div></div><section class="card"><h2>All sales, newest first</h2>%s</section>' % (
            len(made), "s" * (len(made) != 1), money(sales.takings(shop["sales"])),
            table("sales", ("Sale", "Customer", "+Total"), rows,
                  'No sales yet. <a href="/sell">Record the first sale</a>.')))


def sale_page(shop, query, sale):
    rows = ['<tr data-id="%s"><td class="id">%s</td><td class="name">%s</td>'
            '<td class="quantity n">%d</td><td class="unit-price n">%s</td>'
            '<td class="line-total n">%s</td></tr>' % (
                e(line["item_id"]), e(line["item_id"]),
                e(name_of(catalog, shop, line["item_id"])), line["quantity"],
                money(line["unit_price_cents"]), money(line["line_total_cents"]))
            for line in sale["lines"]]
    foot = ('<tfoot><tr><th scope="row" colspan="4">Total</th><td class="n" id="total">%s</td>'
            '</tr></tfoot>' % money(sale["total_cents"]))
    return "Sale " + sale["id"], (
        head('Sale <span id="sale-id">%s</span>' % e(sale["id"]),
             '<a class="btn alt" href="/sales">All sales</a>')
        + status(shop, query, None, "sale") + '<section class="card"><dl><div><dt>Customer</dt>'
        '<dd id="customer">%s</dd></div><div><dt>Customer ID</dt><dd>%s</dd></div></dl>%s'
        '</section>' % (e(name_of(customers, shop, sale["customer_id"])), e(sale["customer_id"]),
                        table("lines", ("ID", "Item", "+Quantity", "+Unit price",
                                        "+Line total"), rows, "", foot)))


PAGES = {"/": overview, "/catalog": catalog_page, "/customers": customers_page,
         "/sell": sell_page, "/sales": sales_page}


# ---- the server ------------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    timeout = 30

    def __getattr__(self, name):
        if name.startswith("do_"):
            return self.answer
        raise AttributeError(name)

    def log_message(self, *args):
        pass

    def answer(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length > 1000000:
            self.close_connection = True
            return self.reply(413, note("Too much", "That form is too large to accept."))
        body = self.rfile.read(length) if length > 0 else b""
        try:
            with LOCK:
                self.reply(*self.route(body))
        except Exception:
            self.reply(500, note("Something went wrong", "The shop’s state file could not be "
                                 "read or written. Nothing was changed."))

    def reply(self, status, page="", headers=()):
        data = page.encode("utf-8", "replace")
        self.send_response(status)
        for key, value in (("Content-Type", "text/html; charset=utf-8"),
                           ("Content-Length", len(data)), ("Cache-Control", "no-store"),
                           ("Content-Security-Policy", CSP)) + tuple(headers):
            self.send_header(key, str(value))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def route(self, body):
        url = urlsplit(self.path)
        path, query = url.path, parse_qs(url.query, keep_blank_values=True)
        shop = load(STATE)
        allowed = [method for method, known in (("GET", PAGES), ("POST", POSTS)) if path in known]
        sale = None
        if path.startswith("/sales/"):
            try:
                sale = sales.get(shop["sales"], unquote(path[7:]))
                allowed = ["GET"]
            except KeyError:
                return 404, note("Sale not found", "There is no sale with that number.", "/sales")
        if not allowed:
            return 404, note("Page not found", "There is nothing at this address.")
        if self.command not in allowed:
            return (405, note("Not allowed", "This address does not answer to that method."),
                    [("Allow", ", ".join(allowed))])
        refusal = None
        if self.command == "POST":
            act, home = POSTS[path]
            fields = {}
            try:
                fields = {key: found[0] for key, found in parse_qs(
                    body.decode("utf-8"), keep_blank_values=True, errors="strict").items()}
                where = act(shop, fields)
                save(STATE, shop)
                return 303, "", [("Location", where)]
            except Refused as reason:
                error = str(reason)
            except UnicodeError:
                error = "The form did not arrive as UTF-8 text. Please try again."
            except (ValueError, KeyError):
                error = "The shop refused this change. Check the values and try again."
            refusal = {"action": path, "fields": fields, "error": error}
            path, shop = home, load(STATE)
        if sale:
            title, main = sale_page(shop, query, sale)
        else:
            title, main = PAGES[path](shop, query, refusal)
        return 400 if refusal else 200, layout(title, "/sales" if sale else path, main)


def main():
    global STATE
    parser = argparse.ArgumentParser(description="The pet shop in a browser.")
    parser.add_argument("--state", required=True, help="the shop's state file")
    parser.add_argument("--port", type=int, default=8000, help="0 means any free port")
    args = parser.parse_args()
    STATE = args.state
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("http://127.0.0.1:%d/" % server.server_address[1], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

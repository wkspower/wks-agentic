#!/usr/bin/env python3
"""The till of a school canteen: a menu, sales in cash or from a prepaid balance,
accounts with top-ups and pay-outs, and the totals of a day.

One program, Python's standard library, one SQLite file, and the web pages on
localhost are the only way in. What it must do is in lessons/12*.md.

    python3 product/canteen.py [--db FILE] [--port N] [--sample] [--today YYYY-MM-DD]
"""
import argparse
import datetime
import html
import json
import re
import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

FORM_BYTES = 65536
SHOWN = 200  # the most rows a long list shows
CEILING = 100000  # no top-up takes a balance above 1,000.00
DB = None
TODAY = None  # the day given with --today, or None for the machine's

SCHEMA = """
create table if not exists items (id integer primary key, name text not null, category text not null,
    price_cents integer not null, available integer not null default 1);
create table if not exists accounts (id integer primary key, name text not null, kind text not null,
    class text not null, card text not null, active integer not null default 1, balance_cents integer not null default 0);
create table if not exists sales (id integer primary key, day text not null, time text not null, method text not null,
    account_id integer, total_cents integer not null, given_cents integer, change_cents integer,
    voided integer not null default 0, voided_day text);
create table if not exists lines (id integer primary key, sale_id integer not null, item_id integer not null,
    name text not null, qty integer not null, price_cents integer not null);
create table if not exists movements (id integer primary key, account_id integer not null, kind text not null,
    amount_cents integer not null, day text not null, time text not null, voided integer not null default 0, voided_day text);
"""


class Refused(Exception):
    """What was asked is not done; nothing of it is recorded."""

    def __init__(self, why, status=400, hint=None):
        super().__init__(why)
        self.why, self.status, self.hint = why, status, hint


def today():
    return TODAY or datetime.date.today().isoformat()


def now():
    return datetime.datetime.now().strftime("%H:%M")


def money(cents):
    return "%s%d.%02d" % ("-" if cents < 0 else "", abs(cents) // 100, abs(cents) % 100)


# ---- the bounds of every input (lessons/1208) ------------------------------------------------

def amount(text, what, least, most):
    text = text.strip()
    if not re.fullmatch(r"\d{1,7}(\.\d{1,2})?", text):
        raise Refused("%s must be an amount such as 2.50, with at most two decimals; \"%s\" is not." % (what, text))
    whole, _, part = text.partition(".")
    cents = int(whole) * 100 + int((part + "00")[:2])
    if not least <= cents <= most:
        raise Refused("%s must be from %s to %s; %s is not." % (what, money(least), money(most), money(cents)))
    return cents


def words(text, what, least, most):
    text = " ".join(text.split())
    if not least <= len(text) <= most:
        raise Refused("%s must have %s%d characters; this has %d." % (what, "%d to " % least if least else "at most ", most, len(text)))
    return text


def one_of(text, what, allowed):
    if text.strip() not in allowed:
        raise Refused("%s must be %s." % (what, " or ".join(allowed)))
    return text.strip()


def card_number(text):
    text = text.strip()
    if text and not re.fullmatch(r"[A-Za-z0-9-]{1,20}", text):
        raise Refused("The card number must be 1 to 20 letters, digits and hyphens.")
    return text


def a_day(text):
    try:
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", text):
            raise ValueError
        return datetime.date.fromisoformat(text).isoformat()
    except ValueError:
        raise Refused("The day must be a real date written as YYYY-MM-DD; \"%s\" is not." % text)


# ---- what is stored ---------------------------------------------------------------------------

def one(sql, *args):
    return DB.execute(sql, args).fetchone()


def every(sql, *args):
    return DB.execute(sql, args).fetchall()


def found(table, ident):
    row = one("select * from %s where id = ?" % table, ident)
    if row is None:
        raise Refused("There is no such page.", 404)
    return row


def lines_of(sale_id):
    return every("select * from lines where sale_id = ? order by id", sale_id)


def items_text(sale_id):
    return ", ".join("%d × %s" % (line["qty"], line["name"]) for line in lines_of(sale_id))


def save_item(form, ident=None):
    name = words(form.get("name"), "The item's name", 1, 80)
    category = words(form.get("category"), "The category", 1, 40)
    price = amount(form.get("price"), "The price", 1, 99999)
    with DB:
        if ident is None:
            DB.execute("insert into items (name, category, price_cents) values (?, ?, ?)", (name, category, price))
        else:
            DB.execute("update items set name = ?, category = ?, price_cents = ? where id = ?", (name, category, price, ident))


def save_account(form, ident=None):
    name = words(form.get("name"), "The name", 1, 80)
    kind = one_of(form.get("kind"), "The kind of account", ("pupil", "staff"))
    klass = words(form.get("class"), "The class", 0, 20)
    card = card_number(form.get("card"))
    active = int(one_of(form.get("active"), "Whether the person is at the school", ("1", "0"))) if ident else 1
    with DB:
        if card and one("select 1 from accounts where card = ? and id is not ?", card, ident):
            raise Refused("Card %s already belongs to another account. A card number belongs to one account." % card)
        if ident is None:
            return DB.execute("insert into accounts (name, kind, class, card) values (?, ?, ?, ?)", (name, kind, klass, card)).lastrowid
        DB.execute("update accounts set name = ?, kind = ?, class = ?, card = ?, active = ? where id = ?",
                   (name, kind, klass, card, active, ident))
    return ident


TILL_HINT = ("Go back to the till: the quantities and the cash given are still there, "
             "and the card field is empty for the next scan.")


def sell(form):
    """One sale, whole or not at all (lessons/1202). Returns its number."""
    idents, qtys = form.all("item_id"), form.all("qty")
    if len(idents) != len(qtys):
        raise Refused("The sale did not arrive whole.", hint=TILL_HINT)
    wanted = []
    for ident, qty in zip(idents, qtys):
        if qty == "":
            continue
        if not re.fullmatch(r"\d{1,2}", qty) or int(qty) < 1:
            raise Refused("A quantity must be a whole number from 1 to 99; \"%s\" is not." % qty, hint=TILL_HINT)
        wanted.append((ident, int(qty)))
    if not wanted:
        raise Refused("Nothing was sold: type a quantity beside at least one item.", hint=TILL_HINT)
    if len(wanted) > 50:
        raise Refused("A sale has at most 50 lines; this one has %d." % len(wanted), hint=TILL_HINT)
    given, card, account_id = form.get("given"), form.get("card"), form.get("account_id")
    if given and (card or account_id):
        raise Refused("A sale is paid in cash or from a balance, not both: give the cash or the card.", hint=TILL_HINT)
    if not (given or card or account_id):
        raise Refused("Type the cash given, or scan a card to pay from its balance.", hint=TILL_HINT)
    with DB:
        total, lines = 0, []
        for ident, qty in wanted:
            item = one("select * from items where id = ?", ident) if ident.isdigit() else None
            if item is None:
                raise Refused("There is no item %s on the menu." % ident, hint=TILL_HINT)
            if not item["available"]:
                raise Refused("%s is sold out. Nothing was sold." % item["name"], hint=TILL_HINT)
            total += qty * item["price_cents"]
            lines.append((item["id"], item["name"], qty, item["price_cents"]))
        if given:
            paid = amount(given, "The cash given", 0, 999999)
            if paid < total:
                raise Refused("The cash given, %s, is less than the total, %s. Nothing was sold." % (money(paid), money(total)), hint=TILL_HINT)
            row = ("cash", None, total, paid, paid - total)
        else:
            if account_id:
                account = one("select * from accounts where id = ?", account_id) if account_id.isdigit() else None
                if account is None:
                    raise Refused("There is no account %s." % account_id, hint=TILL_HINT)
            else:
                account = one("select * from accounts where card = ?", card_number(card))
                if account is None:
                    raise Refused("There is no account with card %s. Nothing was sold." % card, hint=TILL_HINT)
            if not account["active"]:
                raise Refused("%s has left the school and buys nothing. Nothing was sold." % account["name"], hint=TILL_HINT)
            if account["balance_cents"] < total:
                raise Refused("The balance of %s is %s and the total is %s. Nothing was sold." % (
                    account["name"], money(account["balance_cents"]), money(total)), hint=TILL_HINT)
            DB.execute("update accounts set balance_cents = balance_cents - ? where id = ?", (total, account["id"]))
            row = ("account", account["id"], total, None, None)
        sale = DB.execute("insert into sales (day, time, method, account_id, total_cents, given_cents, change_cents) "
                          "values (?, ?, ?, ?, ?, ?, ?)", (today(), now()) + row).lastrowid
        DB.executemany("insert into lines (sale_id, item_id, name, qty, price_cents) values (?, ?, ?, ?, ?)",
                       [(sale,) + line for line in lines])
    return sale


def move(account, kind, form):
    """A top-up or a pay-out, in cash (lessons/1203)."""
    with DB:
        account = found("accounts", account["id"])
        held = account["balance_cents"]
        if kind == "topup":
            if not account["active"]:
                raise Refused("%s has left the school: the account takes no top-up." % account["name"])
            cents = amount(form.get("amount"), "A top-up", 1, 50000)
            if held + cents > CEILING:
                raise Refused("A balance is at most %s: with %s there, the most this top-up can be is %s."
                              % (money(CEILING), money(held), money(CEILING - held)))
        else:
            cents = amount(form.get("amount"), "A pay-out", 1, 9999999)
            if cents > held:
                raise Refused("A pay-out is at most the balance, %s; %s is more." % (money(held), money(cents)))
        DB.execute("update accounts set balance_cents = balance_cents + ? where id = ?", (cents if kind == "topup" else -cents, account["id"]))
        DB.execute("insert into movements (account_id, kind, amount_cents, day, time) values (?, ?, ?, ?, ?)",
                   (account["id"], kind, cents, today(), now()))


def void_sale(ident):
    with DB:
        sale = found("sales", ident)
        if sale["voided"]:
            raise Refused("Sale %d is already voided." % ident, hint="")
        DB.execute("update sales set voided = 1, voided_day = ? where id = ?", (today(), ident))
        if sale["account_id"]:
            DB.execute("update accounts set balance_cents = balance_cents + ? where id = ?", (sale["total_cents"], sale["account_id"]))


def top_up(ident):
    """A top-up by its number; a pay-out has no page of its own."""
    row = found("movements", ident)
    if row["kind"] != "topup":
        raise Refused("There is no such page.", 404)
    return row


def void_top_up(ident):
    with DB:
        row = top_up(ident)
        account = found("accounts", row["account_id"])
        if row["voided"]:
            raise Refused("This top-up is already voided.", hint="")
        if account["balance_cents"] < row["amount_cents"]:
            raise Refused("The top-up of %s cannot be voided: only %s of it is left in the balance of %s."
                          % (money(row["amount_cents"]), money(account["balance_cents"]), account["name"]), hint="")
        DB.execute("update movements set voided = 1, voided_day = ? where id = ?", (today(), ident))
        DB.execute("update accounts set balance_cents = balance_cents - ? where id = ?", (row["amount_cents"], account["id"]))
    return row["account_id"]


def export():
    out = {"today": today()}
    out["items"] = [dict(row, available=bool(row["available"])) for row in map(dict, every("select * from items order by id"))]
    out["accounts"] = [dict(row, active=bool(row["active"])) for row in map(dict, every("select * from accounts order by id"))]
    lines = {}
    for line in every("select * from lines order by id"):
        lines.setdefault(line["sale_id"], []).append(
            {"item_id": line["item_id"], "name": line["name"], "qty": line["qty"], "price_cents": line["price_cents"]})
    out["sales"] = [dict(row, voided=bool(row["voided"]), lines=lines.get(row["id"], []))
                    for row in map(dict, every("select * from sales order by id"))]
    out["movements"] = [dict(row, voided=bool(row["voided"])) for row in map(dict, every("select * from movements order by id"))]
    return out


def sample():
    if one("select 1 from items") or one("select 1 from accounts"):
        return
    form = lambda **fields: Form([(name.rstrip("_"), value) for name, value in fields.items()])
    for name, category, price in [("Cheese roll", "Food", "2.35"), ("Ham roll", "Food", "2.60"), ("Soup of the day", "Food", "3.00"),
                                  ("Pasta bowl", "Food", "4.20"), ("Apple", "Fruit", "0.60"), ("Banana", "Fruit", "0.55"),
                                  ("Apple juice", "Drinks", "1.10"), ("Water", "Drinks", "0.80"), ("Milk", "Drinks", "0.90"),
                                  ("Oat biscuit", "Snacks", "0.75")]:
        save_item(form(name=name, category=category, price=price))
    for name, kind, klass, card, held in [("Ana Lima", "pupil", "7B", "1001", "20.00"), ("Bo Li", "pupil", "9A", "1002", "5.00"),
                                          ("Maria Aparecida de Souza", "pupil", "7B", "1003", ""), ("Ms Kay", "staff", "", "2001", "30.00")]:
        ident = save_account(form(name=name, kind=kind, class_=klass, card=card))
        if held:
            move(found("accounts", ident), "topup", form(amount=held))


# ---- the pages --------------------------------------------------------------------------------

CSS = """
*{box-sizing:border-box}
body{margin:0;font:16px/1.4 system-ui,sans-serif;color:#1c2430;background:#f4f5f7;overflow-wrap:anywhere}
nav{display:flex;flex-wrap:wrap;gap:.25rem 1rem;padding:.6rem 1rem;background:#1f3a5f}
nav a{color:#fff;text-decoration:none;font-weight:600;white-space:nowrap}
nav a.here{text-decoration:underline}
main{max-width:1100px;margin:0 auto;padding:1rem}
h1{font-size:1.4rem;margin:.2rem 0 .8rem}
h2{font-size:1.1rem;margin:1.2rem 0 .5rem}
.note{background:#fff3cd;padding:.4rem 1rem;margin:0}
.done{background:#e3f4e7;border:1px solid #9ccfa8;border-radius:6px;padding:.6rem .9rem}
.done strong{font-size:1.5rem}
.refused{background:#fde8e8;border:1px solid #e0a0a0;border-radius:6px;padding:.6rem .9rem;font-weight:600}
.left{color:#8a1f1f;font-weight:600}
form.card{background:#fff;border:1px solid #cfd4dc;border-radius:6px;padding:.8rem;margin:0 0 1rem;max-width:100%}
form.card .row{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:end}
label{display:block;font-weight:600;font-size:.9rem;min-width:0;max-width:100%}
input,select,button{font:inherit;max-width:100%}
input,select{display:block;width:14rem;padding:.4rem;border:1px solid #9aa3af;border-radius:4px;background:#fff}
input.short{width:7rem}
button{padding:.45rem .9rem;border:1px solid #1f3a5f;border-radius:4px;background:#1f3a5f;color:#fff;cursor:pointer;white-space:nowrap}
button.quiet{background:#fff;color:#1f3a5f}
.menu{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.4rem .8rem;margin:0 0 .6rem}
.menu label{display:grid;grid-template-columns:1fr auto 3.6rem;gap:.5rem;align-items:center;font-weight:400;font-size:1rem;
  padding:.3rem .5rem;border:1px solid #e1e4ea;border-radius:4px}
.menu input{width:3.6rem;text-align:right}
.menu .price{white-space:nowrap;font-variant-numeric:tabular-nums}
.total{font-size:1.3rem;font-weight:700;margin:.4rem 0 .8rem}
.or{align-self:center;font-weight:600}
dl{display:grid;grid-template-columns:max-content 1fr;gap:.2rem 1rem;margin:0 0 1rem}
dt{font-weight:600}dd{margin:0}
.links a{margin-right:1rem;white-space:nowrap}
.scroll{overflow-x:auto;background:#fff;border:1px solid #cfd4dc;border-radius:6px;margin:0 0 1rem}
table{border-collapse:collapse;width:100%}
th,td{padding:.45rem .6rem;text-align:left;vertical-align:top;white-space:nowrap;border-bottom:1px solid #e6e9ee}
th{background:#eef1f5;font-size:.85rem}
td.text{white-space:normal;min-width:150px}
td.wide{min-width:240px}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
td.act a,td.act form{display:inline-block;margin:0 .5rem 0 0}
td.act button{padding:.2rem .6rem}
table.acts th:last-child,table.acts td:last-child{position:sticky;right:0;background:#fff;box-shadow:-6px 0 6px -6px #8893a2;z-index:1}
table.acts th:last-child{background:#eef1f5}
tr.off td{color:#7a828e}
@media (max-width:760px){
  .scroll{overflow-x:visible;background:none;border:0}
  table,tbody,tr,td{display:block;width:auto}
  thead{display:none}
  tr{background:#fff;border:1px solid #cfd4dc;border-radius:6px;margin:0 0 .7rem;padding:.4rem .6rem}
  td,td.text,td.wide{border:0;padding:.15rem 0;min-width:0;text-align:left;white-space:normal}
  td.num{text-align:left}
  td::before{content:attr(data-label) ": ";font-weight:600}
  td.act::before{content:none}
  td.num,td.act a,td.act button{white-space:nowrap}
  table.acts td:last-child{position:static;box-shadow:none;padding-top:.4rem}
  input,select{width:100%}
  .menu input{width:3.6rem}
}
"""

SCRIPT = """
(function () {
  var till = document.getElementById('till'), sum = document.getElementById('sum');
  function add() {
    if (!till || !sum) return;
    var cents = 0, ok = true;
    till.querySelectorAll('input[name=qty]').forEach(function (field) {
      var typed = field.value.trim();
      if (typed === '') return;
      if (/^[0-9]{1,2}$/.test(typed) && Number(typed) > 0) cents += Number(typed) * Number(field.dataset.cents); else ok = false;
    });
    sum.textContent = ok ? Math.floor(cents / 100) + '.' + ('0' + cents % 100).slice(-2) : '?';
  }
  if (till) till.addEventListener('input', add);
  window.addEventListener('pageshow', function () {
    add();
    var scan = document.querySelector('input[data-scan]');
    if (scan) { scan.value = ''; scan.focus(); }
  });
})();
"""

NAV = [("/", "Till"), ("/items", "Menu"), ("/accounts", "Accounts"), ("/sales", "Sales"), ("/day", "Day")]


def esc(value):
    return html.escape(str(value), quote=True)


def page(title, body, here=None):
    links = "".join('<a href="%s"%s>%s</a>' % (path, ' class="here"' if name == here else "", name) for path, name in NAV)
    note = ('<p class="note">Started with --today %s: every sale, top-up and void made now is recorded on that day.</p>' % esc(TODAY)
            if TODAY else "")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>%s — Canteen</title><style>%s</style></head>'
            '<body><nav>%s</nav>%s<main><h1>%s</h1>%s</main><script>%s</script></body></html>'
            % (esc(title), CSS, links, note, esc(title), body, SCRIPT))


def field(label, name, value="", size="", **more):
    extra = "".join(' %s="%s"' % (key.replace("_", "-"), esc(text)) for key, text in more.items())
    return '<label>%s <input name="%s" value="%s"%s%s></label>' % (
        esc(label), name, esc(value), ' class="%s"' % size if size else "", extra)


def choice(label, name, options, chosen=None):
    """A select. With nothing chosen it starts on an empty option: the person chooses."""
    out = "" if chosen is not None else '<option value="">choose</option>'
    out += "".join('<option value="%s"%s>%s</option>' % (esc(value), " selected" if value == chosen else "", esc(text))
                   for value, text in options)
    return '<label>%s <select name="%s">%s</select></label>' % (esc(label), name, out)


def table(heads, rows, acts=False):
    """A list: a table on a wide screen, stacked cards with the name of each column on a narrow one.

    heads: (name, kind) with kind '' for a short text, 'text' or 'text wide' for words, 'num', 'act'.
    rows: (cells, off) where cells are HTML already escaped."""
    if not rows:
        return ""
    head = "".join('<th%s>%s</th>' % (' class="num"' if kind == "num" else "", esc(name)) for name, kind in heads)
    body = ""
    for cells, off in rows:
        body += "<tr%s>%s</tr>" % (' class="off"' if off else "", "".join(
            '<td%s data-label="%s">%s</td>' % (' class="%s"' % kind if kind else "", esc(name), cell)
            for (name, kind), cell in zip(heads, cells)))
    return '<div class="scroll"><table%s><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        ' class="acts"' if acts else "", head, body)


def count(number, thing, things=None):
    return "%d %s" % (number, thing if number == 1 else things or thing + "s")


def who(account):
    return "%s%s" % (account["name"], " (%s)" % account["class"] if account["class"] else "")


def till_page(query):
    body = ""
    sold = query.get("sold")
    if sold.isdigit() and one("select 1 from sales where id = ?", sold):
        sale = found("sales", sold)
        if sale["method"] == "cash":
            paid = "given %s, change <strong>%s</strong>" % (money(sale["given_cents"]), money(sale["change_cents"]))
        else:
            account = found("accounts", sale["account_id"])
            paid = "from the balance of %s, which is now <strong>%s</strong>" % (esc(who(account)), money(account["balance_cents"]))
        body += '<p class="done">Sale %d: %s. Total <strong>%s</strong>, %s. <a href="/sales/%d">Open it</a></p>' % (
            sale["id"], esc(items_text(sale["id"])), money(sale["total_cents"]), paid, sale["id"])
    items = every("select * from items where available = 1 order by category collate nocase, name collate nocase")
    if not items:
        return page("Till", body + '<p>Nothing is on sale. Add items on the <a href="/items">menu</a>.</p>', "Till")
    menu, category = "", None
    for item in items:
        if item["category"] != category:
            category = item["category"]
            menu += '%s<h2>%s</h2><div class="menu">' % ("</div>" if menu else "", esc(category))
        menu += ('<label><span>%s</span><span class="price">%s</span><input type="hidden" name="item_id" value="%d">'
                 '<input name="qty" inputmode="numeric" maxlength="2" data-cents="%d" aria-label="How many %s"></label>'
                 % (esc(item["name"]), money(item["price_cents"]), item["id"], item["price_cents"], esc(item["name"])))
    menu += "</div>"
    account = one("select * from accounts where id = ?", query.get("account")) if query.get("account").isdigit() else None
    if account:
        pay = ('<input type="hidden" name="account_id" value="%d"><p>Paid from the balance of <strong>%s</strong>, which is %s. '
               '<a href="/">Pay another way</a></p><button type="submit">Sell</button>'
               % (account["id"], esc(who(account)), money(account["balance_cents"])))
    else:
        pay = ('<div class="row">%s<span class="or">or</span>%s<button type="submit">Sell</button></div>' % (
            field("Cash given", "given", size="short", inputmode="decimal", placeholder="10.00"),
            field("Card, to pay from its balance", "card", size="short", autocomplete="off", data_scan="1")))
    body += ('<form class="card" id="till" method="post" action="/sales">%s<p class="total">Total <output id="sum">0.00</output></p>%s</form>'
             % (menu, pay))
    return page("Till", body, "Till")


def item_form(action, item=None, button="Add to the menu"):
    return ('<form class="card" method="post" action="%s"><div class="row">%s%s%s<button type="submit">%s</button></div></form>' % (
        action, field("Name", "name", item["name"] if item else "", maxlength="80"),
        field("Category", "category", item["category"] if item else "", placeholder="Food or Drinks", maxlength="40"),
        field("Price, tax included", "price", money(item["price_cents"]) if item else "", size="short", inputmode="decimal", placeholder="2.50"),
        button))


def items_page():
    rows = []
    for item in every("select * from items order by category collate nocase, name collate nocase"):
        flip = ('<form method="post" action="/items/%d/available"><input type="hidden" name="available" value="%d">'
                '<button type="submit" class="quiet">%s</button></form>' % (
                    item["id"], 0 if item["available"] else 1, "Sold out" if item["available"] else "Back on sale"))
        rows.append(([esc(item["name"]), esc(item["category"]), money(item["price_cents"]),
                      "on sale" if item["available"] else "sold out", flip + '<a href="/items/%d/edit">Edit</a>' % item["id"]],
                     not item["available"]))
    body = "<h2>A new item</h2>" + item_form("/items")
    body += "<h2>%s on the menu</h2>" % count(len(rows), "item")
    body += table([("Item", "text"), ("Category", "text"), ("Price", "num"), ("State", ""), ("", "act")], rows, acts=True)
    return page("Menu", body, "Menu")


def account_form(action, account=None, button="Open the account"):
    kinds = [("pupil", "pupil"), ("staff", "staff")]
    out = field("Name", "name", account["name"] if account else "", maxlength="80")
    out += choice("Pupil or staff", "kind", kinds, account["kind"] if account else None)
    out += field("Class", "class", account["class"] if account else "", size="short", placeholder="7B", maxlength="20")
    out += field("Card number, if any", "card", account["card"] if account else "", size="short", maxlength="20")
    if account:
        out += choice("At the school", "active", [("1", "yes"), ("0", "no, has left")], str(account["active"]))
    return '<form class="card" method="post" action="%s"><div class="row">%s<button type="submit">%s</button></div></form>' % (action, out, button)


def accounts_page(query):
    asked = query.get("q")
    if len(asked) > 100:
        raise Refused("The search text has at most 100 characters; this has %d." % len(asked))
    wanted = asked.casefold()
    matching = [row for row in every("select * from accounts order by name collate nocase, id")
                if any(wanted in row[name].casefold() for name in ("name", "class", "card"))]
    rows = []
    for account in matching[:SHOWN]:
        sell_link = '<a href="/?account=%d">Sell</a>' % account["id"] if account["active"] else ""
        rows.append(([esc(account["name"]), account["kind"], esc(account["class"]), esc(account["card"]), money(account["balance_cents"]),
                      "at the school" if account["active"] else "has left",
                      '<a href="/accounts/%d">Open</a>%s' % (account["id"], sell_link)], not account["active"]))
    body = "<h2>A new account</h2>" + account_form("/accounts")
    body += ('<h2>Find an account</h2><form class="card" method="get" action="/accounts"><div class="row">%s'
             '<button type="submit">Search</button></div></form>' % field("Name, class or card", "q", asked, maxlength="100"))
    said = count(len(matching), "account") + (" matching “%s”" % esc(asked) if asked else "")
    if len(matching) > SHOWN:
        said += ", the first %d shown; search to find the others" % SHOWN
    body += "<h2>%s</h2>" % said
    body += table([("Name", "text"), ("Kind", ""), ("Class", ""), ("Card", ""), ("Balance", "num"), ("State", ""), ("", "act")], rows, acts=True)
    return page("Accounts", body, "Accounts")


def sale_rows(sales, with_who=True):
    rows = []
    for sale in sales:
        if sale["method"] == "cash":
            paid = "cash"
        else:
            paid = "balance of " + esc(found("accounts", sale["account_id"])["name"])
        acts = '<a href="/sales/%d">Open</a>' % sale["id"]
        if not sale["voided"]:
            acts += '<a href="/sales/%d/void">Void</a>' % sale["id"]
        cells = [str(sale["id"]), sale["day"], sale["time"], esc(items_text(sale["id"]))] + ([paid] if with_who else [])
        rows.append((cells + [money(sale["total_cents"]), "voided on " + sale["voided_day"] if sale["voided"] else "stands", acts],
                     sale["voided"]))
    return rows


def sales_page():
    total = one("select count(*) from sales")[0]
    rows = sale_rows(every("select * from sales order by id desc limit ?", SHOWN))
    said = count(total, "sale") + (", the latest %d shown" % SHOWN if total > SHOWN else "")
    body = "<h2>%s</h2>" % said + table([("Sale", ""), ("Day", ""), ("Time", ""), ("Items", "text wide"), ("Paid", "text"), ("Total", "num"),
                                         ("State", ""), ("", "act")], rows, acts=True)
    return page("Sales", body, "Sales")


def sale_facts(sale):
    out = "<dt>Day</dt><dd>%s at %s</dd>" % (sale["day"], sale["time"])
    out += "<dt>Total</dt><dd><strong>%s</strong></dd>" % money(sale["total_cents"])
    if sale["method"] == "cash":
        out += "<dt>Paid</dt><dd>in cash: given %s, change %s</dd>" % (money(sale["given_cents"]), money(sale["change_cents"]))
    else:
        account = found("accounts", sale["account_id"])
        out += '<dt>Paid</dt><dd>from the balance of <a href="/accounts/%d">%s</a></dd>' % (account["id"], esc(who(account)))
    out += "<dt>State</dt><dd>%s</dd>" % ("voided on " + sale["voided_day"] if sale["voided"] else "stands")
    lines = [([esc(line["name"]), str(line["qty"]), money(line["price_cents"]), money(line["qty"] * line["price_cents"])], False)
             for line in lines_of(sale["id"])]
    return "<dl>%s</dl>" % out + table([("Item", "text"), ("Quantity", "num"), ("Price", "num"), ("Amount", "num")], lines)


def sale_page(sale):
    body = sale_facts(sale) + '<p class="links">'
    if not sale["voided"]:
        body += '<a href="/sales/%d/void">Void this sale</a>' % sale["id"]
    return page("Sale %d" % sale["id"], body + '<a href="/sales">All sales</a><a href="/">Back to the till</a></p>')


def void_sale_page(sale):
    if sale["voided"]:
        body = "<p>This sale is voided and stays on record. It cannot be voided again.</p>" + sale_facts(sale)
    else:
        back = (" Its %s goes back to the balance it was paid from." % money(sale["total_cents"]) if sale["method"] == "account"
                else " Hand back the %s in cash." % money(sale["total_cents"]))
        body = ("<p>Voiding takes the whole sale back and cannot be undone.%s</p>" % back + sale_facts(sale)
                + '<form class="card" method="post" action="/sales/%d/void"><div class="row"><button type="submit">Void sale %d</button>'
                  '<a href="/sales">Keep it</a></div></form>' % (sale["id"], sale["id"]))
    return page("Void sale %d?" % sale["id"], body)


def void_top_up_page(row):
    account = found("accounts", row["account_id"])
    facts = "<dl><dt>Top-up</dt><dd><strong>%s</strong>, on %s at %s</dd><dt>Account</dt><dd>%s, balance %s</dd></dl>" % (
        money(row["amount_cents"]), row["day"], row["time"], esc(who(account)), money(account["balance_cents"]))
    if row["voided"]:
        body = "<p>This top-up is voided and stays on record. It cannot be voided again.</p>" + facts
    else:
        body = ("<p>Voiding takes the whole top-up out of the balance and cannot be undone. Hand back the %s in cash.</p>%s"
                '<form class="card" method="post" action="/movements/%d/void"><div class="row"><button type="submit">Void this top-up</button>'
                '<a href="/accounts/%d">Keep it</a></div></form>' % (money(row["amount_cents"]), facts, row["id"], account["id"]))
    return page("Void a top-up of %s?" % money(row["amount_cents"]), body)


def account_page(account):
    ident = account["id"]
    body = "<dl><dt>Balance</dt><dd><strong>%s</strong></dd><dt>Kind</dt><dd>%s</dd><dt>Class</dt><dd>%s</dd><dt>Card</dt><dd>%s</dd></dl>" % (
        money(account["balance_cents"]), account["kind"], esc(account["class"]) or "none", esc(account["card"]) or "none")
    if not account["active"]:
        body += '<p class="left">%s has left the school: no sale and no top-up. What is left in the balance can be paid out.</p>' % esc(account["name"])
    body += '<p class="links">%s<a href="/accounts/%d/edit">Correct this account</a></p>' % (
        '<a href="/?account=%d">Sell to this account</a>' % ident if account["active"] else "", ident)
    money_form = '<form class="card" method="post" action="/accounts/%d/%s"><div class="row">%s<button type="submit">%s</button></div></form>'
    if account["active"]:
        body += money_form % (ident, "topup", field("Top-up in cash", "amount", size="short", inputmode="decimal", placeholder="5.00"), "Top up")
    if account["balance_cents"]:
        body += money_form % (ident, "payout", field("Pay-out in cash, at most %s" % money(account["balance_cents"]), "amount",
                                                     size="short", inputmode="decimal"), "Pay out")
    moves = every("select * from movements where account_id = ? order by id desc limit ?", ident, SHOWN)
    total = one("select count(*) from movements where account_id = ?", ident)[0]
    rows = []
    for row in moves:
        state = "voided on " + row["voided_day"] if row["voided"] else "stands"
        void = '<a href="/movements/%d/void">Void</a>' % row["id"] if row["kind"] == "topup" and not row["voided"] else ""
        rows.append(([row["day"], row["time"], "top-up" if row["kind"] == "topup" else "pay-out", money(row["amount_cents"]), state, void],
                     row["voided"]))
    body += "<h2>%s%s</h2>" % (count(total, "top-up or pay-out", "top-ups and pay-outs"), ", the latest %d shown" % SHOWN if total > SHOWN else "")
    body += table([("Day", ""), ("Time", ""), ("What", ""), ("Amount", "num"), ("State", ""), ("", "act")], rows, acts=True)
    total = one("select count(*) from sales where account_id = ?", ident)[0]
    rows = sale_rows(every("select * from sales where account_id = ? order by id desc limit ?", ident, SHOWN), with_who=False)
    body += "<h2>%s%s</h2>" % (count(total, "sale"), ", the latest %d shown" % SHOWN if total > SHOWN else "")
    body += table([("Sale", ""), ("Day", ""), ("Time", ""), ("Items", "text wide"), ("Total", "num"), ("State", ""), ("", "act")], rows, acts=True)
    return page(who(account), body)


def day_page(query):
    day = a_day(query.get("date")) if query.get("date") else today()

    def tot(sql, *args):
        row = one("select count(*), coalesce(sum(%s), 0) from %s" % tuple(sql.split(" from ", 1)), *args)
        return row[0], row[1]

    cash = tot("total_cents from sales where method = 'cash' and day = ?", day)
    held = tot("total_cents from sales where method = 'account' and day = ?", day)
    tops = tot("amount_cents from movements where kind = 'topup' and day = ?", day)
    outs = tot("amount_cents from movements where kind = 'payout' and day = ?", day)
    cash_voided = tot("total_cents from sales where method = 'cash' and voided_day = ?", day)
    held_voided = tot("total_cents from sales where method = 'account' and voided_day = ?", day)
    tops_voided = tot("amount_cents from movements where kind = 'topup' and voided_day = ?", day)
    expected = cash[1] + tops[1] - outs[1] - cash_voided[1] - tops_voided[1]
    rows = [([name, str(pair[0]), money(pair[1])], False) for name, pair in [
        ("Cash sales", cash), ("Sales from a balance", held), ("Top-ups", tops), ("Pay-outs", outs),
        ("Cash sales voided", cash_voided), ("Sales from a balance voided", held_voided), ("Top-ups voided", tops_voided)]]
    rows.append((["<strong>Cash expected in the drawer</strong>", "", "<strong>%s</strong>" % money(expected)], False))
    body = ('<form class="card" method="get" action="/day"><div class="row">%s<button type="submit">Show</button>'
            '<a href="/day">Today</a></div></form>' % field("Another day", "date", day, size="short", placeholder=today(), maxlength="10"))
    body += "<h2>%s%s</h2>" % (day, ", today" if day == today() else "")
    body += ("<p>Sales and top-ups count on the day they were made, voids on the day of the void. Cash expected is cash sales "
             "plus top-ups, less pay-outs, less the cash sales and top-ups voided that day.</p>")
    body += table([("What", "text"), ("How many", "num"), ("Amount", "num")], rows)
    sold = every("select lines.name, sum(lines.qty), sum(lines.qty * lines.price_cents) from lines join sales on sales.id = lines.sale_id "
                 "where sales.day = ? and sales.voided = 0 group by lines.name order by lines.name collate nocase", day)
    body += "<h2>Items sold in sales that stand</h2>"
    body += table([("Item", "text"), ("Quantity", "num"), ("Amount", "num")],
                  [([esc(row[0]), str(row[1]), money(row[2])], False) for row in sold]) or "<p>None.</p>"
    return page("Day", body, "Day")


def refusal(error):
    if error.status == 404:
        return page("Not found", '<p class="refused">There is no such page.</p>')
    hint = "Go back to the form: what you typed is still there." if error.hint is None else error.hint
    return page("Not done", '<p class="refused">%s</p><p>%s</p>' % (esc(error.why), esc(hint)))


# ---- the requests -----------------------------------------------------------------------------

class Form:
    def __init__(self, pairs):
        self.pairs = pairs

    def all(self, name):
        return [value.strip() for other, value in self.pairs if other == name]

    def get(self, name):
        return (self.all(name) or [""])[0]


class Handler(BaseHTTPRequestHandler):
    server_version = "Canteen"

    def log_message(self, *args):
        pass

    def answer(self, status, body, kind="text/html; charset=utf-8", location=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(data)

    def own(self):
        """A request from another site, or to another host name, is refused (lessons/0007)."""
        port = self.server.server_address[1]
        host = self.headers.get("Host", "")
        if host not in ("127.0.0.1:%d" % port, "localhost:%d" % port):
            return False
        if self.headers.get("Origin") not in (None, "http://" + host):
            return False
        return self.headers.get("Sec-Fetch-Site") in (None, "same-origin", "none")

    def handle_one(self, method):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(min(length, 1 << 20)) if length > 0 else b""
            if not self.own():
                return self.answer(403, page("Refused", '<p class="refused">This request came from another site or names another host.</p>'))
            if length > FORM_BYTES:
                return self.answer(413, page("Too large", '<p class="refused">A form is at most 65,536 bytes.</p>'))
            url = urllib.parse.urlsplit(self.path)
            query = Form(urllib.parse.parse_qsl(url.query, keep_blank_values=True))
            form = Form(urllib.parse.parse_qsl(raw.decode("utf-8", "replace"), keep_blank_values=True))
            self.route(method, url.path, query, form)
        except Refused as error:
            self.answer(error.status, refusal(error))

    def do_GET(self):
        self.handle_one("GET")

    def do_POST(self):
        self.handle_one("POST")

    def route(self, method, path, query, form):
        get, post = method == "GET", method == "POST"
        parts = [part for part in path.split("/") if part]
        ident = int(parts[1]) if len(parts) > 1 and re.fullmatch(r"\d{1,9}", parts[1]) else None
        shape = "/".join("N" if spot == 1 and ident is not None else part for spot, part in enumerate(parts))
        go = lambda where: self.answer(303, "", location=where)
        show = lambda body: self.answer(200, body)
        if shape == "" and get:
            return show(till_page(query))
        if shape == "export.json" and get:
            return self.answer(200, json.dumps(export(), indent=1), "application/json")
        if shape == "day" and get:
            return show(day_page(query))
        if shape == "items":
            if get:
                return show(items_page())
            save_item(form)
            return go("/items")
        if shape == "items/N/edit":
            item = found("items", ident)
            if get:
                return show(page("Correct " + item["name"], item_form("/items/%d/edit" % ident, item, "Save")
                                 + '<p class="links"><a href="/items">Back to the menu</a></p>'))
            save_item(form, ident)
            return go("/items")
        if shape == "items/N/available" and post:
            found("items", ident)
            with DB:
                DB.execute("update items set available = ? where id = ?",
                           (int(one_of(form.get("available"), "Whether the item is on sale", ("1", "0"))), ident))
            return go("/items")
        if shape == "accounts":
            if get:
                return show(accounts_page(query))
            return go("/accounts/%d" % save_account(form))
        if shape == "accounts/N" and get:
            return show(account_page(found("accounts", ident)))
        if shape == "accounts/N/edit":
            account = found("accounts", ident)
            if get:
                return show(page("Correct " + account["name"], account_form("/accounts/%d/edit" % ident, account, "Save")
                                 + '<p class="links"><a href="/accounts/%d">Back to the account</a></p>' % ident))
            save_account(form, ident)
            return go("/accounts/%d" % ident)
        if shape in ("accounts/N/topup", "accounts/N/payout") and post:
            move(found("accounts", ident), parts[2], form)
            return go("/accounts/%d" % ident)
        if shape == "sales":
            if get:
                return show(sales_page())
            return go("/?sold=%d" % sell(form))
        if shape == "sales/N" and get:
            return show(sale_page(found("sales", ident)))
        if shape == "sales/N/void":
            if get:
                return show(void_sale_page(found("sales", ident)))
            void_sale(ident)
            return go("/sales/%d" % ident)
        if shape == "movements/N/void":
            if get:
                return show(void_top_up_page(top_up(ident)))
            return go("/accounts/%d" % void_top_up(ident))
        known = ("", "export.json", "day", "items/N/available", "accounts/N", "accounts/N/topup", "accounts/N/payout", "sales/N")
        if shape in known:
            return self.answer(405, page("Not done", '<p class="refused">This address is not used that way.</p>'))
        raise Refused("There is no such page.", 404)


def main():
    global DB, TODAY
    parser = argparse.ArgumentParser(description="The till of a school canteen, on localhost.")
    parser.add_argument("--db", default="canteen.db", help="the one SQLite file that holds everything")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--sample", action="store_true", help="fill an empty file with a small menu and a few accounts")
    parser.add_argument("--today", type=a_day_arg, help="start the till on another day, written YYYY-MM-DD")
    args = parser.parse_args()
    TODAY = args.today
    DB = sqlite3.connect(args.db)
    DB.row_factory = sqlite3.Row
    DB.executescript(SCHEMA)
    if args.sample:
        sample()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print("The canteen till is at http://127.0.0.1:%d/ (Ctrl+C stops it)" % args.port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


def a_day_arg(text):
    try:
        return a_day(text)
    except Refused as error:
        raise argparse.ArgumentTypeError(error.why)


if __name__ == "__main__":
    main()

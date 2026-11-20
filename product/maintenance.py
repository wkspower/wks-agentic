#!/usr/bin/env python3
"""Maintenance requests of one apartment building, for its staff at one desk.

    python3 product/maintenance.py [--db FILE] [--port N] [--sample] [--today YYYY-MM-DD]

A web app on localhost, on Python's standard library and one SQLite file.
What it must do is in lessons/1301 to 1309 and the lessons its labels switch on.
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

CATEGORIES = ["plumbing", "electrical", "heating", "appliance", "doors and windows", "pests", "other"]
PRIORITIES = ["urgent", "normal", "low"]
DAYS = {"urgent": 1, "normal": 7, "low": 30}
KINDS = ["apartment", "area"]
OPEN, CLOSED = ("open", "in progress"), ("done", "cancelled")
CHANGES = {"start": (("open",), "in progress", "started"), "done": (OPEN, "done", "done"),
           "cancel": (OPEN, "cancelled", "cancelled"), "reopen": (CLOSED, "open", "reopened")}
BUTTONS = {"start": "Start", "done": "Done", "cancel": "Cancel", "reopen": "Reopen"}
LIMIT, FORM_BYTES = 200, 65536
NAV = [("/", "Desk"), ("/requests", "Requests"), ("/overdue", "Overdue"), ("/closed", "Closed"),
       ("/places", "Places"), ("/workers", "Workers")]
TYPED = "Go back to the form: what you typed is still there."
SCHEMA = """
create table if not exists places (id integer primary key, kind text not null, name text not null,
  floor integer, active integer not null default 1);
create table if not exists workers (id integer primary key, name text not null, trade text not null,
  phone text not null, active integer not null default 1);
create table if not exists requests (id integer primary key, place_id integer not null references places(id),
  category text not null, priority text not null, description text not null, reporter text not null,
  phone text not null, may_enter integer not null, state text not null, worker_id integer references workers(id),
  reported text not null, due text not null, closed text);
create table if not exists events (id integer primary key, request_id integer not null references requests(id),
  day text not null, what text not null, detail text not null default '', note text not null default '');
"""
CSS = """
*{box-sizing:border-box}
body{margin:0;font:16px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;color:#1c2330;background:#f3f4f6}
nav{display:flex;flex-wrap:wrap;gap:4px 18px;padding:10px 16px;background:#1f3a5f}
nav a{color:#fff;text-decoration:none;white-space:nowrap;padding:2px 0}
nav a.here{font-weight:700;border-bottom:2px solid #fff}
.day{margin:0;padding:6px 16px;background:#b3261e;color:#fff}
main{padding:16px;max-width:1160px;margin:0 auto}
h1,h2{overflow-wrap:anywhere} h1{font-size:24px;margin:4px 0 12px} h2{font-size:18px;margin:22px 0 8px}
p,dd,dt,li{overflow-wrap:anywhere} a{color:#1a56a8}
.count{color:#4a5361} .late{color:#b3261e;font-weight:700}
.tag{display:inline-block;padding:0 7px;border-radius:9px;font-size:13px;background:#e3e7ee;white-space:nowrap}
.tag.urgent{background:#b3261e;color:#fff} .tag.low{background:#eef0f3;color:#4a5361}
.off{color:#6b7380}
.tiles{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 6px;padding:0;list-style:none}
.tiles a{display:block;min-width:130px;padding:10px 14px;background:#fff;border:1px solid #d5d9e0;border-radius:8px;text-decoration:none;color:inherit}
.tiles b{display:block;font-size:26px}
dl{display:grid;grid-template-columns:minmax(90px,max-content) 1fr;gap:4px 14px;margin:0 0 12px;padding:12px 14px;background:#fff;border:1px solid #d5d9e0;border-radius:8px}
dt{color:#4a5361} dd{margin:0;min-width:0}
.text{white-space:pre-wrap}
form.card{display:grid;gap:10px;max-width:600px;margin:0 0 14px;padding:14px;background:#fff;border:1px solid #d5d9e0;border-radius:8px}
form.card label{display:grid;gap:3px;font-size:14px;color:#3b4350;min-width:0}
form.card.find{grid-template-columns:repeat(auto-fit,minmax(150px,1fr));max-width:none;align-items:end}
input,select,textarea{font:inherit;width:100%;min-width:0;padding:7px 8px;border:1px solid #9aa3b0;border-radius:6px;background:#fff;color:inherit}
textarea{min-height:92px;resize:vertical}
.row{display:flex;flex-wrap:wrap;gap:8px;min-width:0}
button{font:inherit;white-space:nowrap;padding:7px 14px;border:1px solid #1f3a5f;border-radius:6px;background:#1f3a5f;color:#fff;cursor:pointer}
button.quiet,td button{background:#fff;color:#1f3a5f}
td button,td a.open{font-size:14px;padding:3px 9px}
td a.open{display:inline-block;border:1px solid transparent;white-space:nowrap}
form.inline{display:inline}
input:focus,select:focus,textarea:focus,button:focus,a:focus{outline:3px solid #f0a500;outline-offset:1px}
.scroll{overflow-x:auto;background:#fff;border:1px solid #d5d9e0;border-radius:8px;margin:0 0 14px}
table{border-collapse:collapse;width:100%}
th,td{padding:8px 7px;text-align:left;vertical-align:top;border-bottom:1px solid #e6e8ec}
th{font-size:13px;color:#4a5361;white-space:nowrap;background:#f8f9fb}
tbody tr:last-child td{border-bottom:0}
td.words{min-width:150px;overflow-wrap:anywhere} td.wide{min-width:230px}
td.num,td.st,td.act{white-space:nowrap}
td.act,th.act{position:sticky;right:0;background:#fff;box-shadow:-1px 0 0 #d5d9e0} th.act{background:#f8f9fb}
td.act>*{margin-right:3px}
@media (max-width:720px){
 .scroll{overflow-x:visible;background:none;border:0}
 table,tbody,tr,td{display:block} thead{display:none}
 tr{margin:0 0 12px;padding:6px 12px;background:#fff;border:1px solid #d5d9e0;border-radius:8px}
 td{border:0;padding:4px 0;min-width:0}
 td::before{content:attr(data-th);display:block;font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:#5b6472}
 td:empty{display:none}
 td.act{position:static;white-space:normal;box-shadow:none;padding-top:8px}
 td.act>*{margin:0 6px 4px 0} td button,td a.open{font-size:16px;padding:6px 12px}
 dl{grid-template-columns:1fr} dt{margin-top:6px;font-size:13px}
}
@media (prefers-color-scheme:dark){
 body{background:#14181f;color:#e6e9ee} a{color:#8ab4f8} .count,dt,th,.off{color:#aab2bf}
 .scroll,form.card,dl,.tiles a,td.act,input,select,textarea{background:#1e242d;border-color:#39424f}
 th,th.act{background:#232a34} th,td{border-color:#39424f} form.card label{color:#c3cad5}
 button{background:#8ab4f8;border-color:#8ab4f8;color:#14181f} button.quiet,td button{background:#1e242d;color:#8ab4f8}
 .tag{background:#39424f} .tag.low{background:#2a313b;color:#aab2bf} .late{color:#ff8a80}
 td.act{box-shadow:-1px 0 0 #39424f}
}
@media (prefers-color-scheme:dark) and (max-width:720px){.scroll{background:none} tr{background:#1e242d;border-color:#39424f}}
"""


class Refused(Exception):
    """What was sent is not accepted. Nothing is stored."""

    def __init__(self, why, status=400, typed=True):
        super().__init__(why)
        self.why, self.status, self.typed = why, status, typed


e = html.escape


def after(day, days):
    return (datetime.date.fromisoformat(day) + datetime.timedelta(days=days)).isoformat()


def between(first, second):
    return (datetime.date.fromisoformat(second) - datetime.date.fromisoformat(first)).days


# What a form sent, read against the bounds of lessons/1309.

def text(form, name, low, high, what):
    value = form.get(name, "").strip()
    if not low <= len(value) <= high:
        raise Refused("%s must be %s characters; this one has %d." % (
            what, "%d to %d" % (low, high) if low != high else str(low), len(value)))
    return value


def choice(form, name, options, what):
    value = form.get(name, "")
    if value not in options:
        raise Refused("%s must be chosen: %s." % (what, ", ".join(options)))
    return value


def number(form, name, what):
    value = form.get(name, "").strip()
    if not (value.isascii() and value.isdigit() and len(value) <= 9):
        raise Refused("%s is named by a number of at most 9 digits." % what)
    return int(value)


def phone(form):
    value = text(form, "phone", 3, 20, "The phone")
    if not all(sign in "0123456789 +-()." for sign in value):
        raise Refused("The phone may hold digits, spaces and + - ( ) . only.")
    return value


def floor(form, needed):
    value = form.get("floor", "").strip()
    if value == "" and not needed:
        return None
    if not (re.fullmatch(r"-?[0-9]{1,3}", value) and -5 <= int(value) <= 200):
        raise Refused("The floor is a whole number from -5 to 200" + ("." if needed else ", or empty for a common area."))
    return int(value)


def yes_no(form, name, what):
    return choice(form, name, ["1", "0"], what) == "1"


class App:
    def __init__(self, path, today=None):
        self.path, self.fixed, self.lock = path, today, threading.Lock()
        with self.open() as db:
            db.executescript(SCHEMA)

    def open(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute("pragma foreign_keys = on")
        return db

    def today(self):
        return self.fixed or datetime.date.today().isoformat()

    # Reading

    def requests(self, db, where="1", args=(), order="r.id"):
        return db.execute(
            "select r.*, p.kind as place_kind, p.name as place_name, w.name as worker_name from requests r "
            "join places p on p.id = r.place_id left join workers w on w.id = r.worker_id where %s order by %s"
            % (where, order), args).fetchall()

    def one(self, db, table, ident):
        row = db.execute("select * from %s where id = ?" % table, (ident,)).fetchone()
        if row is None:
            raise Refused("There is no such page.", 404, typed=False)
        return row

    def export(self, db):
        def rows(table, flags=()):
            out = []
            for row in db.execute("select * from %s order by id" % table):
                row = dict(row)
                for flag in flags:
                    row[flag] = bool(row[flag])
                out.append(row)
            return out
        return {"today": self.today(), "places": rows("places", ["active"]), "workers": rows("workers", ["active"]),
                "requests": rows("requests", ["may_enter"]), "events": rows("events")}

    # Writing

    def event(self, db, request, what, detail="", note=""):
        db.execute("insert into events (request_id, day, what, detail, note) values (?, ?, ?, ?, ?)",
                   (request, self.today(), what, detail, note))

    def place_fields(self, db, form, mine=None):
        kind = choice(form, "kind", KINDS, "Apartment or common area")
        name = (text(form, "name", 1, 10, "An apartment number") if kind == "apartment"
                else text(form, "name", 1, 60, "The name of a common area"))
        level = floor(form, kind == "apartment")
        for row in db.execute("select id, name from places"):
            if row["name"].casefold() == name.casefold() and row["id"] != mine:
                raise Refused("There is already a place called %s." % row["name"])
        return kind, name, level

    def request_fields(self, db, form, current=None):
        place = db.execute("select * from places where id = ?", (number(form, "place_id", "The place"),)).fetchone()
        if place is None:
            raise Refused("There is no such place.")
        if not place["active"] and (current is None or current["place_id"] != place["id"]):
            raise Refused("%s is inactive and takes no request." % place_name(place))
        return (place["id"], choice(form, "category", CATEGORIES, "The category"),
                choice(form, "priority", PRIORITIES, "The priority"),
                text(form, "description", 1, 1000, "The description"), text(form, "reporter", 1, 60, "The reporter's name"),
                phone(form), int(yes_no(form, "may_enter", "Whether staff may enter when nobody is home")))

    def post(self, path, form):
        """Make the change a form asks for and return the address to show next."""
        with self.lock, self.open() as db:
            if path == "/places":
                made = db.execute("insert into places (kind, name, floor) values (?, ?, ?)", self.place_fields(db, form))
                return "/places/%d" % made.lastrowid
            if path == "/workers":
                db.execute("insert into workers (name, trade, phone) values (?, ?, ?)", (
                    text(form, "name", 1, 60, "The worker's name"), text(form, "trade", 0, 40, "The trade"), phone(form)))
                return "/workers"
            if path == "/requests":
                fields = self.request_fields(db, form)
                today = self.today()
                made = db.execute(
                    "insert into requests (place_id, category, priority, description, reporter, phone, may_enter, state, "
                    "reported, due) values (?, ?, ?, ?, ?, ?, ?, 'open', ?, ?)",
                    fields + (today, after(today, DAYS[fields[2]]))).lastrowid
                self.event(db, made, "reported")
                return "/requests/%d" % made
            found = re.fullmatch(r"/(places|workers|requests)/(\d{1,9})/(\w+)", path)
            if not found:
                raise Refused("There is no such page.", 404, typed=False)
            table, ident, verb = found.group(1), int(found.group(2)), found.group(3)
            row = self.one(db, table, ident)
            if verb == "edit" and table == "places":
                fields = self.place_fields(db, form, mine=ident)
                active = int(yes_no(form, "active", "Active or inactive"))
                db.execute("update places set kind = ?, name = ?, floor = ?, active = ? where id = ?", fields + (active, ident))
                return "/places/%d" % ident
            if verb == "edit" and table == "workers":
                db.execute("update workers set name = ?, trade = ?, phone = ?, active = ? where id = ?", (
                    text(form, "name", 1, 60, "The worker's name"), text(form, "trade", 0, 40, "The trade"), phone(form),
                    int(yes_no(form, "active", "Active or inactive")), ident))
                return "/workers/%d" % ident
            if table != "requests":
                raise Refused("There is no such page.", 404, typed=False)
            at = "/requests/%d" % ident
            if verb == "edit":
                names = ("place_id", "category", "priority", "description", "reporter", "phone", "may_enter")
                fields = self.request_fields(db, form, current=row)
                changed = [name.replace("_id", "").replace("_", " ") for name, value in zip(names, fields) if row[name] != value]
                if changed:
                    db.execute("update requests set place_id = ?, category = ?, priority = ?, description = ?, reporter = ?, "
                               "phone = ?, may_enter = ?, due = ? where id = ?",
                               fields + (after(row["reported"], DAYS[fields[2]]), ident))
                    self.event(db, ident, "corrected", ", ".join(changed))
                return at
            if verb == "note":
                self.event(db, ident, "note", note=text(form, "note", 1, 500, "A note"))
                return at
            if verb == "assign":
                if row["state"] in CLOSED:
                    raise Refused("Request #%d is %s. Reopen it to give it to someone." % (ident, row["state"]), typed=False)
                if form.get("worker_id", "") == "":
                    worker, name = None, "nobody"
                else:
                    who = db.execute("select * from workers where id = ?", (number(form, "worker_id", "The worker"),)).fetchone()
                    if who is None:
                        raise Refused("There is no such worker.", typed=False)
                    if not who["active"] and who["id"] != row["worker_id"]:
                        raise Refused("%s is inactive and is given nothing new." % who["name"], typed=False)
                    worker, name = who["id"], who["name"]
                if worker != row["worker_id"]:
                    db.execute("update requests set worker_id = ? where id = ?", (worker, ident))
                    self.event(db, ident, "assigned", "to " + name)
                return at
            if verb in CHANGES:
                before, state, what = CHANGES[verb]
                note = text(form, "note", 0, 500, "A note")
                if row["state"] not in before:
                    raise Refused("Request #%d is %s, so it cannot be %s. Nothing was changed." % (ident, row["state"], what),
                                  typed=False)
                db.execute("update requests set state = ?, closed = ? where id = ?",
                           (state, self.today() if state in CLOSED else None, ident))
                self.event(db, ident, what, note=note)
                return at
            raise Refused("There is no such page.", 404, typed=False)

    def sample(self):
        """A 24-apartment building with some of everything, into an empty file only."""
        with self.lock, self.open() as db:
            if db.execute("select count(*) from places").fetchone()[0]:
                return False
            today = self.today()
            for level in range(1, 7):
                for door in "ABCD":
                    db.execute("insert into places (kind, name, floor) values ('apartment', ?, ?)", ("%d%s" % (level, door), level))
            for name, level in [("Lobby", 0), ("Lift", None), ("Stairwell", None), ("Roof", 7), ("Car park", -1), ("Laundry room", -1)]:
                db.execute("insert into places (kind, name, floor) values ('area', ?, ?)", (name, level))
            for name, trade, number_ in [("Joe Pipe", "plumber", "555 0199"), ("Eve Volt", "electrician", "555 0188"),
                                         ("Sam Okoro", "caretaker", "555 0100"), ("Warmworks Ltd", "heating contractor", "(555) 010-2030")]:
                db.execute("insert into workers (name, trade, phone) values (?, ?, ?)", (name, trade, number_))
            wanted = [  # place, category, priority, description, reporter, phone, may enter, days ago, state, worker, days open
                (10, "plumbing", "urgent", "Water is coming through the bathroom ceiling from the flat above.", "Maria Souza", "555 0142", 1, 0, "open", 1, 0),
                (26, "electrical", "urgent", "Lift stops between floors 3 and 4 and the alarm button does nothing.", "Sam Okoro", "555 0100", 1, 3, "in progress", 2, 0),
                (3, "heating", "normal", "Bedroom radiator stays cold. The others are fine.", "Bo Li", "555 0117", 0, 9, "in progress", 4, 0),
                (14, "appliance", "normal", "Oven door does not close fully.", "Chidi Ene", "555 0163", 1, 2, "open", None, 0),
                (14, "plumbing", "low", "Kitchen tap drips.", "Chidi Ene", "555 0163", 1, 2, "open", None, 0),
                (25, "doors and windows", "normal", "Front door closer slams; it wakes the ground floor.", "Ana Lima", "555 0101", 1, 5, "open", 3, 0),
                (29, "electrical", "low", "Two lights out on level -1, by the ramp.", "Sam Okoro", "555 0100", 1, 40, "open", 2, 0),
                (21, "pests", "normal", "Ants in the kitchen, coming in under the window.", "Tariq Aziz", "555 0155", 0, 1, "open", None, 0),
                (7, "plumbing", "normal", "Toilet keeps running after flushing.", "Ines Prado", "555 0128", 1, 12, "done", 1, 2),
                (18, "heating", "urgent", "No heating or hot water at all.", "Olu Ade", "555 0171", 1, 20, "done", 4, 1),
                (2, "other", "low", "Name on the intercom is wrong.", "Li Wei", "555 0139", 1, 15, "cancelled", None, 1),
                (30, "appliance", "normal", "Dryer 2 takes coins and does not start.", "Ana Lima", "555 0101", 1, 6, "done", 3, 3),
            ]
            for place, category, priority, description, reporter, number_, enter, ago, state, worker, took in wanted:
                reported = after(today, -ago)
                closed = after(reported, took) if state in CLOSED else None
                made = db.execute(
                    "insert into requests (place_id, category, priority, description, reporter, phone, may_enter, state, worker_id, "
                    "reported, due, closed) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (place, category, priority, description, reporter, number_, enter, state, worker, reported,
                     after(reported, DAYS[priority]), closed)).lastrowid
                history = [(reported, "reported", "", "")]
                if worker:
                    history.append((reported, "assigned", "to " + db.execute("select name from workers where id = ?", (worker,)).fetchone()[0], ""))
                if state == "in progress":
                    history.append((after(reported, 1), "started", "", "Part ordered" if category == "heating" else ""))
                if closed:
                    history.append((closed, state, "", "Tenant moved out" if state == "cancelled" else "Fixed and tested"))
                for day, what, detail, note in history:
                    db.execute("insert into events (request_id, day, what, detail, note) values (?, ?, ?, ?, ?)", (made, day, what, detail, note))
            return True

    # Pages

    def page(self, path, query):
        with self.lock, self.open() as db:
            if path == "/export.json":
                return json.dumps(self.export(db), indent=1), "application/json"
            for pattern, make in [
                    ("/", self.desk), ("/requests", self.request_list), ("/overdue", self.overdue), ("/closed", self.closed),
                    ("/places", self.place_list), ("/workers", self.worker_list), (r"/requests/(\d{1,9})", self.request_page),
                    (r"/requests/(\d{1,9})/edit", self.request_edit), (r"/places/(\d{1,9})", self.place_page),
                    (r"/places/(\d{1,9})/edit", self.place_edit), (r"/workers/(\d{1,9})", self.worker_page),
                    (r"/workers/(\d{1,9})/edit", self.worker_edit)]:
                found = re.fullmatch(pattern, path)
                if found:
                    title, body = make(db, query, *[int(group) for group in found.groups()])
                    return self.frame(title, body, path), "text/html; charset=utf-8"
        if re.fullmatch(r"/(places|workers|requests)(/\d+/(edit|note|assign|start|done|cancel|reopen))?", path):
            raise Refused("This address only takes a form. Opening it changes nothing.", 405, typed=False)
        raise Refused("There is no such page.", 404, typed=False)

    def frame(self, title, body, path=""):
        links = "".join('<a href="%s"%s>%s</a>' % (where, ' class="here"' if where == path else "", name) for where, name in NAV)
        day = ('<p class="day">Started with --today: every date here is counted from %s, not from this machine\'s clock.</p>'
               % e(self.fixed)) if self.fixed else ""
        return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, '
                'initial-scale=1"><title>%s · Maintenance</title><style>%s</style></head><body><nav>%s</nav>%s<main><h1>%s</h1>%s'
                '</main></body></html>' % (e(title), CSS, links, day, e(title), body))

    def late(self, row):
        """Days past its day due, for a request that is not closed; 0 when it is not overdue."""
        return max(0, between(row["due"], self.today())) if row["state"] in OPEN else 0

    def table(self, rows, back, closed=False, none="None."):
        """A list of requests. Every link and button of a row is in its last cell."""
        if not rows:
            return '<p class="count">%s</p>' % e(none)
        out = []
        for row in rows:
            short = row["description"] if len(row["description"]) <= 90 else row["description"][:89] + "…"
            due = e(row["closed"] or "") if closed else e(row["due"]) + (' <b class="late">+%d d</b>' % self.late(row) if self.late(row) else "")
            acts = '<a class="open" href="/requests/%d">Open</a>' % row["id"] + "".join(
                '<form class="inline" method="post" action="/requests/%d/%s"><input type="hidden" name="back" value="%s">'
                '<button type="submit">%s</button></form>' % (row["id"], verb, e(back), BUTTONS[verb])
                for verb in CHANGES if row["state"] in CHANGES[verb][0])
            out.append(
                '<tr><td class="words wide" data-th="Request">#%d <span class="tag %s">%s</span> %s: %s</td>'
                '<td class="words" data-th="Place">%s</td><td class="num" data-th="%s">%s</td><td class="st" data-th="State">%s</td>'
                '<td class="words" data-th="Worker">%s</td><td class="act" data-th="Actions">%s</td></tr>'
                % (row["id"], row["priority"], row["priority"], e(row["category"].capitalize()), e(short),
                   e(place_name({"kind": row["place_kind"], "name": row["place_name"]})), "Closed" if closed else "Due", due,
                   e(row["state"]), e(row["worker_name"] or ""), acts))
        return ('<div class="scroll"><table><thead><tr><th>Request</th><th>Place</th><th>%s</th><th>State</th><th>Worker</th>'
                '<th class="act">Actions</th></tr></thead><tbody>%s</tbody></table></div>' % ("Closed" if closed else "Due", "".join(out)))

    def desk(self, db, query):
        rows = self.requests(db, "r.state in ('open', 'in progress')")
        tiles = [("/requests", sum(row["state"] == "open" for row in rows), "open"),
                 ("/requests", sum(row["state"] == "in progress" for row in rows), "in progress"),
                 ("/overdue", sum(self.late(row) > 0 for row in rows), "overdue")]
        urgent = [row for row in rows if row["priority"] == "urgent"]
        return "Desk", (
            '<ul class="tiles">%s</ul><h2>Record a new request</h2><p class="count">Find the apartment or common area; '
            'its page shows what is already open there, and the form.</p>%s<h2>Urgent</h2>%s<h2>Find a request</h2>%s'
            % ("".join('<li><a href="%s"><b>%d</b>%s</a></li>' % tile for tile in tiles), self.place_search(""),
               self.table(sorted(urgent, key=lambda row: (row["reported"], row["id"])), "/", none="Nothing urgent is open."),
               self.request_search(db, {})))

    def place_search(self, typed):
        return ('<form class="card find" method="get" action="/places"><label>Apartment number or name of the area'
                '<input name="q" maxlength="100" value="%s" placeholder="12B or Lobby"></label>'
                '<div class="row"><button type="submit">Find place</button></div></form>' % e(typed))

    def request_search(self, db, query):
        places = [(str(row["id"]), place_name(row)) for row in self.places(db)]
        return ('<form class="card find" method="get" action="/requests"><label>Words in the description or the reporter\'s name'
                '<input name="q" maxlength="100" value="%s" placeholder="tap"></label><label>Place%s</label><label>Category%s</label>'
                '<label>State%s</label><div class="row"><button type="submit">Search</button></div></form>'
                % (e(query.get("q", "")), select("place_id", places, query.get("place_id", ""), "any place"),
                   select("category", [(word, word) for word in CATEGORIES], query.get("category", ""), "any category"),
                   select("state", [(word, word) for word in OPEN + CLOSED], query.get("state", ""), "any state")))

    def places(self, db):
        rows = db.execute("select * from places").fetchall()
        return sorted(rows, key=lambda row: (row["kind"], row["floor"] if row["floor"] is not None else 999, natural(row["name"])))

    def request_list(self, db, query):
        asked = {name: query.get(name, "").strip() for name in ("q", "place_id", "category", "state")}
        if not any(asked.values()):
            rows = self.requests(db, "r.state in ('open', 'in progress')")
            rows.sort(key=lambda row: (PRIORITIES.index(row["priority"]), row["reported"], row["id"]))
            return "Requests", (
                '<p class="count">%d open or in progress, urgent first and then the oldest. '
                'A new request is recorded on the page of its <a href="/places">place</a>.</p>%s<h2>Find a request</h2>%s'
                % (len(rows), self.table(rows, "/requests", none="Nothing is open."), self.request_search(db, {})))
        words = text(asked, "q", 0, 100, "The search text").casefold()
        where, args = ["1"], []
        if asked["place_id"]:
            where.append("r.place_id = ?")
            args.append(number(asked, "place_id", "The place"))
        if asked["category"]:
            where.append("r.category = ?")
            args.append(choice(asked, "category", CATEGORIES, "The category"))
        if asked["state"]:
            where.append("r.state = ?")
            args.append(choice(asked, "state", OPEN + CLOSED, "The state"))
        rows = [row for row in self.requests(db, " and ".join(where), args, "r.id desc")
                if words in row["description"].casefold() or words in row["reporter"].casefold()]
        return "Requests", (
            '%s<p class="count">%d matching %s%s, newest first. <a href="/requests">Back to what is open</a></p>%s'
            % (self.request_search(db, asked), len(rows), "request" if len(rows) == 1 else "requests",
               "; the first %d are shown" % LIMIT if len(rows) > LIMIT else "",
               self.table(rows[:LIMIT], "/requests?" + urllib.parse.urlencode(asked), none="No request matches.")))

    def overdue(self, db, query):
        rows = [row for row in self.requests(db, "r.state in ('open', 'in progress')") if self.late(row)]
        rows.sort(key=lambda row: (row["due"], PRIORITIES.index(row["priority"]), row["id"]))
        return "Overdue", ('<p class="count">%d overdue, the most overdue first. Urgent is due 1 day after it was reported, '
                           'normal 7, low 30.</p>%s' % (len(rows), self.table(rows, "/overdue", none="Nothing is overdue.")))

    def closed(self, db, query):
        count = db.execute("select count(*) from requests where state in ('done', 'cancelled')").fetchone()[0]
        rows = self.requests(db, "r.state in ('done', 'cancelled')", (), "r.closed desc, r.id desc limit %d" % LIMIT)
        return "Closed", ('<p class="count">%d closed %s, done or cancelled%s.</p>%s' % (
            count, "request" if count == 1 else "requests", "; the latest %d are shown" % LIMIT if count > LIMIT else "",
            self.table(rows, "/closed", closed=True, none="Nothing has been closed yet.")))

    def request_page(self, db, query, ident):
        row = self.requests(db, "r.id = ?", (ident,))
        if not row:
            raise Refused("There is no such page.", 404, typed=False)
        row = row[0]
        at = "/requests/%d" % ident
        due = e(row["due"]) + (' <b class="late">overdue by %d %s</b>' % (self.late(row), "day" if self.late(row) == 1 else "days")
                               if self.late(row) else "")
        facts = [("Place", '<a href="/places/%d">%s</a>' % (row["place_id"], e(place_name({"kind": row["place_kind"], "name": row["place_name"]})))),
                 ("Category", e(row["category"])), ("Priority", '<span class="tag %s">%s</span>' % (row["priority"], row["priority"])),
                 ("State", e(row["state"])), ("Reported", "%s by %s, %s" % (e(row["reported"]), e(row["reporter"]), e(row["phone"]))),
                 ("Due", due)] + ([("Closed", e(row["closed"]))] if row["closed"] else []) + [
                 ("May enter", "yes, when nobody is home" if row["may_enter"] else "<b>no</b>, only with someone home"),
                 ("Worker", e(row["worker_name"] or "nobody yet"))]
        buttons = "".join('<button type="submit" class="quiet" formaction="%s/%s">%s</button>' % (at, verb, BUTTONS[verb])
                          for verb in CHANGES if row["state"] in CHANGES[verb][0])
        change = ('<form class="card" method="post" action="%s/note"><label>Note, kept in the history; optional with a change of state'
                  '<input name="note" maxlength="500" placeholder="Waiting for a part"></label>'
                  '<div class="row"><button type="submit">Add note</button>%s</div></form>' % (at, buttons))
        give = ""
        if row["state"] in OPEN:
            workers = [(str(who["id"]), "%s (%s)" % (who["name"], who["trade"]) if who["trade"] else who["name"])
                       for who in db.execute("select * from workers order by name collate nocase, id")
                       if who["active"] or who["id"] == row["worker_id"]]
            give = ('<form class="card" method="post" action="%s/assign"><label>Worker%s</label>'
                    '<div class="row"><button type="submit">Give to this worker</button></div></form>'
                    % (at, select("worker_id", workers, str(row["worker_id"] or ""), "nobody")))
        history = "".join(
            '<tr><td class="num" data-th="Day">%s</td><td class="st" data-th="What">%s</td><td class="words" data-th="Note">%s</td></tr>'
            % (e(event["day"]), e(event["what"]), e(" · ".join(part for part in (event["detail"], event["note"]) if part)))
            for event in db.execute("select * from events where request_id = ? order by id", (ident,)))
        return "Request #%d" % ident, (
            '<p class="text">%s</p><dl>%s</dl>%s%s<p><a href="%s/edit">Correct this request</a></p><h2>History</h2>'
            '<div class="scroll"><table><thead><tr><th>Day</th><th>What</th><th>Note</th></tr></thead><tbody>%s</tbody></table></div>'
            % (e(row["description"]), "".join("<dt>%s</dt><dd>%s</dd>" % fact for fact in facts), change, give, at, history))

    def request_form(self, db, action, row=None, place=None):
        """The form for a new request of one place, or to correct a request."""
        new = row is None
        got = (lambda name: "") if new else (lambda name: str(row[name]))
        where = ('<input type="hidden" name="place_id" value="%d">' % place["id"] if new else "<label>Place%s</label>" % select(
            "place_id", [(str(one["id"]), place_name(one)) for one in self.places(db) if one["active"] or one["id"] == row["place_id"]],
            got("place_id")))
        return ('<form class="card" method="post" action="%s">%s<label>Category%s</label><label>Priority%s</label>'
                '<label>What is wrong<textarea name="description" maxlength="1000" required placeholder="Kitchen tap drips">%s</textarea></label>'
                '<label>Reported by<input name="reporter" maxlength="60" required value="%s" placeholder="Ana Lima"></label>'
                '<label>Their phone<input name="phone" maxlength="20" required value="%s" placeholder="555 0101"></label>'
                '<label>May staff enter when nobody is home?%s</label>'
                '<div class="row"><button type="submit">%s</button></div></form>'
                % (action, where, select("category", [(word, word) for word in CATEGORIES], got("category"), "choose" if new else None),
                   select("priority", [(word, "%s: due in %d %s" % (word, DAYS[word], "day" if DAYS[word] == 1 else "days")) for word in PRIORITIES],
                          got("priority"), "choose" if new else None),
                   e(got("description")), e(got("reporter")), e(got("phone")),
                   select("may_enter", [("1", "yes"), ("0", "no")], got("may_enter"), "choose" if new else None),
                   "Record request" if new else "Save correction"))

    def request_edit(self, db, query, ident):
        row = self.one(db, "requests", ident)
        return "Correct request #%d" % ident, (
            '<p class="count">Reported %s. Changing the priority moves the day due. <a href="/requests/%d">Back to the request</a></p>%s'
            % (e(row["reported"]), ident, self.request_form(db, "/requests/%d/edit" % ident, row=row)))

    def place_form(self, action, row=None):
        got = (lambda name: "") if row is None else (lambda name: "" if row[name] is None else str(row[name]))
        hint = (lambda example: ' placeholder="%s"' % example) if row is None else (lambda example: "")
        return ('<form class="card" method="post" action="%s"><label>Apartment or common area%s</label>'
                '<label>Apartment number (up to 10 characters) or name of the area<input name="name" maxlength="60" required value="%s"%s></label>'
                '<label>Floor, -5 to 200; may be empty for a common area<input name="floor" inputmode="numeric" maxlength="4" value="%s"%s></label>'
                '%s<div class="row"><button type="submit">%s</button></div></form>'
                % (action, select("kind", [("apartment", "apartment"), ("area", "common area")], got("kind"), "choose" if row is None else None),
                   e(got("name")), hint("12B"), e(got("floor")), hint("3"),
                   "" if row is None else "<label>Takes new requests%s</label>" % select(
                       "active", [("1", "active"), ("0", "inactive: takes no new request")], got("active")),
                   "Add place" if row is None else "Save correction"))

    def place_list(self, db, query):
        words = text(query, "q", 0, 100, "The search text")
        counts = dict(db.execute("select place_id, count(*) from requests where state in ('open', 'in progress') group by place_id").fetchall())
        rows = [row for row in self.places(db) if words.casefold() in row["name"].casefold()]
        shown = "".join(
            '<tr><td class="words" data-th="Place">%s</td><td class="num" data-th="Floor">%s</td><td class="num" data-th="Open requests">%d</td>'
            '<td class="st" data-th="Status">%s</td><td class="act" data-th="Actions"><a class="open" href="/places/%d">%s</a>'
            '<a class="open" href="/places/%d/edit">Edit</a></td></tr>'
            % (e(place_name(row)), "" if row["floor"] is None else row["floor"], counts.get(row["id"], 0),
               "active" if row["active"] else '<span class="off">inactive</span>', row["id"],
               "Open / new request" if row["active"] else "Open", row["id"]) for row in rows[:LIMIT])
        table = ('<div class="scroll"><table><thead><tr><th>Place</th><th>Floor</th><th>Open requests</th><th>Status</th>'
                 '<th class="act">Actions</th></tr></thead><tbody>%s</tbody></table></div>' % shown) if rows else ""
        said = ("%d %s matching “%s”" % (len(rows), "place" if len(rows) == 1 else "places", e(words)) if words
                else "%d %s" % (len(rows), "place" if len(rows) == 1 else "places"))
        return "Places", ('%s<p class="count">%s%s.</p>%s<h2>Add a place</h2>%s' % (
            self.place_search(words), said, "; the first %d are shown" % LIMIT if len(rows) > LIMIT else "", table, self.place_form("/places")))

    def place_page(self, db, query, ident):
        row = self.one(db, "places", ident)
        mine = self.requests(db, "r.place_id = ? and r.state in ('open', 'in progress')", (ident,))
        mine.sort(key=lambda one: (PRIORITIES.index(one["priority"]), one["reported"], one["id"]))
        closed = db.execute("select count(*) from requests where place_id = ? and state in ('done', 'cancelled')", (ident,)).fetchone()[0]
        form = ("<h2>Record a new request for %s</h2>%s" % (e(place_name(row)), self.request_form(db, "/requests", place=row)) if row["active"]
                else '<p class="off">This place is inactive and takes no new request. It is made active again on its Edit page.</p>')
        return place_name(row), (
            '<p class="count">%s%s. <a href="/places/%d/edit">Edit</a> · <a href="/requests?place_id=%d">All %d of its requests</a></p>'
            '<h2>Open here now</h2>%s%s'
            % ("Apartment" if row["kind"] == "apartment" else "Common area", "" if row["floor"] is None else ", floor %d" % row["floor"],
               ident, ident, closed + len(mine), self.table(mine, "/places/%d" % ident, none="Nothing is open for this place."), form))

    def place_edit(self, db, query, ident):
        row = self.one(db, "places", ident)
        return "Correct %s" % place_name(row), (
            '<p class="count">Nothing is ever removed: a place no longer in use is made inactive. '
            '<a href="/places/%d">Back to the place</a></p>%s' % (ident, self.place_form("/places/%d/edit" % ident, row)))

    def worker_form(self, action, row=None):
        got = (lambda name: "") if row is None else (lambda name: str(row[name]))
        return ('<form class="card" method="post" action="%s"><label>Name of the worker or contractor'
                '<input name="name" maxlength="60" required value="%s" placeholder="Joe Pipe"></label>'
                '<label>Trade (optional)<input name="trade" maxlength="40" value="%s" placeholder="plumber"></label>'
                '<label>Phone<input name="phone" maxlength="20" required value="%s" placeholder="555 0199"></label>'
                '%s<div class="row"><button type="submit">%s</button></div></form>'
                % (action, e(got("name")), e(got("trade")), e(got("phone")),
                   "" if row is None else "<label>Is given new requests%s</label>" % select(
                       "active", [("1", "active"), ("0", "inactive: is given nothing new")], got("active")),
                   "Add worker" if row is None else "Save correction"))

    def worker_list(self, db, query):
        counts = dict(db.execute("select worker_id, count(*) from requests where state in ('open', 'in progress') group by worker_id").fetchall())
        rows = db.execute("select * from workers order by active desc, name collate nocase, id").fetchall()
        shown = "".join(
            '<tr><td class="words" data-th="Name">%s</td><td class="words" data-th="Trade">%s</td><td class="num" data-th="Phone">%s</td>'
            '<td class="num" data-th="Holds">%d</td><td class="st" data-th="Status">%s</td><td class="act" data-th="Actions">'
            '<a class="open" href="/workers/%d">Open</a><a class="open" href="/workers/%d/edit">Edit</a></td></tr>'
            % (e(row["name"]), e(row["trade"]), e(row["phone"]), counts.get(row["id"], 0),
               "active" if row["active"] else '<span class="off">inactive</span>', row["id"], row["id"]) for row in rows)
        table = ('<div class="scroll"><table><thead><tr><th>Name</th><th>Trade</th><th>Phone</th><th>Holds</th><th>Status</th>'
                 '<th class="act">Actions</th></tr></thead><tbody>%s</tbody></table></div>' % shown) if rows else ""
        return "Workers", ('<p class="count">%d %s. “Holds” counts requests that are open or in progress.</p>%s<h2>Add a worker or contractor</h2>%s'
                           % (len(rows), "worker or contractor" if len(rows) == 1 else "workers and contractors", table, self.worker_form("/workers")))

    def worker_page(self, db, query, ident):
        row = self.one(db, "workers", ident)
        mine = self.requests(db, "r.worker_id = ? and r.state in ('open', 'in progress')", (ident,))
        mine.sort(key=lambda one: (PRIORITIES.index(one["priority"]), one["reported"], one["id"]))
        return row["name"], (
            '<p class="count">%s%s · %s. <a href="/workers/%d/edit">Edit</a></p><h2>Holds now</h2>%s'
            % (e(row["trade"] + " · " if row["trade"] else ""), e(row["phone"]),
               "active" if row["active"] else '<span class="off">inactive: is given nothing new</span>', ident,
               self.table(mine, "/workers/%d" % ident, none="Holds nothing that is open.")))

    def worker_edit(self, db, query, ident):
        row = self.one(db, "workers", ident)
        return "Correct %s" % row["name"], (
            '<p class="count">Nothing is ever removed: someone who no longer works for the building is made inactive. '
            '<a href="/workers/%d">Back to the worker</a></p>%s' % (ident, self.worker_form("/workers/%d/edit" % ident, row)))


def place_name(row):
    return ("Apt " if row["kind"] == "apartment" else "") + row["name"]


def natural(name):
    return [int(part) if part.isdigit() and part.isascii() else part.casefold() for part in re.split(r"(\d+)", name)], name


def select(name, options, current, empty=None):
    """A select. `empty` adds a first option with no value, chosen when nothing is current."""
    first = '<option value="">%s</option>' % ("— %s —" % e(empty)) if empty is not None else ""
    return '<select name="%s"%s>%s%s</select>' % (name, " required" if empty == "choose" else "", first, "".join(
        '<option value="%s"%s>%s</option>' % (e(value), " selected" if value == current else "", e(label)) for value, label in options))


class Handler(BaseHTTPRequestHandler):
    app = None
    server_version = "Maintenance"

    def log_message(self, *args):
        pass

    def answer(self, status, body, kind="text/html; charset=utf-8", location=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(data)

    def refuse(self, status, why, typed=False):
        title = {403: "Refused", 404: "Not found", 405: "Nothing to open here"}.get(status, "Not accepted")
        self.answer(status, self.app.frame(title, '<p>%s</p>%s' % (e(why), "<p>%s</p>" % TYPED if typed else "")))

    def own(self):
        """A request from another site, or to another host name, is refused (L0007)."""
        port = self.server.server_address[1]
        host = self.headers.get("Host", "")
        if host not in ("127.0.0.1:%d" % port, "localhost:%d" % port):
            return False
        if self.headers.get("Origin") not in (None, "http://" + host):
            return False
        return self.headers.get("Sec-Fetch-Site") in (None, "same-origin", "none")

    def do_GET(self):
        if not self.own():
            return self.refuse(403, "This request came from another site or names another host, and was refused.")
        parts = urllib.parse.urlsplit(self.path)
        query = {name: values[0] for name, values in urllib.parse.parse_qs(parts.query, keep_blank_values=True).items()}
        try:
            body, kind = self.app.page(parts.path, query)
        except Refused as refused:
            return self.refuse(refused.status, refused.why, refused.typed and refused.status == 400)
        self.answer(200, body, kind)

    def do_POST(self):
        length = self.headers.get("Content-Length", "")
        length = int(length) if length.isdigit() else 0
        sent = self.rfile.read(length) if length <= 16 * FORM_BYTES else b""
        if not self.own():
            return self.refuse(403, "This request came from another site or names another host, and was refused.")
        if length > FORM_BYTES:
            return self.refuse(400, "A form may be 65,536 bytes at most; this one was %d." % length)
        try:
            form = {name: values[0] for name, values in urllib.parse.parse_qs(
                sent.decode("utf-8"), keep_blank_values=True, strict_parsing=False, max_num_fields=100).items()}
            path = urllib.parse.urlsplit(self.path).path
            where = self.app.post(path, form)
        except Refused as refused:
            return self.refuse(refused.status, refused.why, refused.typed and refused.status == 400)
        except (ValueError, UnicodeDecodeError):
            return self.refuse(400, "The form could not be read.")
        back = form.get("back", "")
        if re.fullmatch(r"/requests/\d+/(start|done|cancel|reopen)", path) and re.fullmatch(r"/[a-z0-9/?=&%+._-]*", back) and not back.startswith("//"):
            where = back  # a button on a list returns to its list
        self.answer(303, "", location=where)

    def other(self):
        self.refuse(405, "Nothing here can be removed or replaced.")

    do_DELETE = do_PUT = do_PATCH = other


def main():
    parser = argparse.ArgumentParser(description="Maintenance requests of one apartment building.")
    parser.add_argument("--db", default="maintenance.db", help="the SQLite file that holds everything")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--sample", action="store_true", help="fill an empty file with a 24-apartment building")
    parser.add_argument("--today", type=lambda day: datetime.date.fromisoformat(day).isoformat(), metavar="YYYY-MM-DD",
                        help="count every date from this day, to see requests fall overdue")
    args = parser.parse_args()
    Handler.app = App(args.db, args.today)
    if args.sample:
        print("Sample building loaded." if Handler.app.sample() else "The file already holds a building; --sample changed nothing.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    print("Maintenance requests: http://127.0.0.1:%d/  (Ctrl+C stops it)" % args.port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

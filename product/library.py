#!/usr/bin/env python3
"""A lending library for a school, for the staff at one desk.

    python3 product/library.py [--db library.db] [--port 8000] [--sample] [--today YYYY-MM-DD]

then open http://127.0.0.1:8000/. The pages are the only way in; everything
is kept in one SQLite file; nothing outside Python's standard library is used.
"""
import argparse
import base64
import collections
import datetime
import hashlib
import html
import json
import re
import sqlite3
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOAN_DAYS = 14
RENEWALS = 2
LIMIT = {"pupil": 3, "staff": 10}
SHOWN = 200          # rows of a list that is searched; loans still out are never cut
FORM_BYTES = 65536
OPEN = "returned IS NULL AND lost IS NULL"   # a loan that is still out
NAV = [("/", "Desk"), ("/titles", "Catalogue"), ("/borrowers", "Borrowers"),
       ("/loans", "Loans"), ("/overdue", "Overdue"), ("/returned", "Returned")]

SCHEMA = """
CREATE TABLE IF NOT EXISTS titles (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
    author TEXT NOT NULL, isbn TEXT NOT NULL, shelf TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS copies (id INTEGER PRIMARY KEY AUTOINCREMENT, title_id INTEGER NOT NULL REFERENCES titles(id),
    status TEXT NOT NULL DEFAULT 'available' CHECK (status IN ('available', 'lost', 'withdrawn')));
CREATE TABLE IF NOT EXISTS borrowers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('pupil', 'staff')), class TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY AUTOINCREMENT, copy_id INTEGER NOT NULL REFERENCES copies(id),
    borrower_id INTEGER NOT NULL REFERENCES borrowers(id), lent TEXT NOT NULL, due TEXT NOT NULL,
    renewals INTEGER NOT NULL DEFAULT 0, returned TEXT, lost TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS one_loan_a_copy ON loans(copy_id) WHERE returned IS NULL AND lost IS NULL;
CREATE INDEX IF NOT EXISTS copies_of ON copies(title_id);
CREATE INDEX IF NOT EXISTS loans_of ON loans(borrower_id);
"""

CSS = """
:root{color-scheme:light dark;--bg:#faf9f5;--fg:#1c1c1a;--soft:#5d5c56;--line:#d6d3c9;--box:#fff;--link:#1b4f80;--bad:#9b1c1c;--badbg:#fdeaea}
@media (prefers-color-scheme:dark){:root{--bg:#17181b;--fg:#e9e7e1;--soft:#a5a39b;--line:#3b3d43;--box:#202226;--link:#93c0ea;--bad:#ffb3b3;--badbg:#4b1f1f}}
*{box-sizing:border-box}
body{margin:0;font:16px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg);overflow-wrap:anywhere}
a{color:var(--link)}
nav{display:flex;flex-wrap:wrap;gap:.2rem 1.1rem;padding:.6rem 1rem;background:var(--box);border-bottom:1px solid var(--line)}
nav a{white-space:nowrap;text-decoration:none;font-weight:600}
nav a.here{color:var(--fg);text-decoration:underline}
main{max-width:76rem;margin:0 auto;padding:1rem}
h1{font-size:1.5rem;margin:.2rem 0 .8rem}
h2{font-size:1.1rem;margin:1.4rem 0 .5rem}
.soft{color:var(--soft)}
.notice,.late{color:var(--bad)}
.notice{background:var(--badbg);border:1px solid var(--bad);border-radius:6px;padding:.5rem .75rem}
form.card{display:flex;flex-wrap:wrap;gap:.5rem .75rem;align-items:flex-end;background:var(--box);border:1px solid var(--line);border-radius:6px;padding:.75rem;margin:0 0 1rem}
form.card label{display:flex;flex-direction:column;flex:1 1 9rem;min-width:0;font-size:.85rem;color:var(--soft)}
form.card label.wide{flex-basis:16rem}
form.card label.short{flex:0 1 7rem}
input,select,button{font:inherit;max-width:100%}
input,select{width:100%;padding:.4rem .5rem;border:1px solid var(--line);border-radius:4px;background:var(--bg);color:var(--fg)}
button{white-space:nowrap;padding:.4rem .8rem;border:1px solid var(--link);border-radius:4px;background:var(--link);color:var(--bg);cursor:pointer}
.scroll{overflow-x:auto;margin:0 0 1rem}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;vertical-align:top;padding:.45rem .4rem;border-bottom:1px solid var(--line)}
th{font-size:.85rem;color:var(--soft);white-space:nowrap}
td{min-width:150px;overflow-wrap:break-word}
td.num,td.short{min-width:0;white-space:nowrap}
td.act{min-width:0}
td.act,th.act{position:sticky;right:0;background:var(--bg)}
td.act span{display:inline-block;white-space:nowrap}
td.act form{display:inline-block;margin:0}
td.act span>*{margin:0 .4rem .2rem 0}
td.act button{padding:.15rem .55rem}
td a{white-space:nowrap}
@media (min-width:761px) and (max-width:999px){.gone{display:none}}
@media (max-width:760px){
.scroll{overflow:visible}
table,tbody,tr,td{display:block}
thead{display:none}
tr{background:var(--box);border:1px solid var(--line);border-radius:6px;margin:0 0 .75rem;padding:.4rem .7rem}
td{min-width:0;border:0;padding:.2rem 0;overflow-wrap:anywhere}
td::before{content:attr(data-label);display:block;font-size:.75rem;color:var(--soft)}
td.short{white-space:normal}
td.empty{display:none}
td.act{position:static;background:none;display:flex;flex-wrap:wrap;gap:.45rem;align-items:center;padding-top:.45rem}
td.act span{display:contents}
td.act span>*{margin:0}
td.act button{padding:.35rem .8rem}
}
"""

# A field that is scanned into comes back empty and focused, however the browser brings the page back.
SCRIPT = ('addEventListener("pageshow",function(){var f=document.querySelector("input[data-scan]");'
          'if(f){f.value="";f.focus()}})')
POLICY = ("default-src 'none'; style-src 'self'; script-src 'sha256-%s'; form-action 'self'; base-uri 'none'; "
          "frame-ancestors 'none'" % base64.b64encode(hashlib.sha256(SCRIPT.encode()).digest()).decode())

KEPT = "Go back to the form: what you typed is still there."
SCAN = "Go back: the copy field is empty again, ready for the next book."


class Refused(Exception):
    """What was asked cannot stand. Nothing was changed; the page says why."""

    def __init__(self, why, then="", status=400):
        super().__init__(why)
        self.why, self.then, self.status = why, then, status


def fold(text):
    """Capitals do not count, for any letter that has one."""
    return (text or "").lower()


def e(value):
    return html.escape(str(value), quote=True)


def plural(number, one, many=None):
    return "%d %s" % (number, one if number == 1 else (many or one + "s"))


# ---- what is typed, and its bounds -----------------------------------------------------------

def text(form, name, most, what, least=0):
    value = form.get(name, "").strip()
    if len(value) < least:
        raise Refused("%s is missing." % what, KEPT)
    if len(value) > most:
        raise Refused("%s is %d characters long; the most is %d." % (what, len(value), most), KEPT)
    return value


def whole(value, what, then=KEPT):
    """Digits only, nine at most: a count or a number the library gave."""
    value = value.strip()
    if not re.fullmatch(r"[0-9]{1,9}", value):
        raise Refused("%s must be a whole number written in digits." % what, then)
    return int(value)


def title_fields(form):
    isbn = form.get("isbn", "").strip().replace("-", "")
    if isbn and not re.fullmatch(r"[0-9]{13}|[0-9]{9}[0-9Xx]", isbn):
        raise Refused("The ISBN must be 10 or 13 digits, with or without hyphens (the last of 10 may be X), or left empty.", KEPT)
    return (text(form, "title", 200, "The title", least=1), text(form, "author", 120, "The author"),
            isbn.upper(), text(form, "shelf", 20, "The shelf mark"))


def copies_asked(form):
    number = whole(form.get("copies", ""), "The number of copies")
    if not 1 <= number <= 50:
        raise Refused("The number of copies must be from 1 to 50.", KEPT)
    return number


def borrower_fields(form):
    kind = form.get("kind", "")
    if kind not in LIMIT:
        raise Refused("Choose pupil or staff.", KEPT)
    return text(form, "name", 80, "The name", least=1), kind, text(form, "class", 20, "The class")


def search_text(query):
    typed = query.get("q", "").strip()
    if len(typed) > 100:
        raise Refused("The search text is %d characters long; the most is 100." % len(typed))
    return typed


# ---- the pages ------------------------------------------------------------------------------

class Library:
    def __init__(self, path, today=None):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.create_function("fold", 1, fold, deterministic=True)
        self.db.execute("PRAGMA foreign_keys = ON")
        with self.db:
            self.db.executescript(SCHEMA)
        self.pretend = today
        self.lock = threading.Lock()

    def today(self):
        return self.pretend or datetime.date.today().isoformat()

    def after(self, days):
        return (datetime.date.fromisoformat(self.today()) + datetime.timedelta(days=days)).isoformat()

    def one(self, sql, *args):
        return self.db.execute(sql, args).fetchone()

    def all(self, sql, *args):
        return self.db.execute(sql, args).fetchall()

    def need(self, table, ident, what):
        row = self.one("SELECT * FROM %s WHERE id = ?" % table, int(ident))
        if row is None:
            raise Refused("There is no %s %s." % (what, ident), status=404)
        return row

    # -- writing a page

    def page(self, name, body, status=200):
        nav = "".join('<a href="%s"%s>%s</a>' % (path, ' class="here"' if label == name else "", label) for path, label in NAV)
        notice = ('<p class="notice">Started with --today: this library takes today to be %s, not the day on the clock.</p>'
                  % e(self.pretend)) if self.pretend else ""
        return status, "text/html; charset=utf-8", (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>%s · School library</title>'
            '<link rel="stylesheet" href="/style.css"></head><body><nav>%s</nav><main>%s%s</main><script>%s</script></body></html>'
            % (e(name), nav, notice, body, SCRIPT))

    def refusal(self, refused):
        head = {400: "Not done", 403: "Refused", 404: "Not found", 405: "Not a page", 413: "Too much"}.get(refused.status, "Not done")
        then = '<p class="soft">%s</p>' % e(refused.then) if refused.then else ""
        return self.page(head, "<h1>%s</h1><p>%s</p>%s" % (head, e(refused.why), then), refused.status)

    @staticmethod
    def table(heads, rows):
        """A list: a table on a wide screen, and one card a row on a narrow one, each field under the name of its column."""
        if not rows:
            return ""
        out = ['<div class="scroll"><table><thead><tr>']
        out += ['<th%s>%s</th>' % (' class="%s"' % kind if kind else "", e(head)) for head, kind in heads]
        out.append("</tr></thead><tbody>")
        for ident, cells in rows:
            out.append("<tr%s>" % (' id="%s"' % ident if ident else ""))
            for (head, kind), cell in zip(heads, cells):
                kinds = " ".join(word for word in (kind, "" if cell != "" else "empty") if word)
                out.append('<td%s data-label="%s">%s</td>' % (' class="%s"' % kinds if kinds else "", e(head), cell))
            out.append("</tr>")
        out.append("</tbody></table></div>")
        return "".join(out)

    @staticmethod
    def acts(*groups):
        """The buttons and links of a row. Each group stays on one line; the groups may stand one under another."""
        return " ".join("<span>%s</span>" % " ".join(group) for group in groups if group)

    @staticmethod
    def button(action, label, **hidden):
        fields = "".join('<input type="hidden" name="%s" value="%s">' % (name, e(value)) for name, value in hidden.items())
        return '<form method="post" action="%s">%s<button type="submit">%s</button></form>' % (action, fields, label)

    @staticmethod
    def search(action, example, label, typed=""):
        return ('<form class="card" method="get" action="%s"><label class="wide">%s <input name="q" value="%s" '
                'placeholder="%s"></label><button type="submit">Search</button></form>' % (action, label, e(typed), e(example)))

    def shown(self, total, rows, one, typed, many=None):
        """The sentence above a searched list: how many there are, and how many of them are on the page."""
        what = plural(total, one, many) + (" matching “%s”" % e(typed) if typed else "")
        if total > len(rows):
            what = "Showing the first %d of %s" % (len(rows), what)
        return '<p class="soft">%s.</p>' % what

    # -- the desk

    def desk(self, query):
        out = self.one("SELECT COUNT(*) FROM loans WHERE " + OPEN)[0]
        late = self.one("SELECT COUNT(*) FROM loans WHERE %s AND due < ?" % OPEN, self.today())[0]
        return self.page("Desk", (
            "<h1>Desk</h1><p>Today is %s. <a href=\"/loans\">%s out</a>, <a href=\"/overdue\">%d overdue</a>.</p>"
            "<h2>Lend a book</h2><p class=\"soft\">Find the borrower, open their page, and type or scan the number of the copy.</p>%s"
            "<h2>Take a book back, or renew it</h2><p class=\"soft\">Find the loan by the number of the copy, the title or the borrower.</p>%s"
            % (e(self.today()), plural(out, "book"), late,
               self.search("/borrowers", "Ana or 7B", "Borrower's name or class"),
               self.search("/loans", "12 or Holes", "Copy number, title or borrower"))))

    # -- the catalogue

    def titles(self, query):
        typed = search_text(query)
        where, args = "1", []
        if typed:
            plain = fold(typed.replace("-", ""))
            where = ("instr(fold(t.title), ?1) OR instr(fold(t.author), ?1) OR instr(fold(t.shelf), ?1) "
                     "OR instr(fold(t.isbn), ?1) OR (?2 <> '' AND instr(fold(t.isbn), ?2))")
            args = [fold(typed), plain]
        total = self.one("SELECT COUNT(*) FROM titles t WHERE " + where, *args)[0]
        found = self.all(
            "SELECT t.*, (SELECT COUNT(*) FROM copies c WHERE c.title_id = t.id) AS held, "
            "(SELECT COUNT(*) FROM copies c WHERE c.title_id = t.id AND c.status = 'available' AND NOT EXISTS "
            "(SELECT 1 FROM loans l WHERE l.copy_id = c.id AND l.returned IS NULL AND l.lost IS NULL)) AS free "
            "FROM titles t WHERE %s ORDER BY fold(t.title), t.id LIMIT %d" % (where, SHOWN), *args)
        rows = [(None, [e(row["title"]), e(row["author"]), e(row["isbn"]), e(row["shelf"]), row["held"], row["free"],
                        self.acts(['<a href="/titles/%d">Copies</a>' % row["id"], '<a href="/titles/%d/edit">Edit</a>' % row["id"]])])
                for row in found]
        heads = [("Title", ""), ("Author", ""), ("ISBN", "num"), ("Shelf", "short"), ("Copies", "num"), ("In", "num"), ("", "act")]
        return self.page("Catalogue", (
            "<h1>Catalogue</h1>%s%s%s<h2>A new title</h2>%s"
            % (self.search("/titles", "sachar or F SAC", "Title, author, ISBN or shelf mark", typed),
               self.shown(total, found, "title", typed), self.table(heads, rows),
               self.title_form("/titles", {}, new=True))))

    @staticmethod
    def title_form(action, row, new=False):
        value = lambda name: e(row[name]) if row else ""
        copies = ('<label class="short">Copies <input name="copies" inputmode="numeric" required placeholder="2"></label>'
                  if new else "")
        return ('<form class="card" method="post" action="%s">'
                '<label class="wide">Title <input name="title" value="%s" required placeholder="Holes"></label>'
                '<label>Author <input name="author" value="%s" placeholder="Louis Sachar"></label>'
                '<label>ISBN <input name="isbn" value="%s" placeholder="978-0-7475-4459-7 or 080442957X"></label>'
                '<label class="short">Shelf mark <input name="shelf" value="%s" placeholder="F SAC"></label>'
                '%s<button type="submit">%s</button></form>'
                % (action, value("title"), value("author"), value("isbn"), value("shelf"), copies,
                   "Add the title" if new else "Save the correction"))

    def new_title(self, form):
        fields, number = title_fields(form), copies_asked(form)
        with self.db:
            made = self.db.execute("INSERT INTO titles (title, author, isbn, shelf) VALUES (?, ?, ?, ?)", fields).lastrowid
            self.db.executemany("INSERT INTO copies (title_id) VALUES (?)", [(made,)] * number)
        return "/titles/%d" % made

    def title(self, query, ident):
        row = self.need("titles", ident, "title")
        copies = self.all(
            "SELECT c.id, c.status, l.id AS loan, l.due, b.id AS who, b.name FROM copies c "
            "LEFT JOIN loans l ON l.copy_id = c.id AND l.returned IS NULL AND l.lost IS NULL "
            "LEFT JOIN borrowers b ON b.id = l.borrower_id WHERE c.title_id = ? ORDER BY c.id", row["id"])
        rows = []
        for copy in copies:
            mark = lambda status, label: self.button("/copies/%d/status" % copy["id"], label, status=status)
            if copy["loan"]:  # out: the borrower, and lost, which ends the loan; withdrawing waits for the book
                acts = [mark("lost", "Mark lost"), '<a href="/borrowers/%d">Borrower</a>' % copy["who"]]
            elif copy["status"] == "available":
                acts = [mark("lost", "Mark lost"), mark("withdrawn", "Withdraw")]
            else:
                other = "withdrawn" if copy["status"] == "lost" else "lost"
                acts = [mark("available", "Mark available"), mark(other, "Withdraw" if other == "withdrawn" else "Mark lost")]
            rows.append(("copy-%d" % copy["id"], [copy["id"], "on loan" if copy["loan"] else copy["status"],
                                                  e(copy["name"] or ""), e(copy["due"] or ""), self.acts(acts)]))
        about = [part for part in ("by " + e(row["author"]) if row["author"] else "", "ISBN " + e(row["isbn"]) if row["isbn"] else "",
                                   "shelf " + e(row["shelf"]) if row["shelf"] else "", plural(len(copies), "copy", "copies")) if part]
        heads = [("Copy", "num"), ("Status", "short"), ("With", ""), ("Due back", "num"), ("", "act")]
        return self.page("Catalogue", (
            '<h1>%s</h1><p>%s. <a href="/titles/%d/edit">Correct this title</a></p>%s<h2>More copies</h2>'
            '<form class="card" method="post" action="/titles/%d/copies"><label class="short">How many '
            '<input name="copies" inputmode="numeric" required placeholder="1"></label>'
            '<button type="submit">Add copies</button></form>'
            % (e(row["title"]), " · ".join(about), row["id"], self.table(heads, rows), row["id"])))

    def edit_title(self, query, ident):
        row = self.need("titles", ident, "title")
        return self.page("Catalogue", '<h1>Correct a title</h1>%s<p><a href="/titles/%d">Back to its copies</a></p>'
                         % (self.title_form("/titles/%d/edit" % row["id"], row), row["id"]))

    def save_title(self, form, ident):
        row = self.need("titles", ident, "title")
        fields = title_fields(form)
        with self.db:
            self.db.execute("UPDATE titles SET title = ?, author = ?, isbn = ?, shelf = ? WHERE id = ?", fields + (row["id"],))
        return "/titles/%d" % row["id"]

    def more_copies(self, form, ident):
        row = self.need("titles", ident, "title")
        number = copies_asked(form)
        with self.db:
            self.db.executemany("INSERT INTO copies (title_id) VALUES (?)", [(row["id"],)] * number)
        return "/titles/%d" % row["id"]

    def mark_copy(self, form, ident):
        copy = self.need("copies", ident, "copy")
        status = form.get("status", "")
        if status not in ("available", "lost", "withdrawn"):
            raise Refused("A copy is marked available, lost or withdrawn, and nothing else.")
        loan = self.one("SELECT l.id, b.name FROM loans l JOIN borrowers b ON b.id = l.borrower_id WHERE l.copy_id = ? AND " + OPEN,
                        copy["id"])
        if loan and status != "lost":
            raise Refused("Copy %d is on loan to %s. It is returned first; if it will not come back, mark it lost."
                          % (copy["id"], loan["name"]))
        with self.db:
            if loan:  # lost while out: the loan ends today, as lost and not as returned
                self.db.execute("UPDATE loans SET lost = ? WHERE id = ?", (self.today(), loan["id"]))
            self.db.execute("UPDATE copies SET status = ? WHERE id = ?", (status, copy["id"]))
        return "/titles/%d" % copy["title_id"]

    # -- the borrowers

    def class_names(self):
        """How each class is shown: the spelling most of its borrowers have; equally common, the one that sorts first."""
        spelled = collections.defaultdict(collections.Counter)
        for row in self.all("SELECT class FROM borrowers WHERE class <> ''"):
            spelled[fold(row["class"])][row["class"]] += 1
        return {key: min(count, key=lambda spelling: (-count[spelling], spelling)) for key, count in spelled.items()}

    def borrowers(self, query):
        typed = search_text(query)
        where, args = ("instr(fold(b.name), ?1) OR instr(fold(b.class), ?1)", [fold(typed)]) if typed else ("1", [])
        total = self.one("SELECT COUNT(*) FROM borrowers b WHERE " + where, *args)[0]
        found = self.all(
            "SELECT b.*, (SELECT COUNT(*) FROM loans l WHERE l.borrower_id = b.id AND l.returned IS NULL AND l.lost IS NULL) AS held "
            "FROM borrowers b WHERE %s ORDER BY fold(b.name), b.id LIMIT %d" % (where, SHOWN), *args)
        rows = [(None, [e(row["name"]), row["kind"], e(row["class"]), "%d of %d" % (row["held"], LIMIT[row["kind"]]),
                        "" if row["active"] else "has left",
                        self.acts(['<a href="/borrowers/%d">%s</a>' % (row["id"], "Lend" if row["active"] else "Open"),
                                   '<a href="/borrowers/%d/edit">Edit</a>' % row["id"]])]) for row in found]
        heads = [("Name", ""), ("Kind", "short"), ("Class", "short"), ("Books out", "num"), ("Left", "short"), ("", "act")]
        return self.page("Borrowers", (
            "<h1>Borrowers</h1>%s%s%s<h2>A new borrower</h2>%s"
            % (self.search("/borrowers", "Ana or 7B", "Name or class", typed), self.shown(total, found, "borrower", typed),
               self.table(heads, rows), self.borrower_form("/borrowers", None))))

    @staticmethod
    def borrower_form(action, row):
        def options(name, choices, chosen):
            return '<select name="%s" required>%s</select>' % (name, "".join(
                '<option value="%s"%s>%s</option>' % (value, " selected" if value == chosen else "", label) for value, label in choices))
        kinds = [("pupil", "Pupil"), ("staff", "Staff")]
        left = ""
        if row is None:  # nothing is chosen for the person on a new borrower
            kinds.insert(0, ("", "Choose…"))
        else:
            left = "<label>At the school %s</label>" % options(
                "active", [("1", "Yes"), ("0", "No, has left the school")], "1" if row["active"] else "0")
        return ('<form class="card" method="post" action="%s">'
                '<label class="wide">Name <input name="name" value="%s" required placeholder="Ana Lima"></label>'
                '<label class="short">Pupil or staff %s</label>'
                '<label class="short">Class <input name="class" value="%s" placeholder="7B"></label>'
                '%s<button type="submit">%s</button></form>'
                % (action, e(row["name"]) if row else "", options("kind", kinds, row["kind"] if row else ""),
                   e(row["class"]) if row else "", left, "Save the correction" if row else "Add the borrower"))

    def new_borrower(self, form):
        fields = borrower_fields(form)
        with self.db:
            made = self.db.execute("INSERT INTO borrowers (name, kind, class) VALUES (?, ?, ?)", fields).lastrowid
        return "/borrowers/%d" % made

    def borrower(self, query, ident):
        row = self.need("borrowers", ident, "borrower")
        loans = self.loans_where("l.borrower_id = ?", row["id"])
        ended = self.one("SELECT COUNT(returned), COUNT(lost) FROM loans WHERE borrower_id = ?", row["id"])
        limit = LIMIT[row["kind"]]
        late = len([1 for loan in loans if loan["due"] < self.today()])
        if not row["active"]:
            lend = "<p>%s has left the school and cannot borrow.</p>" % e(row["name"])
        elif len(loans) >= limit:
            lend = "<p>%s has %s out, the most for a %s: a book comes back before another goes out.</p>" % (
                e(row["name"]), plural(len(loans), "book"), "pupil" if row["kind"] == "pupil" else "member of staff")
        else:
            lend = ('%s<form class="card" method="post" action="/loans"><input type="hidden" name="borrower_id" value="%d">'
                    '<label>Copy number, typed or scanned <input name="copy" inputmode="numeric" autocomplete="off" data-scan '
                    'autofocus required></label><button type="submit">Lend</button></form>'
                    % ('<p class="late">%s overdue. Lending is still allowed: it is for the desk to decide.</p>'
                       % plural(late, "book") if late else "", row["id"]))
        return self.page("Borrowers", (
            '<h1>%s</h1><p>%s%s. <a href="/borrowers/%d/edit">Correct or mark as left</a></p>'
            '<p>Books out: %d of %d allowed. Returned so far: %d. Lost while out: %d.</p>%s%s'
            % (e(row["name"]), "Pupil" if row["kind"] == "pupil" else "Staff", ", class " + e(row["class"]) if row["class"] else "",
               row["id"], len(loans), limit, ended[0], ended[1], lend, self.loan_table(loans, who=False))))

    def edit_borrower(self, query, ident):
        row = self.need("borrowers", ident, "borrower")
        return self.page("Borrowers", '<h1>Correct a borrower</h1>%s<p><a href="/borrowers/%d">Back to their page</a></p>'
                         % (self.borrower_form("/borrowers/%d/edit" % row["id"], row), row["id"]))

    def save_borrower(self, form, ident):
        row = self.need("borrowers", ident, "borrower")
        fields = borrower_fields(form)
        if form.get("active") not in ("0", "1"):
            raise Refused("Say whether the borrower is at the school or has left.", KEPT)
        with self.db:
            self.db.execute("UPDATE borrowers SET name = ?, kind = ?, class = ?, active = ? WHERE id = ?",
                            fields + (int(form["active"]), row["id"]))
        return "/borrowers/%d" % row["id"]

    # -- the loans

    def loans_where(self, where="1", *args):
        return self.all(
            "SELECT l.*, t.id AS title_id, t.title, b.name, b.class FROM loans l JOIN copies c ON c.id = l.copy_id "
            "JOIN titles t ON t.id = c.title_id JOIN borrowers b ON b.id = l.borrower_id "
            "WHERE l.returned IS NULL AND l.lost IS NULL AND (%s) ORDER BY l.due, l.id" % where, *args)

    def loan_table(self, loans, who=True):
        today = datetime.date.fromisoformat(self.today())
        # The class stands beside the name, as typed, and the day lent is left out of a list of everybody's
        # loans between 761 and 999 px: with both as columns the state of a loan was under the buttons.
        heads = [("Copy", "num"), ("Title", "")] + ([("Borrower", "")] if who else []) + [
            ("Due", "num"), ("State", ""), ("Lent", "num gone" if who else "num"), ("", "act")]
        rows = []
        for loan in loans:
            days = (today - datetime.date.fromisoformat(loan["due"])).days
            state = ['<span class="late">%s overdue</span>' % plural(days, "day")] if days > 0 else []
            if loan["renewals"]:
                state.append("renewed once" if loan["renewals"] == 1 else "renewed twice")
            name = e(loan["name"]) + (' <span class="soft">(%s)</span>' % e(loan["class"]) if loan["class"] else "")
            buttons = [self.button("/loans/%d/return" % loan["id"], "Return")]
            if loan["renewals"] < RENEWALS:
                buttons.append(self.button("/loans/%d/renew" % loan["id"], "Renew"))
            links = ['<a href="/titles/%d">Copies</a>' % loan["title_id"]]
            if who:
                links.append('<a href="/borrowers/%d">Borrower</a>' % loan["borrower_id"])
            rows.append(("loan-%d" % loan["id"], [loan["copy_id"], e(loan["title"])] + ([name] if who else [])
                         + [loan["due"], ", ".join(state), loan["lent"], self.acts(buttons, links)]))
        return self.table(heads, rows)

    def loans(self, query):
        typed = search_text(query)
        if typed:
            number = int(typed) if re.fullmatch(r"[0-9]{1,9}", typed) else -1
            found = self.loans_where("l.copy_id = ?1 OR instr(fold(t.title), ?2) OR instr(fold(b.name), ?2)", number, fold(typed))
        else:
            found = self.loans_where()
        said = plural(len(found), "book") + " out" + (" matching “%s”" % e(typed) if typed else "")
        return self.page("Loans", "<h1>Loans</h1>%s<p class=\"soft\">%s.</p>%s" % (
            self.search("/loans", "12 or Holes", "Copy number, title or borrower", typed), said, self.loan_table(found)))

    def lend(self, form):
        who = whole(form.get("borrower_id", ""), "The borrower's number", SCAN)
        number = whole(form.get("copy", ""), "The copy number", SCAN)
        borrower = self.one("SELECT * FROM borrowers WHERE id = ?", who)
        if borrower is None:
            raise Refused("There is no borrower %d." % who, SCAN)
        copy = self.one("SELECT c.*, t.title FROM copies c JOIN titles t ON t.id = c.title_id WHERE c.id = ?", number)
        if copy is None:
            raise Refused("There is no copy %d." % number, SCAN)
        if not borrower["active"]:
            raise Refused("%s has left the school and cannot borrow." % borrower["name"], SCAN)
        out = self.one("SELECT b.name FROM loans l JOIN borrowers b ON b.id = l.borrower_id WHERE l.copy_id = ? AND " + OPEN, number)
        if out:
            raise Refused("Copy %d of %s is already on loan to %s. Return it first if it is the book in your hand."
                          % (number, copy["title"], out["name"]), SCAN)
        if copy["status"] != "available":
            raise Refused("Copy %d of %s is marked %s. Mark it available on the page of its title if it is the book in your hand."
                          % (number, copy["title"], copy["status"]), SCAN)
        held = self.one("SELECT COUNT(*) FROM loans WHERE borrower_id = ? AND " + OPEN, who)[0]
        if held >= LIMIT[borrower["kind"]]:
            raise Refused("%s already has %s out, and %d is the most for %s." % (
                borrower["name"], plural(held, "book"), LIMIT[borrower["kind"]],
                "a pupil" if borrower["kind"] == "pupil" else "staff"), SCAN)
        with self.db:  # the dates are the server's: lent today, due 14 days on
            self.db.execute("INSERT INTO loans (copy_id, borrower_id, lent, due) VALUES (?, ?, ?, ?)",
                            (number, who, self.today(), self.after(LOAN_DAYS)))
        return "/borrowers/%d" % who

    def open_loan(self, ident, doing):
        loan = self.need("loans", ident, "loan")
        if loan["returned"]:
            raise Refused("That book came back on %s: there is nothing to %s." % (loan["returned"], doing))
        if loan["lost"]:
            raise Refused("That copy was marked lost on %s, which ended the loan: there is nothing to %s." % (loan["lost"], doing))
        return loan

    def give_back(self, form, ident):
        loan = self.open_loan(ident, "return")
        with self.db:
            self.db.execute("UPDATE loans SET returned = ? WHERE id = ?", (self.today(), loan["id"]))

    def renew(self, form, ident):
        loan = self.open_loan(ident, "renew")
        if loan["renewals"] >= RENEWALS:
            raise Refused("That loan has been renewed twice, which is the most. The book comes back by %s." % loan["due"])
        with self.db:  # 14 days from the day of the renewal, not from the old due date
            self.db.execute("UPDATE loans SET due = ?, renewals = renewals + 1 WHERE id = ?", (self.after(LOAN_DAYS), loan["id"]))

    def overdue(self, query):
        late = self.loans_where("l.due < ?", self.today())
        names = self.class_names()
        groups = collections.defaultdict(list)
        for loan in late:
            groups[fold(loan["class"])].append(loan)
        body = ["<h1>Overdue</h1><p class=\"soft\">%s overdue, by class. Nothing is sent to anyone.</p>" % plural(len(late), "book")]
        for key in sorted(groups, key=lambda key: (key == "", key)):  # those with no class last
            body.append("<h2>%s</h2>%s" % ("Class " + e(names[key]) if key else "No class", self.loan_table(groups[key])))
        return self.page("Overdue", "".join(body))

    def returned(self, query):
        total = self.one("SELECT COUNT(*) FROM loans WHERE NOT (%s)" % OPEN)[0]
        found = self.all(
            "SELECT l.*, t.title, b.name, COALESCE(l.returned, l.lost) AS ended FROM loans l JOIN copies c ON c.id = l.copy_id "
            "JOIN titles t ON t.id = c.title_id JOIN borrowers b ON b.id = l.borrower_id "
            "WHERE NOT (l.returned IS NULL AND l.lost IS NULL) ORDER BY ended DESC, l.id DESC LIMIT %d" % SHOWN)
        rows = [("loan-%d" % row["id"], [row["copy_id"], e(row["title"]), e(row["name"]), row["lent"], row["ended"],
                                         "returned" if row["returned"] else "lost, not returned"]) for row in found]
        heads = [("Copy", "num"), ("Title", ""), ("Borrower", ""), ("Lent", "num"), ("Ended", "num"), ("How it ended", "")]
        said = ("Showing the latest %d of %d loans that have ended" % (len(found), total) if total > len(found)
                else plural(total, "loan has ended", "loans have ended"))
        return self.page("Returned", "<h1>Returned or lost</h1><p class=\"soft\">%s.</p>%s" % (said, self.table(heads, rows)))

    # -- everything, for whoever keeps a copy

    def export(self, query):
        out = set(row[0] for row in self.all("SELECT copy_id FROM loans WHERE " + OPEN))
        state = {
            "today": self.today(),
            "titles": [dict(row) for row in self.all("SELECT * FROM titles ORDER BY id")],
            "copies": [{"id": row["id"], "title_id": row["title_id"], "status": "on loan" if row["id"] in out else row["status"]}
                       for row in self.all("SELECT * FROM copies ORDER BY id")],
            "borrowers": [dict(row, active=bool(row["active"])) for row in self.all("SELECT * FROM borrowers ORDER BY id")],
            "loans": [dict(row) for row in self.all("SELECT * FROM loans ORDER BY id")],
        }
        return 200, "application/json", json.dumps(state, ensure_ascii=False, indent=1)

    def style(self, query):
        return 200, "text/css; charset=utf-8", CSS

    # -- demonstration data, into an empty file only

    def sample(self):
        if self.one("SELECT (SELECT COUNT(*) FROM titles) + (SELECT COUNT(*) FROM borrowers)")[0]:
            return False
        books = [("Holes", "Louis Sachar", "9780747544597", "F SAC", 3), ("Skellig", "David Almond", "0340716002", "F ALM", 2),
                 ("Noughts & Crosses", "Malorie Blackman", "9780552555708", "F BLA", 2), ("The Hobbit", "J. R. R. Tolkien", "9780261102217", "F TOL", 2),
                 ("Wonder", "R. J. Palacio", "9780552565974", "F PAL", 3), ("Coraline", "Neil Gaiman", "074756210X", "F GAI", 1),
                 ("A Short History of Nearly Everything", "Bill Bryson", "9780552997041", "500 BRY", 1),
                 ("School atlas of the world", "", "", "912 ATL", 4), ("Goodnight Mister Tom", "Michelle Magorian", "9780140315417", "F MAG", 2)]
        people = [("Ana Lima", "pupil", "7B"), ("Bo Li", "pupil", "7b"), ("Cy Roy", "pupil", "7B"), ("Dee Ng", "pupil", "8A"),
                  ("Eli Kay", "pupil", "9A"), ("Fay Orr", "pupil", "9A"), ("Ms Kay", "staff", ""), ("Mr Okafor", "staff", "8A"),
                  ("Gus Hill", "pupil", "10C")]
        loans = [(1, 1, -20, 0, None), (4, 2, -16, 0, None), (6, 5, -30, 1, None), (8, 7, -3, 0, None), (10, 4, -9, 0, None),
                 (13, 1, -1, 0, None), (14, 7, -25, 2, None), (2, 3, -40, 0, -29), (5, 6, -35, 0, -22), (9, 9, -50, 0, -41)]
        with self.db:
            for title, author, isbn, shelf, copies in books:
                made = self.db.execute("INSERT INTO titles (title, author, isbn, shelf) VALUES (?, ?, ?, ?)", (title, author, isbn, shelf)).lastrowid
                self.db.executemany("INSERT INTO copies (title_id) VALUES (?)", [(made,)] * copies)
            self.db.executemany("INSERT INTO borrowers (name, kind, class) VALUES (?, ?, ?)", people)
            for copy, who, lent, renewals, back in loans:
                due = lent + LOAN_DAYS if not renewals else lent + 10 * renewals + LOAN_DAYS
                self.db.execute("INSERT INTO loans (copy_id, borrower_id, lent, due, renewals, returned) VALUES (?, ?, ?, ?, ?, ?)",
                                (copy, who, self.after(lent), self.after(due), renewals, self.after(back) if back is not None else None))
            self.db.execute("UPDATE copies SET status = 'withdrawn' WHERE id = 18")
        return True


GET = [(r"/", Library.desk), (r"/titles", Library.titles), (r"/titles/(\d{1,9})", Library.title),
       (r"/titles/(\d{1,9})/edit", Library.edit_title), (r"/borrowers", Library.borrowers), (r"/borrowers/(\d{1,9})", Library.borrower),
       (r"/borrowers/(\d{1,9})/edit", Library.edit_borrower), (r"/loans", Library.loans), (r"/overdue", Library.overdue),
       (r"/returned", Library.returned), (r"/export\.json", Library.export), (r"/style\.css", Library.style)]
POST = [(r"/titles", Library.new_title), (r"/titles/(\d{1,9})/edit", Library.save_title), (r"/titles/(\d{1,9})/copies", Library.more_copies),
        (r"/copies/(\d{1,9})/status", Library.mark_copy), (r"/borrowers", Library.new_borrower),
        (r"/borrowers/(\d{1,9})/edit", Library.save_borrower), (r"/loans", Library.lend),
        (r"/loans/(\d{1,9})/return", Library.give_back), (r"/loans/(\d{1,9})/renew", Library.renew)]


# ---- the one way in: HTTP on this machine ----------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "SchoolLibrary"

    def log_message(self, *args):
        pass

    def answer(self, status, kind, body, location=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Security-Policy", POLICY)
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def came_from(self):
        """The list the button was on, when it is one of ours; the loans page when it is not."""
        seen = urllib.parse.urlsplit(self.headers.get("Referer", ""))
        if seen.netloc in self.server.hosts and re.fullmatch(r"/loans|/overdue|/borrowers/\d{1,9}", seen.path):
            query = seen.query if seen.path == "/loans" and re.fullmatch(r"[A-Za-z0-9%+=&._~-]*", seen.query) else ""
            return seen.path + ("?" + query if query else "")
        return "/loans"

    def respond(self, method):
        library = self.server.library
        with library.lock:
            try:
                self.answer(*self.work(library, method))
            except Refused as refused:
                self.answer(*library.refusal(refused))

    def work(self, library, method):
        # A page on another site can reach this port through the browser: only this machine's own name
        # is answered, and only a form sent from the library's own pages is taken.
        host = self.headers.get("Host", "")
        if host not in self.server.hosts:
            raise Refused("This library answers only on this machine, as %s." % self.server.hosts[0], status=403)
        path, _, query = self.path.partition("?")
        routes = {"GET": GET, "POST": POST}.get(method, [])
        found = [(re.fullmatch(pattern, path), act) for pattern, act in routes]
        found = [(match, act) for match, act in found if match]
        if method == "GET":
            if not found:
                if any(re.fullmatch(pattern, path) for pattern, _ in POST):
                    raise Refused("This address only takes a form sent by a button; opening it does nothing.", status=405)
                raise Refused("There is no page at this address.", status=404)
            try:
                asked = {name: values[0] for name, values in urllib.parse.parse_qs(
                    query, keep_blank_values=True, errors="strict", max_num_fields=50).items()}
            except ValueError:
                raise Refused("The address could not be read.")
            return found[0][1](library, asked, *found[0][0].groups())
        if method != "POST":
            raise Refused("Nothing here can be removed or replaced: the library only reads pages and takes forms.", status=405)
        origin, site = self.headers.get("Origin"), self.headers.get("Sec-Fetch-Site")
        if (origin is not None and origin != "http://" + host) or (site is not None and site not in ("same-origin", "none")):
            raise Refused("That form was not sent from the library's own pages.", status=403)
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = -1
        if length < 0 or length > FORM_BYTES:
            self.close_connection = True
            if 0 < length <= 4 * 1024 * 1024:
                self.rfile.read(length)  # so that the sender hears the answer
            raise Refused("A form may be at most 65,536 bytes.", status=413)
        try:
            form = {name: values[0] for name, values in urllib.parse.parse_qs(
                self.rfile.read(length).decode("utf-8"), keep_blank_values=True, errors="strict", max_num_fields=50).items()}
        except ValueError:
            raise Refused("The form could not be read.")
        if not found:
            status = 405 if any(re.fullmatch(pattern, path) for pattern, _ in GET) else 404
            raise Refused("No form is taken at this address: nothing is removed, and a loan is never edited.", status=status)
        location = found[0][1](library, form, *found[0][0].groups())
        return 303, "text/plain; charset=utf-8", "", location or self.came_from()

    def do_GET(self):
        self.respond("GET")

    def do_POST(self):
        self.respond("POST")

    def do_other(self):
        self.respond(self.command)

    do_HEAD = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_other


def main():
    parser = argparse.ArgumentParser(description="A lending library for a school, on this machine only.")
    parser.add_argument("--db", default="library.db", help="the one SQLite file everything is kept in")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--sample", action="store_true", help="load demonstration data, if the file is empty")
    parser.add_argument("--today", metavar="YYYY-MM-DD", help="take this day for today, to see a book become overdue; every page says so")
    args = parser.parse_args()
    if args.today:
        try:
            args.today = datetime.date.fromisoformat(args.today).isoformat()
        except ValueError:
            parser.error("--today takes a date written as YYYY-MM-DD")
    library = Library(args.db, args.today)
    if args.sample:
        print("Demonstration data loaded." if library.sample() else "The file already holds data: --sample changed nothing.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    server.library = library
    server.hosts = ["127.0.0.1:%d" % args.port, "localhost:%d" % args.port]
    print("School library on http://127.0.0.1:%d/ (stop with Ctrl-C)" % args.port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""A lending library for a school, for the staff at the library desk.

    python3 product/library.py [--db library.db] [--port 8000] [--sample] [--today YYYY-MM-DD]

then open http://127.0.0.1:8000/. Python's standard library and one SQLite
file; it answers on this machine only, and the web pages are the only way in.
What it must do is written in lessons/ (L0027 to L0033 and the lessons its
labels switch on) and checked by cases/.
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

LOAN_DAYS = 14
RENEWALS = 2
LIMIT = {"pupil": 3, "staff": 10}
SHOWN = 200
FORM_BYTES = 65536
STATUSES = ("available", "lost", "withdrawn")

SCHEMA = """
CREATE TABLE IF NOT EXISTS titles (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
    author TEXT NOT NULL, isbn TEXT NOT NULL, shelf TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS copies (id INTEGER PRIMARY KEY AUTOINCREMENT,
    title_id INTEGER NOT NULL REFERENCES titles(id),
    status TEXT NOT NULL CHECK (status IN ('available', 'lost', 'withdrawn')));
CREATE TABLE IF NOT EXISTS borrowers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('pupil', 'staff')), class TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1)));
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY AUTOINCREMENT,
    copy_id INTEGER NOT NULL REFERENCES copies(id), borrower_id INTEGER NOT NULL REFERENCES borrowers(id),
    lent TEXT NOT NULL, due TEXT NOT NULL, renewals INTEGER NOT NULL, returned TEXT, lost TEXT,
    CHECK (returned IS NULL OR lost IS NULL));
"""
# A loan is out until it has a day of return or a day it was lost (L0031). A file made before loans
# could end as lost gets the column, and the rule of one loan out per copy in its new words.
INDEXES = """
DROP INDEX IF EXISTS one_open_loan_per_copy;
CREATE UNIQUE INDEX IF NOT EXISTS one_loan_out_per_copy ON loans(copy_id) WHERE returned IS NULL AND lost IS NULL;
CREATE INDEX IF NOT EXISTS loans_of_borrower ON loans(borrower_id);
CREATE INDEX IF NOT EXISTS copies_of_title ON copies(title_id);
"""

STYLE = """
:root{color-scheme:light dark;--bg:#f5f4ef;--fg:#1c1c1a;--card:#fff;--line:#d6d3c8;--link:#17527a;--late:#a5371c;--soft:#62605a}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--fg:#e9e7e2;--card:#1f2226;--line:#3b3f45;--link:#84bde6;--late:#f39075;--soft:#a3a19b}}
*{box-sizing:border-box}
body{margin:0;font:16px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg)}
a{color:var(--link)}
nav{display:flex;flex-wrap:wrap;gap:.2rem 1.1rem;padding:.6rem 1rem;background:var(--card);border-bottom:1px solid var(--line)}
nav a{white-space:nowrap;font-weight:600}
nav span{color:var(--soft)}
main{max-width:1100px;margin:0 auto;padding:.5rem 1rem 3rem}
h1{font-size:1.5rem}h2{font-size:1.15rem;margin-top:1.6rem}
h1,h2,p,li{overflow-wrap:anywhere}
.note{color:var(--soft)}
.clock{background:var(--late);color:#fff;padding:.3rem 1rem;margin:0}
.late{color:var(--late);font-weight:600}
form.card{display:flex;flex-wrap:wrap;gap:.6rem;align-items:flex-end;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.8rem;margin:1rem 0}
form.card label{display:flex;flex-direction:column;gap:.15rem;flex:1 1 9rem;min-width:0;font-size:.85rem;color:var(--soft)}
input,select,button{font:inherit;padding:.4rem .55rem;min-width:0;max-width:100%}
input,select{width:100%;border:1px solid var(--line);border-radius:5px;background:var(--bg);color:var(--fg)}
button{white-space:nowrap;cursor:pointer;border:1px solid var(--link);border-radius:5px;background:var(--link);color:var(--card)}
td button{padding:.2rem .55rem;background:transparent;color:var(--link)}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%}
th,td{text-align:left;vertical-align:top;padding:.45rem .5rem;border-bottom:1px solid var(--line)}
th{font-size:.8rem;color:var(--soft);white-space:nowrap}
td{min-width:150px;overflow-wrap:anywhere}
td.num,td.tag,td.act{min-width:0;white-space:nowrap}
td.num,td.act{overflow-wrap:normal}
td small{display:block}
td.act,th.act{position:sticky;right:0;background:var(--bg)}
td.act form{display:inline}
td.act a,td.act button{margin-right:.35rem}
@media (max-width:760px){
 .scroll{overflow-x:visible}
 table,tbody,tr,td{display:block}
 thead{display:none}
 tr{background:var(--card);border:1px solid var(--line);border-radius:8px;margin:.7rem 0;padding:.45rem .7rem}
 td{border:0;padding:.2rem 0;min-width:0}
 td.tag{white-space:normal}
 td.act{position:static;background:transparent;padding-top:.45rem}
 td::before{content:attr(data-label);display:block;font-size:.75rem;color:var(--soft)}
 td.act::before{content:none}
 td:empty{display:none}
}
"""

NAV = (("/", "Desk"), ("/titles", "Catalogue"), ("/borrowers", "Borrowers"), ("/loans", "Loans"),
       ("/overdue", "Overdue"), ("/returned", "Returned"))


class Refused(Exception):
    """What was asked cannot be done; the text says why, in words for the person at the desk."""


def e(text):
    return html.escape(str(text), quote=True)


# ---- what is typed ---------------------------------------------------------------------------

def text(form, name, least, most, what):
    """A line of text, trimmed, within its bound (L0033)."""
    value = " ".join(form.get(name, "").split())
    if any(ord(letter) < 32 or ord(letter) == 127 for letter in value):
        raise Refused("%s has a character that cannot be shown." % what)
    if len(value) < least:
        raise Refused("%s is missing." % what)
    if len(value) > most:
        raise Refused("%s is %d characters long; the most is %d." % (what, len(value), most))
    return value


def isbn(form):
    typed = text(form, "isbn", 0, 40, "The ISBN")
    plain = typed.replace("-", "").upper()
    fine = (len(plain) == 13 and plain.isascii() and plain.isdigit()) or (
        len(plain) == 10 and plain.isascii() and plain[:9].isdigit() and (plain[9].isdigit() or plain[9] == "X"))
    if plain and not fine:
        raise Refused("The ISBN “%s” is not 10 or 13 digits (hyphens are fine, and the last of 10 may be X). "
                      "Leave it empty if the book has none." % typed)
    return plain


def whole(form, name, least, most, what):
    typed = form.get(name, "").strip()
    if not (typed.isascii() and typed.isdigit() and len(typed) <= 9) or not least <= int(typed) <= most:
        raise Refused("%s must be a whole number from %d to %d, written in digits; “%s” is not."
                      % (what, least, most, typed[:40]))
    return int(typed)


def choice(form, name, allowed, what):
    typed = form.get(name, "").strip()
    if typed not in allowed:
        raise Refused("%s must be one of: %s." % (what, ", ".join(allowed)))
    return typed


def title_fields(form):
    return (text(form, "title", 1, 200, "The title"), text(form, "author", 0, 120, "The author"),
            isbn(form), text(form, "shelf", 0, 20, "The shelf mark"))


def borrower_fields(form):
    return (text(form, "name", 1, 80, "The name"), choice(form, "kind", ("pupil", "staff"), "The kind of borrower"),
            text(form, "class", 0, 20, "The class"))


def search(query):
    typed = " ".join(query.get("q", "").split())
    if len(typed) > 100:
        raise Refused("The search text is %d characters long; the most is 100." % len(typed))
    return typed


def fold(typed):
    """Text for comparing without regard to capitals, of any letter and not only A to Z (L0036)."""
    return typed.casefold()


def like(typed):
    """The search text as a pattern in which % and _ are ordinary characters, to be met by fold(column)."""
    typed = fold(typed)
    return "%" + typed.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


# ---- the library -----------------------------------------------------------------------------

class Library:
    def __init__(self, path, today=None):
        self.db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.create_function("fold", 1, fold, deterministic=True)
        self.db.executescript(SCHEMA)
        if "lost" not in [column["name"] for column in self.db.execute("PRAGMA table_info(loans)")]:
            self.db.execute("ALTER TABLE loans ADD COLUMN lost TEXT")
        self.db.executescript(INDEXES)
        self.fixed_today = today
        self.lock = threading.Lock()

    def today(self):
        return self.fixed_today or datetime.date.today().isoformat()

    def after(self, days):
        return (datetime.date.fromisoformat(self.today()) + datetime.timedelta(days=days)).isoformat()

    def all(self, sql, *values):
        return self.db.execute(sql, values).fetchall()

    def one(self, sql, *values):
        return self.db.execute(sql, values).fetchone()

    def row(self, table, ident, what):
        found = self.one("SELECT * FROM %s WHERE id = ?" % table, ident)
        if found is None:
            raise Refused("There is no %s %s." % (what, ident))
        return found

    # -- changes: each is one transaction, done whole or not at all --

    def add_title(self, form):
        fields, copies = title_fields(form), whole(form, "copies", 1, 50, "The number of copies")
        made = self.db.execute("INSERT INTO titles (title, author, isbn, shelf) VALUES (?, ?, ?, ?)", fields).lastrowid
        self.db.executemany("INSERT INTO copies (title_id, status) VALUES (?, 'available')", [(made,)] * copies)
        return "/titles/%d" % made

    def edit_title(self, ident, form):
        self.row("titles", ident, "title")
        self.db.execute("UPDATE titles SET title = ?, author = ?, isbn = ?, shelf = ? WHERE id = ?",
                        title_fields(form) + (ident,))
        return "/titles/%d" % ident

    def add_copies(self, ident, form):
        self.row("titles", ident, "title")
        copies = whole(form, "copies", 1, 50, "The number of copies")
        self.db.executemany("INSERT INTO copies (title_id, status) VALUES (?, 'available')", [(ident,)] * copies)
        return "/titles/%d" % ident

    def mark_copy(self, ident, form):
        copy = self.row("copies", ident, "copy")
        status = choice(form, "status", STATUSES, "The status of a copy")
        out = self.one("SELECT l.id, b.name FROM loans l JOIN borrowers b ON b.id = l.borrower_id "
                       "WHERE l.copy_id = ? AND l.returned IS NULL AND l.lost IS NULL", ident)
        if out is not None and status == "lost":  # lost while it is out: the loan ends today, as lost (L0031)
            self.db.execute("UPDATE loans SET lost = ? WHERE id = ?", (self.today(), out["id"]))
        elif out is not None:
            raise Refused("Copy %d is on loan to %s. Return it first; then it can be marked %s. "
                          "If it will not come back, mark it lost." % (ident, out["name"], status))
        self.db.execute("UPDATE copies SET status = ? WHERE id = ?", (status, ident))
        return "/titles/%d" % copy["title_id"]

    def add_borrower(self, form):
        made = self.db.execute("INSERT INTO borrowers (name, kind, class, active) VALUES (?, ?, ?, 1)",
                               borrower_fields(form)).lastrowid
        return "/borrowers/%d" % made

    def edit_borrower(self, ident, form):
        self.row("borrowers", ident, "borrower")
        active = choice(form, "active", ("1", "0"), "In school or has left")
        self.db.execute("UPDATE borrowers SET name = ?, kind = ?, class = ?, active = ? WHERE id = ?",
                        borrower_fields(form) + (int(active), ident))
        return "/borrowers/%d" % ident

    def lend(self, form):
        typed = form.get("borrower_id", "").strip()
        if not (typed.isascii() and typed.isdigit() and len(typed) <= 9):
            raise Refused("The loan names no borrower.")
        who = self.row("borrowers", int(typed), "borrower")
        typed = form.get("copy", "").strip()
        if not typed:
            raise Refused("Type or scan the number of the copy.")
        if not (typed.isascii() and typed.isdigit() and len(typed) <= 9):
            raise Refused("A copy number is digits only, nine at most; “%s” is not one." % typed[:40])
        copy = self.one("SELECT c.id, c.status, t.title FROM copies c JOIN titles t ON t.id = c.title_id WHERE c.id = ?", int(typed))
        if copy is None:
            raise Refused("There is no copy %d." % int(typed))
        if not who["active"]:
            raise Refused("%s has left the school and cannot borrow." % who["name"])
        if copy["status"] != "available":
            raise Refused("Copy %d (%s) is marked %s and cannot be lent." % (copy["id"], copy["title"], copy["status"]))
        out = self.one("SELECT b.name FROM loans l JOIN borrowers b ON b.id = l.borrower_id "
                       "WHERE l.copy_id = ? AND l.returned IS NULL AND l.lost IS NULL", copy["id"])
        if out is not None:
            raise Refused("Copy %d (%s) is already on loan to %s. Return it first if it has come back."
                          % (copy["id"], copy["title"], out["name"]))
        held = self.one("SELECT COUNT(*) AS n FROM loans WHERE borrower_id = ? AND returned IS NULL AND lost IS NULL", who["id"])["n"]
        if held >= LIMIT[who["kind"]]:
            raise Refused("%s already has %d books out; the limit for %s is %d."
                          % (who["name"], held, "a pupil" if who["kind"] == "pupil" else "staff", LIMIT[who["kind"]]))
        self.db.execute("INSERT INTO loans (copy_id, borrower_id, lent, due, renewals) VALUES (?, ?, ?, ?, 0)",
                        (copy["id"], who["id"], self.today(), self.after(LOAN_DAYS)))
        return "/borrowers/%d" % who["id"]

    def give_back(self, ident, form):
        loan = self.row("loans", ident, "loan")
        if loan["returned"] is not None:
            raise Refused("Copy %d was already returned on %s." % (loan["copy_id"], loan["returned"]))
        if loan["lost"] is not None:
            raise Refused("Copy %d was marked lost on %s, which ended this loan. If the book has turned up, "
                          "mark the copy available on the page of its title." % (loan["copy_id"], loan["lost"]))
        self.db.execute("UPDATE loans SET returned = ? WHERE id = ?", (self.today(), ident))
        return "/loans"

    def renew(self, ident, form):
        loan = self.row("loans", ident, "loan")
        if loan["returned"] is not None:
            raise Refused("Copy %d was returned on %s; lend it again instead." % (loan["copy_id"], loan["returned"]))
        if loan["lost"] is not None:
            raise Refused("Copy %d was marked lost on %s, which ended this loan." % (loan["copy_id"], loan["lost"]))
        if loan["renewals"] >= RENEWALS:
            raise Refused("This loan has been renewed twice, which is the most. Return the book and lend it again "
                          "if nobody else is waiting for it.")
        self.db.execute("UPDATE loans SET due = ?, renewals = renewals + 1 WHERE id = ?", (self.after(LOAN_DAYS), ident))
        return "/loans"

    # -- everything, for /export.json --

    def export(self):
        out = {loan["copy_id"] for loan in self.all("SELECT copy_id FROM loans WHERE returned IS NULL AND lost IS NULL")}
        return {
            "today": self.today(),
            "titles": [dict(row) for row in self.all("SELECT * FROM titles ORDER BY id")],
            "copies": [{"id": row["id"], "title_id": row["title_id"],
                        "status": "on loan" if row["id"] in out else row["status"]}
                       for row in self.all("SELECT * FROM copies ORDER BY id")],
            "borrowers": [dict(row, active=bool(row["active"])) for row in self.all("SELECT * FROM borrowers ORDER BY id")],
            "loans": [dict(row) for row in self.all("SELECT * FROM loans ORDER BY id")],
        }

    def sample(self):
        """Demonstration data, into an empty file only."""
        if self.one("SELECT (SELECT COUNT(*) FROM titles) + (SELECT COUNT(*) FROM borrowers) AS n")["n"]:
            return False
        books = [("Holes", "Louis Sachar", "9780747544597", "F SAC", 3), ("Skellig", "David Almond", "0340716002", "F ALM", 2),
                 ("Wonder", "R. J. Palacio", "9780552565974", "F PAL", 4), ("The Hobbit", "J. R. R. Tolkien", "9780261102217", "F TOL", 2),
                 ("Noughts & Crosses", "Malorie Blackman", "9780552555708", "F BLA", 3),
                 ("A Short History of Nearly Everything", "Bill Bryson", "9780552997041", "500 BRY", 1),
                 ("The Boy in the Striped Pyjamas", "John Boyne", "9780099487821", "F BOY", 2),
                 ("Coraline", "Neil Gaiman", "0747562105", "F GAI", 1),
                 ("Horrible Histories: Rotten Romans", "Terry Deary", "", "937 DEA", 2),
                 ("Oxford School Atlas", "", "9780198487579", "912 OXF", 6)]
        people = [("Ana Lima", "pupil", "7B"), ("Bo Li", "pupil", "7B"), ("Chidi Okafor", "pupil", "8A"),
                  ("Dara Singh", "pupil", "8A"), ("Elif Yilmaz", "pupil", "9C"), ("Finn O'Brien", "pupil", "9C"),
                  ("Ms Kay", "staff", ""), ("Mr Mensah", "staff", "")]
        with self.db:
            self.db.execute("BEGIN")
            for title, author, number, shelf, copies in books:
                made = self.db.execute("INSERT INTO titles (title, author, isbn, shelf) VALUES (?, ?, ?, ?)",
                                       (title, author, number, shelf)).lastrowid
                self.db.executemany("INSERT INTO copies (title_id, status) VALUES (?, 'available')", [(made,)] * copies)
            self.db.executemany("INSERT INTO borrowers (name, kind, class, active) VALUES (?, ?, ?, 1)", people)
            # copy, borrower, days ago, renewals, returned days ago
            for copy, who, ago, renewals, back in [(1, 1, 20, 0, None), (4, 2, 16, 0, None), (6, 3, 3, 0, None),
                                                   (10, 5, 25, 1, None), (13, 7, 1, 0, None), (2, 4, 30, 0, 18),
                                                   (15, 6, 9, 0, 2), (21, 5, 30, 0, None)]:
                due = self.after(-ago + LOAN_DAYS) if not renewals else self.after(-ago + LOAN_DAYS + 9)
                self.db.execute("INSERT INTO loans (copy_id, borrower_id, lent, due, renewals, returned) VALUES (?, ?, ?, ?, ?, ?)",
                                (copy, who, self.after(-ago), due, renewals, None if back is None else self.after(-back)))
            self.db.execute("UPDATE copies SET status = 'lost' WHERE id = 8")
        return True


# ---- pages -----------------------------------------------------------------------------------

def table(heads, rows):
    """A list. Wide, a table; narrow, each row a card whose fields carry the name of their column (L0026).

    heads: the column names, "" for the column of links and buttons. rows: (attributes of the row, cells),
    a cell being (class, html)."""
    out = ['<div class="scroll"><table><thead><tr>']
    out += ['<th%s>%s</th>' % (' class="act"' if not head else "", e(head)) for head in heads]
    out.append("</tr></thead><tbody>")
    for attributes, cells in rows:
        out.append("<tr%s>" % attributes)
        for head, (kind, inside) in zip(heads, cells):
            out.append('<td%s data-label="%s">%s</td>' % (' class="%s"' % kind if kind else "", e(head), inside))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def button(action, label, back=None):
    hidden = '<input type="hidden" name="back" value="%s">' % e(back) if back else ""
    return '<form method="post" action="%s">%s<button type="submit">%s</button></form>' % (e(action), hidden, e(label))


def field(label, name, value="", extra=""):
    return '<label>%s <input name="%s" value="%s"%s></label>' % (e(label), name, e(value), extra)


def options(name, pairs, chosen, empty=None):
    out = ['<select name="%s" required>' % name]
    if empty:
        out.append('<option value="">%s</option>' % e(empty))
    out += ['<option value="%s"%s>%s</option>' % (e(value), " selected" if value == chosen else "", e(label))
            for value, label in pairs]
    return "".join(out) + "</select>"


def search_form(action, label, typed):
    return ('<form class="card" method="get" action="%s"><label>%s <input name="q" value="%s" maxlength="100"></label>'
            '<button type="submit">Search</button></form>' % (action, e(label), e(typed)))


def counted(shown, total, one, many, typed, first="first"):
    what = one if total == 1 else many
    tail = " matching “%s”" % e(typed) if typed else ""
    if total > shown:
        return ('<p class="note">Showing the %s %d of %d %s%s. Search to find the rest.</p>'
                % (first, shown, total, what, tail))
    return '<p class="note">%d %s%s.</p>' % (total, what, tail)


def title_form(action, row=None, copies=True):
    row = row or {"title": "", "author": "", "isbn": "", "shelf": ""}
    return ('<form class="card" method="post" action="%s">' % action
            + field("Title", "title", row["title"], ' required maxlength="200"')
            + field("Author", "author", row["author"], ' maxlength="120"')
            + field("ISBN, if it has one", "isbn", row["isbn"], ' placeholder="978-0-7475-4459-7 or 080442957X" maxlength="40"')
            + field("Shelf mark", "shelf", row["shelf"], ' placeholder="F SAC" maxlength="20"')
            + (field("Copies", "copies", "", ' placeholder="1" required inputmode="numeric" maxlength="2"') if copies else "")
            + '<button type="submit">%s</button></form>' % ("Add title" if copies else "Save"))


def borrower_form(action, row=None):
    new = row is None
    row = row or {"name": "", "kind": "", "class": "", "active": 1}
    return ('<form class="card" method="post" action="%s">' % action
            + field("Name", "name", row["name"], ' required maxlength="80"')
            + "<label>Kind " + options("kind", (("pupil", "Pupil"), ("staff", "Staff")), row["kind"], "Choose…") + "</label>"
            + field("Class", "class", row["class"], ' placeholder="7B" maxlength="20"')
            + ("" if new else "<label>In school " + options("active", (("1", "In school"), ("0", "Has left")),
                                                           str(row["active"])) + "</label>")
            + '<button type="submit">%s</button></form>' % ("Add borrower" if new else "Save"))


OPEN_LOANS = ("SELECT l.*, t.title, t.id AS title_id, b.name, b.class, b.kind FROM loans l "
              "JOIN copies c ON c.id = l.copy_id JOIN titles t ON t.id = c.title_id "
              "JOIN borrowers b ON b.id = l.borrower_id ")


class Pages:
    def __init__(self, library):
        self.lib = library

    def due(self, loan):
        """When a loan is due, and how late it is."""
        out = e(loan["due"])
        if loan["due"] < self.lib.today():
            days = (datetime.date.fromisoformat(self.lib.today()) - datetime.date.fromisoformat(loan["due"])).days
            out += '<small class="late">%d day%s overdue</small>' % (days, "" if days == 1 else "s")
        if loan["renewals"]:
            out += '<small class="note">renewed %s</small>' % ("once" if loan["renewals"] == 1 else "twice")
        return out

    def loan_rows(self, loans, back, borrower=True):
        rows = []
        for loan in loans:
            # "Copies" leads to the title's copies, where a book that will not come back is marked lost (L0031).
            acts = '<a href="/titles/%d">Copies</a>' % loan["title_id"] + button("/loans/%d/return" % loan["id"], "Return", back)
            if loan["renewals"] < RENEWALS:
                acts += button("/loans/%d/renew" % loan["id"], "Renew", back)
            cells = [("num", str(loan["copy_id"])), ("", e(loan["title"]))]
            if borrower:
                cells.append(("", e(loan["name"]) + (" (%s)" % e(loan["class"]) if loan["class"] else "")))
            cells += [("tag", self.due(loan)), ("act", acts)]
            rows.append((' id="loan-%d"' % loan["id"], cells))
        return rows

    def desk(self, query):
        lib = self.lib
        out_now = lib.one("SELECT COUNT(*) AS n FROM loans WHERE returned IS NULL AND lost IS NULL")["n"]
        late = lib.one("SELECT COUNT(*) AS n FROM loans WHERE returned IS NULL AND lost IS NULL AND due < ?", lib.today())["n"]
        return "Desk", (
            "<h1>Library desk</h1>"
            '<p>Today is %s. <a href="/loans">%d book%s out</a>, <a href="/overdue">%d overdue</a>.</p>'
            % (e(lib.today()), out_now, "" if out_now == 1 else "s", late)
            + "<h2>Lend a book</h2><p>Find the borrower; their page has the form.</p>"
            + search_form("/borrowers", "Borrower: name or class", "")
            + "<h2>Take a book back</h2><p>Find the loan by the number on the copy.</p>"
            + search_form("/loans", "Loan: copy number, title or borrower", ""))

    def titles(self, query):
        lib, typed = self.lib, search(query)
        where, values = "", []
        if typed:
            where = ("WHERE fold(title) LIKE ? ESCAPE '\\' OR fold(author) LIKE ? ESCAPE '\\' OR fold(shelf) LIKE ? ESCAPE '\\' "
                     "OR isbn LIKE ? ESCAPE '\\'")
            values = [like(typed)] * 3 + [like(typed.replace("-", ""))]
        total = lib.one("SELECT COUNT(*) AS n FROM titles " + where, *values)["n"]
        found = lib.all("SELECT t.*, (SELECT COUNT(*) FROM copies c WHERE c.title_id = t.id) AS copies, "
                        "(SELECT COUNT(*) FROM copies c WHERE c.title_id = t.id AND c.status = 'available' AND NOT EXISTS "
                        "(SELECT 1 FROM loans l WHERE l.copy_id = c.id AND l.returned IS NULL AND l.lost IS NULL)) AS free "
                        "FROM titles t %s ORDER BY title COLLATE NOCASE, id LIMIT %d" % (where, SHOWN), *values)
        rows = [("", [("", e(row["title"])), ("", e(row["author"])), ("num", e(row["isbn"])), ("tag", e(row["shelf"])),
                      ("num", "%d of %d" % (row["free"], row["copies"])),
                      ("act", '<a href="/titles/%d">Copies</a><a href="/titles/%d/edit">Edit</a>' % (row["id"], row["id"]))])
                for row in found]
        return "Catalogue", (
            "<h1>Catalogue</h1>" + search_form("/titles", "Search title, author, ISBN or shelf mark", typed)
            + counted(len(found), total, "title", "titles", typed)
            + (table(["Title", "Author", "ISBN", "Shelf", "On the shelf", ""], rows) if rows else "")
            + "<h2>Add a title</h2>" + title_form("/titles"))

    def title(self, ident):
        lib = self.lib
        row = lib.row("titles", ident, "title")
        copies = lib.all("SELECT c.*, l.id AS loan, l.due, l.renewals, l.borrower_id, b.name FROM copies c "
                         "LEFT JOIN loans l ON l.copy_id = c.id AND l.returned IS NULL AND l.lost IS NULL "
                         "LEFT JOIN borrowers b ON b.id = l.borrower_id WHERE c.title_id = ? ORDER BY c.id", ident)
        rows = []
        for copy in copies:
            if copy["loan"] is not None:
                status, who, due = "on loan", e(copy["name"]), self.due(copy)
                acts = ('<a href="/borrowers/%d">Borrower</a>' % copy["borrower_id"]
                        + '<form method="post" action="/copies/%d/status"><input type="hidden" name="status" value="lost">'
                          '<button type="submit">Mark lost</button></form>' % copy["id"])
            else:
                status, who, due = copy["status"], "", ""
                acts = "".join(
                    '<form method="post" action="/copies/%d/status"><input type="hidden" name="status" value="%s">'
                    '<button type="submit">%s</button></form>' % (copy["id"], other, label)
                    for other, label in (("available", "Mark available"), ("lost", "Mark lost"), ("withdrawn", "Mark withdrawn"))
                    if other != copy["status"])
            rows.append(("", [("num", str(copy["id"])), ("num", e(status)), ("", who), ("tag", due), ("act", acts)]))
        about = ", ".join(e(part) for part in (row["author"], row["isbn"] and "ISBN " + row["isbn"],
                                               row["shelf"] and "shelf " + row["shelf"]) if part)
        return row["title"], (
            "<h1>%s</h1><p>%s <a href=\"/titles/%d/edit\">Edit</a></p>" % (e(row["title"]), about, ident)
            + '<p class="note">%d cop%s. The number of a copy is written on its label.</p>'
            % (len(copies), "y" if len(copies) == 1 else "ies")
            + table(["Copy", "Status", "With", "Due", ""], rows)
            + "<h2>Add copies</h2>"
            + '<form class="card" method="post" action="/titles/%d/copies">' % ident
            + field("How many", "copies", "", ' placeholder="1" required inputmode="numeric" maxlength="2"')
            + '<button type="submit">Add copies</button></form>')

    def title_edit(self, ident):
        row = self.lib.row("titles", ident, "title")
        return "Edit " + row["title"], ("<h1>Correct a title</h1>" + title_form("/titles/%d/edit" % ident, row, copies=False)
                                        + '<p><a href="/titles/%d">Back to its copies</a></p>' % ident)

    def borrowers(self, query):
        lib, typed = self.lib, search(query)
        where, values = "", []
        if typed:
            where, values = "WHERE fold(name) LIKE ? ESCAPE '\\' OR fold(class) LIKE ? ESCAPE '\\'", [like(typed)] * 2
        total = lib.one("SELECT COUNT(*) AS n FROM borrowers " + where, *values)["n"]
        found = lib.all("SELECT b.*, (SELECT COUNT(*) FROM loans l WHERE l.borrower_id = b.id AND l.returned IS NULL AND l.lost IS NULL) AS held, "
                        "(SELECT COUNT(*) FROM loans l WHERE l.borrower_id = b.id AND l.returned IS NULL AND l.lost IS NULL AND l.due < ?) AS late "
                        "FROM borrowers b %s ORDER BY name COLLATE NOCASE, id LIMIT %d" % (where, SHOWN), lib.today(), *values)
        rows = []
        for row in found:
            held = str(row["held"]) + ('<small class="late">%d overdue</small>' % row["late"] if row["late"] else "")
            rows.append(("", [("", e(row["name"])), ("tag", e(row["kind"]) + ("" if row["active"] else ", has left")),
                              ("tag", e(row["class"])), ("tag", held),
                              ("act", '<a href="/borrowers/%d">%s</a><a href="/borrowers/%d/edit">Edit</a>'
                               % (row["id"], "Lend" if row["active"] else "Loans", row["id"]))]))
        return "Borrowers", (
            "<h1>Borrowers</h1>" + search_form("/borrowers", "Search name or class", typed)
            + counted(len(found), total, "borrower", "borrowers", typed)
            + (table(["Name", "Kind", "Class", "Books out", ""], rows) if rows else "")
            + "<h2>Add a borrower</h2>" + borrower_form("/borrowers"))

    def borrower(self, ident):
        lib = self.lib
        row = lib.row("borrowers", ident, "borrower")
        loans = lib.all(OPEN_LOANS + "WHERE l.borrower_id = ? AND l.returned IS NULL AND l.lost IS NULL ORDER BY l.due, l.id", ident)
        late = [loan for loan in loans if loan["due"] < lib.today()]
        back = lib.one("SELECT COUNT(*) AS n FROM loans WHERE borrower_id = ? AND returned IS NOT NULL", ident)["n"]
        gone = lib.one("SELECT COUNT(*) AS n FROM loans WHERE borrower_id = ? AND lost IS NOT NULL", ident)["n"]
        limit = LIMIT[row["kind"]]
        body = "<h1>%s</h1><p>%s%s%s. <a href=\"/borrowers/%d/edit\">Edit</a></p>" % (
            e(row["name"]), "Pupil" if row["kind"] == "pupil" else "Staff",
            ", class " + e(row["class"]) if row["class"] else "", "" if row["active"] else ", has left the school", ident)
        if late:
            body += '<p class="late">%d book%s overdue. They may still borrow; it is your call.</p>' % (
                len(late), "" if len(late) == 1 else "s")
        if not row["active"]:
            body += '<p class="note">Has left the school and cannot borrow.</p>'
        elif len(loans) >= limit:
            body += '<p class="note">Has %d books out, the limit for %s. A book must come back before another goes out.</p>' % (
                len(loans), "a pupil" if row["kind"] == "pupil" else "staff")
        else:
            body += ('<form class="card" method="post" action="/loans"><input type="hidden" name="borrower_id" value="%d">' % ident
                     + field("Copy number, typed or scanned", "copy", "", ' required inputmode="numeric" maxlength="9" autocomplete="off" autofocus')
                     + '<button type="submit">Lend</button></form>')
        body += '<h2>Books out</h2><p class="note">%d of %d allowed. Returned so far: %d.%s</p>' % (
            len(loans), limit, back, " Lost while out: %d." % gone if gone else "")
        if loans:
            body += table(["Copy", "Title", "Due", ""], self.loan_rows(loans, "/borrowers/%d" % ident, borrower=False))
        return row["name"], body

    def borrower_edit(self, ident):
        row = self.lib.row("borrowers", ident, "borrower")
        return "Edit " + row["name"], ("<h1>Correct a borrower</h1>" + borrower_form("/borrowers/%d/edit" % ident, row)
                                       + '<p><a href="/borrowers/%d">Back to their loans</a></p>' % ident)

    def loans(self, query):
        lib, typed = self.lib, search(query)
        where, values = "", []
        if typed.isascii() and typed.isdigit():
            where, values = "AND l.copy_id = ? ", [int(typed) if len(typed) <= 18 else -1]
        elif typed:
            where, values = "AND (fold(t.title) LIKE ? ESCAPE '\\' OR fold(b.name) LIKE ? ESCAPE '\\') ", [like(typed)] * 2
        found = lib.all(OPEN_LOANS + "WHERE l.returned IS NULL AND l.lost IS NULL " + where + "ORDER BY l.due, l.id", *values)
        return "Loans", (
            "<h1>Books out</h1>" + search_form("/loans", "Search copy number, title or borrower", typed)
            + counted(len(found), len(found), "book out", "books out", typed)
            + (table(["Copy", "Title", "Borrower", "Due", ""], self.loan_rows(found, "/loans")) if found else ""))

    def overdue(self, query):
        """Overdue loans under their class. "7b" and "7B" are one class, headed by the spelling most borrowers
        on record have and, where two are equally common, the one that sorts first: capitals first (L0036)."""
        lib = self.lib
        found = lib.all(OPEN_LOANS + "WHERE l.returned IS NULL AND l.lost IS NULL AND l.due < ?", lib.today())
        found.sort(key=lambda loan: (loan["class"] == "", fold(loan["class"]), fold(loan["name"]), loan["due"], loan["id"]))
        shown = {}
        for row in lib.all("SELECT class, COUNT(*) AS n FROM borrowers GROUP BY class ORDER BY n DESC, class"):
            shown.setdefault(fold(row["class"]), row["class"])
        body = "<h1>Overdue</h1>" + counted(len(found), len(found), "book overdue", "books overdue", "")[:-5] + ", by class.</p>"
        groups = {}
        for loan in found:
            groups.setdefault(fold(loan["class"]), []).append(loan)
        for name, loans in groups.items():
            body += "<h2>%s</h2>" % ("Class " + e(shown[name]) if name else "No class")
            body += table(["Copy", "Title", "Borrower", "Due", ""], self.loan_rows(loans, "/overdue"))
        return "Overdue", body

    def returned(self, query):
        """The loans that have ended: returned, or lost while out and shown as such (L0031)."""
        lib = self.lib
        total = lib.one("SELECT COUNT(*) AS n FROM loans WHERE returned IS NOT NULL OR lost IS NOT NULL")["n"]
        gone = lib.one("SELECT COUNT(*) AS n FROM loans WHERE lost IS NOT NULL")["n"]
        found = lib.all(OPEN_LOANS + "WHERE l.returned IS NOT NULL OR l.lost IS NOT NULL "
                        "ORDER BY COALESCE(l.returned, l.lost) DESC, l.id DESC LIMIT %d" % SHOWN)
        rows = [(' id="loan-%d"' % loan["id"],
                 [("num", str(loan["copy_id"])), ("", e(loan["title"])),
                  ("", e(loan["name"]) + (" (%s)" % e(loan["class"]) if loan["class"] else "")),
                  ("num", e(loan["lent"])),
                  ("tag", e(loan["returned"]) if loan["lost"] is None
                   else e(loan["lost"]) + '<small class="late">lost, not returned</small>')]) for loan in found]
        return "Returned", (
            "<h1>Returned or lost</h1>" + counted(len(found), total, "loan that ended", "loans that ended", "", "latest").replace(
                "Search to find the rest.", "The whole record is in <a href=\"/export.json\">/export.json</a>.")
            + ('<p class="note">%d of them ended with the book marked lost while it was out.</p>' % gone if gone else "")
            + (table(["Copy", "Title", "Borrower", "Lent", "Ended"], rows) if rows else ""))

GET = [(r"/", "desk"), (r"/titles", "titles"), (r"/titles/(\d{1,9})", "title"), (r"/titles/(\d{1,9})/edit", "title_edit"),
       (r"/borrowers", "borrowers"), (r"/borrowers/(\d{1,9})", "borrower"), (r"/borrowers/(\d{1,9})/edit", "borrower_edit"),
       (r"/loans", "loans"), (r"/overdue", "overdue"), (r"/returned", "returned")]
POST = [(r"/titles", "add_title"), (r"/titles/(\d{1,9})/edit", "edit_title"), (r"/titles/(\d{1,9})/copies", "add_copies"),
        (r"/copies/(\d{1,9})/status", "mark_copy"), (r"/borrowers", "add_borrower"),
        (r"/borrowers/(\d{1,9})/edit", "edit_borrower"), (r"/loans", "lend"),
        (r"/loans/(\d{1,9})/return", "give_back"), (r"/loans/(\d{1,9})/renew", "renew")]
BACK = re.compile(r"/(loans|overdue|borrowers/\d{1,9}|titles/\d{1,9})")


def make_handler(library, port):
    pages = Pages(library)
    hosts = {"127.0.0.1:%d" % port, "localhost:%d" % port} | ({"127.0.0.1", "localhost"} if port == 80 else set())

    class Handler(BaseHTTPRequestHandler):
        server_version = "SchoolLibrary"

        def log_message(self, *args):
            pass

        def send(self, status, body, kind="text/html; charset=utf-8", location=None):
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "same-origin")
            self.send_header("Content-Security-Policy",
                             "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
            if location:
                self.send_header("Location", location)
            self.end_headers()
            self.wfile.write(data)

        def page(self, status, title, body):
            clock = ('<p class="clock">The date is set to %s by --today. Start without it for the real date.</p>'
                     % e(library.today()) if library.fixed_today else "")
            links = "".join('<a href="%s">%s</a>' % pair for pair in NAV)
            self.send(status, '<!doctype html><html lang="en"><head><meta charset="utf-8">'
                              '<meta name="viewport" content="width=device-width, initial-scale=1">'
                              "<title>%s – School library</title><style>%s</style></head><body>%s<nav>%s</nav><main>%s</main></body></html>"
                      % (e(title), STYLE, clock, links, body))

        def refuse(self, status, why):
            # Says only what holds for every form: a scanned field comes back empty on purpose (L0035).
            after = ("Nothing was changed. Use your browser’s Back button to return to the form." if status in (400, 413)
                     else 'Nothing was changed. <a href="/">To the desk</a>')
            self.page(status, "Not done", '<h1>Not done</h1><p class="late">%s</p><p class="note">%s</p>' % (e(why), after))

        def own(self):
            """A request to another host name, or a post from another site, is refused (L0007)."""
            host = self.headers.get("Host", "")
            if host not in hosts:
                return False
            if self.command != "GET":
                origin = self.headers.get("Origin")
                if origin is not None and origin != "http://" + host:
                    return False
                if self.headers.get("Sec-Fetch-Site", "same-origin") not in ("same-origin", "none"):
                    return False
            return True

        def route(self, routes):
            parts = urllib.parse.urlsplit(self.path)
            for pattern, name in routes:
                found = re.fullmatch(pattern, parts.path)
                if found:
                    return name, [int(group) for group in found.groups()], parts
            return None, [], parts

        def do_GET(self):
            if not self.own():
                return self.send(403, "Refused: this library answers only to its own pages on this machine.\n", "text/plain; charset=utf-8")
            name, groups, parts = self.route(GET)
            try:
                query = dict(urllib.parse.parse_qsl(parts.query, keep_blank_values=True, max_num_fields=20))
            except ValueError:
                return self.refuse(400, "The address has too many parts.")
            with library.lock:
                try:
                    if parts.path == "/export.json":
                        return self.send(200, json.dumps(library.export(), ensure_ascii=False, indent=1),
                                         "application/json; charset=utf-8")
                    if name is None:
                        if self.route(POST)[0]:
                            return self.refuse(405, "This address only takes a form; opening it does nothing.")
                        return self.refuse(404, "There is no page at this address.")
                    title, body = getattr(pages, name)(*(groups or [query]))
                except Refused as refused:
                    return self.refuse(404 if groups else 400, str(refused))
            self.page(200, title, body)

        def do_POST(self):
            if not self.own():
                return self.send(403, "Refused: this library answers only to its own pages on this machine.\n", "text/plain; charset=utf-8")
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                return self.refuse(400, "The form came without its length.")
            if length < 0:
                return self.refuse(400, "The form came without its length.")
            if length > FORM_BYTES:
                left = min(length, 1 << 22)
                while left > 0:  # take what was sent, so that the answer is read
                    left -= len(self.rfile.read(min(left, 65536))) or left
                return self.refuse(413, "The form is larger than %d bytes." % FORM_BYTES)
            try:
                form = dict(urllib.parse.parse_qsl(self.rfile.read(length).decode("utf-8"), keep_blank_values=True,
                                                   strict_parsing=length > 0, max_num_fields=50))
            except ValueError:
                return self.refuse(400, "The form could not be read.")
            name, groups, _ = self.route(POST)
            if name is None:
                if self.route(GET)[0]:
                    return self.refuse(405, "Nothing can be sent to this address.")
                return self.refuse(404, "There is no page at this address.")
            with library.lock:
                try:
                    library.db.execute("BEGIN IMMEDIATE")
                    where = getattr(library, name)(*groups, form)
                    library.db.execute("COMMIT")
                except Refused as refused:
                    library.db.execute("ROLLBACK")
                    return self.refuse(400, str(refused))
                except BaseException:
                    library.db.execute("ROLLBACK")
                    raise
            back = form.get("back", "")
            self.send(303, "", location=back if name in ("give_back", "renew") and BACK.fullmatch(back) else where)

        def other(self):
            self.refuse(405 if self.own() else 403, "This library only shows pages and takes forms.")

        do_PUT = do_DELETE = do_PATCH = other

    return Handler


def main():
    parser = argparse.ArgumentParser(description="A lending library for a school, for the staff at the desk.")
    parser.add_argument("--db", default="library.db", help="the SQLite file that holds everything (default: library.db)")
    parser.add_argument("--port", type=int, default=8000, help="the port on this machine (default: 8000)")
    parser.add_argument("--sample", action="store_true", help="put demonstration data into an empty file")
    parser.add_argument("--today", type=datetime.date.fromisoformat, metavar="YYYY-MM-DD",
                        help="run as if it were this day, to try out due dates; every page says so")
    args = parser.parse_args()
    library = Library(args.db, args.today.isoformat() if args.today else None)
    if args.sample:
        print("Sample data loaded." if library.sample() else "The file already holds data; no sample was loaded.")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(library, args.port))
    server.daemon_threads = True
    print("School library on http://127.0.0.1:%d/ (file: %s). Ctrl-C stops it." % (args.port, args.db), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()

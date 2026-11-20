"""What the cases over HTTP share. Not a case itself.

A case starts the product ("the shop": the first one was a pet shop) on a
scratch database and talks to it over HTTP, which is the only way in (L0006).
That makes the cases the contract a rebuilt product has to meet: the command
line below, the form fields, /export.json. No case reads the product's
source, and nothing here does either (L0019).

A case that belongs to one product names its pages itself and asks for that
product by its label. A case under a general label names none: what it needs
to know about the product in front of it is in surface/NAME.json, one file
per product, read by product() (L0024, L0034).

A wrong variant (L0002, L0019) is the same shop with one fault in front of
it: a function that stands in for the shop on the requests it names, and may
change the request, change the answer, or send requests of its own. It adds
to shop.acted each time it does something a right shop would not. The case
must fail on it, or the case is not testing its lesson; and a fault that
never acted has shown the case nothing (L0001).
"""
import http.client
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse

# The command line. SHOP lets the same cases be put to another build of the product.
# No product is known here until a case has asked for one with product() (L0034).
MAIN = os.environ.get("SHOP")


def label(text):
    return " ".join(text.split("#")[0].split()).lower()


def product(name=None):
    """The surface of one product, and from here on the product the cases start.

    Which one: the name given, or SURFACE, or the one label in product/LABELS
    that has a file in surface/. No product to find is a failure, not a skip."""
    global MAIN
    found = {}
    for file in sorted(os.listdir("surface")) if os.path.isdir("surface") else []:
        if file.endswith(".json"):
            with open(os.path.join("surface", file), encoding="utf-8") as handle:
                one = json.load(handle)
            found[label(one["label"])] = one
    name = name or os.environ.get("SURFACE")
    if name is None:
        try:
            with open(os.path.join("product", "LABELS"), encoding="utf-8") as handle:
                declared = [label(line) for line in handle]
        except OSError:
            declared = []
        named = [word for word in declared if word in found]
        if len(named) != 1:
            print("product/LABELS declares %d labels that have a surface in surface/ (%s): "
                  "there is no one product to put this case to" % (len(named), ", ".join(sorted(found)) or "none there"))
            sys.exit(1)
        name = named[0]
    if label(name) not in found:
        print("no surface/*.json is labelled '%s'" % name)
        sys.exit(1)
    MAIN = os.environ.get("SHOP") or found[label(name)]["main"]
    return found[label(name)]
# No site-packages and no environment: an import from outside the standard library stops the shop (L0006).
FLAGS = ["-S", "-E", "-s"]


class Failure(Exception):
    """The shop, or the wrong shop, did not do what the lesson says."""


class Broken(Exception):
    """A fault could not do its wrong thing. That is a defect of the case, not a refusal."""


class Ask:
    """One request on its way to the shop, for a fault to look at, change and send on."""

    def __init__(self, shop, method, path, pairs, headers):
        self.shop, self.method, self.path = shop, method, path
        self.pairs = [(name, str(value)) for name, value in pairs]
        self.headers = dict(headers or {})

    def all(self, name):
        return [value.strip() for other, value in self.pairs if other == name]

    def get(self, name):
        return (self.all(name) or [""])[0]

    def put(self, name, value):
        self.pairs = [pair for pair in self.pairs if pair[0] != name] + [(name, str(value))]

    def send(self):
        return self.shop.real(self.method, self.path, self.pairs, self.headers)


def fault(method, pattern):
    """Make a wrong variant of a function that answers in the shop's place.

    The function gets the shop, the request as an Ask, and the groups of the
    path's pattern, and returns (status, body). Requests that do not match go
    to the shop untouched."""
    def make(act):
        def install(shop):
            def front(ask):
                found = re.fullmatch(pattern, ask.path) if method in (None, ask.method) else None
                return act(shop, ask, *found.groups()) if found else ask.send()
            return front
        return install
    return make


class Shop:
    def __init__(self, db=None):
        self.checks = self.acted = 0
        self.front = self.wrapper = self.proc = None
        self.closing = []
        self.args = []  # what follows the usual command line, for a product that takes more
        self.dir = tempfile.mkdtemp()
        self.db = db or os.path.join(self.dir, "shop.db")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.port = probe.getsockname()[1]
        self.log = open(os.path.join(self.dir, "log"), "w+")

    def start(self):
        if MAIN is None:
            raise Failure("the case started a product without asking for its surface with product()")
        command = [sys.executable] + FLAGS
        if self.wrapper:  # a program that does one wrong thing and then runs the shop as it is
            path = os.path.join(self.dir, "wrong.py")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(self.wrapper)
            command.append(path)
        self.proc = subprocess.Popen(command + [MAIN, "--db", self.db, "--port", str(self.port)] + self.args,
                                     stdout=self.log, stderr=self.log)
        for _ in range(100):
            if self.proc.poll() is not None:
                break
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=1).close()
                return self
            except OSError:
                time.sleep(0.05)
        said = self.said().strip().splitlines()
        self.stop()
        raise Failure("the shop did not start: %s" % (said[-1] if said else "no output"))

    def restart(self, *args):
        """Stop the product and start it again on the same file, with these arguments after the usual ones."""
        self.proc.terminate()
        self.proc.wait(timeout=5)
        self.args = list(args)
        return self.start()

    def said(self):
        """What the shop has printed so far."""
        with open(self.log.name, encoding="utf-8", errors="replace") as handle:
            return handle.read()

    def stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        for close in self.closing:
            close()
        self.log.close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def real(self, method, path, pairs=(), headers=None):
        """One request to the shop itself, redirects not followed. Returns (status, body text)."""
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        send = dict(headers or {})
        body = None
        if method == "POST":
            body = urllib.parse.urlencode(list(pairs))
            send.setdefault("Content-Type", "application/x-www-form-urlencoded")
        try:
            conn.request(method, path, body=body, headers=send)
            answer = conn.getresponse()
            return answer.status, answer.read().decode("utf-8", "replace")
        except OSError as error:
            raise Failure("%s %s got no answer: %s" % (method, path, error))
        finally:
            conn.close()

    def state(self):
        """/export.json from the shop itself, for a fault that needs to know what is stored."""
        status, body = self.real("GET", "/export.json")
        if status != 200:
            raise Broken("/export.json answered %d to a fault" % status)
        return json.loads(body)

    def request(self, method, path, pairs=(), headers=None):
        """One request as the case sees it: through the fault, when there is one."""
        if self.front is None:
            return self.real(method, path, pairs, headers)
        try:
            return self.front(Ask(self, method, path, pairs, headers))
        except (Failure, Broken):
            raise
        except Exception as error:
            raise Broken("%s: %s" % (type(error).__name__, error))

    def export(self):
        status, body = self.request("GET", "/export.json")
        if status != 200:
            raise Failure("/export.json answered %d" % status)
        return json.loads(body)

    def expect(self, condition, what):
        if not condition:
            raise Failure("wrong: " + what)
        self.checks += 1

    def post(self, status, path, *pairs, **fields):
        """POST and require this status. 303 is accepted, 400 is refused."""
        got, body = self.request("POST", path, list(pairs) + list(fields.items()))
        self.expect(got == status, "POST %s %s answered %d, expected %d"
                    % (path, dict(list(pairs) + list(fields.items())), got, status))
        return body

    def add(self, table, *pairs, **fields):
        """Create a row through its form and return its id."""
        self.post(303, "/" + table, *pairs, **fields)
        return max(row["id"] for row in self.export()[table])

    def row(self, table, ident):
        for row in self.export()[table]:
            if row["id"] == ident:
                return row
        raise Failure("no row %s in %s" % (ident, table))


def attempt(checks, wrong=None):
    """Run the checks on the shop, or on the shop behind a fault. Returns (checks passed, times the fault acted)."""
    shop = Shop()
    try:
        if wrong:
            shop.front = wrong(shop)
        shop.start()
        checks(shop)
        return shop.checks, shop.acted
    except Failure as failure:
        failure.acted = shop.acted
        raise
    except Broken:
        raise
    except Exception as error:  # a broken product is a failed case, not a crashed one
        failure = Failure("%s: %s" % (type(error).__name__, error))
        failure.acted = shop.acted
        raise failure
    finally:
        shop.stop()


def run(checks, wrong):
    """Run the checks on the product, then on each wrong variant, and say what was measured."""
    try:
        passed, _ = attempt(checks)
    except Failure as failure:
        print(failure)
        sys.exit(1)
    if not passed or not wrong:
        print("%d checks and %d wrong variants: nothing was measured" % (passed, len(wrong)))
        sys.exit(1)
    acted = 0
    for name, install in wrong:
        try:
            attempt(checks, install)
        except Broken as broken:
            print("the fault of wrong variant '%s' broke: %s" % (name, broken))
            sys.exit(1)
        except Failure as failure:
            if not failure.acted:
                print("wrong variant '%s' never acted, and the case failed on it anyway: %s" % (name, failure))
                sys.exit(1)
            acted += failure.acted
            print("refused '%s': %s" % (name, failure))
            continue
        print("the case passes on a wrong variant: %s" % name)
        sys.exit(1)
    print("%d checks passed; %d of %d wrong variants refused, each after its fault acted (%d acts)"
          % (passed, len(wrong), len(wrong), acted))

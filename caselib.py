"""What the pet shop cases share. Not a case itself.

A case starts the shop on a scratch database and talks to it over HTTP, which
is the only way in (L0006). That makes the cases the contract a rebuilt
product has to meet: the command line below, the form fields, /export.json.

A wrong variant (L0002) is one piece of text in product/petshop.py replaced in
a scratch copy when the case runs. The case must fail on it, or the case is
not testing its lesson.
"""
import http.client
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse

MAIN = "petshop.py"


class Failure(Exception):
    pass


class Shop:
    def __init__(self, product="product", db=None):
        self.checks = 0
        self.dir = tempfile.mkdtemp()
        self.db = db or os.path.join(self.dir, "shop.db")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.port = probe.getsockname()[1]
        self.log = open(os.path.join(self.dir, "log"), "w+")
        self.proc = subprocess.Popen(
            [sys.executable, os.path.join(product, MAIN), "--db", self.db, "--port", str(self.port)],
            stdout=self.log, stderr=self.log)
        for _ in range(100):
            if self.proc.poll() is not None:
                break
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=1).close()
                return
            except OSError:
                time.sleep(0.05)
        self.log.seek(0)
        said = self.log.read().strip().splitlines()
        self.stop()
        raise Failure("the shop did not start: %s" % (said[-1] if said else "no output"))

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        self.log.close()
        shutil.rmtree(self.dir, ignore_errors=True)

    def request(self, method, path, pairs=(), headers=None):
        """One request, redirects not followed. Returns (status, body text)."""
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


def attempt(checks, product):
    shop = Shop(product)
    try:
        checks(shop)
        return shop.checks
    except Failure:
        raise
    except Exception as error:  # a broken product is a failed case, not a crashed one
        raise Failure("%s: %s" % (type(error).__name__, error))
    finally:
        shop.stop()


def run(checks, wrong):
    """Run the checks on the product, then on each wrong variant, and say what was measured."""
    try:
        passed = attempt(checks, "product")
    except Failure as failure:
        print(failure)
        sys.exit(1)
    if not passed or not wrong:
        print("%d checks and %d wrong variants: nothing was measured" % (passed, len(wrong)))
        sys.exit(1)
    for name, old, new in wrong:
        work = tempfile.mkdtemp()
        try:
            copy = os.path.join(work, "product")
            shutil.copytree("product", copy, ignore=shutil.ignore_patterns("__pycache__", "*.db*"))
            path = os.path.join(copy, MAIN)
            with open(path, encoding="utf-8") as handle:
                source = handle.read()
            if source.count(old) != 1:
                print("wrong variant '%s' cannot be applied: its text occurs %d times in product/%s"
                      % (name, source.count(old), MAIN))
                sys.exit(1)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(source.replace(old, new))
            try:
                attempt(checks, copy)
            except Failure:
                continue
            print("the case passes on a wrong variant: %s" % name)
            sys.exit(1)
        finally:
            shutil.rmtree(work, ignore_errors=True)
    print("%d checks passed; %d of %d wrong variants refused" % (passed, len(wrong), len(wrong)))

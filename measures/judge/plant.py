"""Planted trees for the measure of the Judge unit.

Every case of this measure builds a small repository in a temporary
directory -- a tiny `src/petshop/` package plus the measures of the four
known units, following the conventions of `units/judge/unit.md` -- changes
it to plant what the case is about, commits it in a fresh git repository and
runs the judge through its declared interface only:

    python3 -m units.judge.verdict <command>

with the planted tree as the working directory (the judge is "run from the
repository root") and the judge under test made importable through
PYTHONPATH.

Which judge is under test (first match wins):
  1. the environment variable JUDGE_ROOT, a directory holding units/judge/;
  2. the first PYTHONPATH entry holding units/judge/verdict(.py);
  3. the real repository root, two levels above this file.
The subprocess gets PYTHONPATH set to exactly that directory, nothing else,
so the planted tree's `src/` is reachable only as the judge itself puts it on
the path. The planted tree never contains a `units/` directory, so `units`
always resolves to the judge under test.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

UNITS = ("catalog", "stock", "orders", "pet-shop")
MODULE = {"catalog": "catalog", "stock": "stock", "orders": "orders", "pet-shop": "app"}

# Seconds allowed for one call of the judge from this measure. A full
# `judge --base` runs every measure twice and every proof once; its budget is
# 10 minutes.
CALL_TIMEOUT = 300
# The judge's own timeout per measure is 120 s; a hanging measure must come
# back as a fail well before this.
HANG_CALL_TIMEOUT = 420


def _holds_judge(directory):
    judge = Path(directory) / "units" / "judge"
    return (judge / "verdict.py").is_file() or (judge / "verdict").is_dir()


def judge_root():
    """Directory placed on PYTHONPATH so that `units.judge.verdict` imports."""
    env = os.environ.get("JUDGE_ROOT")
    if env:
        return Path(env).resolve()
    for entry in os.environ.get("PYTHONPATH", "").split(os.pathsep):
        if entry and _holds_judge(entry):
            return Path(entry).resolve()
    return REPO_ROOT


# --------------------------------------------------------------------------
# The minimal tree: correct code and a passing measure for every unit, with
# one planted case per unit that fails its measure.
# --------------------------------------------------------------------------

CATALOG = '''\
import json

_ITEMS = {
    "bowl-1": {"sku": "bowl-1", "name": "Bowl", "kind": "supply", "price_cents": 250},
    "cat-1": {"sku": "cat-1", "name": "Tom", "kind": "pet", "price_cents": 5000},
}


def get(sku):
    item = _ITEMS.get(sku)
    return dict(item) if item else None


def listing():
    return json.dumps([_ITEMS[k] for k in sorted(_ITEMS)])
'''

# Wrong catalog: an unknown sku returns an item. Used both as a planted case
# and as buggy `src/` (number 1/2 under the catalog measure).
CATALOG_WRONG = '''\
# Defect: an unknown sku returns an item instead of None.
import json

_ITEMS = {
    "bowl-1": {"sku": "bowl-1", "name": "Bowl", "kind": "supply", "price_cents": 250},
    "cat-1": {"sku": "cat-1", "name": "Tom", "kind": "pet", "price_cents": 5000},
}


def get(sku):
    return dict(_ITEMS.get(sku, _ITEMS["cat-1"]))


def listing():
    return json.dumps([_ITEMS[k] for k in sorted(_ITEMS)])
'''

STOCK = '''\
_LEVELS = {"cat-1": 1, "bowl-1": 10}


def available(sku):
    return _LEVELS.get(sku, 0)
'''

ORDERS = '''\
from petshop import catalog


def total_cents(lines):
    return sum(catalog.get(sku)["price_cents"] * qty for sku, qty in lines)
'''

APP = '''\
import json


def application(environ, start_response):
    body = json.dumps({"error": "not found"}).encode()
    start_response("404 Not Found", [("Content-Type", "application/json")])
    return [body]
'''

TEST_CATALOG = '''\
import unittest

from petshop import catalog


class CatalogTest(unittest.TestCase):
    def test_known_sku(self):
        self.assertEqual(catalog.get("cat-1")["price_cents"], 5000)

    def test_unknown_sku(self):
        self.assertIsNone(catalog.get("nope"))
'''

TEST_STOCK = '''\
import unittest

from petshop import stock


class StockTest(unittest.TestCase):
    def test_known_sku(self):
        self.assertEqual(stock.available("cat-1"), 1)

    def test_unknown_sku(self):
        self.assertEqual(stock.available("nope"), 0)
'''

TEST_ORDERS = '''\
import unittest

from petshop import orders


class OrdersTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(orders.total_cents([("cat-1", 1), ("bowl-1", 2)]), 5500)

    def test_empty(self):
        self.assertEqual(orders.total_cents([]), 0)
'''

TEST_APP = '''\
import json
import unittest

from petshop import app


class AppTest(unittest.TestCase):
    def call(self, method, path):
        seen = {}

        def start_response(status, headers):
            seen["status"] = status
            seen["headers"] = dict(headers)

        body = b"".join(app.application({"REQUEST_METHOD": method, "PATH_INFO": path}, start_response))
        return seen, body

    def test_unknown_path_is_404(self):
        seen, body = self.call("GET", "/nope")
        self.assertTrue(seen["status"].startswith("404"))
        self.assertIn("error", json.loads(body))

    def test_json_content_type(self):
        seen, _ = self.call("GET", "/nope")
        self.assertEqual(seen["headers"]["Content-Type"], "application/json")
'''

PLANTED = {
    "catalog": ("wrong_unknown", CATALOG_WRONG),
    "stock": ("wrong_unknown", '''\
# Defect: an unknown sku reports one available.
_LEVELS = {"cat-1": 1, "bowl-1": 10}


def available(sku):
    return _LEVELS.get(sku, 1)
'''),
    "orders": ("wrong_qty", '''\
# Defect: the quantity of a line is ignored.
from petshop import catalog


def total_cents(lines):
    return sum(catalog.get(sku)["price_cents"] for sku, qty in lines)
'''),
    "pet-shop": ("wrong_status", '''\
# Defect: an unknown path answers 200.
import json


def application(environ, start_response):
    body = json.dumps({"error": "not found"}).encode()
    start_response("200 OK", [("Content-Type", "application/json")])
    return [body]
'''),
}


def base_files():
    files = {
        ".gitignore": "__pycache__/\n*.pyc\n",
        "src/petshop/__init__.py": '"""Planted pet shop."""\n',
        "src/petshop/catalog.py": CATALOG,
        "src/petshop/stock.py": STOCK,
        "src/petshop/orders.py": ORDERS,
        "src/petshop/app.py": APP,
        "measures/catalog/test_catalog.py": TEST_CATALOG,
        "measures/stock/test_stock.py": TEST_STOCK,
        "measures/orders/test_orders.py": TEST_ORDERS,
        "measures/pet-shop/test_app.py": TEST_APP,
    }
    for unit, (case, text) in PLANTED.items():
        files["measures/%s/planted/%s.py" % (unit, case)] = text
    return files


# --------------------------------------------------------------------------
# Tree and calls
# --------------------------------------------------------------------------

GIT = ["git", "-c", "user.name=planted", "-c", "user.email=planted@example.invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]


class Result:
    def __init__(self, args, proc):
        self.args = args
        self.code = proc.returncode
        self.stdout = proc.stdout
        self.stderr = proc.stderr
        try:
            self.data = json.loads(proc.stdout)
        except ValueError:
            self.data = None

    def describe(self):
        return "judge %s -> exit %s\nstdout: %s\nstderr: %s" % (
            " ".join(self.args), self.code, self.stdout[-2000:], self.stderr[-2000:])


class Tree:
    """A planted repository in a temporary directory."""

    def __init__(self):
        self.path = Path(tempfile.mkdtemp(prefix="judge-measure-"))
        for rel, text in base_files().items():
            self.write(rel, text)
        self._git("init", "-q")

    def cleanup(self):
        shutil.rmtree(self.path, ignore_errors=True)

    def write(self, rel, text):
        target = self.path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def read(self, rel):
        return (self.path / rel).read_text()

    def remove(self, rel):
        target = self.path / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()

    def insert_line(self, rel, line_text, after=0):
        """Insert one line after line `after` (0 = top); return its line number."""
        lines = self.read(rel).splitlines(True)
        lines.insert(after, line_text.rstrip("\n") + "\n")
        self.write(rel, "".join(lines))
        return after + 1

    def append(self, rel, text):
        """Append text; return the line number its first line lands on."""
        current = self.read(rel)
        if not current.endswith("\n"):
            current += "\n"
        first = current.count("\n") + 1
        self.write(rel, current + text)
        return first

    def _git(self, *args):
        subprocess.run(GIT + list(args), cwd=self.path, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    def commit(self, message="planted"):
        self._git("add", "-A")
        self._git("commit", "-q", "--allow-empty", "-m", message)

    def branch(self, name):
        self._git("branch", "-f", name)

    def run(self, *args, timeout=CALL_TIMEOUT, commit=True):
        """Run the judge on this tree; the working tree is committed first,
        so that what the judge reads equals HEAD."""
        if commit:
            self.commit()
        env = dict(os.environ)
        env.pop("JUDGE_ROOT", None)
        env["PYTHONPATH"] = str(judge_root())
        proc = subprocess.run(
            [sys.executable, "-m", "units.judge.verdict"] + list(args),
            cwd=self.path, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            timeout=timeout)
        return Result(list(args), proc)


class TreeCase:
    """Mixin for unittest.TestCase: a fresh planted tree per case."""

    def setUp(self):
        super().setUp()
        self.tree = Tree()
        self.addCleanup(self.tree.cleanup)

    # Assertions on a judge's answer ------------------------------------

    def assertDecision(self, res, passed):
        """Exit 0 and "pass": true, or exit 1 and "pass": false; one JSON object."""
        self.assertEqual(res.code, 0 if passed else 1, res.describe())
        self.assertIsInstance(res.data, dict, "stdout is not one JSON object\n" + res.describe())
        self.assertIs(res.data.get("pass"), passed, res.describe())

    def assertMalformed(self, res):
        self.assertEqual(res.code, 2, res.describe())

    def assertNumber(self, res, expected):
        number = res.data.get("number")
        self.assertIsInstance(number, (int, float), res.describe())
        self.assertAlmostEqual(number, expected, places=6, msg=res.describe())

    def violations(self, res):
        found = res.data.get("violations")
        self.assertIsInstance(found, list, res.describe())
        for v in found:
            self.assertIsInstance(v, dict, res.describe())
            for key in ("rule", "file", "line", "detail"):
                self.assertIn(key, v, res.describe())
        return found

    def assertViolation(self, res, rule, file, line=None):
        """A violation of `rule` in `file` (path relative to the tree; the judge
        may report it relative or absolute) and, if given, at `line`."""
        def matches(v):
            path = str(v["file"]).replace("\\", "/")
            if not (path == file or path.endswith("/" + file)):
                return False
            if rule not in str(v["rule"]):
                return False
            if line is not None and v["line"] != line:
                return False
            return True
        found = self.violations(res)
        self.assertTrue(any(matches(v) for v in found),
                        "no %s violation in %s at line %s\n%s" % (rule, file, line, res.describe()))

    def planted_status(self, res, case):
        planted = res.data.get("planted")
        self.assertIsInstance(planted, dict, res.describe())
        for key in (case, case + ".py"):
            if key in planted:
                return planted[key]
        self.fail("planted case %r not reported\n%s" % (case, res.describe()))

"""The Judge: decides whether a change to a unit below the root stands.

Interface and conventions: units/judge/unit.md (cited, not repeated).

    python3 -m units.judge.verdict build <unit>
    python3 -m units.judge.verdict verdict <unit>
    python3 -m units.judge.verdict proof <unit>
    python3 -m units.judge.verdict rules
    python3 -m units.judge.verdict judge --base <git-ref>

Every command prints one JSON object on stdout and exits 0 (pass), 1 (fail)
or 2 (malformed call). Diagnostics go to stderr. The repository judged is the
current working directory; only its `src/` and `measures/` are read (J2), and
code from `src/` is only ever imported inside the measure processes (J1).
Python 3 standard library only.
"""

import ast
import io
import json
import os
import py_compile
import re
import signal
import subprocess
import sys
import tarfile
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UNITS = ("catalog", "stock", "orders", "pet-shop")
MODULE = {"catalog": "catalog", "stock": "stock", "orders": "orders", "pet-shop": "app"}
PACKAGE = "petshop"
MEASURE_TIMEOUT = 120  # seconds per measure run; a timeout is a fail
WORKERS = max(1, min(4, os.cpu_count() or 1))


class Malformed(Exception):
    """A malformed call: exit 2."""


def log(message):
    print("judge: %s" % message, file=sys.stderr)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def build(root):
    """Byte-compile every .py under src/ into a fresh temporary directory."""
    src = Path(root) / "src"
    files = sorted(p for p in src.rglob("*.py") if p.is_file()) if src.is_dir() else []
    if not files:
        log("build: no Python source under %s" % src)
        return False
    ok = True
    with tempfile.TemporaryDirectory(prefix="judge-build-") as out:
        for path in files:
            target = Path(out) / path.relative_to(src).with_suffix(".pyc")
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                py_compile.compile(str(path), cfile=str(target), doraise=True)
            except py_compile.PyCompileError as exc:
                log("build: %s" % exc.msg)
                ok = False
    return ok


# --------------------------------------------------------------------------
# Running a measure: one fresh process per run
# --------------------------------------------------------------------------

# Runs in a fresh interpreter (-I -B): imports what it needs before any
# measure puts src/ on the path, optionally loads a planted file in place of
# petshop.<module>, discovers measures/<unit>/test_*.py and writes the counts
# to a result file (not stdout, which the measure may use).
RUNNER = r'''
import importlib.util, json, sys, unittest
measure_dir, src_dir, result_file, module, planted = sys.argv[1:6]

class Counting(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.seen = []
        self.bad = set()
    def startTest(self, test):
        super().startTest(test)
        self.seen.append(test.id())
    def _bad(self, test, *rest):
        self.bad.add(test.id())
    def addFailure(self, test, err):
        super().addFailure(test, err); self._bad(test)
    def addError(self, test, err):
        super().addError(test, err); self._bad(test)
    def addSkip(self, test, reason):
        super().addSkip(test, reason); self._bad(test)
    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test); self._bad(test)
    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self._bad(test)

sys.path.insert(0, src_dir)
if planted:
    package = __import__("petshop")
    name = "petshop." + module
    try:
        spec = importlib.util.spec_from_file_location(name, planted)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        setattr(package, module, mod)
    except BaseException as exc:
        # the planted case cannot be loaded: it tests nothing
        sys.stderr.write("planted case does not load: %r\n" % (exc,))
        with open(result_file, "w") as f:
            json.dump({"load_error": "%s: %s" % (type(exc).__name__, exc)}, f)
        sys.exit(0)

suite = unittest.defaultTestLoader.discover(measure_dir, pattern="test_*.py", top_level_dir=measure_dir)
result = Counting()
suite.run(result)
for test, err in result.errors + result.failures:
    sys.stderr.write("%s\n%s\n" % (test.id(), err))
cases = len(result.seen)
passed = len([t for t in result.seen if t not in result.bad])
with open(result_file, "w") as f:
    json.dump({"cases": cases, "passed": passed}, f)
'''


def run_measure(root, unit, planted=None):
    """Run the measure of `unit` in `root` against root/src (with `planted`
    in place of the unit's module). Return (number, cases, error); error is
    "error" when a planted case cannot be loaded (or its run crashes before
    reporting), else None."""
    root = Path(root).resolve()
    measure = root / "measures" / unit
    if not measure.is_dir() or not any(measure.glob("test_*.py")):
        log("%s: no measure at %s" % (unit, measure))
        return 0.0, 0, None
    fd, result_file = tempfile.mkstemp(prefix="judge-result-", suffix=".json")
    os.close(fd)
    os.unlink(result_file)
    cmd = [sys.executable, "-I", "-B", "-c", RUNNER, str(measure), str(root / "src"),
           result_file, MODULE[unit], str(planted) if planted else ""]
    try:
        proc = subprocess.Popen(cmd, cwd=str(root), stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        try:
            out, err = proc.communicate(timeout=MEASURE_TIMEOUT)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                proc.kill()
            proc.communicate()
            log("%s%s: measure timed out after %d s" % (
                unit, " (planted %s)" % Path(planted).stem if planted else "", MEASURE_TIMEOUT))
            return 0.0, 0, None
        try:
            with open(result_file) as f:
                counts = json.load(f)
        except (OSError, ValueError):
            log("%s: measure produced no result (exit %s)\n%s" % (
                unit, proc.returncode, err.decode(errors="replace")[-2000:]))
            return 0.0, 0, ("error" if planted else None)
    finally:
        try:
            os.unlink(result_file)
        except OSError:
            pass
    if "load_error" in counts:
        log("%s: planted %s does not load: %s" % (unit, Path(planted).stem, counts["load_error"]))
        return 0.0, 0, "error"
    cases, passed = int(counts.get("cases", 0)), int(counts.get("passed", 0))
    if not planted and passed < cases:
        log("%s: %d/%d cases pass\n%s" % (unit, passed, cases, err.decode(errors="replace")[-4000:]))
    return (passed / cases if cases else 0.0), cases, None


def verdict(root, unit):
    number, cases, _ = run_measure(root, unit)
    return number, (cases > 0 and number == 1)


def planted_cases(root, unit):
    directory = Path(root) / "measures" / unit / "planted"
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.py") if p.is_file())


def proof(root, unit, pool=None):
    cases = planted_cases(root, unit)
    if not cases:
        log("%s: no planted case" % unit)
    run = (pool.map if pool else map)(lambda p: run_measure(root, unit, p), cases)
    planted = {p.stem: (error or ("passed" if number == 1 else "failed"))
               for p, (number, _, error) in zip(cases, run)}
    ok = bool(planted) and all(v == "failed" for v in planted.values())
    return planted, ok


# --------------------------------------------------------------------------
# rules: R1-R3 of units/pet-shop/unit.md on src/
# --------------------------------------------------------------------------

FORBIDDEN = ("socket", "urllib", "http.client", "smtplib", "subprocess", "ftplib", "ssl")
# Process and file effects through os/shutil/pathlib (R1, "no process or file effects").
OS_EFFECTS = {"system", "popen", "fork", "forkpty", "kill", "killpg", "remove", "unlink",
              "rename", "renames", "replace", "mkdir", "makedirs", "rmdir", "removedirs",
              "truncate", "open", "symlink", "link", "chmod", "chown", "mkfifo", "mknod",
              "startfile", "posix_spawn", "posix_spawnp"}
OS_EFFECT_PREFIXES = ("exec", "spawn")
PATH_WRITES = {"write_text", "write_bytes", "touch"}
OPEN_FUNCS = {"open"}
OPEN_MODULES = {"io", "builtins", "codecs", "os"}
WRITE_MODE = re.compile(r"[wax+]")

PERSONAL = {"email", "emails", "mail", "phone", "phones", "telephone", "mobile", "address",
            "addresses", "card", "cards", "iban", "ssn", "birth", "birthday", "birthdate",
            "dob", "surname", "firstname", "lastname", "fullname", "passport", "postcode",
            "zipcode", "street", "cvv", "cvc"}
NAME_QUALIFIERS = {"first", "last", "full", "given", "family", "customer", "client",
                   "buyer", "user", "owner", "person", "contact"}
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | set(sys.builtin_module_names)


def _tokens(name):
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return [t for t in re.split(r"[^a-zA-Z0-9]+", name.lower()) if t]


def personal_field(name):
    """Whether `name` names personal data of a customer (a plain `name` does not)."""
    if not isinstance(name, str) or not name:
        return False
    toks = _tokens(name)
    if any(t in PERSONAL for t in toks):
        return True
    for i, t in enumerate(toks):
        if t == "name" and i > 0 and toks[i - 1] in NAME_QUALIFIERS:
            return True
    return False


def _forbidden(module):
    for f in FORBIDDEN:
        if module == f or module.startswith(f + "."):
            return f
    return None


def _check_module(module, add, line, how):
    f = _forbidden(module)
    if f:
        add("R1", line, "%s %s: forbidden module (network/process/file effect)" % (how, module))
        return
    top = module.split(".")[0]
    if top != PACKAGE and STDLIB and top not in STDLIB:
        add("R1", line, "%s %s: not in the standard library" % (how, module))


def _dotted(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _check_file(path, rel, violations):
    def add(rule, line, detail):
        violations.append({"rule": rule, "file": rel, "line": line, "detail": detail})

    try:
        tree = ast.parse(path.read_bytes(), filename=str(path))
    except (SyntaxError, ValueError) as exc:
        add("R1", getattr(exc, "lineno", None) or 1,
            "cannot be parsed, so R1-R3 cannot be checked: %s" % exc)
        return

    for node in ast.walk(tree):
        line = getattr(node, "lineno", 1)
        # R1: imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                _check_module(alias.name, add, line, "import")
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                _check_module(node.module, add, line, "from")
                for alias in node.names:
                    full = "%s.%s" % (node.module, alias.name)
                    if not _forbidden(node.module) and _forbidden(full):
                        add("R1", line, "from %s import %s: forbidden module" % (node.module, alias.name))
        elif isinstance(node, ast.Call):
            func = _dotted(node.func) or ""
            last = func.rsplit(".", 1)[-1] if func else getattr(node.func, "attr", "")
            # dynamic imports with a literal name
            if func in ("__import__", "importlib.import_module", "import_module") and node.args \
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                _check_module(node.args[0].value, add, line, func)
            # open( for writing
            mode = None
            is_open = False
            if func in OPEN_FUNCS or (func.count(".") == 1 and func.split(".")[0] in OPEN_MODULES
                                      and last == "open" and func != "os.open"):
                is_open = True
                if len(node.args) > 1:
                    mode = node.args[1]
            elif isinstance(node.func, ast.Attribute) and last == "open" and func != "os.open":
                is_open = True  # e.g. Path(...).open(mode)
                if node.args:
                    mode = node.args[0]
            if is_open:
                for kw in node.keywords:
                    if kw.arg == "mode":
                        mode = kw.value
                if mode is not None:
                    if not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
                        add("R1", line, "open( with a mode that is not a literal: may write")
                    elif WRITE_MODE.search(mode.value):
                        add("R1", line, "open( with mode %r: file effect" % mode.value)
            # os / shutil / pathlib effects
            if func.startswith("os.") and func.count(".") == 1 and (
                    last in OS_EFFECTS or last.startswith(OS_EFFECT_PREFIXES)):
                add("R1", line, "%s(: process or file effect" % func)
            elif func.startswith("shutil.") and func.count(".") == 1:
                add("R1", line, "%s(: file effect" % func)
            elif isinstance(node.func, ast.Attribute) and last in PATH_WRITES:
                add("R1", line, ".%s(: file effect" % last)
            # R2: keyword argument names
            for kw in node.keywords:
                if kw.arg and personal_field(kw.arg):
                    add("R2", getattr(kw, "lineno", line), "keyword argument %r: personal data" % kw.arg)
        # R2: dict keys, subscripts, attributes, arguments, class fields
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if isinstance(key, ast.Constant) and personal_field(key.value):
                    add("R2", key.lineno, "dict key %r: personal data" % key.value)
        elif isinstance(node, ast.Subscript):
            key = node.slice
            if isinstance(key, ast.Constant) and personal_field(key.value):
                add("R2", line, "key %r: personal data" % key.value)
        elif isinstance(node, ast.Attribute):
            if personal_field(node.attr):
                add("R2", line, "attribute %r: personal data" % node.attr)
        elif isinstance(node, ast.arg):
            if personal_field(node.arg):
                add("R2", line, "argument %r: personal data" % node.arg)
        elif isinstance(node, ast.ClassDef):
            for stmt in node.body:
                targets = []
                if isinstance(stmt, ast.AnnAssign):
                    targets = [stmt.target]
                elif isinstance(stmt, ast.Assign):
                    targets = stmt.targets
                for t in targets:
                    if isinstance(t, ast.Name) and personal_field(t.id):
                        add("R2", t.lineno, "class field %r: personal data" % t.id)
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, (ast.Tuple, ast.List)) \
                        and any(isinstance(t, ast.Name) and t.id == "__slots__" for t in stmt.targets):
                    for elt in stmt.value.elts:
                        if isinstance(elt, ast.Constant) and personal_field(elt.value):
                            add("R2", elt.lineno, "slot %r: personal data" % elt.value)


def rules(root):
    root = Path(root)
    src = root / "src"
    violations = []
    if src.is_dir():
        for path in sorted(p for p in src.rglob("*") if p.is_file()):
            rel = path.relative_to(root).as_posix()
            parts = path.relative_to(src).parts
            if "__pycache__" in parts:
                continue
            if path.suffix in (".so", ".pyd", ".dll", ".dylib", ".pth"):
                violations.append({"rule": "R1", "file": rel, "line": 1,
                                   "detail": "binary or path-hook code: not checkable as standard library only"})
                continue
            if path.suffix != ".py":
                continue
            if parts[0] != PACKAGE or len(parts) < 2:
                violations.append({"rule": "R3", "file": rel, "line": 1,
                                   "detail": "code outside src/%s/" % PACKAGE})
            _check_file(path, rel, violations)
    # one violation per (rule, file, line, detail)
    seen, unique = set(), []
    for v in violations:
        key = (v["rule"], v["file"], v["line"], v["detail"])
        if key not in seen:
            seen.add(key)
            unique.append(v)
    return {"violations": unique, "pass": not unique}


# --------------------------------------------------------------------------
# judge --base <ref>
# --------------------------------------------------------------------------

def _git(root, *args, binary=False):
    proc = subprocess.run(["git"] + list(args), cwd=str(root), stdin=subprocess.DEVNULL,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise Malformed("git %s: %s" % (" ".join(args), proc.stderr.decode(errors="replace").strip()))
    return proc.stdout if binary else proc.stdout.decode()


def export_base(root, ref, into):
    """Extract `src/` and `measures/` of commit `ref` into `into` (git archive;
    the repository and its worktrees are not touched)."""
    commit = _git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}").strip()
    present = [p for p in ("src", "measures")
               if _git(root, "ls-tree", "--name-only", commit, p).strip()]
    if not present:
        return commit
    data = _git(root, "archive", "--format=tar", commit, *present, binary=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        try:
            tar.extractall(into, filter="data")
        except TypeError:  # Python without extraction filters
            safe = [m for m in tar.getmembers()
                    if not (m.name.startswith("/") or ".." in Path(m.name).parts)
                    and (m.isfile() or m.isdir())]
            tar.extractall(into, members=safe)
    return commit


def judge(root, ref):
    try:
        _git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
    except Malformed:
        raise Malformed("unknown git ref %r" % ref)
    with tempfile.TemporaryDirectory(prefix="judge-base-") as base, \
            ThreadPoolExecutor(max_workers=WORKERS) as pool:
        export_base(root, ref, base)
        rules_result = rules(root)
        builds = {u: pool.submit(build, root) for u in UNITS}
        now = {u: pool.submit(verdict, root, u) for u in UNITS}
        then = {u: pool.submit(run_measure, base, u) for u in UNITS}
        units, ok = {}, rules_result["pass"]
        for u in UNITS:
            number, passed = now[u].result()
            base_number = then[u].result()[0]
            planted, proven = proof(root, u, pool)
            built = builds[u].result()
            units[u] = {"build": built, "number": number, "base_number": base_number,
                        "proof": proven}
            if not (built and passed and proven and number >= base_number):
                ok = False
                log("%s: build %s, verdict %s (number %s, base %s), proof %s %s" % (
                    u, built, passed, number, base_number, proven, planted))
    return {"units": units, "rules": rules_result, "pass": ok}


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

USAGE = ("usage: python3 -m units.judge.verdict "
         "build|verdict|proof <unit> | rules | judge --base <git-ref>; units: " + ", ".join(UNITS))


def _unit(args):
    if len(args) != 1:
        raise Malformed("expected exactly one unit")
    if args[0] not in UNITS:
        raise Malformed("unknown unit %r" % args[0])
    return args[0]


def dispatch(argv, root):
    if not argv:
        raise Malformed("no command")
    command, args = argv[0], argv[1:]
    if command == "build":
        unit = _unit(args)
        return {"unit": unit, "pass": build(root)}
    if command == "verdict":
        unit = _unit(args)
        number, passed = verdict(root, unit)
        return {"unit": unit, "number": number, "pass": passed}
    if command == "proof":
        unit = _unit(args)
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            planted, ok = proof(root, unit, pool)
        return {"unit": unit, "planted": planted, "pass": ok}
    if command == "rules":
        if args:
            raise Malformed("rules takes no argument")
        return rules(root)
    if command == "judge":
        if len(args) == 1 and args[0].startswith("--base="):
            ref = args[0][len("--base="):]
        elif len(args) == 2 and args[0] == "--base":
            ref = args[1]
        else:
            raise Malformed("judge needs --base <git-ref>")
        if not ref or ref.startswith("-"):
            raise Malformed("judge needs --base <git-ref>")
        return judge(root, ref)
    raise Malformed("unknown command %r" % command)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    root = Path.cwd()
    try:
        result = dispatch(argv, root)
    except Malformed as exc:
        print(json.dumps({"error": str(exc), "usage": USAGE, "pass": False}))
        return 2
    except Exception as exc:  # a judgement it cannot make fails, and is reported
        log("error: %r" % exc)
        print(json.dumps({"error": "%s: %s" % (type(exc).__name__, exc), "pass": False}))
        return 1
    print(json.dumps(result))
    return 0 if result.get("pass") is True else 1


if __name__ == "__main__":
    sys.exit(main())

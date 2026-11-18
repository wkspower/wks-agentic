"""Proof of the measure of the Judge unit.

    python3 measures/judge/prove.py            # prove the measure (exit 0 = proven)
    python3 measures/judge/prove.py --number   # the number against the judge under test

Proving does two things, neither using any judge:

1. Fixtures: in the planted tree, every unit's measure passes on src/, and
   every planted case, put in place of its module, fails it -- so the cases
   that expect the judge to pass or fail a unit expect the right thing.
2. Planted judges: the measure is run against each stub under
   measures/judge/planted/ (always_pass, always_fail), pointed at by
   PYTHONPATH, and must fail: its number must be below 1.

--number runs the measure in this process and prints
{"cases", "passed", "number"}; a skipped case counts as not passed. The judge
under test is chosen as described in plant.py (JUDGE_ROOT, PYTHONPATH, else
the repository root).
"""

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
STUBS = ("always_pass", "always_fail")


class Counting(unittest.TestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen = []
        self.bad = set()

    def startTest(self, test):
        super().startTest(test)
        self.seen.append(test.id())

    def _bad(self, test):
        self.bad.add(test.id())

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._bad(test)

    def addError(self, test, err):
        super().addError(test, err)
        self._bad(test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._bad(test)

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._bad(test)

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self._bad(test)


def number():
    sys.path.insert(0, str(REPO_ROOT))
    os.chdir(REPO_ROOT)
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py", top_level_dir=str(REPO_ROOT))
    result = Counting()
    suite.run(result)
    cases = len(result.seen)
    passed = len([t for t in result.seen if t not in result.bad])
    # errors outside any case (e.g. an import error) make the number 0
    if result.errors and not cases:
        cases = 1
    return {"cases": cases, "passed": passed, "number": passed / cases if cases else 0.0}


def run_measure(tree, unit, src):
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(tree / "measures" / unit), "-p", "test_*.py"],
        cwd=tree, env=dict(os.environ, PYTHONPATH=str(src)),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
    return proc.returncode == 0


def prove_fixtures():
    sys.path.insert(0, str(REPO_ROOT))
    from measures.judge import plant

    tree = plant.Tree()
    ok = True
    try:
        for unit in plant.UNITS:
            good = run_measure(tree.path, unit, tree.path / "src")
            print("fixture %-8s measure on src/ passes: %s" % (unit, good))
            ok &= good
            for case in sorted((tree.path / "measures" / unit / "planted").glob("*.py")):
                swapped = tree.path / ("swapped-%s-%s" % (unit, case.stem))
                shutil.copytree(tree.path / "src", swapped, ignore=shutil.ignore_patterns("__pycache__"))
                shutil.copy(case, swapped / "petshop" / (plant.MODULE[unit] + ".py"))
                failed = not run_measure(tree.path, unit, swapped)
                print("fixture %-8s planted %s fails the measure: %s" % (unit, case.stem, failed))
                ok &= failed
        wrong = tree.path / "swapped-catalog-src"
        shutil.copytree(tree.path / "src", wrong)
        (wrong / "petshop" / "catalog.py").write_text(plant.CATALOG_WRONG)
        failed = not run_measure(tree.path, "catalog", wrong)
        print("fixture catalog  buggy src/ fails the measure: %s" % failed)
        ok &= failed
    finally:
        tree.cleanup()
    return ok


def prove_stubs():
    ok = True
    for stub in STUBS:
        env = dict(os.environ)
        env.pop("JUDGE_ROOT", None)
        env["PYTHONPATH"] = str(HERE / "planted" / stub)
        proc = subprocess.run([sys.executable, str(HERE / "prove.py"), "--number"],
                              cwd=REPO_ROOT, env=env, stdout=subprocess.PIPE, text=True)
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        fails = result["number"] < 1
        print("stub %-11s number %.3f (%d/%d) -> measure fails: %s"
              % (stub, result["number"], result["passed"], result["cases"], fails))
        ok &= fails
    return ok


def main(argv):
    if argv == ["--number"]:
        import io
        real_stdout, sys.stdout = sys.stdout, io.StringIO()  # keep stdout to the result line
        try:
            result = number()
        finally:
            sys.stdout = real_stdout
        print(json.dumps(result))
        return 0 if result["number"] == 1 else 1
    if argv:
        print(__doc__)
        return 2
    fixtures = prove_fixtures()
    stubs = prove_stubs()
    proven = fixtures and stubs
    print("measure proven: %s" % proven)
    return 0 if proven else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

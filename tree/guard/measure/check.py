#!/usr/bin/env python3
"""Measure of the guard. Usage: check.py UNIT_DIR (the folder holding work/guard.py).
Each scenario plants one violation in a throwaway repository; the guard must
block it. Two controls must be allowed. Prints what it measured; exit 0 = pass."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture as fx

HERE = Path(__file__).resolve()


def ask(repo):
    done = fx.run(repo, "tree/guard/work/guard.py", "check", "tree/toy")
    try:
        return json.loads(done.stdout)
    except ValueError:
        return {"allowed": None, "kind": None}


def scenarios(repo):
    w = lambda path, text: fx.write(repo, path, text)
    doc = (repo / "tree/toy/unit.md").read_text()

    def blocked(name, plant):
        fx.reset(repo)
        plant()
        yield name, ask(repo)["allowed"] is False

    def allowed(name, kind, plant):
        fx.reset(repo)
        plant()
        answer = ask(repo)
        yield name, answer["allowed"] is True and answer["kind"] == kind

    yield from allowed("control: a change to the work alone is allowed", "work",
                       lambda: w("tree/toy/work/toy.py", fx.GOOD))
    yield from allowed("control: a change to the measure that keeps its proof is allowed", "give",
                       lambda: w("tree/toy/measure/planted/zero/work/toy.py", "def double(x):\n    return 0\n"))
    yield from blocked("nothing changed", lambda: None)
    yield from blocked("the work and its own measure in one change",
                       lambda: (w("tree/toy/work/toy.py", fx.WRONG),
                                w("tree/toy/measure/check.py", "print('{\"pass\": true, \"passed\": 3, \"total\": 3}')\n")))
    yield from blocked("the work and its own document in one change",
                       lambda: (w("tree/toy/work/toy.py", fx.GOOD), w("tree/toy/unit.md", doc + "\nmore\n")))
    yield from blocked("another unit touched",
                       lambda: (w("tree/toy/work/toy.py", fx.GOOD), w("tree/other/work/x.py", "x = 1\n")))
    yield from blocked("the root document touched",
                       lambda: (w("tree/toy/work/toy.py", fx.GOOD), w("root.md", (repo / "root.md").read_text() + "\n")))
    yield from blocked("the record touched",
                       lambda: (w("tree/toy/work/toy.py", fx.GOOD), w("record/ledger.jsonl", "{}\n")))
    yield from blocked("a declaration removed from the document",
                       lambda: w("tree/toy/unit.md", doc.replace("6. **Judge** — the judge.\n", "")))
    yield from blocked("a declaration left without value",
                       lambda: w("tree/toy/unit.md", doc.replace("the judge.", "not yet given.")))
    yield from blocked("a principle removed from the document",
                       lambda: w("tree/toy/unit.md", doc.replace("| 5 Return | x |\n", "")))
    yield from blocked("a parent that does not exist",
                       lambda: w("tree/toy/unit.md", doc.replace("../../root.md", "../nowhere.md")))
    yield from blocked("a document that is not short",
                       lambda: w("tree/toy/unit.md", doc + "more\n" * 100))
    yield from blocked("a measure left without planted case",
                       lambda: (repo / "tree/toy/measure/planted/adds/work/toy.py").unlink())
    yield from blocked("a measure its planted wrong result passes",
                       lambda: w("tree/toy/measure/check.py", "print('{\"pass\": true, \"passed\": 3, \"total\": 3}')\n"))
    yield from blocked("work that reaches the network",
                       lambda: w("tree/toy/work/toy.py", "import socket\n" + fx.GOOD))
    yield from blocked("work that reaches the network from inside a function",
                       lambda: w("tree/toy/work/toy.py", "def double(x):\n    from urllib import request\n    return x * 2\n"))
    yield from blocked("work that starts other programs",
                       lambda: w("tree/toy/work/toy.py", "import subprocess\n" + fx.GOOD))
    yield from blocked("a unit outside the tree",
                       lambda: w("elsewhere/work/toy.py", fx.GOOD))


def main(unit_dir):
    results = []
    try:
        repo = fx.make(HERE.parents[2], guard_work=Path(unit_dir).resolve() / "work")
        try:
            results = list(scenarios(repo))
        finally:
            fx.destroy(repo)
    except Exception as error:  # a guard that cannot even be tried has failed
        results.append((f"could not be tried: {error!r}", False))
    failed = [name for name, ok in results if not ok]
    passed = len(results) - len(failed)
    ok = bool(results) and not failed and len(results) >= 19
    print(json.dumps({"pass": ok, "passed": passed, "total": max(len(results), 19), "failed": failed}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

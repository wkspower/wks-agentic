#!/usr/bin/env python3
"""Measure of the judge. Usage: check.py UNIT_DIR (the folder holding work/judge.py).
In a throwaway repository the judge is given changes to a toy unit: the wrong
ones must not stand, the right ones must, and the undo must be proven by doing
it. Prints what it measured; exit 0 = pass."""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "guard" / "measure"))
import fixture as fx

TOY = "tree/toy/work/toy.py"


def scenarios(repo):
    judge = lambda *args: fx.run(repo, "tree/judge/work/judge.py", *(args or ("tree/toy",))).returncode
    head = lambda: fx.git(repo, "rev-parse", "HEAD").stdout.strip()
    clean = lambda: fx.git(repo, "status", "--porcelain").stdout.strip() == ""
    text = lambda: (repo / TOY).read_text() if (repo / TOY).exists() else None

    def ledger():
        path = repo / "record/ledger.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    last = lambda: ledger()[-1] if ledger() else {}
    stood = lambda: [e for e in ledger() if e.get("kind") == "work" and e.get("verdict") == "pass"
                     and e.get("judge") == "stand"]

    # 1. a violation never stands, whatever its verdict would be
    fx.write(repo, TOY, fx.WRONG)
    fx.write(repo, "tree/toy/measure/check.py", "print('{\"pass\": true, \"passed\": 3, \"total\": 3}')\n")
    before = head()
    code = judge()
    yield "a change that also rewrites its measure does not stand", code != 0 and not stood() \
        and fx.git(repo, "diff", "--name-only", before, "HEAD", "--", "tree").stdout.strip() == ""
    fx.reset(repo)

    # 2. the first build, right
    fx.write(repo, TOY, fx.GOOD)
    code = judge()
    entry = last()
    yield "a right first build stands", code == 0 and len(stood()) == 1 and clean()
    yield "what stands is committed, with its number and its undo", \
        fx.git(repo, "show", "HEAD:" + TOY).stdout == fx.GOOD and bool(entry.get("undo")) \
        and entry.get("number", {}).get("passed") == 3
    first = head()

    # 3. passing is not enough: it must be better by the same measure
    fx.write(repo, TOY, fx.SAME_SIZE)
    code = judge()
    yield "a change that passes but is not better does not stand", code != 0 and len(stood()) == 1 and head() != first \
        and fx.git(repo, "show", "HEAD:" + TOY).stdout == fx.GOOD
    yield "a refusal is told in the record", last().get("judge") == "refuse"
    fx.reset(repo)

    # 4. better stands
    fx.write(repo, TOY, fx.BETTER)
    code = judge()
    yield "a change that passes and is better stands", code == 0 and len(stood()) == 2 and clean()
    better = head()

    # 5. wrong does not stand; after the attempts of the budget the unit returns
    codes = []
    for attempt in range(3):
        fx.write(repo, TOY, fx.WRONG)
        codes.append(judge())
        if attempt == 0:
            yield "a wrong change does not stand and may be tried again", codes[0] != 0 and text() == fx.WRONG
    yield "after 3 failed attempts the unit is back at the last passing state", \
        all(codes) and text() == fx.BETTER and clean() and len(stood()) == 2 \
        and fx.git(repo, "show", "HEAD:" + TOY).stdout == fx.BETTER
    yield "the return is told in the record", last().get("judge") == "returned"

    # 6. the undo, proven by doing it
    target = stood()[-1]
    code = judge("--undo", str(target["id"]), "trial of the undo")
    yield "the undo of a standing change brings back the state before it, and is recorded", \
        code == 0 and text() == fx.GOOD and clean() and last().get("kind") == "revoke" \
        and last().get("revokes") == target["id"] and bool(target.get("commit"))

    # 7. changes to the measure, by the parent
    fx.write(repo, "tree/toy/measure/planted/zero/work/toy.py", "def double(x):\n    return 0\n")
    code = judge()
    yield "a change to the measure that keeps its proof stands, and is not counted as a result", \
        code == 0 and last().get("kind") == "give" and len(stood()) == 2 and clean()
    fx.write(repo, "tree/toy/measure/check.py", "print('{\"pass\": true, \"passed\": 3, \"total\": 3}')\n")
    code = judge()
    yield "a change to the measure that its planted cases pass does not stand", code != 0 and last().get("judge") == "refuse"
    fx.reset(repo)

    # 8. a result shown wrong later
    code = judge("--revoke", str(stood()[0]["id"]), "shown wrong by a case")
    yield "a standing result can be marked wrong, for the giver of the measure to see", \
        code == 0 and last().get("kind") == "revoke" and last().get("revokes") == stood()[0]["id"] and clean()

    # 9. the judge does not judge itself
    fx.write(repo, "tree/judge/work/judge.py", (repo / "tree/judge/work/judge.py").read_text() + "\n# changed\n")
    before = head()
    code = judge("tree/judge")
    yield "the judge does not decide a change to itself", code != 0 and \
        fx.git(repo, "diff", "--name-only", before, "HEAD", "--", "tree").stdout.strip() == ""
    fx.reset(repo)

    # 10. whoever runs the judge can sign its commits
    fx.write(repo, TOY, fx.BETTER)
    signed = dict(fx.ENV, TREE_COMMIT_TRAILER="Signed-By: someone\nSession: somewhere")
    done = subprocess.run([sys.executable, str(repo / "tree/judge/work/judge.py"), "tree/toy"], cwd=repo,
                          capture_output=True, text=True, env=signed)
    messages = [fx.git(repo, "log", "-1", "--format=%B", ref).stdout.rstrip() for ref in ("HEAD", "HEAD~1")]
    yield "the lines given in TREE_COMMIT_TRAILER end every commit the judge makes", \
        done.returncode == 0 and all(m.endswith("\n\nSigned-By: someone\nSession: somewhere") for m in messages)


EXPECTED = 15


def main(unit_dir):
    results = []
    try:
        repo = fx.make(HERE.parents[2], judge_work=Path(unit_dir).resolve() / "work")
        try:
            for result in scenarios(repo):
                results.append(result)
        finally:
            fx.destroy(repo)
    except Exception as error:
        results.append((f"could not be tried further: {error!r}", False))
    failed = [name for name, ok in results if not ok]
    passed = len(results) - len(failed)
    ok = len(results) == EXPECTED and not failed
    print(json.dumps({"pass": ok, "passed": passed, "total": EXPECTED, "failed": failed}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))

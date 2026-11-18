#!/usr/bin/env python3
"""The judge: decides whether a change to a unit stands.

Usage: judge.py UNIT                  decide the uncommitted change to UNIT
       judge.py --undo ID REASON      undo a standing change, and record it
       judge.py --revoke ID REASON    mark a standing result as shown wrong

A change stands only if the guard allows it, its verdict passes in rehearsal
and it is better, by the same measure, than what exists. What stands is
committed; what does not is recorded, and after the attempts of the budget the
unit is returned to its last passing state. Exit 0 = stands.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=ENV)


def attempts_allowed(root):
    found = re.search(r"\| `attempts_per_change` \| (\d+) \|", (root / "root.md").read_text())
    if not found:
        raise SystemExit("root.md gives no attempts_per_change: no budget, no effect")
    return int(found.group(1))


def read_ledger(root):
    path = root / "record" / "ledger.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def record(root, subject, **entry):
    """Append one line to the ledger and commit the record alone."""
    entries = read_ledger(root)
    entry = {"id": max([e["id"] for e in entries], default=0) + 1,
             "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **entry}
    (root / "record").mkdir(exist_ok=True)
    with open(root / "record" / "ledger.jsonl", "a") as book:
        book.write(json.dumps(entry) + "\n")
    git(root, "add", "record")
    git(root, "commit", "-qm", f"record: {subject} #{entry['id']}", "--", "record")
    return entry


def attempts(root, unit, value=None):
    path = root / "record" / "attempts.json"
    table = json.loads(path.read_text()) if path.exists() else {}
    if value is None:
        return table.get(unit, 0)
    table[unit] = value
    (root / "record").mkdir(exist_ok=True)
    path.write_text(json.dumps(table, indent=1, sort_keys=True) + "\n")


def verdict(measure_tree, unit, subject_tree):
    """Run the measure of `unit` found in measure_tree on the unit in subject_tree."""
    check = measure_tree / unit / "measure" / "check.py"
    done = subprocess.run([sys.executable, str(check), str(subject_tree / unit)], cwd=subject_tree,
                          capture_output=True, text=True, env=ENV, timeout=900)
    try:
        number = json.loads(done.stdout)
    except ValueError:
        number = {"pass": False, "passed": 0, "total": None, "failed": ["the measure printed no number"]}
    number["pass"] = bool(number.get("pass")) and done.returncode == 0
    work = subject_tree / unit / "work"
    number["lines"] = sum(1 for f in work.rglob("*.py") for line in f.read_text().splitlines() if line.strip()) \
        if work.is_dir() else 0
    return number


def rehearse(root, unit):
    """The place of principle 4: copies under .rehearsal/, ignored by git, from
    which nothing leaves. Returns the numbers of the candidate and of what exists."""
    place = root / ".rehearsal" / ("judge-" + unit.replace("/", "-"))
    shutil.rmtree(place, ignore_errors=True)
    (place / "exists").mkdir(parents=True)
    shutil.copytree(root / "tree", place / "candidate" / "tree")
    archive = subprocess.run(["git", "archive", "HEAD", "tree"], cwd=root, capture_output=True, env=ENV)
    subprocess.run(["tar", "-x", "-C", str(place / "exists")], input=archive.stdout, env=ENV)
    candidate = verdict(place / "candidate", unit, place / "candidate")
    exists = None
    if any((place / "exists" / unit / "work").rglob("*.py")):
        exists = verdict(place / "candidate", unit, place / "exists")  # the same measure
    shutil.rmtree(place, ignore_errors=True)
    return candidate, exists


def refuse(root, unit, kind, by, reasons, number=None):
    used = attempts(root, unit) + 1
    allowed = attempts_allowed(root)
    returned = used >= allowed
    if returned:  # principle 5: back to the last state where the verdict passed
        for part in ("work", "measure", "unit.md"):
            git(root, "checkout", "-q", "HEAD", "--", f"{unit}/{part}")
        git(root, "clean", "-fdq", "--", unit)
    attempts(root, unit, 0 if returned else used)
    record(root, f"{'returned' if returned else 'refuse'}: {unit}", unit=unit, kind=kind, by=by,
           verdict="pass" if number and number.get("pass") else "fail",
           judge="returned" if returned else "refuse", attempt=used, reasons=reasons, number=number)
    print(json.dumps({"stands": False, "attempt": f"{used} of {allowed}", "returned_to_last_passing_state": returned,
                      "reasons": reasons, "number": number}, indent=1))
    return 1


def decide(unit, root=ROOT, by="tree/judge"):
    unit = unit.strip("/")
    if unit == "tree/judge" and by != "tree/guard":
        print("The judge does not decide a change to itself; its judge is the guard:\n"
              "  python3 tree/guard/work/guard.py judge-the-judge")
        return 1
    asked = subprocess.run([sys.executable, str(root / "tree/guard/work/guard.py"), "check", unit],
                           cwd=root, capture_output=True, text=True, env=ENV)
    try:
        guard = json.loads(asked.stdout)
    except ValueError:
        guard = {"allowed": False, "kind": None, "reasons": ["the guard gave no answer"]}
    kind = guard.get("kind")
    if not guard.get("allowed"):
        if not guard.get("measured", {}).get("changed"):
            print(json.dumps({"stands": False, "reasons": guard["reasons"]}, indent=1))
            return 1
        return refuse(root, unit, kind, by, ["guard: " + r for r in guard["reasons"]])
    number = None
    if kind == "work":
        number, exists = rehearse(root, unit)
        if not number["pass"]:
            return refuse(root, unit, kind, by, ["the verdict fails in rehearsal"], number)
        if exists and exists["pass"] and not (number["passed"], -number["lines"]) > (exists["passed"], -exists["lines"]):
            return refuse(root, unit, kind, by,
                          [f"passes, but is not better than what exists: scenarios {number['passed']} against "
                           f"{exists['passed']}, lines {number['lines']} against {exists['lines']}"], number)
    paths = [f"{unit}/work"] if kind == "work" else [f"{unit}/unit.md", f"{unit}/measure"]
    paths = [p for p in paths if (root / p).exists() or git(root, "ls-files", "--", p).stdout.strip()]
    git(root, "add", "-A", "--", *paths)
    done = git(root, "commit", "-qm", f"stand: {unit} ({kind})", "--", *paths)
    if done.returncode:
        print(done.stdout + done.stderr)
        return 1
    commit = git(root, "rev-parse", "HEAD").stdout.strip()
    attempts(root, unit, 0)
    entry = record(root, f"stand: {unit}", unit=unit, kind=kind, by=by,
                   verdict="pass" if kind == "work" else "none", judge="stand", number=number,
                   commit=commit, undo=f"python3 tree/judge/work/judge.py --undo ID 'reason'  (git revert {commit[:12]})")
    print(json.dumps({"stands": True, "id": entry["id"], "kind": kind, "number": number, "commit": commit[:12]}, indent=1))
    return 0


def revoke(root, ident, reason, undo):
    target = next((e for e in read_ledger(root) if e.get("id") == ident and e.get("judge") == "stand"
                   and e.get("kind") in ("work", "give")), None)
    if not target:
        print(f"no standing change #{ident}")
        return 1
    if git(root, "status", "--porcelain").stdout.strip():
        print("there is a change in progress; decide it first")
        return 1
    if undo:
        done = git(root, "revert", "--no-edit", target["commit"])
        if done.returncode:
            git(root, "revert", "--abort")
            print("the undo does not apply cleanly; later changes stand on this one:\n" + done.stderr)
            return 1
    record(root, f"{'undo' if undo else 'revoke'}: {target['unit']}", unit=target["unit"], kind="revoke",
           revokes=ident, undone=undo, reason=reason, judge="stand",
           undo="git revert of the revert" if undo else "remove this line")
    print(json.dumps({"revoked": ident, "undone": undo}))
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3 and args[0] in ("--undo", "--revoke") and args[1].isdigit():
        sys.exit(revoke(ROOT, int(args[1]), args[2], args[0] == "--undo"))
    if len(args) == 1 and not args[0].startswith("-"):
        sys.exit(decide(args[0]))
    print(__doc__)
    sys.exit(2)

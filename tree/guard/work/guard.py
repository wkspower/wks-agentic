#!/usr/bin/env python3
"""The guard: enforces on every change the rules a unit cannot be trusted to
keep by itself. Usage: guard.py check UNIT   |   guard.py judge-the-judge

`check` looks at the uncommitted change in the repository as a change to UNIT
and prints {"allowed", "kind", "reasons", "measured"}; exit 0 = allowed.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
DECLARATIONS = ["Purpose", "Interface", "Rules", "Budget", "Measure", "Judge"]
PRINCIPLES = ["1 Boundary", "2 Single source", "3 External enforcement", "4 Rehearsal before effect",
              "5 Return", "6 Selection", "7 Escalation"]
DOC_LINES = 80
NETWORK = ["socket", "ssl", "urllib", "http", "ftplib", "smtplib", "poplib", "imaplib", "telnetlib",
           "xmlrpc", "requests", "httpx", "aiohttp", "webbrowser", "asyncio"]
PROCESS = ["subprocess", "multiprocessing", "pty", "ctypes"]
MAY_START_PROGRAMS = ["tree/judge", "tree/guard"]  # they run git and the measures
CALLS = [r"os\.system", r"os\.popen", r"os\.exec\w*", r"os\.spawn\w*", r"os\.fork", r"__import__", r"\beval\(", r"\bexec\("]


def changed():
    out = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=ROOT, capture_output=True,
                         text=True, env=ENV).stdout
    paths = []
    for line in out.splitlines():
        path = line[3:]
        paths.extend(part.strip('"') for part in path.split(" -> "))
    return sorted(set(paths))


def document(unit, reasons):
    doc = ROOT / unit / "unit.md"
    if not doc.exists():
        reasons.append(f"{unit}/unit.md does not exist: a unit without declarations causes no effect")
        return
    text = doc.read_text()
    lines = text.count("\n")
    if lines > DOC_LINES:
        reasons.append(f"document has {lines} lines; a unit's document is at most {DOC_LINES}")
    parent = re.search(r"^Parent: .*?\]\(([^)#]+)\)", text, re.M)
    if not parent:
        reasons.append("document names no parent")
    elif not (doc.parent / parent.group(1)).resolve().is_file():
        reasons.append(f"parent {parent.group(1)} does not exist")
    for number, name in enumerate(DECLARATIONS, 1):
        stated = re.search(rf"^{number}\. \*\*{name}\*\* — (.+)$", text, re.M)
        if not stated:
            reasons.append(f"declaration missing: {name}")
        elif re.search(r"not yet|to be defined|\bTBD\b", stated.group(1), re.I):
            reasons.append(f"declaration without value: {name}")
    for principle in PRINCIPLES:
        if not re.search(rf"^\| {principle} \| \S.*\|\s*$", text, re.M):
            reasons.append(f"principle not stated: {principle}")


def proof(unit, reasons, measured):
    check = ROOT / unit / "measure" / "check.py"
    if not check.exists():
        reasons.append("no measure/check.py: the measure is written before the unit")
        return
    planted = ROOT / unit / "measure" / "planted"
    cases = sorted(c for c in planted.iterdir() if c.is_dir() and any(f.is_file() for f in c.rglob("*"))) \
        if planted.is_dir() else []
    if not cases:
        reasons.append("the measure has no planted wrong result: it is not proven")
    for case in cases:
        done = subprocess.run([sys.executable, str(check), str(case)], cwd=ROOT, capture_output=True,
                              text=True, env=ENV)
        measured.setdefault("planted", {})[case.name] = "fails" if done.returncode else "PASSES"
        if done.returncode == 0:
            reasons.append(f"planted wrong result '{case.name}' passes the measure")


def reach(unit, reasons, measured):
    work = ROOT / unit / "work"
    banned = NETWORK + ([] if unit in MAY_START_PROGRAMS else PROCESS)
    files = sorted(f for f in work.rglob("*") if "__pycache__" not in f.parts) if work.is_dir() else []
    measured["work_files_scanned"] = len([f for f in files if f.is_file()])
    for file in files:
        if not file.is_file():
            continue
        if file.suffix != ".py":
            reasons.append(f"{file.relative_to(ROOT)}: only .py files are scanned, so only .py files may be work")
            continue
        text = file.read_text()
        for module in banned:
            if re.search(rf"^\s*(import\s+(.*,\s*)?{module}\b|from\s+{module}\b)", text, re.M):
                reasons.append(f"{file.relative_to(ROOT)}: uses {module}; effects stay in the repository")
        for call in CALLS if unit not in MAY_START_PROGRAMS else CALLS[:5]:
            if re.search(call, text):
                reasons.append(f"{file.relative_to(ROOT)}: uses {call}")
        if re.search("[\"']pu" + "sh[\"']", text):
            reasons.append(f"{file.relative_to(ROOT)}: sends the repository elsewhere")


def check(unit):
    unit = unit.strip("/")
    reasons, measured, kind = [], {}, None
    paths = changed()
    measured["changed"] = paths
    if not re.fullmatch(r"tree(/[a-z][a-z0-9_]*)+", unit) or not (ROOT / unit).is_dir():
        reasons.append(f"{unit} is not a unit of the tree")
    elif not paths:
        reasons.append("nothing changed: there is nothing to decide")
    else:
        in_work = [p for p in paths if p.startswith(unit + "/work/")]
        in_given = [p for p in paths if p == unit + "/unit.md" or p.startswith(unit + "/measure/")]
        outside = [p for p in paths if p not in in_work and p not in in_given]
        if outside:
            reasons.append(f"the change touches what is not {unit}'s: {outside}")
        if in_work and in_given:
            reasons.append("one change touches both the work and what the parent gives (document, measure)")
        kind = "work" if in_work else "give"
        document(unit, reasons)
        proof(unit, reasons, measured)
        reach(unit, reasons, measured)
    return {"allowed": not reasons, "kind": kind, "reasons": reasons, "measured": measured}


def judge_the_judge():
    """The guard is the judge of the judge: it applies the judging procedure
    that stands in history, not the candidate one, to the change."""
    source = subprocess.run(["git", "show", "HEAD:tree/judge/work/judge.py"], cwd=ROOT,
                            capture_output=True, text=True, env=ENV)
    if source.returncode:
        print("no standing judge in history")
        return 1
    place = ROOT / ".rehearsal" / "standing-judge"
    place.mkdir(parents=True, exist_ok=True)
    (place / "judge.py").write_text(source.stdout)
    spec = importlib.util.spec_from_file_location("standing_judge", place / "judge.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decide("tree/judge", ROOT, by="tree/guard")


if __name__ == "__main__":
    if sys.argv[1:2] == ["check"] and len(sys.argv) == 3:
        answer = check(sys.argv[2])
        print(json.dumps(answer, indent=1))
        sys.exit(0 if answer["allowed"] else 1)
    if sys.argv[1:] == ["judge-the-judge"]:
        sys.exit(judge_the_judge())
    print(__doc__)
    sys.exit(2)

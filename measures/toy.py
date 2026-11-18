"""Toy tree used by the measures of enforcer, judge, second-judge and cycle.

A tiny tree with the same layout as the real one: units `toy` (child of root),
`toy/part` (child of toy) and a toy `judge` (child of root). The measure of
each is: units/<name>/value holds an integer > 0; the number is that integer.
"""
import json, os, shutil, subprocess, sys

CHECK = '''#!/usr/bin/env python3
import json, os, sys
p = os.path.join(sys.argv[1], "units/%s/value")
v = int(open(p).read()) if os.path.exists(p) else 0
print(json.dumps({"pass": v > 0, "number": v}))
sys.exit(0 if v > 0 else 1)
'''


def doc(parent, judge="judge"):
    rows = "\n".join(f"| {i} | here |" for i in range(1, 8))
    return (f"# Toy\n\nParent: {parent}\n\n1. **Purpose** — p\n2. **Interface** — i\n"
            f"3. **Rules** — r\n4. **Budget** — b\n5. **Measure** — m\n"
            f"6. **Judge** — [`{judge}`](x)\n\n| Principle | Here |\n|---|---|\n{rows}\n")


def write(tree, rel, text, mode=None):
    p = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(text)
    if mode:
        os.chmod(p, mode)


def make(tree, **values):
    """Create the toy tree at `tree`; values = {unit name: integer} already built."""
    write(tree, "principles.md", "principles\n")
    write(tree, "root.md", "root\n")
    write(tree, "state.md", "state\n")
    write(tree, "ledger.jsonl", "")
    write(tree, "queue.md", "# Queue\n\n### Q1 — a\n\n- Asked: 2026-01-01, after result 0. Answered: 2026-01-01.\n\n"
                            "### Q2 — b\n\n- Asked: 2026-01-01, after result 0. Answered: —\n")
    for name, parent in (("toy", "root"), ("toy/part", "toy"), ("judge", "root")):
        write(tree, f"units/{name}/unit.md", doc(parent, "second-judge" if name == "judge" else "judge"))
        write(tree, f"measures/{name}/check", CHECK % name, 0o755)
        write(tree, f"measures/{name}/plants/zero/units/{name}/value", "0\n")
    for name, v in values.items():
        write(tree, f"units/{name.replace('__', '/')}/value", f"{v}\n")
    return tree


def clone(src, dst):
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", ".rehearsal", "__pycache__"))
    return dst


def run(cmd, cwd=None, env=None):
    """Run; return (exit code, last stdout line parsed as JSON or {})."""
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=600)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    try:
        out = json.loads(last)
    except ValueError:
        out = {"_stdout": r.stdout[-400:], "_stderr": r.stderr[-400:]}
    return r.returncode, out


class Cases:
    """Collects named cases; prints what each measured; the number is cases right."""
    def __init__(self):
        self.rows = []

    def add(self, name, ok, seen=""):
        self.rows.append((name, bool(ok), seen))

    def finish(self):
        right = sum(ok for _, ok, _ in self.rows)
        for name, ok, seen in self.rows:
            print(("ok   " if ok else "FAIL ") + name + (f"  [{seen}]" if not ok else ""))
        out = {"pass": bool(self.rows) and right == len(self.rows), "number": right, "cases": len(self.rows),
               "failed": [n for n, ok, _ in self.rows if not ok]}
        print(json.dumps(out))
        sys.exit(0 if out["pass"] else 1)

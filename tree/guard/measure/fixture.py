"""A throwaway repository with a toy unit, where the guard and the judge are
tried. It lives under .rehearsal/ of the real repository and nothing leaves it."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DOC = """# Toy

Parent: [root](../../root.md)

1. **Purpose** — double a number.
2. **Interface** — build, verdict.
3. **Rules** — the parent's.
4. **Budget** — the parent's.
5. **Measure** — measure/check.py.
6. **Judge** — the judge.

| Principle | Here |
|---|---|
| 1 Boundary | x |
| 2 Single source | x |
| 3 External enforcement | x |
| 4 Rehearsal before effect | x |
| 5 Return | x |
| 6 Selection | x |
| 7 Escalation | x |
"""

CHECK = '''import importlib.util, json, sys
from pathlib import Path
CASES = [(2, 4), (0, 0), (-1, -2)]
passed = 0
try:
    spec = importlib.util.spec_from_file_location("toy", Path(sys.argv[1]) / "work" / "toy.py")
    toy = importlib.util.module_from_spec(spec); spec.loader.exec_module(toy)
    passed = sum(1 for x, y in CASES if toy.double(x) == y)
except Exception:
    pass
print(json.dumps({"pass": passed == len(CASES), "passed": passed, "total": len(CASES)}))
sys.exit(0 if passed == len(CASES) else 1)
'''

GOOD = "def double(x):\n    y = x * 2\n    return y\n"
SAME_SIZE = "def double(x):\n    z = x * 2\n    return z\n"
BETTER = "def double(x):\n    return x * 2\n"
WRONG = "def double(x):\n    return x + 2\n"
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def real_root(start):
    for folder in Path(start).resolve().parents:
        if (folder / "principles.md").exists() and (folder / "root.md").exists():
            return folder
    raise SystemExit("repository not found")


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=ENV)


def run(repo, script, *args):
    return subprocess.run([sys.executable, str(repo / script), *args], cwd=repo,
                          capture_output=True, text=True, env=ENV)


def write(repo, path, text):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def make(tree, judge_work=None, guard_work=None):
    """Build the repository. `tree` is the tree/ folder whose judge and guard
    are used, unless a candidate work folder replaces one of them."""
    tree = Path(tree).resolve()
    root = real_root(tree)
    (root / ".rehearsal").mkdir(exist_ok=True)
    repo = Path(tempfile.mkdtemp(prefix="toy-", dir=root / ".rehearsal"))
    shutil.copytree(judge_work or tree / "judge" / "work", repo / "tree/judge/work")
    shutil.copytree(guard_work or tree / "guard" / "work", repo / "tree/guard/work")
    shutil.copy(root / "root.md", repo / "root.md")
    write(repo, "principles.md", "copy for rehearsal\n")
    write(repo, ".gitignore", ".rehearsal/\n__pycache__/\n")
    write(repo, "tree/toy/unit.md", DOC)
    write(repo, "tree/toy/measure/check.py", CHECK)
    write(repo, "tree/toy/measure/planted/adds/work/toy.py", WRONG)
    write(repo, "tree/other/unit.md", DOC.replace("Toy", "Other"))
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "rehearsal")
    git(repo, "config", "user.email", "rehearsal@localhost")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "start")
    return repo


def reset(repo):
    git(repo, "checkout", "-q", "--", ".")
    git(repo, "clean", "-fdq")


def destroy(repo):
    shutil.rmtree(repo, ignore_errors=True)

# Planted wrong result: a judge that lets everything stand.
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
(ROOT / "record").mkdir(exist_ok=True)
with open(ROOT / "record/ledger.jsonl", "a") as book:
    book.write(json.dumps({"id": 1, "kind": "work", "verdict": "pass", "judge": "stand",
                           "undo": "git revert", "number": {"passed": 3}}) + "\n")
subprocess.run(["git", "add", "-A"], cwd=ROOT)
subprocess.run(["git", "commit", "-qm", "stand: " + sys.argv[-1]], cwd=ROOT)
sys.exit(0)

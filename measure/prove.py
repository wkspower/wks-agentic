#!/usr/bin/env python3
"""Proof of the root's check: every planted wrong record must fail it and the
control record must pass it. Run at every change to check.py. Exit 0 = proven."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOW = "2026-06-01T00:00Z"


def run(record):
    done = subprocess.run([sys.executable, str(HERE / "check.py"), str(record), "--now", NOW],
                          capture_output=True, text=True)
    return done.returncode, json.loads(done.stdout)


ok = True
planted = sorted(p for p in (HERE / "planted").iterdir() if p.is_dir())
if not planted:
    ok = False
    print("no planted case: nothing is proven")
for case in planted:
    code, out = run(case)
    good = code == 1 and out["failures"]
    ok &= bool(good)
    print(f"planted {case.name}: {'fails as it must' if good else 'PASSES - the check is wrong'}: {out['failures']}")
code, out = run(HERE / "control")
ok &= code == 0
print(f"control: {'passes as it must' if code == 0 else 'FAILS - the check is wrong'}: "
      f"{out['correct_results']} correct results, latest {out.get('latest_window')}, "
      f"previous {out.get('previous_window')}, failures {out['failures']}")
print("proven" if ok else "NOT proven")
sys.exit(0 if ok else 1)

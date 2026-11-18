#!/usr/bin/env python3
"""Check of the root's measure: the person's attention per correct result.

Usage: check.py [RECORD_DIR] [--now 2026-01-01T00:00Z]

RECORD_DIR holds queue.md and record/ledger.jsonl (default: the repository).
The budget values are read from root.md, their single source.
Prints what it measured as JSON; exit 0 = pass, 1 = fail.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = r"\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z"


def when(text):
    fmt = "%Y-%m-%dT%H:%M:%SZ" if text.count(":") == 2 else "%Y-%m-%dT%H:%MZ"
    return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)


def budget():
    """The values of declaration 4 of root.md."""
    found = dict(re.findall(r"^\s*\| `(\w+)` \| (\d+) \|", (ROOT / "root.md").read_text(), re.M))
    return {k: int(v) for k, v in found.items()}


def queue(record):
    """One (number, opened, answered-or-None) per `## Qn` section of queue.md."""
    items = []
    for part in re.split(r"^(?=## Q\d+)", (record / "queue.md").read_text(), flags=re.M)[1:]:
        number = int(re.match(r"## Q(\d+)", part).group(1))
        opened = re.search(rf"^Opened: ({STAMP})\s*$", part, re.M)
        answered = re.search(rf"^Answered: ({STAMP}|—)\s*$", part, re.M)
        if not opened or not answered:
            raise SystemExit(f"queue item Q{number} has no Opened/Answered line")
        done = None if answered.group(1) == "—" else when(answered.group(1))
        items.append((number, when(opened.group(1)), done))
    return sorted(items, key=lambda i: i[1])


def ledger(record):
    path = record / "record" / "ledger.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def measure(record, now):
    b = budget()
    missing = [k for k in ("open_items_max", "first_batch_items", "correct_results_per_item",
                           "effects_without_undo", "attempts_per_change", "window_results") if k not in b]
    if missing:
        return {"pass": False, "failures": [f"budget value not given in root.md: {k}" for k in missing]}
    items, entries = queue(record), ledger(record)
    revoked = {e.get("revokes") for e in entries if e.get("kind") == "revoke"}
    # A correct result: a change to a unit's work whose verdict passed, that its
    # judge let stand, and that no later case showed wrong.
    correct = sorted((when(e["time"]) for e in entries
                      if e.get("kind") == "work" and e.get("verdict") == "pass"
                      and e.get("judge") == "stand" and e.get("id") not in revoked))
    failures = []

    open_now = sum(1 for _, _, done in items if done is None)
    if open_now > b["open_items_max"]:
        failures.append(f"{open_now} items open, budget is {b['open_items_max']}")

    for index, (number, opened, _) in enumerate(items):
        extra = index - b["first_batch_items"] + 1
        if extra > 0:
            had = sum(1 for t in correct if t <= opened)
            if had < extra * b["correct_results_per_item"]:
                failures.append(f"Q{number} was item {extra} after the first batch with {had} correct "
                                f"results; budget is 1 per {b['correct_results_per_item']}")

    without_undo = [e.get("id") for e in entries if e.get("judge") == "stand" and not e.get("undo")]
    if len(without_undo) > b["effects_without_undo"]:
        failures.append(f"standing changes without undo: {without_undo}; budget is {b['effects_without_undo']}")

    def attention(after, until):
        mine = [(o, d) for _, o, d in items if (after is None or o > after) and o <= until]
        hours = sum(((d or now) - o).total_seconds() / 3600 for o, d in mine)
        return len(mine), round(hours, 2)

    w, n = b["window_results"], len(correct)
    out = {"correct_results": n, "items": len(items), "open": open_now, "window_results": w,
           "budget": b, "now": now.strftime("%Y-%m-%dT%H:%MZ")}
    total_items, total_hours = attention(None, now)
    out["items_per_correct_result"] = round(total_items / n, 3) if n else None
    out["waiting_hours_per_correct_result"] = round(total_hours / n, 3) if n else None
    if n >= 2 * w:
        edge_old = correct[n - 2 * w - 1] if n > 2 * w else None
        edge = correct[n - w - 1]
        before, latest = attention(edge_old, edge), attention(edge, now)
        out["previous_window"] = {"items": before[0], "waiting_hours": before[1]}
        out["latest_window"] = {"items": latest[0], "waiting_hours": latest[1]}
        if latest[0] > before[0]:
            failures.append(f"items per {w} correct results rose from {before[0]} to {latest[0]}")
        if latest[1] > before[1]:
            failures.append(f"waiting hours per {w} correct results rose from {before[1]} to {latest[1]}")
    else:
        out["trend"] = f"not yet measurable: {n} correct results, two windows need {2 * w}; only the budget is checked"
    out["failures"] = failures
    out["pass"] = not failures
    return out


def main(argv):
    now = datetime.now(timezone.utc)
    if "--now" in argv:
        at = argv.index("--now")
        now = when(argv[at + 1])
        argv = argv[:at] + argv[at + 2:]
    record = Path(argv[0]) if argv else ROOT
    out = measure(record, now)
    print(json.dumps(out, indent=1))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

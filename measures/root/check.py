#!/usr/bin/env python3
"""Executable check for declaration 5 (Measure) of root.md.

The person's attention per correct result, as a trend (principle 7).
Input format: measures/root/INPUT.md. Pass rule: measures/root/README.md.
Prints one JSON object; exits 0 for pass, 1 for fail (any error is a fail).
Python 3 standard library only.
"""

import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone

# Budget values from record/root.log.md, Queue 1, Q1 ("accept").
MAX_ITEMS_PER_7_DAYS = 5
MAX_DECIDE_MINUTES = 5
# Choices of this measure (see README.md).
WINDOW_WEEKS = 4        # trailing window over which each weekly ratio is taken
TREND_PERIODS = 3       # last periods with data compared for the trend
BOOTSTRAP_DAYS = 28     # grace after the first queue item before a correct result is required

QUEUE_KINDS = {"decision", "proposal", "notice", "effect_without_undo"}
VERDICTS = {"pass", "fail"}
WEEK = timedelta(days=7)


class Malformed(Exception):
    pass


def parse_ts(value, where):
    if not isinstance(value, str):
        raise Malformed(f"{where}: timestamp must be a string")
    try:
        ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise Malformed(f"{where}: not an ISO 8601 timestamp: {value!r}")
    if ts.tzinfo is None:
        raise Malformed(f"{where}: timestamp has no timezone: {value!r}")
    return ts.astimezone(timezone.utc)


def read_jsonl(path):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        raise Malformed(f"{path}: cannot read ({exc.strerror})")
    rows = []
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise Malformed(f"{path}:{n}: invalid JSON ({exc.msg})")
        if not isinstance(obj, dict):
            raise Malformed(f"{path}:{n}: line is not a JSON object")
        rows.append((f"{path}:{n}", obj))
    return rows


def require(obj, where, field, types, optional=False):
    if field not in obj:
        if optional:
            return None
        raise Malformed(f"{where}: missing field {field!r}")
    value = obj[field]
    if optional and value is None:
        return None
    # bool is a subclass of int: reject it where a number is expected.
    if isinstance(value, bool) and bool not in types:
        raise Malformed(f"{where}: field {field!r} has wrong type")
    if not isinstance(value, types):
        raise Malformed(f"{where}: field {field!r} has wrong type")
    return value


def load_queue(path, now):
    items, seen = [], set()
    for where, obj in read_jsonl(path):
        qid = require(obj, where, "id", (str,))
        if not qid or qid in seen:
            raise Malformed(f"{where}: empty or duplicate id {qid!r}")
        seen.add(qid)
        kind = require(obj, where, "kind", (str,))
        if kind not in QUEUE_KINDS:
            raise Malformed(f"{where}: unknown kind {kind!r}")
        opened = parse_ts(require(obj, where, "opened", (str,)), where)
        if "decided" not in obj:
            raise Malformed(f"{where}: missing field 'decided' (null when open)")
        decided = obj["decided"]
        decided = None if decided is None else parse_ts(decided, where)
        minutes = require(obj, where, "decide_minutes", (int, float), optional=True)
        if minutes is not None and (minutes < 0 or not math.isfinite(minutes)):
            raise Malformed(f"{where}: decide_minutes must be a finite number >= 0")
        if decided is not None and decided < opened:
            raise Malformed(f"{where}: decided before opened")
        if opened > now or (decided is not None and decided > now):
            raise Malformed(f"{where}: timestamp after now")
        items.append({"id": qid, "kind": kind, "opened": opened,
                      "decided": decided, "decide_minutes": minutes})
    return items


def load_deliveries(path, now, queue_by_id):
    out, seen = [], set()
    for where, obj in read_jsonl(path):
        did = require(obj, where, "id", (str,))
        if not did or did in seen:
            raise Malformed(f"{where}: empty or duplicate id {did!r}")
        seen.add(did)
        at = parse_ts(require(obj, where, "at", (str,)), where)
        if at > now:
            raise Malformed(f"{where}: timestamp after now")
        verdict = require(obj, where, "verdict", (str,))
        if verdict not in VERDICTS:
            raise Malformed(f"{where}: verdict must be 'pass' or 'fail'")
        wrong = require(obj, where, "later_shown_wrong", (bool,))
        undo = require(obj, where, "undo", (bool,), optional=True)
        undo = True if undo is None else undo
        asked = require(obj, where, "asked", (str,), optional=True)
        if asked is not None and asked not in queue_by_id:
            raise Malformed(f"{where}: asked refers to unknown queue id {asked!r}")
        out.append({"id": did, "at": at, "verdict": verdict, "wrong": wrong,
                    "undo": undo, "asked": asked, "where": where})
    return out


def week_start(ts):
    day = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    return day - timedelta(days=day.weekday())


def ratio(num, den):
    if den == 0:
        return None if num == 0 else math.inf
    return num / den


def js(x):
    """JSON-safe number: infinity becomes the string "inf"."""
    if x is None:
        return None
    if math.isinf(x):
        return "inf"
    return round(x, 4)


def evaluate(queue, deliveries, now):
    failures = []

    # Budget: more than 5 items opened in any 7-day window.
    opened = sorted(q["opened"] for q in queue)
    worst = 0
    for i, start in enumerate(opened):
        count = sum(1 for t in opened[i:] if t < start + WEEK)
        if count > worst:
            worst = count
        if count > MAX_ITEMS_PER_7_DAYS:
            failures.append(f"budget: {count} items opened in the 7 days from "
                            f"{start.isoformat()} (max {MAX_ITEMS_PER_7_DAYS})")
            break
    for q in queue:
        if q["decide_minutes"] is not None and q["decide_minutes"] > MAX_DECIDE_MINUTES:
            failures.append(f"budget: item {q['id']} took {q['decide_minutes']} "
                            f"minutes to decide (max {MAX_DECIDE_MINUTES})")

    # Cap on effects without undo is zero: each must have been asked and
    # decided before it happened.
    for d in deliveries:
        if d["undo"]:
            continue
        q = next((x for x in queue if x["id"] == d["asked"]), None)
        if q is None or q["decided"] is None or q["decided"] > d["at"]:
            failures.append(f"cap: delivery {d['id']} has an effect without undo "
                            f"not decided by the person before it happened")

    # Weekly series. An item's wait is attributed to the week it was opened.
    def wait_hours(q):
        end = q["decided"] if q["decided"] is not None else now
        return (end - q["opened"]).total_seconds() / 3600.0

    correct = [d for d in deliveries if d["verdict"] == "pass" and not d["wrong"]]
    stamps = [q["opened"] for q in queue] + [d["at"] for d in deliveries]
    weekly = []
    if stamps:
        first, last = week_start(min(stamps)), week_start(now)
        w = first
        while w <= last:
            lo = w - (WINDOW_WEEKS - 1) * WEEK
            hi = w + WEEK
            win_items = [q for q in queue if lo <= q["opened"] < hi]
            win_correct = sum(1 for d in correct if lo <= d["at"] < hi)
            win_deliv = sum(1 for d in deliveries if lo <= d["at"] < hi)
            items = len(win_items)
            wait = sum(wait_hours(q) for q in win_items)
            weekly.append({
                "week": w.date().isoformat(),
                "items": sum(1 for q in queue if w <= q["opened"] < hi),
                "correct": sum(1 for d in correct if w <= d["at"] < hi),
                "window_items": items,
                "window_wait_hours": wait,
                "window_correct": win_correct,
                "has_data": items > 0 or win_deliv > 0,
                "items_per_correct": ratio(items, win_correct),
                "wait_hours_per_correct": ratio(wait, win_correct),
            })
            w += WEEK

    with_data = [p for p in weekly if p["has_data"]]
    in_bootstrap = (not queue) or now < min(opened) + timedelta(days=BOOTSTRAP_DAYS)

    # No correct result at all.
    if not correct:
        if queue and not in_bootstrap:
            failures.append(f"no correct result {BOOTSTRAP_DAYS} days after the "
                            f"first queue item: attention per correct result is infinite")
        status = "no_correct_results"
    else:
        status = "measured"

    # Trend over the last periods with data.
    trend = "insufficient"
    tail = with_data[-TREND_PERIODS:]
    if correct and len(tail) >= 2:
        first_p, last_p = tail[0], tail[-1]
        rising, falling = [], []
        for key in ("items_per_correct", "wait_hours_per_correct"):
            a = first_p[key] if first_p[key] is not None else 0.0
            b = last_p[key] if last_p[key] is not None else 0.0
            if b > a:
                rising.append(key)
            elif b < a:
                falling.append(key)
        if rising:
            trend = "rising"
            failures.append(f"trend: {', '.join(rising)} rose from week "
                            f"{first_p['week']} to week {last_p['week']}")
        elif falling:
            trend = "falling"
        else:
            trend = "flat"
        if math.isinf(last_p["items_per_correct"] or 0) and not in_bootstrap and not rising:
            failures.append(f"trend: attention with no correct result in the "
                            f"window ending week {last_p['week']}")

    latest = with_data[-1] if with_data else None
    return {
        "pass": not failures,
        "failures": failures,
        "status": status,
        "trend": trend,
        "number": {
            "items_per_correct": js(latest["items_per_correct"]) if latest else None,
            "wait_hours_per_correct": js(latest["wait_hours_per_correct"]) if latest else None,
            "window_weeks": WINDOW_WEEKS,
            "week": latest["week"] if latest else None,
        },
        "totals": {
            "items": len(queue),
            "open_items": sum(1 for q in queue if q["decided"] is None),
            "wait_hours": round(sum(wait_hours(q) for q in queue), 4),
            "deliveries": len(deliveries),
            "correct": len(correct),
            "shown_wrong": sum(1 for d in deliveries if d["wrong"]),
            "max_items_in_7_days": worst,
        },
        "weekly": [
            {"week": p["week"], "items": p["items"], "correct": p["correct"],
             "items_per_correct": js(p["items_per_correct"]),
             "wait_hours_per_correct": js(p["wait_hours_per_correct"])}
            for p in weekly
        ],
        "now": now.isoformat(),
    }


def run(argv):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", default="record/queue.jsonl")
    ap.add_argument("--deliveries", default="record/deliveries.jsonl")
    ap.add_argument("--now", help="ISO 8601 time to evaluate at (default: current UTC time)")
    args = ap.parse_args(argv)
    try:
        now = parse_ts(args.now, "--now") if args.now else datetime.now(timezone.utc)
        queue = load_queue(args.queue, now)
        deliveries = load_deliveries(args.deliveries, now, {q["id"]: q for q in queue})
        result = evaluate(queue, deliveries, now)
    except Malformed as exc:
        result = {"pass": False, "failures": [f"malformed: {exc}"], "status": "malformed"}
    return result


def main(argv=None):
    try:
        result = run(argv)
    except SystemExit:  # argparse usage error: still a fail, exit 1
        return 1
    except Exception as exc:  # any other error is a fail, never a pass
        result = {"pass": False, "failures": [f"error: {type(exc).__name__}: {exc}"],
                  "status": "error"}
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

"""Proof of the measure: planted wrong results must fail, correct ones pass.

Run: python3 -m unittest discover -s measures/root
"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check  # noqa: E402

NOW = "2026-12-31T12:00:00Z"


def q(i, opened, decided="same", kind="decision", **extra):
    if decided == "same":
        decided = opened.replace("T09:", "T10:")
    row = {"id": f"q{i}", "opened": opened, "decided": decided, "kind": kind}
    row.update(extra)
    return row


def d(i, at, verdict="pass", wrong=False, **extra):
    row = {"id": f"d{i}", "at": at, "verdict": verdict, "later_shown_wrong": wrong}
    row.update(extra)
    return row


def day(n, hour=9):
    """Timestamp n days after Monday 2026-11-02."""
    from datetime import datetime, timedelta, timezone
    t = datetime(2026, 11, 2, hour, tzinfo=timezone.utc) + timedelta(days=n)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def falling_history():
    """Weekly attention falls while correct results grow."""
    queue = [q(1, day(0)), q(2, day(1)), q(3, day(2)), q(4, day(8)), q(5, day(15))]
    deliveries = [d(1, day(3)), d(2, day(9)), d(3, day(10)), d(4, day(16)),
                  d(5, day(17)), d(6, day(18)), d(7, day(23)), d(8, day(24)),
                  d(9, day(25)), d(10, day(26))]
    return queue, deliveries


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, rows):
        path = os.path.join(self.tmp.name, name)
        with open(path, "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write((r if isinstance(r, str) else json.dumps(r)) + "\n")
        return path

    def run_check(self, queue, deliveries, now=NOW):
        qp = self.write("queue.jsonl", queue)
        dp = self.write("deliveries.jsonl", deliveries)
        out = io.StringIO()
        with redirect_stdout(out):
            code = check.main(["--queue", qp, "--deliveries", dp, "--now", now])
        return code, json.loads(out.getvalue())

    def assertPasses(self, queue, deliveries, now=NOW):
        code, res = self.run_check(queue, deliveries, now)
        self.assertEqual(code, 0, res.get("failures"))
        self.assertTrue(res["pass"])
        return res

    def assertFails(self, queue, deliveries, contains, now=NOW):
        code, res = self.run_check(queue, deliveries, now)
        self.assertEqual(code, 1, res)
        self.assertFalse(res["pass"])
        self.assertTrue(any(contains in f for f in res["failures"]), res["failures"])
        return res


class CorrectInputsPass(Base):
    def test_falling_trend_within_budget_passes(self):
        res = self.assertPasses(*falling_history(), now=day(27, 12))
        self.assertEqual(res["trend"], "falling")
        self.assertEqual(res["totals"]["correct"], 10)

    def test_no_deliveries_during_bootstrap_passes(self):
        queue = [q(i, day(0)) for i in range(1, 6)]  # Queue 1: five items
        res = self.assertPasses(queue, [], now=day(10))
        self.assertEqual(res["status"], "no_correct_results")
        self.assertEqual(res["number"]["items_per_correct"], "inf")

    def test_empty_record_passes(self):
        res = self.assertPasses([], [], now=day(0))
        self.assertEqual(res["totals"]["items"], 0)

    def test_zero_attention_with_results_passes(self):
        res = self.assertPasses([], [d(1, day(1)), d(2, day(9))], now=day(10))
        self.assertEqual(res["number"]["items_per_correct"], 0.0)

    def test_exactly_five_items_in_seven_days_passes(self):
        queue = [q(i, day(i)) for i in range(5)]
        self.assertPasses(queue, [d(1, day(5))], now=day(6))

    def test_effect_without_undo_decided_first_passes(self):
        queue = [q(1, day(0), kind="effect_without_undo")]
        self.assertPasses(queue, [d(1, day(1), undo=False, asked="q1")], now=day(2))

    def test_decide_minutes_at_limit_passes(self):
        self.assertPasses([q(1, day(0), decide_minutes=5)], [d(1, day(1))], now=day(2))


class PlantedWrongResultsFail(Base):
    def test_budget_exceeded_six_items_in_seven_days(self):
        queue = [q(i, day(i)) for i in range(6)]
        self.assertFails(queue, [d(1, day(6))], "budget", now=day(7))

    def test_budget_exceeded_across_week_boundary(self):
        # Sliding window, not calendar week: Fri..Thu holds six items.
        queue = [q(i, day(4 + i)) for i in range(6)]
        self.assertFails(queue, [d(1, day(10))], "budget", now=day(11))

    def test_item_not_decidable_in_five_minutes(self):
        self.assertFails([q(1, day(0), decide_minutes=12)], [d(1, day(1))],
                         "minutes", now=day(2))

    def test_rising_trend_in_item_count(self):
        queue = [q(1, day(0)), q(2, day(8)), q(3, day(9)), q(4, day(15)),
                 q(5, day(16)), q(6, day(17))]
        deliveries = [d(i, day(2 + i)) for i in range(1, 5)]  # all in week 1
        self.assertFails(queue, deliveries, "trend", now=day(18))

    def test_rising_trend_in_waiting_time_only(self):
        # Same item count and results each week, but items wait longer.
        queue = [q(1, day(0), decided=day(0, 10)),
                 q(2, day(7), decided=day(9, 10)),
                 q(3, day(14), decided=None)]
        deliveries = [d(1, day(1)), d(2, day(8)), d(3, day(15))]
        res = self.assertFails(queue, deliveries, "wait_hours_per_correct", now=day(20))
        self.assertEqual(res["trend"], "rising")

    def test_later_shown_wrong_is_not_counted_as_correct(self):
        queue, deliveries = falling_history()
        # Last weeks' results are later shown wrong: counted as correct, the
        # trend would fall; not counted, attention per correct result rises.
        for row in deliveries[3:]:
            row["later_shown_wrong"] = True
        res = self.assertFails(queue, deliveries, "trend", now=day(27, 12))
        self.assertEqual(res["totals"]["correct"], 3)
        self.assertEqual(res["totals"]["shown_wrong"], 7)

    def test_failed_verdict_is_not_counted_as_correct(self):
        queue, deliveries = falling_history()
        for row in deliveries[3:]:
            row["verdict"] = "fail"
        self.assertFails(queue, deliveries, "trend", now=day(27, 12))

    def test_no_correct_result_after_bootstrap(self):
        queue = [q(1, day(0))]
        self.assertFails(queue, [d(1, day(2), wrong=True)], "no correct result",
                         now=day(40))

    def test_attention_without_results_in_latest_window(self):
        queue = [q(1, day(0)), q(2, day(35))]
        self.assertFails(queue, [d(1, day(1))], "trend", now=day(36))

    def test_effect_without_undo_not_asked(self):
        self.assertFails([], [d(1, day(1), undo=False)], "cap", now=day(2))

    def test_effect_without_undo_decided_after_it_happened(self):
        queue = [q(1, day(0), decided=day(2), kind="effect_without_undo")]
        self.assertFails(queue, [d(1, day(1), undo=False, asked="q1")], "cap",
                         now=day(3))

    def test_effect_without_undo_still_open(self):
        queue = [q(1, day(0), decided=None, kind="effect_without_undo")]
        self.assertFails(queue, [d(1, day(1), undo=False, asked="q1")], "cap",
                         now=day(3))


class MalformedInputFails(Base):
    def check_malformed(self, queue, deliveries, now=day(30)):
        res = self.assertFails(queue, deliveries, "malformed", now=now)
        self.assertEqual(res["status"], "malformed")

    def test_invalid_json(self):
        self.check_malformed(["{not json"], [])

    def test_line_not_object(self):
        self.check_malformed([], ["[1, 2]"])

    def test_missing_field(self):
        row = q(1, day(0))
        del row["kind"]
        self.check_malformed([row], [])

    def test_missing_decided_field(self):
        row = q(1, day(0))
        del row["decided"]
        self.check_malformed([row], [])

    def test_missing_later_shown_wrong(self):
        row = d(1, day(1))
        del row["later_shown_wrong"]
        self.check_malformed([], [row])

    def test_later_shown_wrong_as_string(self):
        self.check_malformed([], [d(1, day(1), wrong="false")])

    def test_unknown_verdict(self):
        self.check_malformed([], [d(1, day(1), verdict="ok")])

    def test_unknown_kind(self):
        self.check_malformed([q(1, day(0), kind="chat")], [])

    def test_timestamp_without_timezone(self):
        self.check_malformed([q(1, "2026-11-02T09:00:00", decided=None)], [])

    def test_not_a_timestamp(self):
        self.check_malformed([q(1, "last tuesday", decided=None)], [])

    def test_decided_before_opened(self):
        self.check_malformed([q(1, day(2), decided=day(1))], [])

    def test_timestamp_in_future(self):
        self.check_malformed([], [d(1, day(5))], now=day(1))

    def test_duplicate_id(self):
        self.check_malformed([q(1, day(0)), q(1, day(1))], [])

    def test_asked_refers_to_unknown_item(self):
        self.check_malformed([], [d(1, day(1), undo=False, asked="q9")])

    def test_decide_minutes_as_bool(self):
        self.check_malformed([q(1, day(0), decide_minutes=True)], [])

    def test_missing_file(self):
        dp = self.write("deliveries.jsonl", [])
        out = io.StringIO()
        with redirect_stdout(out):
            code = check.main(["--queue", os.path.join(self.tmp.name, "nope.jsonl"),
                               "--deliveries", dp, "--now", NOW])
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out.getvalue())["pass"])

    def test_bad_now_argument(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = check.main(["--queue", self.write("a.jsonl", []),
                               "--deliveries", self.write("b.jsonl", []),
                               "--now", "tomorrow"])
        self.assertEqual(code, 1)


class CommandLine(unittest.TestCase):
    def test_script_exit_codes(self):
        import subprocess
        here = os.path.dirname(os.path.abspath(__file__))
        with tempfile.TemporaryDirectory() as tmp:
            qp, dp = os.path.join(tmp, "q.jsonl"), os.path.join(tmp, "d.jsonl")
            open(dp, "w").close()
            with open(qp, "w") as fh:
                fh.write("\n".join(json.dumps(q(i, day(i))) for i in range(6)) + "\n")
            cmd = [sys.executable, os.path.join(here, "check.py"),
                   "--queue", qp, "--deliveries", dp, "--now", day(7)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)
            with open(qp, "w") as fh:
                fh.write(json.dumps(q(1, day(0))) + "\n")
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)


if __name__ == "__main__":
    unittest.main()

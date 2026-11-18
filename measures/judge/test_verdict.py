"""verdict <unit>: runs the unit's measure against src/."""

import os
import unittest

from .plant import CATALOG_WRONG, HANG_CALL_TIMEOUT, UNITS, TreeCase


class VerdictTest(TreeCase, unittest.TestCase):
    def test_passes_each_unit_whose_measure_passes(self):
        for unit in UNITS:
            with self.subTest(unit=unit):
                res = self.tree.run("verdict", unit)
                self.assertDecision(res, True)
                self.assertEqual(res.data.get("unit"), unit, res.describe())
                self.assertNumber(res, 1)

    def test_fails_unit_with_a_failing_case(self):
        self.tree.write("src/petshop/catalog.py", CATALOG_WRONG)
        res = self.tree.run("verdict", "catalog")
        self.assertDecision(res, False)
        self.assertNumber(res, 0.5)

    def test_number_counts_every_test_file_and_errors_as_not_passed(self):
        self.tree.write("measures/catalog/test_more.py", (
            "import unittest\n"
            "from petshop import catalog\n\n\n"
            "class More(unittest.TestCase):\n"
            "    def test_listing(self):\n"
            "        self.assertIn('cat-1', catalog.listing())\n\n"
            "    def test_crashes(self):\n"
            "        raise RuntimeError('a case that errors')\n"))
        res = self.tree.run("verdict", "catalog")
        self.assertDecision(res, False)
        self.assertNumber(res, 0.75)

    def test_other_units_do_not_count(self):
        # a failing measure of another unit does not touch this unit's verdict
        self.tree.write("src/petshop/catalog.py", CATALOG_WRONG)
        res = self.tree.run("verdict", "stock")
        self.assertDecision(res, True)
        self.assertNumber(res, 1)

    def test_fails_unit_with_zero_cases(self):
        self.tree.write("measures/catalog/test_catalog.py",
                        "import unittest\n\n\nclass Empty(unittest.TestCase):\n    pass\n")
        res = self.tree.run("verdict", "catalog")
        self.assertDecision(res, False)

    def test_fails_known_unit_without_a_measure(self):
        self.tree.remove("measures/stock")
        res = self.tree.run("verdict", "stock")
        self.assertDecision(res, False)

    @unittest.skipIf(os.environ.get("JUDGE_MEASURE_SKIP_SLOW") == "1",
                     "slow (over 120 s); a run with it skipped gives no valid number")
    def test_fails_a_measure_that_hangs_beyond_the_timeout(self):
        # SLOW: the judge's timeout is 120 s, so this case takes at least that.
        self.tree.write("measures/orders/test_hang.py", (
            "import time\nimport unittest\n\n\n"
            "class Hang(unittest.TestCase):\n"
            "    def test_hangs(self):\n"
            "        time.sleep(10 ** 6)\n"))
        res = self.tree.run("verdict", "orders", timeout=HANG_CALL_TIMEOUT)
        self.assertDecision(res, False)


if __name__ == "__main__":
    unittest.main()

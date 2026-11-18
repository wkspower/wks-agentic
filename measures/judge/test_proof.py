"""proof <unit>: every planted case must fail the measure, and there is one."""

import unittest

from .plant import CATALOG, UNITS, TreeCase


class ProofTest(TreeCase, unittest.TestCase):
    def test_passes_each_unit_whose_planted_cases_fail(self):
        for unit in UNITS:
            with self.subTest(unit=unit):
                res = self.tree.run("proof", unit)
                self.assertDecision(res, True)
                self.assertEqual(res.data.get("unit"), unit, res.describe())

    def test_passes_when_all_planted_cases_fail(self):
        self.tree.write("measures/catalog/planted/wrong_price.py", CATALOG.replace(
            '"price_cents": 5000', '"price_cents": 0').replace(
            "import json", "# Defect: the cat costs nothing.\nimport json", 1))
        res = self.tree.run("proof", "catalog")
        self.assertDecision(res, True)
        self.assertEqual(self.planted_status(res, "wrong_unknown"), "failed", res.describe())
        self.assertEqual(self.planted_status(res, "wrong_price"), "failed", res.describe())

    def test_fails_when_a_planted_case_passes_the_measure(self):
        # a planted case whose defect the measure does not see
        self.tree.write("measures/catalog/planted/unseen.py", CATALOG.replace(
            "import json", "# Defect: the listing is empty (the measure does not check it).\nimport json", 1
        ).replace("return json.dumps([_ITEMS[k] for k in sorted(_ITEMS)])", "return '[]'"))
        res = self.tree.run("proof", "catalog")
        self.assertDecision(res, False)
        self.assertEqual(self.planted_status(res, "unseen"), "passed", res.describe())
        self.assertEqual(self.planted_status(res, "wrong_unknown"), "failed", res.describe())

    def test_fails_with_no_planted_directory(self):
        self.tree.remove("measures/stock/planted")
        res = self.tree.run("proof", "stock")
        self.assertDecision(res, False)

    def test_fails_with_no_planted_case_in_the_directory(self):
        self.tree.remove("measures/stock/planted/wrong_unknown.py")
        self.tree.write("measures/stock/planted/README.txt", "nothing planted\n")
        res = self.tree.run("proof", "stock")
        self.assertDecision(res, False)


if __name__ == "__main__":
    unittest.main()

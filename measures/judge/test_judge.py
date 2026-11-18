"""judge --base <git-ref>: the decision on a change.

Each case commits a base tree on the branch `base`, changes the tree, commits
the change on HEAD (so the working tree equals HEAD) and runs
`judge --base base`. The measures are the same at the base and at HEAD
unless the case says otherwise, so the base number is the same whether the
judge runs the base's measure or HEAD's against the base's src/.
"""

import unittest

from .plant import CATALOG, CATALOG_WRONG, UNITS, TreeCase, base_files


class JudgeTest(TreeCase, unittest.TestCase):
    def judge_change(self, plant_base=None, plant_head=None):
        if plant_base:
            plant_base(self.tree)
        self.tree.commit("base")
        self.tree.branch("base")
        if plant_head:
            plant_head(self.tree)
        return self.tree.run("judge", "--base", "base")

    def unit(self, res, unit):
        units = res.data.get("units")
        self.assertIsInstance(units, dict, res.describe())
        self.assertIn(unit, units, res.describe())
        return units[unit]

    def assertNumbers(self, res, unit, number, base_number):
        entry = self.unit(res, unit)
        self.assertAlmostEqual(entry.get("number"), number, places=6, msg=res.describe())
        self.assertAlmostEqual(entry.get("base_number"), base_number, places=6, msg=res.describe())

    def assertFailed(self, res, unit, field):
        """`field` of the unit's entry is false (or an object whose "pass" is false)."""
        value = self.unit(res, unit).get(field)
        if isinstance(value, dict):
            value = value.get("pass")
        self.assertIs(value, False, res.describe())

    def test_passes_when_numbers_are_equal(self):
        res = self.judge_change(plant_head=lambda t: t.append("src/petshop/stock.py", "# a harmless change\n"))
        self.assertDecision(res, True)
        for unit in UNITS:
            with self.subTest(unit=unit):
                self.assertNumbers(res, unit, 1, 1)
        self.assertIn("rules", res.data, res.describe())

    def test_passes_when_a_number_rises(self):
        res = self.judge_change(
            plant_base=lambda t: t.write("src/petshop/catalog.py", CATALOG_WRONG),
            plant_head=lambda t: t.write("src/petshop/catalog.py", CATALOG))
        self.assertDecision(res, True)
        self.assertNumbers(res, "catalog", 1, 0.5)

    def test_passes_a_unit_absent_at_the_base(self):
        # absent at the base counts 0 there
        def absent(t):
            t.remove("measures/stock")
        def present(t):
            for rel, text in base_files().items():
                if rel.startswith("measures/stock/"):
                    t.write(rel, text)
        res = self.judge_change(plant_base=absent, plant_head=present)
        self.assertDecision(res, True)
        self.assertNumbers(res, "stock", 1, 0)

    def test_fails_when_a_number_drops(self):
        res = self.judge_change(plant_head=lambda t: t.write("src/petshop/catalog.py", CATALOG_WRONG))
        self.assertDecision(res, False)
        self.assertNumbers(res, "catalog", 0.5, 1)

    def test_fails_when_verdict_fails_without_a_drop(self):
        # the base was already failing; the number stays, the verdict still fails
        def wrong(t):
            t.write("src/petshop/catalog.py", CATALOG_WRONG)
        res = self.judge_change(plant_base=wrong,
                                plant_head=lambda t: t.append("src/petshop/stock.py", "# unrelated\n"))
        self.assertDecision(res, False)
        self.assertNumbers(res, "catalog", 0.5, 0.5)

    def test_fails_when_rules_fail(self):
        res = self.judge_change(plant_head=lambda t: t.insert_line("src/petshop/stock.py", "import socket"))
        self.assertDecision(res, False)

    def test_fails_when_build_fails(self):
        res = self.judge_change(plant_head=lambda t: t.append("src/petshop/orders.py", "def broken(:\n"))
        self.assertDecision(res, False)
        self.assertFailed(res, "orders", "build")

    def test_fails_when_proof_fails(self):
        # a planted case that passes the stock measure (it is the correct module)
        def unproven(t):
            t.write("measures/stock/planted/not_wrong.py",
                    "# Defect: claimed, but none.\n" + t.read("src/petshop/stock.py"))
        res = self.judge_change(plant_head=unproven)
        self.assertDecision(res, False)
        self.assertFailed(res, "stock", "proof")

    def test_fails_when_a_unit_has_no_measure(self):
        res = self.judge_change(plant_head=lambda t: t.remove("measures/orders"))
        self.assertDecision(res, False)


if __name__ == "__main__":
    unittest.main()

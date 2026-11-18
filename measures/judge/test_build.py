"""build <unit>: byte-compiles src/ into a fresh temporary directory."""

import unittest

from .plant import TreeCase


class BuildTest(TreeCase, unittest.TestCase):
    def test_passes_on_valid_src(self):
        res = self.tree.run("build", "catalog")
        self.assertDecision(res, True)
        self.assertEqual(res.data.get("unit"), "catalog", res.describe())

    def test_fails_on_syntax_error_in_the_units_module(self):
        self.tree.append("src/petshop/catalog.py", "def broken(:\n    pass\n")
        res = self.tree.run("build", "catalog")
        self.assertDecision(res, False)
        self.assertEqual(res.data.get("unit"), "catalog", res.describe())

    def test_fails_on_syntax_error_anywhere_in_src(self):
        # build compiles all of src/, not only the unit's own module
        self.tree.append("src/petshop/orders.py", "x = = 1\n")
        res = self.tree.run("build", "pet-shop")
        self.assertDecision(res, False)

    def test_writes_nothing_into_src(self):
        res = self.tree.run("build", "stock")
        self.assertDecision(res, True)
        written = [str(p) for p in (self.tree.path / "src").rglob("*")
                   if p.name == "__pycache__" or p.suffix == ".pyc"]
        self.assertEqual(written, [], "build wrote into src/ instead of a temporary directory")


if __name__ == "__main__":
    unittest.main()

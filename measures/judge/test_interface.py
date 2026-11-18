"""Malformed calls and unknown units exit 2."""

import unittest

from .plant import TreeCase


class InterfaceTest(TreeCase, unittest.TestCase):
    def test_unknown_unit_build(self):
        self.assertMalformed(self.tree.run("build", "nosuch"))

    def test_unknown_unit_verdict(self):
        self.assertMalformed(self.tree.run("verdict", "nosuch"))

    def test_unknown_unit_proof(self):
        self.assertMalformed(self.tree.run("proof", "nosuch"))

    def test_unknown_unit_with_a_measure_on_disk(self):
        # a measure directory does not make a unit known
        self.tree.write("measures/payments/test_payments.py",
                        "import unittest\n\n\nclass T(unittest.TestCase):\n"
                        "    def test_ok(self):\n        pass\n")
        self.assertMalformed(self.tree.run("verdict", "payments"))

    def test_no_command(self):
        self.assertMalformed(self.tree.run())

    def test_unknown_command(self):
        self.assertMalformed(self.tree.run("deploy", "catalog"))

    def test_verdict_without_unit(self):
        self.assertMalformed(self.tree.run("verdict"))

    def test_judge_without_base(self):
        self.assertMalformed(self.tree.run("judge"))

    def test_judge_base_without_ref(self):
        self.assertMalformed(self.tree.run("judge", "--base"))

    def test_malformed_call_prints_one_json_object(self):
        # "Every command prints one JSON object on stdout", a malformed one too
        res = self.tree.run("verdict", "nosuch")
        self.assertMalformed(res)
        self.assertIsInstance(res.data, dict, "stdout is not one JSON object\n" + res.describe())


if __name__ == "__main__":
    unittest.main()

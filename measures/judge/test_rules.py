"""rules: the pet shop's rules R1-R3 (units/pet-shop/unit.md) on src/.

Each violation is planted alone in an otherwise clean tree, at a known file
and line; the judge must fail and report it.
"""

import unittest

from .plant import STOCK as STOCK_SRC
from .plant import TreeCase

STOCK = "src/petshop/stock.py"


class CleanTreeTest(TreeCase, unittest.TestCase):
    def test_passes_a_clean_tree(self):
        # the clean tree has catalog items with a "name" (a pet's, not a customer's)
        res = self.tree.run("rules")
        self.assertDecision(res, True)
        self.assertEqual(self.violations(res), [], res.describe())

    def test_passes_open_for_reading(self):
        self.tree.append(STOCK, (
            "\n\ndef load(path):\n"
            "    with open(path) as f:\n"
            "        return f.read()\n"))
        res = self.tree.run("rules")
        self.assertDecision(res, True)

    def test_checks_src_only(self):
        # measures may use what src/ may not
        self.tree.insert_line("measures/stock/test_stock.py", "import subprocess  # noqa")
        res = self.tree.run("rules")
        self.assertDecision(res, True)


class R1Test(TreeCase, unittest.TestCase):
    """R1: standard library only; no network, process or file effects."""

    def plant_import(self, statement):
        line = self.tree.insert_line(STOCK, statement, after=1)
        res = self.tree.run("rules")
        self.assertDecision(res, False)
        self.assertViolation(res, "R1", STOCK, line)

    def test_socket(self):
        self.plant_import("import socket")

    def test_urllib(self):
        self.plant_import("from urllib import request")

    def test_http_client(self):
        self.plant_import("import http.client")

    def test_smtplib(self):
        self.plant_import("import smtplib")

    def test_subprocess(self):
        self.plant_import("from subprocess import run")

    def test_ftplib(self):
        self.plant_import("import ftplib")

    def test_ssl(self):
        self.plant_import("import ssl")

    def test_outside_standard_library(self):
        self.plant_import("import requests")

    def test_open_for_writing(self):
        for call in ('open("levels.txt", "w")', 'open("levels.txt", mode="a")'):
            with self.subTest(call=call):
                self.tree.write(STOCK, STOCK_SRC)
                first = self.tree.append(STOCK, "\n\ndef save(levels):\n    with %s as f:\n        f.write(str(levels))\n" % call)
                line = first + 3  # blank, blank, def, with
                res = self.tree.run("rules")
                self.assertDecision(res, False)
                self.assertViolation(res, "R1", STOCK, line)


class R2Test(TreeCase, unittest.TestCase):
    """R2: no field for personal data of a customer."""

    def plant_field(self, text):
        line = self.tree.append("src/petshop/orders.py", "\n\n" + text + "\n") + 2
        res = self.tree.run("rules")
        self.assertDecision(res, False)
        self.assertViolation(res, "R2", "src/petshop/orders.py", line)

    def test_email(self):
        self.plant_field('CUSTOMER = {"email": None}')

    def test_email_parameter(self):
        self.plant_field("def notify(order, email): return (order, email)")

    def test_card(self):
        self.plant_field('PAYMENT = {"card_number": None}')

    def test_address(self):
        self.plant_field('SHIPPING = {"address": None}')

    def test_customer_name(self):
        self.plant_field('CUSTOMER = {"customer_name": None}')


class R3Test(TreeCase, unittest.TestCase):
    """R3: code lives in src/petshop/."""

    def test_code_outside_src_petshop(self):
        self.tree.write("src/helper.py", "def helper():\n    return 1\n")
        res = self.tree.run("rules")
        self.assertDecision(res, False)
        self.assertViolation(res, "R3", "src/helper.py")

    def test_code_in_another_package_under_src(self):
        self.tree.write("src/other/__init__.py", "X = 1\n")
        res = self.tree.run("rules")
        self.assertDecision(res, False)
        self.assertViolation(res, "R3", "src/other/__init__.py")


if __name__ == "__main__":
    unittest.main()

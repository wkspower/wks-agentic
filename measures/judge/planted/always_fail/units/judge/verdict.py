# Defect: decides nothing; every call fails (exit 1, "pass": false).
"""Planted judge that always fails. The measure of the Judge unit must fail
against it: python3 measures/judge/prove.py"""

import json
import sys

print(json.dumps({"pass": False}))
sys.exit(1)

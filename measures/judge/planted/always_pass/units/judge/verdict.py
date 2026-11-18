# Defect: decides nothing; every call passes (exit 0, "pass": true).
"""Planted judge that always passes. The measure of the Judge unit must fail
against it: python3 measures/judge/prove.py"""

import json
import sys

print(json.dumps({"pass": True}))
sys.exit(0)

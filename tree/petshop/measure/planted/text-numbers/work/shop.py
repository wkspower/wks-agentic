# Planted wrong result: the work that stood and was shown wrong (ledger, revoked).
#!/usr/bin/env python3
"""The pet shop: customers and pets, appointments, stock and counter sales,
kept in one file on this machine.

    python3 shop.py FILE AREA COMMAND [ARGUMENT ...]

AREA is customers, appointments, stock or sales; COMMAND is one of the area's
(see its unit.md). An argument is text, unless it starts with = and is then
JSON: =3 is the number 3, =[[1,2]] is two of product 1. Examples:

    python3 shop.py shop.json customers add_customer "Ana Souza" 555-0101
    python3 shop.py shop.json customers add_pet =1 Rex dog
    python3 shop.py shop.json appointments book =2 bath 2026-11-20T10:00
    python3 shop.py shop.json stock add_product "Dog food 1 kg" =2500 =10
    python3 shop.py shop.json sales sell "=[[1, 2]]"

Each command prints its result as JSON and saves. A refused command says why,
exits with an error and leaves the file as it was.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

AREAS = ("customers", "appointments", "stock", "sales")
MARK = "petshop"


def _child(name):
    """A child unit, reached only through the module its document names."""
    for folder in Path(__file__).resolve().parents:
        path = folder / name / "work" / f"{name}.py"
        if path.exists():
            spec = importlib.util.spec_from_file_location(f"petshop_{name}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"unit {name} not found")


class Shop:
    def __init__(self, path, stations=1):
        self._path = Path(path)
        state = {MARK: 1}
        if self._path.exists():
            try:
                state = json.loads(self._path.read_text())
            except ValueError:
                state = None
            if not isinstance(state, dict) or state.get(MARK) != 1:
                raise ValueError(f"{self._path} is not a pet shop file; it was left as it is")
        self._state = state
        part = lambda name: state.setdefault(name, {})
        self.customers = _child("customers").Customers(part("customers"))
        self.appointments = _child("appointments").Appointments(part("appointments"), self.customers.has_pet, stations)
        self.stock = _child("stock").Stock(part("stock"))
        self.sales = _child("sales").Sales(part("sales"), self.stock, self.customers.has_customer)

    def save(self):
        """Write the whole file, or nothing: the old file is replaced only by a complete new one."""
        fresh = self._path.with_name(self._path.name + ".new")
        fresh.write_text(json.dumps(self._state, indent=1, ensure_ascii=False) + "\n")
        os.replace(fresh, self._path)


def main(argv):
    if len(argv) < 3 or argv[1] not in AREAS or argv[2].startswith("_"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        shop = Shop(argv[0])
        command = getattr(getattr(shop, argv[1]), argv[2], None)
        if not callable(command):
            print(f"{argv[1]} has no command {argv[2]}", file=sys.stderr)
            return 2
        result = command(*[json.loads(a[1:]) if a.startswith("=") else a for a in argv[3:]])
    except (ValueError, LookupError, TypeError) as refusal:
        print(f"refused: {str(refusal).strip(chr(34) + chr(39))}", file=sys.stderr)
        return 1
    shop.save()
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

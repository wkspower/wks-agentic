"""Planted wrong result: a shop that works all day and saves nothing."""
import importlib.util
from pathlib import Path


def child(name):
    for folder in Path(__file__).resolve().parents:
        path = folder / name / "work" / f"{name}.py"
        if path.exists():
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(name)


class Shop:
    def __init__(self, path):
        state = {}
        self.customers = child("customers").Customers(state.setdefault("customers", {}))
        self.appointments = child("appointments").Appointments(state.setdefault("appointments", {}), self.customers.has_pet)
        self.stock = child("stock").Stock(state.setdefault("stock", {}))
        self.sales = child("sales").Sales(state.setdefault("sales", {}), self.stock, self.customers.has_customer)

    def save(self):
        pass

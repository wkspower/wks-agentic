"""Planted wrong result: books anything valid, never looks at what is already booked."""
from datetime import datetime


class Appointments:
    def __init__(self, state, pet_exists, capacity=1):
        self.rows = state.setdefault("rows", [])
        self.pet_exists = pet_exists

    def book(self, pet_id, service, start, minutes=60):
        if service not in ("bath", "grooming") or minutes <= 0:
            raise ValueError("not valid")
        datetime.strptime(start, "%Y-%m-%dT%H:%M")
        if not self.pet_exists(pet_id):
            raise LookupError("no such pet")
        self.rows.append({"id": len(self.rows) + 1, "pet_id": pet_id, "service": service, "start": start,
                          "minutes": minutes, "status": "booked"})
        return len(self.rows)

    def _set(self, ident, status):
        rows = [r for r in self.rows if r["id"] == ident]
        if not rows:
            raise LookupError("no such booking")
        if rows[0]["status"] != "booked":
            raise ValueError("not booked")
        rows[0]["status"] = status

    def cancel(self, ident):
        self._set(ident, "cancelled")

    def done(self, ident):
        self._set(ident, "done")

    def day(self, date):
        datetime.strptime(date, "%Y-%m-%d")
        return sorted((dict(r) for r in self.rows if r["start"].startswith(date)), key=lambda r: r["start"])

    def for_pet(self, pet_id):
        return sorted((dict(r) for r in self.rows if r["pet_id"] == pet_id), key=lambda r: r["start"])

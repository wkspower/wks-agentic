"""Bookings of bath and grooming: no station and no pet twice at the same time."""
from datetime import datetime, timedelta

SERVICES = ("bath", "grooming")
FORMAT = "%Y-%m-%dT%H:%M"


def _moment(text):
    try:
        moment = datetime.strptime(text, FORMAT)
    except (TypeError, ValueError):
        raise ValueError(f"'{text}' is not a date and time like 2026-11-20T10:00")
    if moment.strftime(FORMAT) != text:
        raise ValueError(f"'{text}' is not a date and time like 2026-11-20T10:00")
    return moment


class Appointments:
    def __init__(self, state, pet_exists, capacity=1):
        self._rows = state.setdefault("appointments", [])
        self._pet_exists = pet_exists
        self._capacity = capacity

    @staticmethod
    def _span(row):
        start = _moment(row["start"])
        return start, start + timedelta(minutes=row["minutes"])

    def _row(self, appointment_id):
        for row in self._rows:
            if row["id"] == appointment_id:
                return row
        raise LookupError(f"no appointment {appointment_id}")

    def book(self, pet_id, service, start, minutes=60):
        if service not in SERVICES:
            raise ValueError(f"the service is one of {SERVICES}")
        if type(minutes) is not int or minutes <= 0:
            raise ValueError("the duration is a whole number of minutes above zero")
        begin = _moment(start)
        end = begin + timedelta(minutes=minutes)
        if not self._pet_exists(pet_id):
            raise LookupError(f"no pet {pet_id}")
        together = [r for r in self._rows if r["status"] != "cancelled"
                    and self._span(r)[0] < end and begin < self._span(r)[1]]
        if any(r["pet_id"] == pet_id for r in together):
            raise ValueError("this pet already has an appointment at that time")
        if len(together) >= self._capacity:
            raise ValueError("no station is free at that time")
        row = {"id": max((r["id"] for r in self._rows), default=0) + 1, "pet_id": pet_id, "service": service,
               "start": start, "minutes": minutes, "status": "booked"}
        self._rows.append(row)
        return row["id"]

    def _close(self, appointment_id, status):
        row = self._row(appointment_id)
        if row["status"] != "booked":
            raise ValueError(f"appointment {appointment_id} is already {row['status']}")
        row["status"] = status

    def cancel(self, appointment_id):
        self._close(appointment_id, "cancelled")

    def done(self, appointment_id):
        self._close(appointment_id, "done")

    def _listed(self, keep):
        return sorted((dict(r) for r in self._rows if keep(r)), key=lambda r: (r["start"], r["id"]))

    def day(self, date):
        _moment(f"{date}T00:00")
        return self._listed(lambda r: r["start"].startswith(date + "T"))

    def for_pet(self, pet_id):
        return self._listed(lambda r: r["pet_id"] == pet_id)

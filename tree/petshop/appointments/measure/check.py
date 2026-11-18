#!/usr/bin/env python3
"""Measure of appointments. Usage: check.py UNIT_DIR (the folder holding work/appointments.py).
The pets are numbers given by the measure; pet 1 and 2 and 3 exist, others do not."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "measure"))
from scenarios import main, refuses, scenario, through_json


DAY = "2026-11-20"
known = lambda pet_id: pet_id in (1, 2, 3)


def book_one(m, **more):
    a = m.Appointments({}, known, **more)
    return a, a.book(1, "bath", DAY + "T10:00")


@scenario
def book(m):
    """a booking is listed on its day with pet, service, start, minutes and status"""
    a, first = book_one(m)
    assert a.day(DAY) == [{"id": first, "pet_id": 1, "service": "bath", "start": DAY + "T10:00",
                           "minutes": 60, "status": "booked"}]


@scenario
def services(m):
    """only bath and grooming are booked"""
    a, _ = book_one(m)
    a.book(2, "grooming", DAY + "T12:00", minutes=90)
    refuses(ValueError, a.book, 2, "surgery", DAY + "T15:00")
    assert len(a.day(DAY)) == 2


@scenario
def pet_must_exist(m):
    """a booking for a pet the shop does not know is refused"""
    a, _ = book_one(m)
    refuses(LookupError, a.book, 999, "bath", DAY + "T15:00")
    assert len(a.day(DAY)) == 1


@scenario
def time_must_be_valid(m):
    """a start that is not a date and time, or a duration that is not positive, is refused"""
    a, _ = book_one(m)
    for start in ("tomorrow", "2026-13-01T10:00", "2026-11-20", "2026-11-20T25:00", ""):
        refuses(ValueError, a.book, 2, "bath", start)
    refuses(ValueError, a.book, 2, "bath", DAY + "T15:00", minutes=0)
    refuses(ValueError, a.book, 2, "bath", DAY + "T15:00", minutes=-30)
    assert len(a.day(DAY)) == 1


@scenario
def no_overlap(m):
    """with one station, a booking that overlaps another is refused, whichever way it overlaps"""
    a, _ = book_one(m)
    for start, minutes in (("T10:00", 60), ("T10:30", 60), ("T09:30", 60), ("T09:00", 180), ("T10:15", 15)):
        refuses(ValueError, a.book, 2, "grooming", DAY + start, minutes=minutes)
    assert len(a.day(DAY)) == 1


@scenario
def back_to_back(m):
    """a booking may start when another ends, and end when another starts"""
    a, _ = book_one(m)
    a.book(2, "bath", DAY + "T11:00")
    a.book(3, "bath", DAY + "T09:00")
    assert [x["pet_id"] for x in a.day(DAY)] == [3, 1, 2]


@scenario
def overlap_across_midnight(m):
    """a booking that runs past midnight still blocks the next morning's first minutes"""
    a = m.Appointments({}, known)
    a.book(1, "grooming", "2026-11-20T23:30", minutes=60)
    refuses(ValueError, a.book, 2, "bath", "2026-11-21T00:15")
    a.book(2, "bath", "2026-11-21T00:30")


@scenario
def capacity(m):
    """the number of stations is given: with two, two bookings may overlap and a third may not"""
    a, _ = book_one(m, capacity=2)
    a.book(2, "bath", DAY + "T10:30")
    refuses(ValueError, a.book, 3, "bath", DAY + "T10:45")
    a.book(3, "bath", DAY + "T11:00")


@scenario
def one_pet_one_place(m):
    """the same pet is never in two overlapping bookings, however many stations there are"""
    a, _ = book_one(m, capacity=2)
    refuses(ValueError, a.book, 1, "grooming", DAY + "T10:30")


@scenario
def cancel(m):
    """a cancelled booking stays in the list as cancelled and frees its time"""
    a, first = book_one(m)
    a.cancel(first)
    assert a.day(DAY)[0]["status"] == "cancelled"
    a.book(2, "bath", DAY + "T10:00")
    refuses(ValueError, a.cancel, first)
    refuses(LookupError, a.cancel, 999)


@scenario
def done(m):
    """a booking is marked done; what is done cannot be cancelled or done again, and still holds its time"""
    a, first = book_one(m)
    a.done(first)
    assert a.day(DAY)[0]["status"] == "done"
    refuses(ValueError, a.cancel, first)
    refuses(ValueError, a.done, first)
    refuses(LookupError, a.done, 999)
    refuses(ValueError, a.book, 2, "bath", DAY + "T10:30")


@scenario
def day_list(m):
    """the list of a day has only that day, in order of start"""
    a, _ = book_one(m)
    a.book(2, "bath", DAY + "T08:00")
    a.book(3, "bath", "2026-11-21T08:00")
    assert [x["start"] for x in a.day(DAY)] == [DAY + "T08:00", DAY + "T10:00"]
    assert a.day("2026-11-22") == []
    refuses(ValueError, a.day, "someday")


@scenario
def history(m):
    """the bookings of one pet, in order of start"""
    a, _ = book_one(m)
    a.book(1, "grooming", "2026-11-10T10:00")
    a.book(2, "bath", "2026-11-12T10:00")
    assert [x["start"] for x in a.for_pet(1)] == ["2026-11-10T10:00", DAY + "T10:00"]
    assert a.for_pet(3) == []


@scenario
def copies(m):
    """what is read is a copy"""
    a, _ = book_one(m)
    a.day(DAY)[0]["status"] = "x"
    assert a.day(DAY)[0]["status"] == "booked"


@scenario
def state_is_data(m):
    """everything lives in the state it was given, which survives being written as JSON"""
    state = {}
    a = m.Appointments(state, known)
    first = a.book(1, "bath", DAY + "T10:00")
    again = m.Appointments(through_json(state), known)
    assert [x["id"] for x in again.day(DAY)] == [first]
    refuses(ValueError, again.book, 2, "bath", DAY + "T10:30")
    assert again.book(2, "bath", DAY + "T11:00") != first


if __name__ == "__main__":
    main("appointments", expected=15)

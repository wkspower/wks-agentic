# L0011 — Grooming has one groomer and one-hour slots: an appointment belongs to a pet, and a taken slot is refused

## Reason
With one groomer, two pets in one slot is the error that matters. Slots start
on the hour, first 09:00, last 17:00, every day; the hours are the builder's
choice. A cancelled appointment stays on record and frees its slot. A date
before today is refused.

## Source
The person, run 001, 2026-11-19 (answer 11). The opening hours have not been
seen by the person.

## What would be a regression
Two live appointments in one slot, an appointment with no pet or for a pet
that does not exist, a time off the hour accepted, or a cancelled appointment
still blocking its slot.

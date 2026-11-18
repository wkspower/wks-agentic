# Appointments

Parent: [petshop](../unit.md). Governed by [`principles.md`](../../../principles.md).

## The six declarations

1. **Purpose** — The staff book bath and grooming for a pet and see what each day holds.
2. **Interface** — Offers the executable `units/petshop/appointments/run`, speaking [the shop's protocol](../unit.md), with the operations below; *build* and *verdict* through [`tree`](../../cycle/unit.md). Receives a data directory and `PETSHOP_PEER`.
3. **Rules** — Its parent's; none added.
4. **Budget** — Attempts: 3 per change (root). Effects without undo: zero. Attention: one item open in the shop's queue (`units/petshop/queue.md`). Time: a verdict within 5 minutes. Context: this document within 80 lines. Cost: no spending.
5. **Measure** — [`measures/petshop/appointments/check`](../../../measures/petshop/appointments/check), written by the shop before this unit: one case or more per line below. Number: cases right.
6. **Judge** — [`judge`](../../judge/unit.md).

## The operations

- `appointments.book {pet, service, date, time}` → `{id}`. `service` is `bath` or `grooming`. `invalid` for an impossible service, date or time; `not_found` when the peer does not know the pet (`customers.pet_get`); `conflict` when a booked appointment already holds that date and time.
- `appointments.day {date}` → `{appointments: [{id, pet, service, date, time, status}]}`, earliest first; `status` is `booked`, `cancelled` or `done`.
- `appointments.cancel {id}` and `appointments.done {id}` → `{}`. A cancelled appointment stays on its day and frees its date and time.

## The principles here

| Principle | At this part |
|---|---|
| 1 Boundary | It answers through `run` and nothing else; it learns whether a pet exists only by asking its peer. |
| 2 Single source | The operations above live here; the protocol and the codes are cited from the shop. |
| 3 External enforcement | By the [enforcer](../../enforcer/unit.md), from the last recorded state. |
| 4 Rehearsal before effect | Its verdict runs on a copy in `.rehearsal/`, with a data directory created there. |
| 5 Return | A failing change is returned by the cycle; a refused request changes nothing, which the measure checks. |
| 6 Selection | A change stands only by the judge, on the number of the measure. |
| 7 Escalation | What its measure does not decide it asks in the shop's queue; none is open. Limit: the measure's peer is a stand-in that knows two pets; the real pairing is measured by the shop. |

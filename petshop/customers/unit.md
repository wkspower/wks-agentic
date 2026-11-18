# Customers

Parent: [`petshop`](../unit.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — Know who the shop sells to: registered customers, each with an id that is never reused.
2. **Interface** — A module `customers.py`. Every function takes the customers state first; the state is made only by `new()`, is opaque to callers and survives `json.loads(json.dumps(state))` unchanged in behaviour. A customer is a dict with exactly `id` and `name`; returned customers are copies. Nothing but a name is held (no real personal data).
   - `new()` returns an empty state.
   - `register(state, name)` stores the name stripped of surrounding whitespace and returns the new id: `"C1"`, then `"C2"`, and so on. `ValueError` when `name` is not a string or is empty once stripped. Two customers may share a name.
   - `get(state, customer_id)` returns the customer; `KeyError` when unknown.
   - `find(state, text)` returns the customers whose name contains `text`, ignoring case, in order of registration; every customer when `text` is `""`.

   A refused call changes nothing. Offers *build* and *verdict*.
3. **Rules** — Those of [`petshop`](../unit.md), none added.
4. **Budget** — cost 2 runs; time 0.4 h; context 8 KB; attempts 2; alternatives 1; attention 0; no-undo cap 0.
5. **Measure** — `measure/check <build-dir>`: cases that call `customers.py` from the build; passes only if all pass; number: bytes of `customers.py`. Written before the unit by an agent that does not build it; planted wrong modules in `measure/planted/` must each fail. Error (seen by the pet shop, in [`record.md`](../record.md)): unknown, and a limit, until audit cases exist: cases written from this document alone by an agent that sees neither measure nor build.
6. **Judge** — The [`judge`](../../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The shop sees `verdict`, the number and the functions above; the module holds no state of its own and imports no other unit's module. |
| 2 Single source | Customers live only in this state; others hold ids and ask `get`. |
| 3 External enforcement | As [`petshop`](../unit.md) row 3. |
| 4 Rehearsal before effect | As [`petshop`](../unit.md) row 4. |
| 5 Return | As [`petshop`](../unit.md) row 5. A refused call leaves the state as it was. |
| 6 Selection | By the judge, against what exists and 1 alternative made without sight of the change. |
| 7 Escalation | Asks the pet shop only what no judge decides. Round before first effect: nothing foreseen beyond the declarations given. |

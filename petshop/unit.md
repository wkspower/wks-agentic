# Pet shop

Parent: [`root`](../root.md). Governed by [`principles.md`](../principles.md).

## The six declarations

1. **Purpose** — A pet shop system that sells animals and products to registered customers and keeps the stock right (Q9 of [`queue.md`](../queue.md), the person's words).
2. **Interface** — Offers one program, `shop.py`, run as `python3 shop.py --state FILE COMMAND ...`; the state file is created when missing. Commands, each printing one line on success and exiting 0:
   - `add-item ID NAME KIND PRICE_CENTS` prints `ID`
   - `receive ID QUANTITY` prints the quantity now on hand
   - `register NAME` prints the new customer id
   - `sell CUSTOMER_ID ID=QUANTITY [ID=QUANTITY ...]` prints `SALE_ID TOTAL_CENTS`
   - `stock ID` prints the quantity on hand
   - `takings` prints the sum of all sales in cents

   Anything its units refuse, an item unknown to the catalog (in `receive`, `stock` or `sell`), an unknown customer, or a malformed command (surplus arguments included): exit 1, a message on stderr, nothing on stdout, state file unchanged. Receives the modules of its four units ([`catalog`](catalog/unit.md), [`stock`](stock/unit.md), [`customers`](customers/unit.md), [`sales`](sales/unit.md)) and uses them only as their documents state. Offers *build* (`petshop/build`: assembles `shop.py` and the four modules into one directory) and *verdict* (`petshop/verdict`).
3. **Rules** — The root's and the enforcer's, plus, for itself and its units: Python 3 standard library only; no network, no real money, no real personal data (Q9); money is integer cents; no line longer than 100 characters; a unit's module imports no other unit's module.
4. **Budget** — cost 14 runs; time 2.5 h; context 8 KB; attempts 2; alternatives 1; attention 1; no-undo cap 0.
5. **Measure** — `petshop/measure/check <build-dir>`: scenarios run against `shop.py` as a program, from outside; number: bytes of the build's `shop.py`. Written before the unit by an agent that builds nothing here; planted wrong shops in `measure/planted/` must each fail. Error: unknown until the shop is built; its source will be audit scenarios written from this document alone, kept by the root.
6. **Judge** — The [`judge`](../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The root sees `verdict`, the number and what it is asked. The shop reaches its units only through the functions their documents list. |
| 2 Single source | Each unit's behaviour is stated only in its own document; the rules common to them only in rule 3 above. |
| 3 External enforcement | By the enforcer and by the measures, none of which the builders can alter: builders work outside the record and only the judge installs. |
| 4 Rehearsal before effect | Builds are made and checked in a directory outside the record; the judge checks copies. Nothing here acts outside the repository. |
| 5 Return | Each installation is one change, undone by reverting it, proven with `enforcer/undo`. The state file of a refused command is unchanged. |
| 6 Selection | By the judge, against what exists and 1 alternative made without sight of the change. |
| 7 Escalation | Asks the root only what no judge decides. Its round before first effect: nothing foreseen beyond the declarations given. |

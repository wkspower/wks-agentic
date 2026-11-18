# Web

Parent: [`petshop`](../unit.md). Governed by [`principles.md`](../../principles.md).

## The six declarations

1. **Purpose** — A professional user interface for the pet shop: everything the four units offer, in a browser, for someone who runs a shop and not a terminal (the person's goal and Q19, Q20 of [`queue.md`](../../queue.md)).
2. **Interface** — One program, `web.py`, run as `python3 web.py --state FILE [--port N]`. It listens on `127.0.0.1` only and serves the pages, forms and responses stated in [`pages.md`](pages.md), which is part of this declaration. It works on the same state file as `shop.py` ([`petshop`](../unit.md), declaration 2). Receives the modules of [`catalog`](../catalog/unit.md), [`stock`](../stock/unit.md), [`customers`](../customers/unit.md) and [`sales`](../sales/unit.md) and uses them only as their documents state. Offers *build* (`build`: `web.py` and the four modules assembled in one directory; `src` also holds the copies it was judged with, but `build` takes the modules from the units) and *verdict*.
3. **Rules** — Those of [`petshop`](../unit.md), plus what `pages.md` lists under *Rules of a professional interface*.
4. **Budget** — cost 4 runs; time 2.5 h; context 8 KB; attempts 2; alternatives 1; attention 0; no-undo cap 0.
5. **Measure** — `measure/check <build-dir>`: starts the program on a free port and checks every sentence of `pages.md`, over HTTP and in a real browser at 390, 768 and 1280 px. It passes only if every hard check passes. Number: the graded defects of `pages.md` counted over the pages, plus bytes of `web.py` ÷ 1,000,000. Written before the unit by an agent that does not build it; planted wrong builds in `measure/planted/` must each fail. Error (seen by the pet shop, in [`record.md`](../record.md)): wrong passes and wrong fails, from audit cases written from this document and `pages.md` alone, kept in `petshop/audit/web/`. Limits: the browser checks need the Chromium and Playwright of the place where they run; "professional" is measured only by what `pages.md` lists, and taste is not measured.
6. **Judge** — The [`judge`](../../judge/unit.md).

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The pet shop sees `verdict` and the number. The program reaches the four units only through the functions their documents list, and keeps nothing between requests but the state file. |
| 2 Single source | What the pages are is stated only in `pages.md`. What the shop knows lives only in the units' states; the pages show it and never keep a copy. |
| 3 External enforcement | As [`petshop`](../unit.md) row 3. |
| 4 Rehearsal before effect | As [`petshop`](../unit.md) row 4. The program is tried on a port of this machine with a state file in a temporary directory. |
| 5 Return | As [`petshop`](../unit.md) row 5. A refused request leaves the state file as it was; the file is replaced whole, never half written. |
| 6 Selection | By the judge, against what exists and 1 alternative made without sight of the change. |
| 7 Escalation | Asks the pet shop only what no judge decides. Round before first effect: kind, scope and budget were asked of the person by the root (Q19 to Q22); nothing else foreseen. |

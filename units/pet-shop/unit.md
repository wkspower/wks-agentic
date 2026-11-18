# Pet shop

Parent: [`root.md`](../../root.md). Governed by [`principles.md`](../../principles.md).
Record: [`record/pet-shop.log.md`](../../record/pet-shop.log.md).

## The six declarations

1. **Purpose** — A demonstration pet shop (scope decided by the person, Q4 in [`record/root.log.md`](../../record/root.log.md)): offer pets and supplies, keep stock, take and cancel orders, correctly, so that the tree's attention per correct result can be measured on real development work. Never deployed; no real customers, payments or personal data.
2. **Interface** — Offers *build* (`python3 -m units.judge.verdict build pet-shop`) and *verdict* (`python3 -m units.judge.verdict verdict pet-shop`), as defined by [`units/judge/unit.md`](../judge/unit.md). Offers the WSGI application `petshop.app:application` (Python 3, standard library only) with JSON bodies:
   - `GET /catalog[?kind=pet|supply]` → `200 [item, …]` sorted by `sku`.
   - `POST /catalog` body `item` → `201 item`; `400` invalid; `409` sku exists.
   - `GET /catalog/{sku}` → `200 item`; `404`.
   - `POST /stock/{sku}` body `{"qty": n}` → `200 {"sku", "available"}`; `404` unknown sku; `400` invalid qty; `409` a pet would exceed 1.
   - `GET /stock/{sku}` → `200 {"sku", "available"}`; `404`.
   - `POST /orders` body `{"lines": [{"sku", "qty"}, …]}` → `201 order`; `400` invalid; `404` unknown sku; `409` insufficient stock.
   - `GET /orders/{id}` → `200 order`; `404`.
   - `POST /orders/{id}/cancel` → `200 order`; `404`; `409` already cancelled.
   - Any other path or method → `404` or `405`. Every error body is `{"error": "<message>"}`.

   `item` is `{"sku": str, "name": str, "kind": "pet"|"supply", "price_cents": int}`; `order` is `{"id": str, "status": "placed"|"cancelled", "lines": [{"sku", "qty", "price_cents"}], "total_cents": int}`. Receives its declarations from the root.
3. **Rules** — The root's, plus: R1 standard library only and no network, process or file effects from `src/` (no `socket`, `urllib`, `http.client`, `smtplib`, `subprocess`, `ftplib`, `ssl`, and no `open(` for writing); R2 no field for personal data (no name, email, address or card of a customer); R3 code lives in `src/petshop/`, one module per child unit.
4. **Budget** — From the root's: cost at most USD 60 of the monthly USD 100; attempts 3 per change; cap on effects without undo zero; attention: it asks the root only, never the person.
5. **Measure** — [`measures/pet-shop/`](../../measures/pet-shop/), written by an agent that builds nothing here. Number: fraction of its cases passing; the children's numbers must also be 1.
6. **Judge** — [`units/judge`](../judge/unit.md).

Children: [`catalog`](catalog/unit.md), [`stock`](stock/unit.md), [`orders`](orders/unit.md). The application `src/petshop/app.py` belongs to this unit itself.

## The principles here

| Principle | Here |
|---|---|
| 1 Boundary | The root sees the verdict, the number and what is asked; the children are reached only through their Python interfaces. |
| 2 Single source | Interfaces live in each unit document; code and measures cite them. |
| 3 External enforcement | R1–R3 are checked by the judge, which this unit cannot alter. Limit: see the root's row 3. |
| 4 Rehearsal before effect | Every change is a commit on a working branch and a pull request to `develop`; the judge runs there. Nothing leaves the repository: there is no deployment. |
| 5 Return | Every change is a commit, undone by `git revert`; on failure the branch returns to the last commit whose verdict passed. |
| 6 Selection | The judge compares the number with `develop`'s. Limit: the budget does not pay for alternatives made without sight; recorded, not met. |
| 7 Escalation | Asks the root, through [`record/pet-shop.log.md`](../../record/pet-shop.log.md), what no judge decides. |

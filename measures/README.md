# Measures

Written by an agent that builds none of these units, without sight of `src/`,
following the conventions of [`units/judge`](../units/judge/unit.md). Each is
Python 3 `unittest`, standard library only, run from the repository root:
`python3 -m unittest discover -s measures/<unit>`.

| Unit | Measure | Against | Cases | Planted |
|---|---|---|---|---|
| [`catalog`](../units/pet-shop/catalog/unit.md) | [`catalog/`](catalog/) | `petshop.catalog` | 32 | 7 |
| [`stock`](../units/pet-shop/stock/unit.md) | [`stock/`](stock/) | `petshop.stock` | 30 | 7 |
| [`orders`](../units/pet-shop/orders/unit.md) | [`orders/`](orders/) | `petshop.orders` | 35 | 8 |
| [`pet-shop`](../units/pet-shop/unit.md) | [`pet-shop/`](pet-shop/) | `petshop.app:application` (WSGI, in-process) | 37 | 8 |

Number of each measure: passed cases / all cases (1 is a pass). Until `src/`
exists every measure fails at import, number 0.

Every planted case in `<unit>/planted/` is a whole replacement of the unit's
module, correct except for the defect named in its first line; each fails its
measure (verified against a private reference implementation that is not in
this repository). Every planted case must compile (`python3 -m py_compile
measures/*/planted/*.py`) and import cleanly, so that it fails its measure by
assertion, not by error.

The pet-shop application keeps state for the life of the process and offers no
reset, so each case of `pet-shop/` uses skus of its own and asserts only on them.

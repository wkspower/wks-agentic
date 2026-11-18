# Record of the pet shop

**State.** Not built: `shop.py` does not exist, so `verdict` fails. Its
measure exists (52 scenarios, 25 planted wrong shops, all failing).

| Unit | Document | Measure | Judge | Built |
|---|---|---|---|---|
| catalog | yes | 18 cases, 23 planted | judge | stands, 1190 |
| stock | yes | 12 cases, 17 planted | judge | no |
| customers | yes | 16 cases, 22 planted | judge | no |
| sales | yes | 56 cases, 24 planted | judge | no |
| pet shop | yes | 52 scenarios, 25 planted | judge | no |

**Error of the measures it gave** (declaration 5 of each unit).
- catalog, source `audit/catalog/check` (123 cases written from the
  document alone by an agent that saw neither measure nor build).
  Wrong passes: 0 of 2 builds that passed the measure (both pass all 123).
  Wrong fails: 0 of 23 builds that failed the measure (the planted ones);
  22 also fail the audit, and the one the audit passes imports a network
  module, which rule 3 forbids and the audit does not look for.
  Limit: the builds that failed are the measure writer's own planted ones.
- stock, customers, sales: unknown. No audit cases exist yet.

**Round before first effect.** Nothing asked of the root.

**Absorbed.** Gaps the measure writers reported, turned into rules in the
documents before any build: state changes in place; either refusal when two
apply; an item unknown to the catalog is refused by `receive`, `stock` and
`sell`; surplus arguments are malformed; returned sales copy their lines.

**Spend.** 5 of 13 runs (see `ledger.tsv`): 2 for measures, 3 for catalog.

**Due next.** Build stock, customers and sales (each: one build, one
alternative, the judge), then the shop. Audit cases for each need runs the
budget does not hold: 8 remain, the four builds take 8.

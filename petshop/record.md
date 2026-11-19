# Record of the pet shop

**State.** Built and standing. Verdict passes (61 scenarios); number 2824.
A fifth unit, web, offers the same shop in a browser on the same state file.
The shop runs: `python3 shop.py --state FILE COMMAND ...` after
`petshop/build <dir>`.

| Unit | Measure | Stands by the judge | Number |
|---|---|---|---|
| catalog | 23 cases, 26 planted | candidate over alternative | 1190 |
| stock | 12 cases, 17 planted | alternative over candidate | 862 |
| customers | 16 cases, 22 planted | alternative over candidate | 753 |
| sales | 56 cases, 24 planted | candidate over alternative | 1890 |
| web | 223 checks, 35 planted | alternative over candidate | 0.028550 |
| pet shop | 61 scenarios, 29 planted | candidate (2824) over alternative (2883) | 2824 |

**How the shop stood.** Two agents each wrote `shop.py` on unchanged copies
of the four standing modules, neither seeing the other. `src` holds what was
judged; `build` takes the modules from the units (declaration 2).

**Error of the measures it gave** (source: `audit/<unit>/check`, cases
written from each document alone by agents that saw neither measure nor
build). Wrong passes: builds that passed the measure and fail the audit.
Wrong fails: builds that failed the measure and are right by the audit.

| Unit | Audit cases | Wrong passes | Wrong fails |
|---|---|---|---|
| catalog | 123 | 0 of 2 | 0 of 23 |
| stock | 60 | 0 of 2 | 0 of 17 |
| customers | 97 | 0 of 2 | 0 of 22 |
| sales | 75 | 0 of 2 | 0 of 24 |
| web | 197 | 0 of 2 | 0 of 35 |

Where the audit passes a planted build (one each for catalog, stock,
customers), the build breaks rule 3 (a network import), which the audits do
not look for: the measure is right. Limit: the builds that failed are the
measure writers' own planted ones, and every offered build passed, so the
wrong-pass count rests on 2 builds per unit.

**Round before first effect.** Nothing asked of the root.

**Absorbed.** Gaps the measure writers reported became rules in the
documents before any build; the three points catalog's builders decided
became rules with cases.

**Spend.** 22 of 24 runs (`ledger.tsv`).

**Due next.** The points the builders of stock, customers, sales and the
shop and web decided for themselves (their records; for the shop: number
spellings, where `--state` goes, when the state file is written) become
rules with cases: about 5 runs; 2 remain here and 4 at the root.

# State of the work

Part of the durable record of [`root.md`](root.md). Whoever arrives resumes
from here, [`queue.md`](queue.md), [`ledger.jsonl`](ledger.jsonl) and the
history of this repository. Each unit's document is `units/<unit>/unit.md`;
its own notes are `units/<unit>/record.md`.

## How work proceeds

Edit the working tree in the name of one unit, then `./tree decide <unit> -m
"<what>"`. The [cycle](units/cycle/unit.md) rehearses, the unit's judge
decides, and the change is either committed with its ledger line or returned
and kept under `rejected/`. A measure changes in its own change, in the name
of the unit's parent, before the work it governs. `./tree verdict <unit>`
runs any measure; `./tree verdict root` gives the person's number.

## The tree on 2026-11-18

| Unit | Parent | Verdict | Number |
|---|---|---|---|
| root | the person | passes | 3 items, 0 days waited, 2 correct results; trend needs 20 |
| enforcer | root | passes | 36 of 36 |
| judge | root | passes | 16 of 16 |
| second-judge | root | passes | 9 of 9 |
| cycle | root | passes | 12 of 12 |
| petshop | root | fails: not built | 3 of 14 |
| petshop/customers | petshop | passes | 20 of 20 |
| petshop/appointments | petshop | fails: not built | 1 of 20 |
| petshop/stock | petshop | fails: not built | 1 of 19 |
| petshop/sales | petshop | fails: not built | 1 of 15 |

The numbers are a photograph; the commands above give them now.

## Next

1. Build `petshop/appointments`, `petshop/stock`, `petshop/sales`, each alone
   through the cycle; after each, the shop plants near-correct wrong results
   in its measure, as done for customers.
2. Build `units/petshop/run`; the shop's verdict then crosses the parts.
3. The shop gives a part for what the staff see, with its measure (the limit
   in principle 7 of [`units/petshop/unit.md`](units/petshop/unit.md)).
4. When the shop's verdict passes: real use is asked in `queue.md`. Under the
   budget that item needs 5 correct results; there are 2.

None of this waits for the person.

## Effects and how they were rehearsed

- `queue.md`, `state.md`: first effect, no rehearsal place existed; one
  commit, undone by `git revert`.
- `root.md` (decisions Q1, Q2): made in a branch, the check run there, the
  restore from history proven identical, then fast-forwarded; branch deleted.
- Bootstrap: `measures/` and the documents of enforcer, judge, second-judge
  and cycle were committed first, then the four units together. No judge
  existed to decide them, so they have no ledger line and count as no result.
- Everything since went through the cycle: ledger lines 1 onward.

## Limits, stated as limits

- **One agent.** The same agent wrote every measure, judge and unit.
  Independence holds by what a change can alter (the cycle takes judge,
  enforcer and measure from the last commit), not by who created what.
- **Nothing forces the cycle.** Whoever can write the repository can commit
  around it; a commit without a `Ledger:` line shows it and blocks nothing.
- **Measures of unbuilt parts are unproven upward.** Their plants are gross
  (a part that agrees with everything, one that refuses everything) and no
  implementation has yet passed them, so a wrong fail would not be seen until
  the part is built. Customers has six near-correct plants and a passing build.
- **Alternatives without sight** (principle 6) are not made; nothing pays for them.
- **Correct results** count only changes to a unit's own work that its judge
  compared by number. Declarations, measures and records given through the
  cycle are in the ledger and are not counted, so the number cannot be
  lowered by paperwork.
- **The window of 10** and "shown wrong stops counting" come from Q2 as
  asked, not from the words of the answer; see `queue.md`.

## Tried and rejected

- Building below the root before the answers: `root.md` forbade any effect.
- Changing `root.md` without a decision: only the person decides it; the
  enforcer now blocks it (rule E6).
- Ledger lines for the bootstrap: a judge deciding its own first build is no
  decision; left out.
- One judge for everything, itself included: not independent. Two judges
  that share no code judge each other.
- A stricter judge that lets a change stand only on a higher number: it
  could never accept the same result for less; equal number and fewer bytes
  stands.

# Queue of the root

The one queue of principle 7: what the root puts before the person. One entry
per item, with when it was opened and when it was answered; the waiting time
of each item is attention, and is counted. An answer given in the chat counts
only once it is written here.

State: **0 open, 3 answered.** Format read by the root's check: each item is a
`## Qn` section with one `Opened:` line and one `Answered:` line (`—` while open).

---

## Q1 — Budget values of the root

Opened: 2026-11-18T18:58Z
Answered: 2026-11-18T19:05Z
Why you are asked: `root.md` declaration 4 says "values: not yet given"; the
budget is given by the parent, and no judge exists above the root.

| Value | A — tight | **B — recommended** | C — loose |
|---|---|---|---|
| Attention: items open at once | 1 | **3** | 5 |
| Attention: items to build the tree, before the first delivery | 3 (these) | **6** | 12 |
| Attention: items afterwards | 1 per 10 correct results | **1 per 5 correct results, falling** | 1 per 2 |
| Cap on effects without undo | none allowed | **none allowed** | you name them |
| Where effects may happen | this repository, this branch | **this repository, this branch; no push, no deploy, no network** | you name it |
| Attempts per change, before it returns to the last passing state | 2 | **3** | 5 |
| Time per change, before it counts as exhausted | 1 session | **1 session** | no limit |
| Context per unit | its own document | **its own document (one page) plus what it cites** | no limit |
| Cost (money, compute) | — | **what one session of this channel costs; you state a number if you want one enforced** | — |

Recommendation: **B**. Reason: a cap of zero means nothing irreversible can
happen without an item reaching you, and everything inside a git branch has a
proven undo (restore from history), so nothing else needs your attention.
Limit, said as a limit: I cannot measure money from inside this repository; a
money value would be recorded but enforced by nothing until you give a source
for it.
Cost of waiting: total. Without these values the root causes no effect and
nothing below it is built.

**Answer of the person (Q1).** At most 3 items open at once. After this first
batch, at most 1 item per 5 correct results. Zero effects without undo:
everything stays in the repository, with no push, deploy, spending or real
customer data. 3 attempts per change before returning to the last passing
state. — Absorbed: values written in `root.md` declaration 4, read from there
by the root's check and by the judge.

## Q2 — Executable check of the root's measure

Opened: 2026-11-18T18:58Z
Answered: 2026-11-18T19:05Z
Why you are asked: `root.md` declaration 5 says "executable check: not yet
written"; the measure is given by the parent and written by someone who does
not build the unit.

What has to be decided is what the check counts. Proposed definition:

- **Attention** = entries of this file: the number of items, and the hours
  each waited between "opened" and "answered".
- **Correct result** = a change that stood: its unit's verdict passed, its
  judge accepted it, and no later case showed it wrong (a result later shown
  wrong is subtracted, and the case goes into the measure that let it pass).
- **Number** = items per correct result, and waiting hours per correct
  result, over the last 10 correct results.
- **Pass** = both numbers are not higher than in the previous window, the
  queue is not longer than at the previous window, and the attention values
  of Q1 are respected. While there are fewer than 10 correct results, pass =
  the Q1 values are respected.
- **Planted wrong result**: a copy of the record with attention rising, one
  with the queue growing, and one with a "correct result" its judge never
  accepted; each must fail the check, at every change to the check.
- **Your view of its error**: wrong passes and wrong fails are counted from
  what you notice and write here, a source the check does not read.

Options for who writes it:

- **A — recommended.** You adopt the definition above (with your edits); a
  unit that builds nothing else writes the script from it, before any other
  unit is built, and proves it with the planted cases.
- B. You write the script yourself.
- C. You give a different definition; same procedure as A.

Limit, said as a limit: in this channel a single agent both writes that
script and builds the tree, so "written by someone who does not build it" is
met only by your adopting the definition, not by the script. Under A the
script is kept where builders of other units are not allowed to change it,
and that is enforced by a check, but the independence is weaker than the
principle asks until a second agent exists.
Cost of waiting: total, same as Q1.

**Answer of the person (Q2).** Attention per correct result: queue items and
waiting time, divided by changes that passed their verdict and that their
judge let stand. It passes when the latest window is no worse than the one
before and the budget is respected. The agent writes it from this definition
before any other unit, with planted cases that must fail, and records the
single-agent limit as a limit. — Absorbed: `root.md` declaration 5 and
`measure/`. Absorbed as a rule for every later case of the same kind: where
one agent is both writer and builder, the measure is still written first and
proven by planted cases, and the missing independence is stated as a limit
in the unit's document; it is not asked again.

## Q3 — Purpose of the pet shop system

Opened: 2026-11-18T18:58Z
Answered: 2026-11-18T19:05Z
Why you are asked: the purpose of a unit is given by its parent. The parent
of the pet shop system is the root, and the root's declarations are yours; no
judge can decide what the system is for. Asked now, with Q1 and Q2, so it
does not cost a second wait.

- **A — recommended.** A system for the staff of one pet shop: customers and
  their animals, appointments for services (bath, grooming), products and
  stock, sales at the counter. It runs locally from this repository. It makes
  no effect outside it: no real payments, no messages to customers, no
  deployment. "Correct" is judged by executable scenarios of those four
  areas, written before the code.
- B. A plus an online side for customers (booking and shop). Larger, and it
  only makes sense with deployment, which Q1-B forbids.
- C. Your own sentence of purpose.

Recommendation: **A**, because it is the largest scope whose every effect has
an undo under Q1-B; anything in B can be added later as a change that goes
through selection.
Cost of waiting: none until Q1 and Q2 are answered; after that, total for the
pet shop branch of the tree.

**Answer of the person (Q3).** A system for the staff of one physical shop:
customers and their pets, appointments for bath and grooming, products with
stock, and counter sales. It runs locally, with no real payments. Real use:
not yet. Required technology: none. — Absorbed: purpose of
`tree/petshop/unit.md`.


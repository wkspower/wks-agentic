# Queue of the root

The one queue of principle 7: everything the root puts before the person.
Each item carries the options, a recommendation and the cost of waiting. An
answer counts once it is written here under its item. Items are never deleted;
their history is the source for the attention number.

| # | Asked | Answered | Waited | Subject |
|---|---|---|---|---|
| 1 | 2026-11-18T18:58Z | open | | Root budget values |
| 2 | 2026-11-18T18:58Z | open | | Root executable check |
| 3 | 2026-11-18T18:58Z | open | | What the pet shop system is for |

## 1. Root budget values (root.md, declaration 4)

Why asked: root.md says the values are not given and that they are the first
thing the person is asked. No judge exists that could give them.

Recommendation (option A), one value per kind named in principles.md:

| Kind | Value |
|---|---|
| Attention | At most 5 items before the first pet shop result judged correct, this queue's three included; after that, at most 1 item per 5 correct results, falling. Items are asked together, never one by one. |
| Cap on effects without undo | Zero. Everything the tree does is a commit in this repository, undone by reverting it. Anything that leaves the repository (push, deploy, paid service, real customer data, message to a third party) is an item here first. |
| Cost | No spending beyond the sessions the person starts. Any other cost is an item here. |
| Time | The tree down to the first buildable pet shop unit is in the record within 2 exchanges after these answers. A unit's change that has not passed by the end of the session that started it is returned (principle 5). |
| Context | One document of at most 80 lines per unit. Whoever resumes a unit reads principles.md, the documents of its ancestors and the unit's own record, nothing else. |
| Attempts | 3 per change. After the third failure the unit returns to its last passing state and the failure goes to its parent's queue as work, not to the person. |

Options: A, the table as written. B, the table with values the person
changes, named by kind. C, the person gives all values themselves.

Cost of waiting: nothing is built; no child unit can receive a budget, since
each is derived from this one.

## 2. Root executable check (root.md, declaration 5)

Why asked: root.md says the check is not written and is asked first. The
measure is given by the parent, here the person, who owns its error.

Recommended definition (option A):

- Source of attention: the table at the top of this file. One row per item;
  waiting is answered minus asked.
- Source of correct results: a ledger `results.md`, one row per delivery
  whose verdict passed and whose judge let it stand. A row is struck when a
  case later shows the result wrong, and stops counting from then on.
- Number: items per correct result, and hours waited per correct result, for
  the whole history and for the last 5 results.
- Verdict: passes when the last 5 results cost no more attention per result
  than the 5 before them and the count of open items is not higher than at
  the previous verdict. Fails otherwise, and fails while there are zero
  correct results.
- Planted wrong results that must fail it, rerun at every change to it: a
  history where items grow and results stay flat; a history where a struck
  result is still counted; an empty ledger.
- Error of the measure, from a source it does not use: whenever the person
  notices a wrong result that the ledger counts as correct, or attention
  spent that the table lacks, they say so here and it becomes a case.

Who writes the script:

- A (recommended): the person approves this definition; the script is
  written from it before any child unit exists, with the planted cases, and
  the person is its judge as root.md says. Limit, stated and not hidden: the
  same hands then build the units below, so "written by someone who does not
  build it" holds for the root itself, which the person wrote, but not for
  the tree under it. The planted cases and the person's noticing are the
  only checks on that.
- B: the person writes the script, or has it written in a session that never
  sees the rest of the tree. Meets the principle fully; costs the person
  more attention now.
- C: the person changes the definition; then A or B.

Cost of waiting: no verdict exists at the root, so the root causes no effect
and no change below it can ever be said to stand.

## 3. What the pet shop system is for

Why asked: the purpose of the pet shop unit is given by its parent and
derived from the root's, but what the shop needs is known only to the
person; what a unit was not given does not exist for it. Asked now, together
with 1 and 2, to save one round of waiting.

Recommendation (option A): a system for one physical pet shop, used by its
staff, that keeps customers and their pets, books and records services
(bath, grooming), sells products at the counter with stock kept right, and
shows the day's takings. A correct result is one such capability working
end to end for a member of staff, proven by its measure. Not included until
asked for: online store, payments through a card provider, tax documents,
veterinary records, more than one shop.

Options: A, as written. B, A with capabilities added or removed, named.
C, the person states the purpose in their own words.

Also needed under any option, one line each, or "not yet":
- whether a real shop will use it (if yes, real data and deployment are
  effects without undo and will come back here under item 1's cap);
- any technology the person requires. If none, the choice is made below the
  root by comparison (principle 6) and is not asked.

Cost of waiting: the pet shop unit has no purpose, so it and everything
under it stay unbuilt even after 1 and 2 are answered.

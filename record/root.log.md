# Root — record

Record of the unit [`root.md`](../root.md): the person's decisions verbatim,
the state of the work, and what was tried and rejected. Newest last. Cites
[`principles.md`](../principles.md); states no rule.

## 2026-11-18 — Queue 1 (asked in chat) and the person's answers

Asked because `root.md` says the budget values and the executable check are
the first thing the person is asked, and nothing else could be deduced.

**Q1. Root budget values.** Recommendation put: attention ≤ 5 queue items per
week, each decidable in ≤ 5 minutes (exceeding it is a design defect); cost a
monthly compute amount the person accepts losing entirely, suggested about
USD 100/month; time: no deadline, trend reviewed monthly; attempts: 3 failed
attempts per change, then it returns to the last passing state and becomes
work; cap on effects without undo: zero (anything irreversible is asked first).
**Answer: "accept".**

**Q2. Who writes the root's executable check.** Options: (a) the person;
(b) an independent agent without sight of the builder's work, which the person
accepts or rejects once, the person owning it and judging it; (c) the builder
(breaks principle 5 of the unit, declaration 5). Recommendation (b).
**Answer: "b".**

**Q3. Is the working branch the record.** Recommendation put: commits to
`claude/dreamy-cori-h2njwl` are the unit's own record, not an effect, each
undone by `git revert`; changes reach `main` (or any other branch) only with
the person's approval. **Answer: "accept".**

**Q4. Scope of the pet shop.** Options: (a) a demonstration system, built and
tested, never deployed, no real customers, payments or personal data; (b) a
real system. Recommendation (a), with a one-sentence purpose.
**Answer: "a".** (No sentence given; the child's purpose is derived by the root
from its own, as `principles.md` § The unit allows.)

**Q5. External enforcement on GitHub** (protection of the person's branch with
required status checks; measure and judge files owned by the person through
`CODEOWNERS`). Options: the person sets it up; the person gives admin access;
record as a limit. Recommendation: the person sets it up.
**Answer: "I give you admin access".**

## State after Queue 1

- Default branch of the repository is `develop` (there is no `main`); Q3's
  "main" is read as the default branch `develop`, the person's branch.
- Q5 could not be executed: the agent's GitHub tools offer no operation on
  branch protection or rulesets, whatever the access. Recorded as a limit and
  put back in the queue with the exact settings (see [`queue.md`](../queue.md)).

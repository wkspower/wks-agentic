# Queue

The root's one queue (principle 7): everything put before the person. Each
item is complete enough to decide without reading the work. Items are also
counted in [`record/queue.jsonl`](record/queue.jsonl) when they open, and
answers are recorded in [`record/root.log.md`](record/root.log.md).

The budget is at most 5 items per 7 days. Queue 1 (Q1–Q5) used that budget on
2026-11-18, so the items below open on **2026-11-25 at 18:40 UTC** and not before.

## Held — opens 2026-11-25

### Q6. Accept the root's executable check

[`measures/root/`](measures/root/) was written by an agent that saw only
`principles.md`, `root.md` and the record (your Q2 b). It counts each item put
before you and how long it waits, per delivery whose verdict passed and that
was not later shown wrong, week by week. It fails when more than 5 items open
in 7 days, when an item takes over 5 minutes, when an effect without undo was
not asked first, when the trend rises, or after 28 days with attention and no
correct result. It passes on the record today.

- **Options:** (a) accept as written; (b) accept with the strict reading, where a flat trend also fails (principle 7 says "does not fall"); (c) reject, and another agent writes one without sight of this one.
- **Recommendation:** (a). The strict reading fails a steady, low level of attention, which is not a defect.
- **Cost of waiting:** until it is accepted the root causes no effect, so nothing reaches `develop`. The work continues on the branch.

### Q7. Let the judge, not you, admit changes to `develop`

Under your Q3, changes reach `develop` only with your approval. That would
mean being asked about every delivery, which principle 7 forbids. Instead, the
judge ([`units/judge`](units/judge/unit.md)) runs as the status check `judge`.
The agents act on GitHub as your own account, so a review "by you" cannot be
told apart from one by an agent, and the agents' tools cannot set branch
rules at all (your Q5 grant could not be used).

- **Options:**
  - (a) You protect `develop`, and from then on a change that passes `judge` merges without asking you. A change to `principles.md`, `root.md`, `measures/`, `units/judge/` or `.github/` still comes to you as a queue item.
  - (b) As (a), but the agents get their own GitHub account or app, so `CODEOWNERS` review becomes yours alone. This takes more of your time once.
  - (c) Keep your approval on every merge.
- **Recommendation:** (a). It takes about 2 minutes: in Settings → Rules → Rulesets → New branch ruleset, set:
  - Name: `develop`.
  - Enforcement: Active.
  - Bypass list: empty.
  - Target: `develop`.
  - Rules: Restrict deletions; Block force pushes; Require a pull request before merging (0 approvals); Require status checks to pass, with `judge` required and branches up to date.
- **Cost of waiting:** nothing reaches `develop`. The work continues on the branch, but without the enforcement it does not count as judged.

## After these

Once Q6 and Q7 are decided, the root opens a pull request from the working
branch to `develop` and the judge decides it. It also schedules the
development cycle within the cost budget: a recurring session that takes the
next open work from the units' records. No further item is planned.

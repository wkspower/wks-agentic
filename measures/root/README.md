# Root measure

Executable check for declaration 5 of [`root.md`](../../root.md): the person's
attention per correct result, as a trend (principle 7). Budget values from
`record/root.log.md`, Queue 1, Q1. Written under Q2 (b), without sight of the
builder's work. Input format: [`INPUT.md`](INPUT.md).

## What it measures

Per week (Monday 00:00 UTC), over a trailing window of 4 weeks:

- **items per correct result** — queue items opened in the window ÷ correct results delivered in it;
- **wait hours per correct result** — total waiting time of those items ÷ the same.

The latest week with data is printed as `number`; every week is in `weekly`.
Infinite (attention, no correct result) prints as `"inf"`.

## Pass rule

Exit 0 (pass) only if none of these holds; otherwise exit 1 (fail), with the
reasons in `failures`:

1. **Malformed** — a file is missing, or any line breaks `INPUT.md`. Any unexpected error is also a fail.
2. **Budget** — more than 5 items opened in any sliding 7-day window, or an item with `decide_minutes` > 5.
3. **Cap** — a delivery with `undo: false` not tied (`asked`) to a queue item decided before it happened (cap on effects without undo is zero).
4. **Trend** — over the last 3 weeks with data, the latest value of either ratio is higher than the earliest. Also a fail: attention with no correct result in the latest window, once past bootstrap.
5. **No correct result** — queue items exist, none correct, and 28 days have passed since the first item.

**No deliveries yet:** within 28 days of the first queue item, the check passes
on rules 1–3 only (`status: no_correct_results`, number `inf`, trend
`insufficient`). Reason: the root must ask before it can deliver (Queue 1), so
failing at once would leave no passing state to return to (principle 5).
Indefinite asking without delivering is still caught by rule 5. With no queue
items and no deliveries it passes. A flat trend passes; principle 7's
"does not fall" is read as "rises" to avoid wrong fails at a steady low level.

## Run

```sh
python3 measures/root/check.py [--queue record/queue.jsonl] [--deliveries record/deliveries.jsonl] [--now 2026-11-18T12:00:00Z]
python3 -m unittest discover -s measures/root    # proof: planted wrong results fail
```

## Known error sources

Wrong passes (the check passes, the purpose is not served):
- Attention not written to the queue (asked in chat, unrecorded) is invisible. Compare the queue with what the person actually saw.
- `later_shown_wrong` never set, or `verdict` from a judge that is not independent, inflates correct results.
- Trivial or split deliveries inflate the count of results; the measure counts results, not their size.
- `decide_minutes` is optional and self-reported; without it the 5-minute limit is unchecked.
- The trend compares only the first and last of 3 weeks, so a rise inside them that falls back is missed; a flat trend passes.
- Malformed history rewritten to fit the format (lines deleted, not marked) is not detected; the git history of the files is the only check.

Wrong fails (the check fails, the purpose is served):
- Weekly noise: a quiet week with one notice and few deliveries can read as a rise.
- Open items accrue waiting time until now, so a long-open item raises the latest ratio every run.
- A burst of 6 well-founded items in 7 days fails the budget even if each was needed.
- Clock or timezone errors in the record (timestamps after `now`) fail as malformed.

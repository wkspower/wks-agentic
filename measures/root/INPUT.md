# Input of the root measure

Two JSON Lines files (UTF-8, one JSON object per line, blank lines ignored).
Default paths, relative to the repository root; both can be given as arguments
(`--queue`, `--deliveries`). Both files must exist; an empty file is valid.
A missing file, or any line that breaks this format, makes the check fail.

Timestamps: ISO 8601 with a timezone (`2026-11-18T09:30:00Z` or `+01:00`), not
after the time of the check. Ids: non-empty strings, unique within their file.

## `record/queue.jsonl` — everything put before the person

One line per item (a decision, a proposal, a notice to read), written when the
item is opened and updated when it is decided.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Unique id of the item. |
| `opened` | timestamp | yes | When the item was put before the person. |
| `decided` | timestamp or `null` | yes (key present) | When the person decided or acknowledged it; `null` while open. Not before `opened`. |
| `kind` | string | yes | One of `decision`, `proposal`, `notice`, `effect_without_undo`. |
| `decide_minutes` | number ≥ 0 or `null` | no | Minutes the person spent deciding, if recorded. |

```json
{"id": "Q1-1", "opened": "2026-11-18T09:00:00Z", "decided": "2026-11-18T09:20:00Z", "kind": "decision", "decide_minutes": 2}
{"id": "Q1-5", "opened": "2026-11-18T09:00:00Z", "decided": null, "kind": "proposal"}
```

## `record/deliveries.jsonl` — results delivered

One line per delivery whose verdict has run.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Unique id of the delivery. |
| `at` | timestamp | yes | When the verdict was given. |
| `verdict` | `"pass"` or `"fail"` | yes | The verdict of its judge. |
| `later_shown_wrong` | boolean | yes | `true` once a case shows the result was wrong (principle 6). Set it on the existing line; never delete the line. |
| `undo` | boolean | no, default `true` | `false` if the delivery made an effect without a proven undo. |
| `asked` | string | when `undo` is `false` | `id` of the queue item in which the person decided that effect. |

```json
{"id": "petshop-001", "at": "2026-11-20T15:00:00Z", "verdict": "pass", "later_shown_wrong": false}
```

A *correct result* is a line with `verdict` `pass` and `later_shown_wrong`
`false`. Attention is counted from the queue only: items, and their waiting
time (`decided − opened`, or `now − opened` while open).

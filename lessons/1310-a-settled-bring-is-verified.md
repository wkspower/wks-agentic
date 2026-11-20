# L1310 — A settled bring is still verified: what was taken from the other side is as that side has it and no marker is left, and what this side alone had changed may change in the settling and is named

## Reason
When two runs change one shared thing, the base refuses the second and the
branch with the product takes the base in (L1102). `./bring` there leaves
the files both changed marked, and a session settles them. Nothing after
that point said whether the settling had kept to its ground.

`./bring --verify OURS THEIRS` was the only tool that compares a tree with
what the rules give, and after a settling it could only say NOT. Two shared
cases that differ in what they call their part of a surface cannot be made
one without changing a file that was never marked: the surface of the
product whose name was not kept, which only its own side had written. The
rules give that file as its side had it, so the one right tree was "not
what the rules give", in the same words as a tree that had undone what the
other run learned. And a file left to a reader was not looked at at all:
a lesson file still holding `<<<<<<< here` passed, there and in `./check`.

So `--verify`, where the two sides left something to settle, tells three
things apart:

| What | Said |
|---|---|
| A file, or a line of the handoff, that came from the other side and is not as that side has it | NOT, and named. The settling does not reach it. |
| A file that was left to a reader or to the cases and still holds a marker | NOT, and named. |
| A file, or a line of the handoff, that this side alone had changed, and that the settling changed again | Accepted, and named, for whoever brings the branch next to read. |

Lesson lines stay exact in every case: one changes as any lesson does, in a
commit of its own. Where nothing was left to settle nothing is relaxed: the
tree is what the rules give or it is not.

After a settling is committed: `./bring --verify HEAD^1 HEAD^2`.

## Source
Run 013, 2026-11-20, real data: the first time two real runs met. Runs 012
and 013 had each made L0042 general; `./bring origin/lessons-and-cases` on
this branch left four files marked. The settled tree kept run 012's name
for a surface's part (`under`), so `surface/maintenance-requests.json`,
which was not marked, changed from `fits`; and this run's own lines in the
handoff were rewritten. `./bring --verify HEAD^1 HEAD^2` then said: "this
tree is NOT what the rules give", naming that surface and 12 lines of the
handoff. The instruction for the step, written by the coordinating session,
asked that what `./bring` takes not be undone; no tool could say it had not
been. That a marker left behind passes was found writing the case, not met
in the real bring. The person has not seen this lesson.

## What would be a regression
`--verify` refusing a settling that changed only the marked files and this
side's own; `--verify` accepting a settled tree in which a file or a handoff
line of the other side was changed, or a marker is left; `--verify` accepting
any change at all where the two sides left nothing to settle.

What no case catches: a settling that is wrong and touches only what it
may. That is for the cases with the product, and for `./bring --try`.

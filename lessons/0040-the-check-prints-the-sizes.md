# L0040 — The summary line of the check says the lines of the product and of the cases in force; no limit is set

## Reason
The thesis predicts that the cost of lessons and cases stays small next to
the product. Nobody was looking: the sizes were counted by hand at the end
of some runs and written into their records, and by run 007 the cases were
3,007 lines against a product of 800.

A number printed on every run is seen on the run that changes it. So the
summary line of `./check` says how many lines the product has, how many the
cases in force have, and the second over the first. A limit would be a
guess, and a case cut to fit a limit proves less; the number is there to be
read, and a jump in it is a question for the run that made it.

Counted: every line of every file in `product/` except `LABELS`, and every
line of every case of a lesson in force. Not counted: what the cases share
(`caselib.py`, `caselib.js`, the files in `surface/`), the cases that are
off, and the lesson files.

## Source
The coordinating session's instruction for run 008, 2026-11-20: "Add to the
summary line of `./check` the lines of product and the lines of the cases in
force, so that the ratio is printed on every run. Set no limit." Its
measurement: cases 3,007 lines, product 800. The person's own word was
"growth", choosing which open problem to work on. The person has not seen
this lesson.

## What would be a regression
A summary line without the two counts; a case that is off counted as in
force; a limit on either number enforced by the check.

The case plants a tree whose sizes it knows. It does not say whether a size
is too much: `runs/008-growth.md` has what the lines of the cases went to
when this lesson was written.

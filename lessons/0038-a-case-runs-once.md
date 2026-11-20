# L0038 — The check runs every case once, on a copy of the tree with the product's source taken away, and prints the seconds each took

## Reason
What one case proves by running the other cases again, the check can prove
by the way it runs them all. The case of L0019 ran every other case a second
time in a tree without the product's source. That second run cost as much as
the first, and it grew with every case anyone added: by run 007 it was half
of the whole check.

So `./check` makes one copy of the tree, compiles the product there, removes
its source, and runs the cases in that copy and nowhere else. That every case
passes without the source is then what the ordinary run says, and the case of
L0019 keeps only what the ordinary run cannot show: that the copy tells a
case which reads the source from one which only runs the product.

The check prints the seconds of each case and of the whole run, so that the
next case to grow this way is seen on the run that adds it. No limit is set.

## Source
The coordinating session's instruction for run 008, 2026-11-20, and its
measurement: `./check` about 110 s with the school library, 56 s of it in
`cases/0019-cases-know-no-source`. Measured again in the run's own session
before any change: 87 s, 42 s of it in that case. The person's own word was
"growth", choosing which open problem to work on; the measurements and the
proposal to run the cases without the source in the first place are the
coordinating session's. The person has not seen this lesson.

## What would be a regression
A case that starts the other cases of its tree; `./check` running a case
while the product's source is in the tree the case runs in; a case line or
the summary line without its seconds.

The case plants a tree whose cases write down each time they are run and
what they find in `product/`. It does not catch a case that starts other
cases by itself, as the old case of L0019 did: that shows only as seconds on
its line. The case of L0023 still runs `./check` on a copy without
`product/`, which runs the `always` cases once more there: another tree, the
base, and the only way to know the base passes.

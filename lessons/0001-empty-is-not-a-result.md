# L0001 — A check that measured nothing has failed; every check prints what it measured

## Reason
A check that says only "ok" cannot be told apart from one that looked at
nothing. Printing the count of what was examined lets the reader see an
empty input for what it is.

## Source
The method section of the torre repository ("a gate prints what it measured
and its own parameter; empty input is never a result"). Confirmed in the
wizardly-cerf run of this repository, 2026-11-18: the web check was written
to fail when the browser was missing instead of skipping, and that is the
only reason its 150 browser cases can be trusted.

## What would be a regression
A case that exits 0 with no output, or `./check` passing on a tree with no
lessons. `./check --selftest` plants both.

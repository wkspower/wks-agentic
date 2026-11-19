# L0006 — The web app on localhost is the only way in, on Python's standard library and one SQLite file

## Reason
Two entry points mean two pieces of code that write the same state, and on
2026-11-18 the command line and the web app overwrote each other's. One way
in removes the question. Standard library only means the shop starts with one
command on any machine with Python and nothing to install. Listening only on
localhost is what makes "no login" acceptable.

## Source
The person, run 001, 2026-11-19 (answers 3, 4 and 7). The overwrite is one of
the four problems found by hand in the wizardly-cerf run, 2026-11-18.
Read as written and accepted by the person, 2026-11-19 (run 005).

## What would be a regression
A second program that changes the database, an import from outside the
standard library, the shop answering on an address other than loopback, or
state kept anywhere but the one SQLite file.

Since L0019 (the person, 2026-11-19) the case no longer reads the source. An
import from outside the standard library is seen by starting the shop
without site-packages and reading Python's own record of what it imported.
"A second program that changes the database" was counted in the source
before and is now checked by no machine: it needs a reader.

## When it applies
Three choices under one label, `python stdlib and sqlite on localhost`,
because one case checks them together. A product that wants one of them
without the others is the evidence that splits this lesson (L0024).

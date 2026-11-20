# L1306 — A request has at most one worker at a time, from the register of workers and contractors; the worker can be changed or taken off while the request is not closed, and an inactive worker is given nothing new

## Reason
"Who is on it" needs one answer. The register holds a name, a trade and a
phone per worker or contractor. Assigning replaces whoever was there, and
assigning nobody takes them off; each is a row in the history. A worker who
no longer works for the building is marked inactive: what they hold stays
theirs on record, and nothing new is given to them. A closed request is
changed by reopening it, so it takes no assignment. A worker's page lists
what they hold that is not closed.

## Source
The person, run 013, 2026-11-20: "Accepted", typed, to the sixteen recommendations asked in one round before building (answer 8). The builder's: no assignment on a closed request; an
inactive worker keeps what they hold; the worker's page.

## What would be a regression
A request assigned to a worker who is inactive or does not exist; an
assignment on a done or cancelled request; an assignment with no row in the
history; a worker's page without the open requests they hold.

# L1209 — A connection that is open and sends nothing holds nobody up: the next request is answered all the same

## Reason
A browser opens connections it does not use yet, to have one ready for the
next click. A server that takes one connection at a time waits for that
silent one to speak, and meanwhile answers nobody: the page that was asked
for does not come, with a queue at the till. Nothing is wrong in any
request, so no check that sends one request after another sees it.

So each connection is served on its own, and what the requests do to the
one SQLite file still happens one request at a time.

## Source
A defect found in run 012, 2026-11-20, by the agent, not by a person at a
browser: thinking about how Chromium keeps spare connections, it opened a
connection to the canteen's first build, sent nothing on it, and asked for
the till on another. No answer came in 5 seconds. All 29 cases in force had
passed; the browser cases had not met it. Whether a person's browser would
have stalled on that build, and for how long, was not tried. The label is
`local web server` because nothing in it is the canteen's; the pet shop and
the library declare that label too, and what the case says of their builds
is in the run record. The person has not seen this lesson.

## What would be a regression
A request that waits while another connection is open and silent.

The case holds one silent connection open and allows 2 seconds. It does
not try many of them, or a connection that sends half a request.
